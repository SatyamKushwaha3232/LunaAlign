import cv2
import numpy as np


def create_match_visualization(
    reference_image,
    target_image,
    reference_keypoints,
    target_keypoints,
    good_matches,
    mask,
    output_path
):
    """
    Create a visual correspondence map.

    Green lines = RANSAC inlier matches
    Red lines   = rejected/outlier matches
    """

    if reference_image is None:
        raise ValueError("Reference image is empty.")

    if target_image is None:
        raise ValueError("Target image is empty.")

    if mask is None:
        raise ValueError("RANSAC mask is empty.")

    mask = mask.ravel().tolist()

    match_image = cv2.drawMatches(
        reference_image,
        reference_keypoints,
        target_image,
        target_keypoints,
        good_matches,
        None,
        matchColor=(0, 255, 0),
        singlePointColor=(255, 255, 255),
        matchesMask=mask,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
    )

    saved = cv2.imwrite(
        output_path,
        match_image
    )

    if not saved:
        raise ValueError(
            f"Unable to save match visualization: {output_path}"
        )

    return match_image


def create_difference_visualization(
    reference_image,
    registered_image,
    output_path
):
    """
    Create a visual difference map between
    reference and registered images.
    """

    if reference_image is None:
        raise ValueError("Reference image is empty.")

    if registered_image is None:
        raise ValueError("Registered image is empty.")

    if reference_image.shape != registered_image.shape:
        registered_image = cv2.resize(
            registered_image,
            (
                reference_image.shape[1],
                reference_image.shape[0]
            )
        )

    difference = cv2.absdiff(
        reference_image,
        registered_image
    )

    difference = cv2.normalize(
        difference,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    saved = cv2.imwrite(
        output_path,
        difference
    )

    if not saved:
        raise ValueError(
            f"Unable to save difference visualization: {output_path}"
        )

    return difference