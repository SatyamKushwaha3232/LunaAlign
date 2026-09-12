import cv2
import numpy as np


def estimate_homography(
    reference_keypoints,
    target_keypoints,
    good_matches,
    reprojection_threshold=5.0
):
    """
    Estimate geometric transformation between
    reference and target images using RANSAC.

    Returns:
        homography: 3x3 transformation matrix
        mask: RANSAC inlier/outlier mask
    """

    if len(good_matches) < 4:
        raise ValueError(
            "At least 4 good matches are required "
            "to estimate homography."
        )

    reference_points = np.float32([
        reference_keypoints[m.queryIdx].pt
        for m in good_matches
    ]).reshape(-1, 1, 2)

    target_points = np.float32([
        target_keypoints[m.trainIdx].pt
        for m in good_matches
    ]).reshape(-1, 1, 2)

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


def get_geometry_summary(mask):
    """
    Calculate RANSAC inlier/outlier statistics.
    """

    if mask is None:
        return {
            "total_matches": 0,
            "inliers": 0,
            "outliers": 0,
            "inlier_ratio": 0.0,
        }

    mask = mask.ravel()

    total_matches = len(mask)
    inliers = int(np.sum(mask == 1))
    outliers = int(np.sum(mask == 0))

    inlier_ratio = (
        inliers / total_matches
        if total_matches > 0
        else 0.0
    )

    return {
        "total_matches": total_matches,
        "inliers": inliers,
        "outliers": outliers,
        "inlier_ratio": round(inlier_ratio * 100, 2),
    }