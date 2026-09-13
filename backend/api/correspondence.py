from pathlib import Path
from uuid import uuid4

import cv2
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
):

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
    # 2. PREPROCESSING
    # =========================================================

    try:

        reference_processed = (
            preprocess_image(
                str(reference_path)
            )
        )

        target_processed = (
            preprocess_image(
                str(target_path)
            )
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

    try:

        (
            reference_keypoints,
            reference_descriptors,
        ) = extract_multiscale_features(
            reference_image,
            scales=request.scales,
        )

        (
            target_keypoints,
            target_descriptors,
        ) = extract_multiscale_features(
            target_image,
            scales=request.scales,
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

    job_id = str(uuid4())

    aligned_path = (
        OUTPUT_DIR
        / f"{job_id}_aligned.png"
    )

    correspondence_path = (
        OUTPUT_DIR
        / f"{job_id}_correspondence.png"
    )

    difference_path = (
        OUTPUT_DIR
        / f"{job_id}_difference.png"
    )

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

    return {

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

            "scales": list(
                request.scales
            ),

            "illumination_normalization": True,

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

        # -----------------------------------------------------
        # OUTPUT FILES
        # -----------------------------------------------------

        "outputs": {

            "aligned_image": (
                f"/outputs/"
                f"{aligned_path.name}"
            ),

            "correspondence_map": (
                f"/outputs/"
                f"{correspondence_path.name}"
            ),

            "difference_map": (
                f"/outputs/"
                f"{difference_path.name}"
            ),

        },

    }