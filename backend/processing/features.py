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


def extract_multiscale_features(
    image,
    scales=(1.0, 0.75, 0.5)
):
    """
    Extract SIFT features at multiple image scales.

    Multiple scales improve robustness when the same
    lunar surface appears at different image sizes.

    Scales:
        1.0  = original resolution
        0.75 = reduced resolution
        0.5  = half resolution

    Keypoint coordinates are converted back to the
    original image coordinate system.
    """

    if image is None:
        raise ValueError("Input image is empty.")

    all_keypoints = []
    all_descriptors = []

    for scale in scales:

        # Create scaled image
        if scale == 1.0:

            scaled_image = image

        else:

            width = int(image.shape[1] * scale)
            height = int(image.shape[0] * scale)

            scaled_image = cv2.resize(
                image,
                (width, height),
                interpolation=cv2.INTER_AREA
            )

        # Extract SIFT features
        keypoints, descriptors = extract_features(
            scaled_image
        )

        if descriptors is None or len(keypoints) == 0:
            continue

        # Convert keypoint coordinates back
        # to original image coordinates.
        if scale != 1.0:

            for keypoint in keypoints:

                keypoint.pt = (
                    keypoint.pt[0] / scale,
                    keypoint.pt[1] / scale
                )

                keypoint.size = (
                    keypoint.size / scale
                )

        all_keypoints.extend(keypoints)
        all_descriptors.append(descriptors)

    # Combine descriptors from all scales
    if all_descriptors:

        descriptors = cv2.vconcat(
            all_descriptors
        )

    else:

        descriptors = None

    return all_keypoints, descriptors


def get_feature_summary(keypoints, descriptors):
    """
    Return useful feature statistics.
    """

    return {
        "keypoints": len(keypoints),
        "descriptor_count": (
            0
            if descriptors is None
            else len(descriptors)
        ),
        "descriptor_dimension": (
            0
            if descriptors is None
            else descriptors.shape[1]
        ),
    }