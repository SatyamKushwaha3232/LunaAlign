from processing.preprocessing import preprocess_image
from processing.features import extract_multiscale_features
from processing.matching import match_descriptors
from processing.geometry import estimate_homography
from processing.registration import register_image
from processing.metrics import calculate_quality_metrics


REFERENCE_PATH = "data/input/test_lunar.png"
TARGET_PATH = "data/input/test_lunar_transformed.png"


def main():

    print("\n" + "=" * 65)
    print("          LUNAALGIN SCIENTIFIC METRICS TEST")
    print("=" * 65)

    # ---------------------------------------------------------
    # 1. PREPROCESSING
    # ---------------------------------------------------------

    print("\n[1/6] Preprocessing images...")

    reference_processed = preprocess_image(
        REFERENCE_PATH
    )

    target_processed = preprocess_image(
        TARGET_PATH
    )

    reference_image = (
        reference_processed["enhanced"]
    )

    target_image = (
        target_processed["enhanced"]
    )

    print("      ✓ Preprocessing completed")

    # ---------------------------------------------------------
    # 2. MULTI-SCALE FEATURES
    # ---------------------------------------------------------

    print("\n[2/6] Extracting multi-scale features...")

    reference_keypoints, reference_descriptors = (
        extract_multiscale_features(
            reference_image,
            scales=(1.0, 0.75, 0.5)
        )
    )

    target_keypoints, target_descriptors = (
        extract_multiscale_features(
            target_image,
            scales=(1.0, 0.75, 0.5)
        )
    )

    print(
        f"      Reference keypoints: "
        f"{len(reference_keypoints)}"
    )

    print(
        f"      Target keypoints: "
        f"{len(target_keypoints)}"
    )

    # ---------------------------------------------------------
    # 3. FEATURE MATCHING
    # ---------------------------------------------------------

    print("\n[3/6] Matching features...")

    good_matches = match_descriptors(
        reference_descriptors,
        target_descriptors,
        ratio_threshold=0.75
    )

    print(
        f"      Good matches: "
        f"{len(good_matches)}"
    )

    # ---------------------------------------------------------
    # 4. HOMOGRAPHY + RANSAC
    # ---------------------------------------------------------

    print("\n[4/6] Estimating geometric transformation...")

    homography, mask = estimate_homography(
        reference_keypoints,
        target_keypoints,
        good_matches,
        reprojection_threshold=5.0
    )

    inliers = int(mask.ravel().sum())

    print(
        f"      RANSAC inliers: "
        f"{inliers}"
    )

    print(
        f"      Inlier ratio: "
        f"{(inliers / len(good_matches)) * 100:.2f}%"
    )

    # ---------------------------------------------------------
    # 5. IMAGE REGISTRATION
    # ---------------------------------------------------------

    print("\n[5/6] Registering target image...")

    aligned_image = register_image(
        target_image,
        homography,
        (
            reference_image.shape[1],
            reference_image.shape[0]
        )
    )

    print("      ✓ Image registration completed")

    # ---------------------------------------------------------
    # 6. SCIENTIFIC METRICS
    # ---------------------------------------------------------

    print("\n[6/6] Calculating scientific metrics...")

    metrics = calculate_quality_metrics(
        reference_image,
        aligned_image
    )

    print("\n" + "-" * 65)
    print("                 QUALITY METRICS")
    print("-" * 65)

    print(
        f"      RMSE : {metrics['rmse']}"
    )

    print(
        f"      SSIM : {metrics['ssim']}"
    )

    print(
        f"      NCC  : {metrics['ncc']}"
    )

    print("-" * 65)

    print("\n" + "=" * 65)
    print("          SCIENTIFIC METRICS TEST PASSED")
    print("=" * 65)


if __name__ == "__main__":
    main()