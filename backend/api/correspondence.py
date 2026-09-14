from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
import json
import time
from threading import Thread

import cv2
import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from processing.preprocessing import preprocess_image
from processing.features import extract_multiscale_features
from processing.matching import (
    match_descriptors,
    get_match_summary,
)
from processing.geometry import (
    estimate_geometry,
    calculate_reprojection_errors,
    get_geometry_summary,
)
from processing.registration import register_image
from processing.visualization import (
    create_match_visualization,
    create_difference_visualization,
)
from processing.metrics import calculate_quality_metrics
from processing.report import create_scientific_report
from api.upload import build_dataset_metadata
from database import create_job, get_job as get_saved_job, update_job


# =============================================================
# ROUTER
# =============================================================

router = APIRouter(
    prefix="/api/v1/correspondence",
    tags=["Correspondence"],
)


# =============================================================
# DIRECTORIES
# =============================================================

INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/output")

INPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

JOBS = {}

PIPELINE_STAGES = [
    "queued", "metadata", "preprocessing", "features", "matching",
    "geometry", "registration", "metrics", "visualization", "completed",
]


def set_job_stage(job_id, stage):
    if job_id and job_id in JOBS:
        JOBS[job_id].update({"status": "processing", "stage": stage})
    if job_id:
        update_job(job_id, status="processing", stage=stage)


# =============================================================
# REQUEST MODEL
# =============================================================

class CorrespondenceRequest(BaseModel):
    """
    Request schema for lunar image correspondence.

    reference_filename:
        Fixed/reference image.

    target_filename:
        Moving/target image.

    ratio_threshold:
        Lowe's ratio test threshold.

    reprojection_threshold:
        RANSAC reprojection error threshold in pixels.

    scales:
        Image scales used for multi-scale SIFT.

    geometric_model:
        Similarity, Affine or Homography.
    """

    reference_filename: str

    target_filename: str

    ratio_threshold: float = Field(
        default=0.75,
        gt=0.0,
        lt=1.0,
    )

    reprojection_threshold: float = Field(
        default=5.0,
        gt=0.0,
    )

    scales: tuple[float, ...] = (
        1.0,
        0.75,
        0.5,
    )

    geometric_model: str = "homography"

    reference_modality: str | None = None
    target_modality: str | None = None
    sun_angle_compensation: bool = True
    scale_aware_matching: bool = True


# =============================================================
# HELPER FUNCTIONS
# =============================================================

def calculate_alignment_score(
    reference_image,
    aligned_image,
):
    """
    Calculate a simple pixel-difference based
    alignment score.

    Score:
        100 = very low difference
        0   = very high difference
    """

    if reference_image is None:
        raise ValueError(
            "Reference image is empty."
        )

    if aligned_image is None:
        raise ValueError(
            "Aligned image is empty."
        )

    reference_height, reference_width = (
        reference_image.shape[:2]
    )

    if aligned_image.shape[:2] != (
        reference_height,
        reference_width,
    ):
        aligned_image = cv2.resize(
            aligned_image,
            (
                reference_width,
                reference_height,
            ),
            interpolation=cv2.INTER_LINEAR,
        )

    difference = cv2.absdiff(
        reference_image,
        aligned_image,
    )

    mean_difference = float(
        difference.mean()
    )

    score = (
        100.0
        - (
            mean_difference
            / 255.0
            * 100.0
        )
    )

    return round(
        max(
            0.0,
            min(
                100.0,
                score,
            ),
        ),
        2,
    )


def get_minimum_matches(
    geometric_model: str,
):
    """
    Return minimum number of matches required
    by each geometric transformation.
    """

    minimum_matches = {
        "similarity": 2,
        "affine": 3,
        "homography": 4,
    }

    return minimum_matches[
        geometric_model
    ]


# =============================================================
# CORRESPONDENCE ENDPOINT
# =============================================================

