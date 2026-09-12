import cv2


def create_matcher():
    """
    Create a Brute-Force matcher for SIFT descriptors.

    SIFT descriptors use floating-point values,
    therefore L2 norm is used.
    """

    matcher = cv2.BFMatcher(
        cv2.NORM_L2,
        crossCheck=False
    )

    return matcher


def match_descriptors(
    descriptors_reference,
    descriptors_target,
    ratio_threshold=0.75
):
    """
    Match descriptors using KNN + Lowe's Ratio Test.

    Parameters:
        descriptors_reference:
            Descriptors from reference/fixed image.

        descriptors_target:
            Descriptors from target/moving image.

        ratio_threshold:
            Threshold used to reject ambiguous matches.

    Returns:
        good_matches:
            Reliable feature matches.
    """

    if descriptors_reference is None:
        raise ValueError("Reference descriptors are empty.")

    if descriptors_target is None:
        raise ValueError("Target descriptors are empty.")

    matcher = create_matcher()

    knn_matches = matcher.knnMatch(
        descriptors_reference,
        descriptors_target,
        k=2
    )

    good_matches = []

    for pair in knn_matches:

        if len(pair) < 2:
            continue

        first_match, second_match = pair

        if first_match.distance < ratio_threshold * second_match.distance:
            good_matches.append(first_match)

    return good_matches


def get_match_summary(good_matches):
    """
    Return statistics about accepted feature matches.
    """

    distances = [
        match.distance
        for match in good_matches
    ]

    if not distances:
        return {
            "good_matches": 0,
            "average_distance": 0.0,
            "best_distance": 0.0,
        }

    return {
        "good_matches": len(good_matches),
        "average_distance": round(
            sum(distances) / len(distances),
            2
        ),
        "best_distance": round(
            min(distances),
            2
        ),
    }