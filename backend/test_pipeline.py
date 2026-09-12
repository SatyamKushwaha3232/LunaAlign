import cv2

from processing.preprocessing import preprocess_image
from processing.features import extract_features
from processing.matching import (
    match_descriptors,
    get_match_summary
)
from processing.geometry import (
    estimate_homography,
    get_geometry_summary
)
from processing.registration import (
    register_image,
    calculate_alignment_score
)


REFERENCE_PATH = "data/input/test_lunar.png"
TARGET_PATH = "data/input/test_lunar_transformed.png"

OUTPUT_PATH = "data/output/aligned_lunar.png"


print("\n")
print("=" * 60)
print("          LUNAALGIN END-TO-END TEST")
print("=" * 60)


# --------------------------------------------------
# STEP 1 — PREPROCESSING
# --------------------------------------------------

print("\n[1/6] Preprocessing images...")

reference_processed = preprocess_image(
    REFERENCE_PATH
)

target_processed = preprocess_image(
    TARGET_PATH
)

reference_enhanced = reference_processed["enhanced"]
target_enhanced = target_processed["enhanced"]

print("      ✓ Preprocessing completed")


# --------------------------------------------------
# STEP 2 — FEATURE EXTRACTION
# --------------------------------------------------

print("\n[2/6] Extracting SIFT features...")

reference_keypoints, reference_descriptors = extract_features(
    reference_enhanced
)

target_keypoints, target_descriptors = extract_features(
    target_enhanced
)

print(
    "      Reference keypoints:",
    len(reference_keypoints)
)

print(
    "      Target keypoints:",
    len(target_keypoints)
)


# --------------------------------------------------
# STEP 3 — FEATURE MATCHING
# --------------------------------------------------

print("\n[3/6] Matching feature descriptors...")

good_matches = match_descriptors(
    reference_descriptors,
    target_descriptors,
    ratio_threshold=0.75
)

match_summary = get_match_summary(
    good_matches
)

print(
    "      Good matches:",
    match_summary["good_matches"]
)

print(
    "      Average distance:",
    match_summary["average_distance"]
)


# --------------------------------------------------
# STEP 4 — RANSAC + HOMOGRAPHY
# --------------------------------------------------

print("\n[4/6] Estimating geometric transformation...")

homography, mask = estimate_homography(
    reference_keypoints,
    target_keypoints,
    good_matches,
    reprojection_threshold=5.0
)

geometry_summary = get_geometry_summary(
    mask
)

print(
    "      Total matches:",
    geometry_summary["total_matches"]
)

print(
    "      RANSAC inliers:",
    geometry_summary["inliers"]
)

print(
    "      RANSAC outliers:",
    geometry_summary["outliers"]
)

print(
    "      Inlier ratio:",
    str(geometry_summary["inlier_ratio"]) + "%"
)


# --------------------------------------------------
# STEP 5 — IMAGE REGISTRATION
# --------------------------------------------------

print("\n[5/6] Registering target image...")

height, width = reference_enhanced.shape

registered_image = register_image(
    target_processed["original"],
    homography,
    (width, height)
)

saved = cv2.imwrite(
    OUTPUT_PATH,
    registered_image
)

if not saved:
    raise ValueError(
        "Unable to save registered image."
    )

print(
    "      ✓ Aligned image saved:"
)

print(
    "      ",
    OUTPUT_PATH
)


# --------------------------------------------------
# STEP 6 — ALIGNMENT SCORE
# --------------------------------------------------

print("\n[6/6] Calculating alignment score...")

reference_original = reference_processed["original"]

score = calculate_alignment_score(
    reference_original,
    registered_image
)

print(
    "      Alignment score:",
    str(score) + "%"
)


# --------------------------------------------------
# FINAL SUMMARY
# --------------------------------------------------

print("\n")
print("=" * 60)
print("             LUNAALGIN RESULT")
print("=" * 60)

print(
    "Reference image       :",
    REFERENCE_PATH
)

print(
    "Target image          :",
    TARGET_PATH
)

print(
    "Reference keypoints   :",
    len(reference_keypoints)
)

print(
    "Target keypoints      :",
    len(target_keypoints)
)

print(
    "Good matches          :",
    match_summary["good_matches"]
)

print(
    "RANSAC inliers        :",
    geometry_summary["inliers"]
)

print(
    "RANSAC inlier ratio   :",
    str(geometry_summary["inlier_ratio"]) + "%"
)

print(
    "Alignment score       :",
    str(score) + "%"
)

print(
    "Output                :",
    OUTPUT_PATH
)

print("=" * 60)

print("\n✓ LUNAALGIN PIPELINE COMPLETED SUCCESSFULLY")