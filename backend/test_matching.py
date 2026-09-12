import cv2
import numpy as np

from processing.preprocessing import preprocess_image
from processing.features import extract_features
from processing.matching import match_descriptors, get_match_summary


# --------------------------------------------------
# 1. Load original synthetic lunar image
# --------------------------------------------------

reference_path = "data/input/test_lunar.png"

reference_image = cv2.imread(reference_path, cv2.IMREAD_GRAYSCALE)

if reference_image is None:
    raise ValueError("Reference image not found.")


# --------------------------------------------------
# 2. Create transformed image
#    Simulates viewpoint / rotation / scale change
# --------------------------------------------------

height, width = reference_image.shape

center = (width // 2, height // 2)

transform_matrix = cv2.getRotationMatrix2D(
    center,
    12,      # rotation angle
    0.85     # scale
)

transform_matrix[0, 2] += 35
transform_matrix[1, 2] += 20

target_image = cv2.warpAffine(
    reference_image,
    transform_matrix,
    (width, height)
)

target_path = "data/input/test_lunar_transformed.png"

cv2.imwrite(
    target_path,
    target_image
)


print("\nTransformed lunar image created:")
print(target_path)


# --------------------------------------------------
# 3. Preprocess reference image
# --------------------------------------------------

reference_processed = preprocess_image(
    reference_path
)

reference_enhanced = reference_processed["enhanced"]


# --------------------------------------------------
# 4. Preprocess transformed image
# --------------------------------------------------

target_processed = preprocess_image(
    target_path
)

target_enhanced = target_processed["enhanced"]


# --------------------------------------------------
# 5. Extract SIFT features
# --------------------------------------------------

reference_keypoints, reference_descriptors = extract_features(
    reference_enhanced
)

target_keypoints, target_descriptors = extract_features(
    target_enhanced
)


print("\n========== FEATURE EXTRACTION ==========")

print(
    "Reference keypoints :",
    len(reference_keypoints)
)

print(
    "Target keypoints    :",
    len(target_keypoints)
)


# --------------------------------------------------
# 6. Match descriptors
# --------------------------------------------------

good_matches = match_descriptors(
    reference_descriptors,
    target_descriptors,
    ratio_threshold=0.75
)


# --------------------------------------------------
# 7. Display matching statistics
# --------------------------------------------------

summary = get_match_summary(
    good_matches
)


print("\n========== LUNAALGIN MATCHING TEST ==========")

print(
    "Good matches        :",
    summary["good_matches"]
)

print(
    "Average distance    :",
    summary["average_distance"]
)

print(
    "Best distance       :",
    summary["best_distance"]
)

print("============================================")

print("\nSIFT + KNN + Lowe Ratio Test completed successfully.")