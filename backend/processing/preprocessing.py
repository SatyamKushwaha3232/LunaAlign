import cv2
import numpy as np


def load_image(image_path: str):
    """Load image from disk."""

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Unable to read image: {image_path}")

    return image


def convert_to_grayscale(image):
    """Convert BGR image into grayscale."""

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return gray


def denoise_image(gray):
    """Reduce noise while preserving useful image structures."""

    denoised = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    return denoised


def estimate_illumination(gray):
    """
    Estimate the slowly varying illumination field.

    Lunar images can contain large brightness variations
    caused by changing solar illumination and shadows.

    A large Gaussian blur is used as a simple illumination model.
    """

    illumination = cv2.GaussianBlur(
        gray,
        (0, 0),
        sigmaX=25,
        sigmaY=25
    )

    return illumination


def normalize_illumination(gray, illumination):
    """
    Normalize illumination using a Retinex-style division model.

    This reduces large-scale brightness differences while
    preserving local surface structures and crater boundaries.
    """

    gray_float = gray.astype(np.float32) + 1.0
    illumination_float = illumination.astype(np.float32) + 1.0

    normalized = gray_float / illumination_float

    normalized = cv2.normalize(
        normalized,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    normalized = normalized.astype(np.uint8)

    return normalized


def enhance_contrast(gray):
    """
    Enhance local contrast using CLAHE.

    Useful for lunar images because illumination
    can vary across the lunar surface.
    """

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    return enhanced


def apply_sun_angle_compensation(image, reference_illumination, target_illumination):
    """Apply a deliberately conservative metadata-guided gain correction.

    It is only used when both products provide sun elevation metadata.  The
    Retinex/CLAHE pipeline remains the primary normalisation, while this small
    correction reduces gross exposure differences without inventing metadata.
    """
    if not reference_illumination or not target_illumination:
        return image
    reference_elevation = reference_illumination.get("sun_elevation_deg")
    target_elevation = target_illumination.get("sun_elevation_deg")
    if reference_elevation is None or target_elevation is None:
        return image
    target_signal = max(np.sin(np.deg2rad(float(target_elevation))), 0.15)
    reference_signal = max(np.sin(np.deg2rad(float(reference_elevation))), 0.15)
    gain = np.clip(reference_signal / target_signal, 0.65, 1.55)
    return cv2.convertScaleAbs(image, alpha=float(gain))


def preprocess_image(image_path: str, reference_illumination=None,
                     target_illumination=None, compensate_sun_angle=False):
    """
    Complete LunaAlgin preprocessing pipeline.

    Image
      ↓
    Load Image
      ↓
    Grayscale
      ↓
    Denoising
      ↓
    Illumination Estimation
      ↓
    Illumination Normalization
      ↓
    CLAHE
      ↓
    Normalized Image
    """

    image = load_image(image_path)

    gray = convert_to_grayscale(image)

    denoised = denoise_image(gray)

    illumination = estimate_illumination(denoised)

    normalized = normalize_illumination(
        denoised,
        illumination
    )

    enhanced = enhance_contrast(normalized)
    if compensate_sun_angle:
        enhanced = apply_sun_angle_compensation(
            enhanced, reference_illumination, target_illumination
        )

    return {
        "original": image,
        "grayscale": gray,
        "denoised": denoised,
        "illumination": illumination,
        "normalized": normalized,
        "enhanced": enhanced,
    }
