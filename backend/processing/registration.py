import cv2


def register_image(
    target_image,
    homography,
    output_size
):
    """
    Warp the target/moving image into the
    reference/fixed image coordinate system.

    Parameters:
        target_image:
            Moving/target image.

        homography:
            3x3 transformation matrix obtained
            using RANSAC.

        output_size:
            (width, height) of reference image.

    Returns:
        registered_image:
            Geometrically aligned target image.
    """

    if target_image is None:
        raise ValueError("Target image is empty.")

    if homography is None:
        raise ValueError("Homography matrix is empty.")

    width, height = output_size

    registered_image = cv2.warpPerspective(
        target_image,
        homography,
        (width, height)
    )

    return registered_image


def calculate_difference(
    reference_image,
    registered_image
):
    """
    Calculate absolute pixel difference between
    reference and registered images.

    Lower difference generally indicates
    better geometric alignment.
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

    return difference


def calculate_alignment_score(
    reference_image,
    registered_image
):
    """
    Calculate a simple 0-100 alignment score.

    Higher score = lower average pixel difference.
    """

    difference = calculate_difference(
        reference_image,
        registered_image
    )

    mean_difference = float(difference.mean())

    score = max(
        0.0,
        100.0 - (mean_difference / 255.0 * 100.0)
    )

    return round(score, 2)