import cv2

from processing.preprocessing import preprocess_image
from processing.features import extract_features
from processing.matching import match_descriptors
from processing.geometry import (
    estimate_homography,
    get_geometry_summary
)


# --------------------------------------------------
# 1. Image paths
# --------------------------------------------------

reference_path = "data/input/test_lunar.png"
target_path = "data/input/test_lunar_transformed.png"


# --------------------------------------------------
# 2. Preprocess both images
# --------------------------------------------------

reference_processed = preprocess_image(reference_path)
target_processed = preprocess_image(target_path)

reference_image = reference_processed["enhanced"]
target_image = target_processed["enhanced"]


# --------------------------------------------------
# 3. Extract SIFT features
# --------------------------------------------------

reference_keypoints, reference_descriptors = extract_features(
    reference_image
)

target_keypoints, target_descriptors = extract_features(
    target_image
)


# --------------------------------------------------
# 4. Match features
# --------------------------------------------------

good_matches = match_descriptors(
    reference_descriptors,
    target_descriptors,
    ratio_threshold=0.75
)


print("\n========== MATCHING ==========")
print("Good matches:", len(good_matches))


# --------------------------------------------------
# 5. Estimate Homography using RANSAC
# --------------------------------------------------

homography, mask = estimate_homography(
    reference_keypoints,
    target_keypoints,
    good_matches,
    reprojection_threshold=5.0
)


# --------------------------------------------------
# 6. Calculate geometry statistics
# --------------------------------------------------

summary = get_geometry_summary(mask)


print("\n========== LUNAALGIN GEOMETRY TEST ==========")

print(
    "Total matches :",
    summary["total_matches"]
)

print(
    "RANSAC inliers:",
    summary["inliers"]
)

print(
    "RANSAC outliers:",
    summary["outliers"]
)

print(
    "Inlier ratio  :",
    str(summary["inlier_ratio"]) + "%"
)


# --------------------------------------------------
# 7. Display Homography Matrix
# --------------------------------------------------

print("\n========== HOMOGRAPHY MATRIX ==========")

print(homography)

print("\n========================================")
print("RANSAC + Homography completed successfully.")