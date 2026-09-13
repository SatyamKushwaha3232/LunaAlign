import cv2
import numpy as np


def _get_match_points(
    reference_keypoints,
    target_keypoints,
    good_matches
):
    """
    Convert feature matches into point arrays.

    Target image = moving image
    Reference image = fixed image

    Transformation maps:
        target -> reference
    """

    reference_points = np.float32([
        reference_keypoints[m.queryIdx].pt
        for m in good_matches
    ]).reshape(-1, 1, 2)

    target_points = np.float32([
        target_keypoints[m.trainIdx].pt
        for m in good_matches
    ]).reshape(-1, 1, 2)

    return reference_points, target_points


def estimate_homography(
    reference_keypoints,
    target_keypoints,
    good_matches,
    reprojection_threshold=5.0
):
    """
    Estimate a projective Homography using RANSAC.

    Maps target/moving image coordinates
    into reference/fixed image coordinates.

    Minimum matches required: 4

    Returns:
        homography: 3x3 transformation matrix
        mask: RANSAC inlier/outlier mask
    """

    if len(good_matches) < 4:
        raise ValueError(
            "At least 4 matches are required "
            "to estimate homography."
        )

    reference_points, target_points = _get_match_points(
        reference_keypoints,
        target_keypoints,
        good_matches
    )

    homography, mask = cv2.findHomography(
        target_points,
        reference_points,
        cv2.RANSAC,
        reprojection_threshold
    )

    if homography is None or mask is None:
        raise ValueError(
            "Unable to estimate a valid homography."
        )

    return homography, mask


def estimate_affine(
    reference_keypoints,
    target_keypoints,
    good_matches,
    reprojection_threshold=5.0
):
    """
    Estimate a full affine transformation using RANSAC.

    Supports:
        - translation
        - rotation
        - scaling
        - shear

    Minimum matches required: 3

    Returns:
        affine_matrix: 3x3 transformation matrix
        mask: RANSAC inlier/outlier mask
    """

    if len(good_matches) < 3:
        raise ValueError(
            "At least 3 matches are required "
            "to estimate affine transformation."
        )

    reference_points, target_points = _get_match_points(
        reference_keypoints,
        target_keypoints,
        good_matches
    )

    affine_matrix, mask = cv2.estimateAffine2D(
        target_points,
        reference_points,
        method=cv2.RANSAC,
        ransacReprojThreshold=reprojection_threshold,
        maxIters=5000,
        confidence=0.99,
        refineIters=10
    )

    if affine_matrix is None or mask is None:
        raise ValueError(
            "Unable to estimate a valid affine transformation."
        )

    # Convert 2x3 affine matrix into 3x3 matrix
    affine_3x3 = np.vstack([
        affine_matrix,
        [0.0, 0.0, 1.0]
    ])

    return affine_3x3, mask


def estimate_similarity(
    reference_keypoints,
    target_keypoints,
    good_matches,
    reprojection_threshold=5.0
):
    """
    Estimate a similarity transformation using RANSAC.

    Supports:
        - translation
        - rotation
        - uniform scaling

    Does NOT support:
        - shear
        - perspective distortion

    Minimum matches required: 2

    Returns:
        similarity_matrix: 3x3 transformation matrix
        mask: RANSAC inlier/outlier mask
    """

    if len(good_matches) < 2:
        raise ValueError(
            "At least 2 matches are required "
            "to estimate similarity transformation."
        )

    reference_points, target_points = _get_match_points(
        reference_keypoints,
        target_keypoints,
        good_matches
    )

    similarity_matrix, mask = cv2.estimateAffinePartial2D(
        target_points,
        reference_points,
        method=cv2.RANSAC,
        ransacReprojThreshold=reprojection_threshold,
        maxIters=5000,
        confidence=0.99,
        refineIters=10
    )

    if similarity_matrix is None or mask is None:
        raise ValueError(
            "Unable to estimate a valid similarity transformation."
        )

    # Convert 2x3 matrix into 3x3 matrix
    similarity_3x3 = np.vstack([
        similarity_matrix,
        [0.0, 0.0, 1.0]
    ])

    return similarity_3x3, mask


def estimate_geometry(
    reference_keypoints,
    target_keypoints,
    good_matches,
    model="homography",
    reprojection_threshold=5.0
):
    """
    Estimate the requested geometric transformation.

    Supported models:
        similarity
        affine
        homography

    All transformations are returned as
    a 3x3 matrix for a common downstream interface.
    """

    model = model.lower().strip()

    if model == "similarity":
        return estimate_similarity(
            reference_keypoints,
            target_keypoints,
            good_matches,
            reprojection_threshold
        )

    if model == "affine":
        return estimate_affine(
            reference_keypoints,
            target_keypoints,
            good_matches,
            reprojection_threshold
        )

    if model == "homography":
        return estimate_homography(
            reference_keypoints,
            target_keypoints,
            good_matches,
            reprojection_threshold
        )

    raise ValueError(
        "Unsupported geometric model. "
        "Choose similarity, affine or homography."
    )


def calculate_reprojection_errors(
    reference_keypoints,
    target_keypoints,
    good_matches,
    homography,
    mask
):
    """
    Calculate geometric reprojection error
    for RANSAC inlier matches.

    The supplied transformation can be:
        - similarity
        - affine
        - homography

    Lower error means better geometric consistency.
    """

    if homography is None:
        raise ValueError(
            "Transformation matrix is empty."
        )

    if mask is None:
        raise ValueError(
            "RANSAC mask is empty."
        )

    reference_points, target_points = _get_match_points(
        reference_keypoints,
        target_keypoints,
        good_matches
    )

    projected_points = cv2.perspectiveTransform(
        target_points,
        homography
    )

    errors = np.linalg.norm(
        reference_points - projected_points,
        axis=2
    ).reshape(-1)

    inlier_mask = mask.ravel().astype(bool)

    inlier_errors = errors[inlier_mask]

    if len(inlier_errors) == 0:
        return {
            "mean_error": 0.0,
            "median_error": 0.0,
            "max_error": 0.0,
            "min_error": 0.0,
        }

    return {
        "mean_error": round(
            float(np.mean(inlier_errors)),
            4
        ),
        "median_error": round(
            float(np.median(inlier_errors)),
            4
        ),
        "max_error": round(
            float(np.max(inlier_errors)),
            4
        ),
        "min_error": round(
            float(np.min(inlier_errors)),
            4
        ),
    }


def get_geometry_summary(
    good_matches,
    mask,
    reprojection_errors=None,
    model="homography"
):
    """
    Return geometric registration statistics.
    """

    total_matches = len(good_matches)

    inliers = int(
        mask.ravel().sum()
    )

    outliers = (
        total_matches -
        inliers
    )

    inlier_ratio = (
        (inliers / total_matches) * 100
        if total_matches > 0
        else 0.0
    )

    summary = {
        "model": model,
        "total_matches": total_matches,
        "inliers": inliers,
        "outliers": outliers,
        "inlier_ratio": round(
            inlier_ratio,
            2
        ),
    }

    if reprojection_errors is not None:
        summary["reprojection_error"] = (
            reprojection_errors
        )

    return summary