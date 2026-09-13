import cv2
import numpy as np
from skimage.metrics import structural_similarity


def prepare_images(reference_image, registered_image):
    """
    Prepare reference and registered images
    for scientific quality metrics.

    Both images are converted to grayscale
    and resized to the same dimensions.
    """

    if reference_image is None:
        raise ValueError("Reference image is empty.")

    if registered_image is None:
        raise ValueError("Registered image is empty.")

    # Convert reference to grayscale if needed
    if len(reference_image.shape) == 3:
        reference_gray = cv2.cvtColor(
            reference_image,
            cv2.COLOR_BGR2GRAY
        )
    else:
        reference_gray = reference_image.copy()

    # Convert registered image to grayscale if needed
    if len(registered_image.shape) == 3:
        registered_gray = cv2.cvtColor(
            registered_image,
            cv2.COLOR_BGR2GRAY
        )
    else:
        registered_gray = registered_image.copy()

    # Resize registered image if dimensions differ
    if reference_gray.shape != registered_gray.shape:
        registered_gray = cv2.resize(
            registered_gray,
            (
                reference_gray.shape[1],
                reference_gray.shape[0]
            ),
            interpolation=cv2.INTER_LINEAR
        )

    return reference_gray, registered_gray


def calculate_rmse(
    reference_image,
    registered_image
):
    """
    Calculate Root Mean Square Error (RMSE).

    Lower RMSE = better pixel-level similarity.
    """

    reference_gray, registered_gray = (
        prepare_images(
            reference_image,
            registered_image
        )
    )

    reference_float = (
        reference_gray.astype(np.float32)
    )

    registered_float = (
        registered_gray.astype(np.float32)
    )

    squared_error = (
        (reference_float - registered_float) ** 2
    )

    mse = float(
        np.mean(squared_error)
    )

    rmse = float(
        np.sqrt(mse)
    )

    return round(rmse, 4)


def calculate_ssim(
    reference_image,
    registered_image
):
    """
    Calculate Structural Similarity Index (SSIM).

    SSIM range:
        -1 to 1

    Higher SSIM = better structural similarity.
    """

    reference_gray, registered_gray = (
        prepare_images(
            reference_image,
            registered_image
        )
    )

    reference_gray = reference_gray.astype(
        np.uint8
    )

    registered_gray = registered_gray.astype(
        np.uint8
    )

    score = structural_similarity(
        reference_gray,
        registered_gray,
        data_range=255
    )

    return round(float(score), 4)


def calculate_ncc(
    reference_image,
    registered_image
):
    """
    Calculate Normalized Cross-Correlation (NCC).

    Range:
        approximately -1 to 1

    Higher NCC = better image correlation.
    """

    reference_gray, registered_gray = (
        prepare_images(
            reference_image,
            registered_image
        )
    )

    reference_float = (
        reference_gray.astype(np.float32)
    )

    registered_float = (
        registered_gray.astype(np.float32)
    )

    reference_mean = np.mean(
        reference_float
    )

    registered_mean = np.mean(
        registered_float
    )

    reference_centered = (
        reference_float - reference_mean
    )

    registered_centered = (
        registered_float - registered_mean
    )

    numerator = np.sum(
        reference_centered
        * registered_centered
    )

    denominator = np.sqrt(
        np.sum(reference_centered ** 2)
        * np.sum(registered_centered ** 2)
    )

    if denominator == 0:
        return 0.0

    ncc = numerator / denominator

    return round(float(ncc), 4)


def calculate_quality_metrics(
    reference_image,
    registered_image
):
    """
    Calculate all scientific image-quality metrics.
    """

    rmse = calculate_rmse(
        reference_image,
        registered_image
    )

    ssim = calculate_ssim(
        reference_image,
        registered_image
    )

    ncc = calculate_ncc(
        reference_image,
        registered_image
    )

    return {
        "rmse": rmse,
        "ssim": ssim,
        "ncc": ncc
    }