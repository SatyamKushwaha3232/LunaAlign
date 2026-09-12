import cv2


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


def preprocess_image(image_path: str):
    """
    Complete LunaAlgin preprocessing pipeline.

    Image
      ↓
    Grayscale
      ↓
    Denoising
      ↓
    Contrast Enhancement
    """

    image = load_image(image_path)

    gray = convert_to_grayscale(image)

    denoised = denoise_image(gray)

    enhanced = enhance_contrast(denoised)

    return {
        "original": image,
        "grayscale": gray,
        "denoised": denoised,
        "enhanced": enhanced,
    }