@router.post("")
def calculate_correspondence(
    request: CorrespondenceRequest,
    job_id: str | None = None,
):

    started_at = time.perf_counter()
    job_id = job_id or str(uuid4())
    # =========================================================
    # 0. VALIDATE GEOMETRIC MODEL
    # =========================================================

    geometric_model = (
        request.geometric_model
        .lower()
        .strip()
    )

    allowed_models = {
        "similarity",
        "affine",
        "homography",
    }

    if geometric_model not in allowed_models:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported geometric model. "
                "Choose similarity, affine or homography."
            ),
        )

    # =========================================================
    # 1. LOCATE INPUT IMAGES
    # =========================================================

    reference_path = (
        INPUT_DIR
        / Path(
            request.reference_filename
        ).name
    )

    target_path = (
        INPUT_DIR
        / Path(
            request.target_filename
        ).name
    )

    if not reference_path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "Reference image not found: "
                f"{request.reference_filename}"
            ),
        )

    if not target_path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "Target image not found: "
                f"{request.target_filename}"
            ),
        )

    # =========================================================
    set_job_stage(job_id, "metadata")
    # 2. PREPROCESSING
    # =========================================================

    set_job_stage(job_id, "preprocessing")
    try:

        reference_metadata = build_dataset_metadata(reference_path)
        target_metadata = build_dataset_metadata(target_path)
        reference_processed = preprocess_image(str(reference_path))
        target_processed = preprocess_image(
            str(target_path),
            reference_metadata.get("illumination"),
            target_metadata.get("illumination"),
            request.sun_angle_compensation,
        )

        reference_image = (
            reference_processed[
                "enhanced"
            ]
        )

        target_image = (
            target_processed[
                "enhanced"
            ]
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Preprocessing failed: "
                f"{error}"
            ),
        )

    # =========================================================
    # 3. MULTI-SCALE FEATURE EXTRACTION
    # =========================================================

    set_job_stage(job_id, "features")
    try:

        (
            reference_keypoints,
            reference_descriptors,
        ) = extract_multiscale_features(
            reference_image,
            scales=request.scales if request.scale_aware_matching else (1.0,),
        )

        (
            target_keypoints,
            target_descriptors,
        ) = extract_multiscale_features(
            target_image,
            scales=request.scales if request.scale_aware_matching else (1.0,),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Feature extraction failed: "
                f"{error}"
            ),
        )

    # =========================================================
    # 4. FEATURE VALIDATION
    # =========================================================

    if reference_descriptors is None:

        raise HTTPException(
            status_code=422,
            detail=(
                "No features detected "
                "in reference image."
            ),
        )

    if target_descriptors is None:

        raise HTTPException(
            status_code=422,
            detail=(
                "No features detected "
                "in target image."
            ),
        )

    # =========================================================
    # 5. FEATURE MATCHING
    # =========================================================

    set_job_stage(job_id, "matching")
    try:

        good_matches = match_descriptors(
            reference_descriptors,
            target_descriptors,
            ratio_threshold=(
                request.ratio_threshold
            ),
        )

        match_summary = (
            get_match_summary(
                good_matches
            )
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Feature matching failed: "
                f"{error}"
            ),
        )

    # =========================================================
    # 6. MINIMUM MATCH VALIDATION
    # =========================================================

    minimum_matches = (
        get_minimum_matches(
            geometric_model
        )
    )

    if len(good_matches) < minimum_matches:

        raise HTTPException(
            status_code=422,
            detail=(
                f"Not enough good matches "
                f"for {geometric_model} "
                f"transformation. "
                f"Minimum required: "
                f"{minimum_matches}. "
                f"Detected: "
                f"{len(good_matches)}."
            ),
        )

    # =========================================================
    # 7. GEOMETRIC TRANSFORMATION + RANSAC
    # =========================================================

    set_job_stage(job_id, "geometry")
    try:

        (
            transformation_matrix,
            mask,
        ) = estimate_geometry(
            reference_keypoints,
            target_keypoints,
            good_matches,
            model=geometric_model,
            reprojection_threshold=(
                request.reprojection_threshold
            ),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Geometric transformation "
                "failed: "
                f"{error}"
            ),
        )

    if (
        transformation_matrix is None
        or mask is None
    ):

        raise HTTPException(
            status_code=422,
            detail=(
                "Unable to estimate a valid "
                f"{geometric_model} transformation."
            ),
        )

    # =========================================================
    # 8. REPROJECTION ERROR
    # =========================================================

    try:

        reprojection_errors = (
            calculate_reprojection_errors(
                reference_keypoints,
                target_keypoints,
                good_matches,
                transformation_matrix,
                mask,
            )
        )

        geometry_summary = (
            get_geometry_summary(
                good_matches,
                mask,
                reprojection_errors,
                model=geometric_model,
            )
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Reprojection error "
                "calculation failed: "
                f"{error}"
            ),
        )

    # =========================================================
    # 9. IMAGE REGISTRATION
    # =========================================================

    set_job_stage(job_id, "registration")
    try:

        reference_height, reference_width = (
            reference_image.shape[:2]
        )

        aligned_image = register_image(
            target_image,
            transformation_matrix,
            (
                reference_width,
                reference_height,
            ),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Image registration failed: "
                f"{error}"
            ),
        )

    # =========================================================
    # 10. SCIENTIFIC QUALITY METRICS
    # =========================================================

    set_job_stage(job_id, "metrics")
    try:

        quality_metrics = (
            calculate_quality_metrics(
                reference_image,
                aligned_image,
            )
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Scientific metrics "
                "calculation failed: "
                f"{error}"
            ),
        )

    # =========================================================
    # 11. ALIGNMENT SCORE
    # =========================================================

    try:

        alignment_score = (
            calculate_alignment_score(
                reference_image,
                aligned_image,
            )
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Alignment score "
                "calculation failed: "
                f"{error}"
            ),
        )

    # =========================================================
    # 12. CREATE JOB ID
    # =========================================================

    set_job_stage(job_id, "visualization")

    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    aligned_path = job_dir / "aligned.png"
    correspondence_path = job_dir / "matches.png"
    difference_path = job_dir / "difference.png"
    reference_preprocessed_path = job_dir / "reference_preprocessed.png"
    target_preprocessed_path = job_dir / "target_preprocessed.png"

    # =========================================================
    # 13. SAVE ALIGNED IMAGE
    # =========================================================

    saved = cv2.imwrite(
        str(aligned_path),
        aligned_image,
    )

    if not saved:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to save "
                "aligned image."
            ),
        )

    if not cv2.imwrite(str(reference_preprocessed_path), reference_image):
        raise HTTPException(status_code=500, detail="Unable to save reference preprocessing preview.")
    if not cv2.imwrite(str(target_preprocessed_path), target_image):
        raise HTTPException(status_code=500, detail="Unable to save target preprocessing preview.")

    # =========================================================
    # 14. CREATE CORRESPONDENCE MAP
    # =========================================================

    try:

        create_match_visualization(
            reference_image,
            target_image,
            reference_keypoints,
            target_keypoints,
            good_matches,
            mask,
            str(correspondence_path),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Correspondence visualization "
                "failed: "
                f"{error}"
            ),
        )

    # =========================================================
    # 15. CREATE DIFFERENCE MAP
    # =========================================================

    try:

        create_difference_visualization(
            reference_image,
            aligned_image,
            str(difference_path),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Difference visualization "
                "failed: "
                f"{error}"
            ),
        )

    # =========================================================
    # 16. FINAL RESPONSE
    # =========================================================

    reprojection_mean = geometry_summary["reprojection_error"]["mean_error"]
    confidence = round(max(0, min(100, (
        geometry_summary["inlier_ratio"] * 0.55
        + alignment_score * 0.20
        + max(0, 100 - reprojection_mean * 10) * 0.25
    ))), 2)
    result = {

        "status": "completed",

        "job_id": job_id,

        # -----------------------------------------------------
        # INPUT
        # -----------------------------------------------------

        "input": {

            "reference": (
                reference_path.name
            ),

            "target": (
                target_path.name
            ),

        },

        # -----------------------------------------------------
        # PROCESSING
        # -----------------------------------------------------

        "processing": {

            "method": (
                "SIFT Multi-Scale"
            ),

            "scales": list(request.scales if request.scale_aware_matching else (1.0,)),

            "illumination_normalization": True,
            "sun_angle_compensation": request.sun_angle_compensation,
            "scale_aware_matching": request.scale_aware_matching,

            "ratio_threshold": (
                request.ratio_threshold
            ),

            "reprojection_threshold": (
                request.reprojection_threshold
            ),

            "geometric_model": (
                geometric_model
            ),

        },

        # -----------------------------------------------------
        # FEATURES
        # -----------------------------------------------------

        "features": {

            "reference_keypoints": (
                len(reference_keypoints)
            ),

            "target_keypoints": (
                len(target_keypoints)
            ),

            "reference_descriptors": (
                0
                if reference_descriptors is None
                else len(
                    reference_descriptors
                )
            ),

            "target_descriptors": (
                0
                if target_descriptors is None
                else len(
                    target_descriptors
                )
            ),

            "descriptor_dimension": (
                int(
                    reference_descriptors.shape[1]
                )
                if reference_descriptors is not None
                else 0
            ),

        },

        # -----------------------------------------------------
        # MATCHING
        # -----------------------------------------------------

        "matching": match_summary,

        # -----------------------------------------------------
        # GEOMETRY
        # -----------------------------------------------------

        "geometry": geometry_summary,

        # -----------------------------------------------------
        # TRANSFORMATION
        # -----------------------------------------------------

        "transformation": {

            "model": (
                geometric_model
            ),

            "matrix": (
                transformation_matrix.tolist()
            ),

        },

        # -----------------------------------------------------
        # REGISTRATION
        # -----------------------------------------------------

        "registration": {

            "alignment_score": (
                alignment_score
            ),

            "quality_metrics": (
                quality_metrics
            ),

        },

        "metadata": {"reference": reference_metadata, "target": target_metadata},
        "confidence": {"label": "LunaAlgin-derived confidence", "score": confidence},
        "processing_time_seconds": round(time.perf_counter() - started_at, 2),

        # -----------------------------------------------------
        # OUTPUT FILES
        # -----------------------------------------------------

        "outputs": {

            "aligned_image": (
                f"/outputs/{job_id}/aligned.png"
            ),

            "correspondence_map": (
                f"/outputs/{job_id}/matches.png"
            ),

            "difference_map": (
                f"/outputs/{job_id}/difference.png"
            ),

            "reference_preprocessed": f"/outputs/{job_id}/reference_preprocessed.png",
            "target_preprocessed": f"/outputs/{job_id}/target_preprocessed.png",

        },

    }
    result["outputs"].update({
        "metadata": f"/outputs/{job_id}/metadata.json",
        "metrics": f"/outputs/{job_id}/metrics.json",
        "result": f"/outputs/{job_id}/result.json",
    })
    (job_dir / "metadata.json").write_text(json.dumps(result["metadata"], indent=2), encoding="utf-8")
    (job_dir / "metrics.json").write_text(json.dumps(result["registration"]["quality_metrics"], indent=2), encoding="utf-8")
    (job_dir / "transformation.json").write_text(json.dumps(result["transformation"], indent=2), encoding="utf-8")
    (job_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    JOBS[job_id] = {"status": "completed", "stage": "completed", "completed_at": datetime.now(timezone.utc).isoformat(), "result": result}
    update_job(job_id, status="completed", stage="completed", completed_at=datetime.now(timezone.utc), result=result)
    return result


def _run_correspondence_job(job_id, request):
    try:
        calculate_correspondence(request, job_id=job_id)
    except HTTPException as error:
        _save_failure_result(job_id, request, str(error.detail))
    except Exception as error:
        _save_failure_result(job_id, request, str(error))


def _save_failure_result(job_id, request, reason):
    """Persist useful diagnostic output for an unsuccessful run."""
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    outputs = {"diagnostic": f"/outputs/{job_id}/failure.json"}
    for role, filename in (("reference", request.reference_filename), ("target", request.target_filename)):
        source = INPUT_DIR / Path(filename).name
        try:
            processed = preprocess_image(str(source))["enhanced"]
            artifact = f"{role}_preprocessed.png"
            cv2.imwrite(str(job_dir / artifact), processed)
            outputs[f"{role}_preprocessed"] = f"/outputs/{job_id}/{artifact}"
        except Exception:
            pass
    result = {
        "status": "failed", "job_id": job_id,
        "input": {"reference": Path(request.reference_filename).name, "target": Path(request.target_filename).name},
        "error": {"message": reason, "guidance": "Choose images with an overlapping lunar footprint, or use the synthetic ground-truth test to validate the pipeline."},
        "outputs": outputs,
    }
    (job_dir / "failure.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    JOBS[job_id] = {"status": "failed", "stage": "failed", "error": reason, "result": result}
    update_job(job_id, status="failed", stage="failed", error=reason, result=result)


@router.post("/jobs")
def start_correspondence_job(request: CorrespondenceRequest):
    job_id = str(uuid4())
    JOBS[job_id] = {"status": "queued", "stage": "queued", "created_at": datetime.now(timezone.utc).isoformat()}
    create_job(job_id)
    Thread(target=_run_correspondence_job, args=(job_id, request), daemon=True).start()
    return {"status": "queued", "job_id": job_id, "stage": "queued", "stages": PIPELINE_STAGES}


def create_synthetic_lunar_scene(width=900, height=650):
    """Create a deterministic crater-texture scene for ground-truth validation."""
    rng = np.random.default_rng(26166)
    scene = rng.normal(92, 18, (height, width)).clip(0, 255).astype(np.uint8)
    scene = cv2.GaussianBlur(scene, (0, 0), 1.2)
    for _ in range(140):
        x, y = int(rng.integers(20, width - 20)), int(rng.integers(20, height - 20))
        radius = int(rng.integers(4, 28))
        cv2.circle(scene, (x, y), radius, int(rng.integers(45, 100)), -1, cv2.LINE_AA)
        cv2.circle(scene, (x - radius // 4, y - radius // 4), radius, int(rng.integers(110, 180)), 1, cv2.LINE_AA)
    return cv2.normalize(scene, None, 0, 255, cv2.NORM_MINMAX)


@router.post("/synthetic")
def run_synthetic_validation():
    """Run the production pipeline on a known transform; no external data needed."""
    reference = create_synthetic_lunar_scene()
    forward = np.array([[0.93, -0.12, 61.0], [0.12, 0.93, -34.0], [0.00003, -0.00002, 1.0]], dtype=np.float32)
    target = cv2.warpPerspective(reference, forward, (reference.shape[1], reference.shape[0]))
    target = cv2.convertScaleAbs(target, alpha=1.10, beta=8)
    reference_name, target_name = "synthetic_reference.png", "synthetic_target.png"
    cv2.imwrite(str(INPUT_DIR / reference_name), reference)
    cv2.imwrite(str(INPUT_DIR / target_name), target)
    result = calculate_correspondence(CorrespondenceRequest(
        reference_filename=reference_name, target_filename=target_name,
        geometric_model="homography", ratio_threshold=0.75, reprojection_threshold=5.0,
    ))
    expected = np.linalg.inv(forward)
    estimated = np.array(result["transformation"]["matrix"], dtype=np.float64)
    corners = np.float32([[[0, 0], [reference.shape[1], 0], [reference.shape[1], reference.shape[0]], [0, reference.shape[0]]]])
    expected_corners = cv2.perspectiveTransform(corners, expected)[0]
    estimated_corners = cv2.perspectiveTransform(corners, estimated)[0]
    result["validation"] = {
        "type": "synthetic ground truth",
        "known_transform": expected.round(6).tolist(),
        "corner_rmse_px": round(float(np.sqrt(np.mean((expected_corners - estimated_corners) ** 2))), 4),
        "test_conditions": "rotation, scale, translation, perspective and brightness variation",
    }
    job_dir = OUTPUT_DIR / result["job_id"]
    (job_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    JOBS[result["job_id"]]["result"] = result
    return result


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = JOBS.get(job_id) or get_saved_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return {key: value for key, value in job.items() if key != "result"}


@router.get("/results/{job_id}")
def get_result(job_id: str):
    job = JOBS.get(job_id) or get_saved_job(job_id, include_result=True)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job["result"]


@router.post("/report/{job_id}")
def generate_report(job_id: str):
    job = JOBS.get(job_id) or get_saved_job(job_id, include_result=True)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found. Run correspondence before requesting a report.")
    report_path = create_scientific_report(job["result"], OUTPUT_DIR / job_id)
    job["result"]["outputs"]["report"] = f"/outputs/{job_id}/{report_path.name}"
    (OUTPUT_DIR / job_id / "result.json").write_text(json.dumps(job["result"], indent=2), encoding="utf-8")
    update_job(job_id, result=job["result"])
    return {"status": "completed", "report_url": job["result"]["outputs"]["report"]}
