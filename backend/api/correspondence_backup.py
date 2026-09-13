from pathlib import Path
import uuid

import cv2
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from processing.preprocessing import preprocess_image
from processing.features import extract_features
from processing.matching import (
    match_descriptors,
    get_match_summary,
)
from processing.geometry import (
    estimate_homography,
    get_geometry_summary,
)
from processing.registration import (
    register_image,
    calculate_alignment_score,
)
from processing.visualization import (
    create_match_visualization,
    create_difference_visualization,
)


router = APIRouter(
    prefix="/api/v1/correspondence",
    tags=["Correspondence"],
)


INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/output")

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class CorrespondenceRequest(BaseModel):
    reference_filename: str
    target_filename: str
    ratio_threshold: float = 0.75
    reprojection_threshold: float = 5.0


@router.post("")
def run_correspondence(request: CorrespondenceRequest):
    """
    Run complete LunaAlgin correspondence pipeline.

    Reference image = fixed image
    Target image    = moving image
    """

    reference_path = INPUT_DIR / Path(
        request.reference_filename
    ).name

    target_path = INPUT_DIR / Path(
        request.target_filename
    ).name

    # --------------------------------------------------
    # 1. Validate input files
    # --------------------------------------------------

    if not reference_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Reference image not found: {reference_path.name}",
        )

    if not target_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Target image not found: {target_path.name}",
        )

    # --------------------------------------------------
    # 2. Create unique job ID
    # --------------------------------------------------

    job_id = str(uuid.uuid4())

    aligned_path = OUTPUT_DIR / f"{job_id}_aligned.png"
    match_path = OUTPUT_DIR / f"{job_id}_correspondence.png"
    difference_path = OUTPUT_DIR / f"{job_id}_difference.png"

    try:

        # --------------------------------------------------
        # 3. Preprocessing
        # --------------------------------------------------

        reference_processed = preprocess_image(
            str(reference_path)
        )

        target_processed = preprocess_image(
            str(target_path)
        )

        reference_enhanced = reference_processed["enhanced"]
        target_enhanced = target_processed["enhanced"]

        # --------------------------------------------------
        # 4. SIFT feature extraction
        # --------------------------------------------------

        reference_keypoints, reference_descriptors = (
            extract_features(reference_enhanced)
        )

        target_keypoints, target_descriptors = (
            extract_features(target_enhanced)
        )

        # --------------------------------------------------
        # 5. Feature matching
        # --------------------------------------------------

        good_matches = match_descriptors(
            reference_descriptors,
            target_descriptors,
            ratio_threshold=request.ratio_threshold,
        )

        match_summary = get_match_summary(
            good_matches
        )

        # --------------------------------------------------
        # 6. RANSAC + Homography
        # --------------------------------------------------

        if len(good_matches) < 4:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Not enough reliable feature matches. "
                    "At least 4 matches are required."
                ),
            )

        homography, mask = estimate_homography(
            reference_keypoints,
            target_keypoints,
            good_matches,
            reprojection_threshold=request.reprojection_threshold,
        )

        geometry_summary = get_geometry_summary(
            mask
        )

        # --------------------------------------------------
        # 7. Image registration
        # --------------------------------------------------

        height, width = reference_enhanced.shape

        registered_image = register_image(
            target_processed["original"],
            homography,
            (width, height),
        )

        cv2.imwrite(
            str(aligned_path),
            registered_image,
        )

        # --------------------------------------------------
        # 8. Alignment score
        # --------------------------------------------------

        alignment_score = calculate_alignment_score(
            reference_processed["original"],
            registered_image,
        )

        # --------------------------------------------------
        # 9. Correspondence visualization
        # --------------------------------------------------

        create_match_visualization(
            reference_processed["original"],
            target_processed["original"],
            reference_keypoints,
            target_keypoints,
            good_matches,
            mask,
            str(match_path),
        )

        # --------------------------------------------------
        # 10. Difference visualization
        # --------------------------------------------------

        create_difference_visualization(
            reference_processed["original"],
            registered_image,
            str(difference_path),
        )

        # --------------------------------------------------
        # 11. Final response
        # --------------------------------------------------

        return {
            "status": "completed",
            "job_id": job_id,

            "input": {
                "reference": reference_path.name,
                "target": target_path.name,
            },

            "features": {
                "reference_keypoints": len(
                    reference_keypoints
                ),
                "target_keypoints": len(
                    target_keypoints
                ),
            },

            "matching": match_summary,

            "geometry": geometry_summary,

            "homography": homography.tolist(),

            "registration": {
                "alignment_score": alignment_score,
            },

            "outputs": {
                "aligned_image": f"/outputs/{aligned_path.name}",
                "correspondence_map": f"/outputs/{match_path.name}",
                "difference_map": f"/outputs/{difference_path.name}",
            },
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Correspondence processing failed: {error}",
        )