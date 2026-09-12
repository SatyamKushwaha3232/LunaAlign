import cv2


def create_sift_detector():
    """
    Create SIFT feature detector.

    SIFT is used to detect important and
    scale/rotation-resistant features.
    """

    sift = cv2.SIFT_create(
        nfeatures=3000,
        nOctaveLayers=3,
        contrastThreshold=0.04,
        edgeThreshold=10,
        sigma=1.6
    )

    return sift


def extract_features(image):
    """
    Detect keypoints and calculate descriptors.

    Parameters:
        image: Grayscale/preprocessed image

    Returns:
        keypoints: Detected feature points
        descriptors: Feature descriptors
    """

    if image is None:
        raise ValueError("Input image is empty.")

    sift = create_sift_detector()

    keypoints, descriptors = sift.detectAndCompute(
        image,
        None
    )

    return keypoints, descriptors


def get_feature_summary(keypoints, descriptors):
    """
    Return useful feature statistics.
    """

    return {
        "keypoints": len(keypoints),
        "descriptor_count": 0 if descriptors is None else len(descriptors),
        "descriptor_dimension": (
            0 if descriptors is None else descriptors.shape[1]
        ),
    }