import cv2

from processing.preprocessing import preprocess_image
from processing.features import extract_features
from processing.matching import match_descriptors
from processing.geometry import estimate_homography
from processing.registration import register_image
from processing.visualization import (
    create_match_visualization,
    create_difference_visualization
)


REFERENCE_PATH = "data/input/test_lunar.png"
TARGET_PATH = "data/input/test_lunar_transformed.png"

ALIGNED_PATH = "data/output/aligned_lunar.png"
MATCH_PATH = "data/output/correspondence_map.png"
DIFFERENCE_PATH = "data/output/difference_map.png"


print("\n" + "=" * 60)
print("       LUNAALGIN VISUAL PIPELINE TEST")
print("=" * 60)


# 1. Preprocessing
print("\n[1/7] Preprocessing...")

reference_processed = preprocess_image(REFERENCE_PATH)
target_processed = preprocess_image(TARGET_PATH)

reference = reference_processed["enhanced"]
target = target_processed["enhanced"]


# 2. SIFT
print("[2/7] Extracting SIFT features...")

reference_keypoints, reference_descriptors = extract_features(
    reference
)

target_keypoints, target_descriptors = extract_features(
    target
)

print("      Reference keypoints:", len(reference_keypoints))
print("      Target keypoints   :", len(target_keypoints))


# 3. Matching
print("[3/7] Matching descriptors...")

good_matches = match_descriptors(
    reference_descriptors,
    target_descriptors,
    ratio_threshold=0.75
)

print("      Good matches:", len(good_matches))


# 4. RANSAC
print("[4/7] Running RANSAC + Homography...")

homography, mask = estimate_homography(
    reference_keypoints,
    target_keypoints,
    good_matches,
    reprojection_threshold=5.0
)

inliers = int(mask.sum())

print("      RANSAC inliers:", inliers)


# 5. Registration
print("[5/7] Registering target image...")

height, width = reference.shape

aligned = register_image(
    target_processed["original"],
    homography,
    (width, height)
)

cv2.imwrite(ALIGNED_PATH, aligned)

print("      Saved:", ALIGNED_PATH)


# 6. Correspondence map
print("[6/7] Creating correspondence map...")

create_match_visualization(
    reference_processed["original"],
    target_processed["original"],
    reference_keypoints,
    target_keypoints,
    good_matches,
    mask,
    MATCH_PATH
)

print("      Saved:", MATCH_PATH)


# 7. Difference map
print("[7/7] Creating difference map...")

create_difference_visualization(
    reference_processed["original"],
    aligned,
    DIFFERENCE_PATH
)

print("      Saved:", DIFFERENCE_PATH)


print("\n" + "=" * 60)
print("           VISUAL PIPELINE COMPLETE")
print("=" * 60)

print("\nGenerated files:")

print("1. " + ALIGNED_PATH)
print("2. " + MATCH_PATH)
print("3. " + DIFFERENCE_PATH)

print("\n✓ LunaAlgin visual correspondence pipeline completed.")