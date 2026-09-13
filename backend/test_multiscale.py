from processing.preprocessing import preprocess_image
from processing.features import (
    extract_multiscale_features,
    get_feature_summary,
)


IMAGE_PATH = "data/input/test_lunar.png"


def main():

    print("\n" + "=" * 60)
    print("       LUNAALGIN MULTI-SCALE FEATURE TEST")
    print("=" * 60)

    print("\n[1/3] Preprocessing image...")

    processed = preprocess_image(
        IMAGE_PATH
    )

    image = processed["enhanced"]

    print("      ✓ Preprocessing completed")

    print("\n[2/3] Extracting multi-scale features...")

    keypoints, descriptors = extract_multiscale_features(
        image,
        scales=(1.0, 0.75, 0.5)
    )

    print("      ✓ Multi-scale extraction completed")

    print("\n[3/3] Feature statistics...")

    summary = get_feature_summary(
        keypoints,
        descriptors
    )

    print(
        f"      Total keypoints: "
        f"{summary['keypoints']}"
    )

    print(
        f"      Descriptors: "
        f"{summary['descriptor_count']}"
    )

    print(
        f"      Descriptor dimension: "
        f"{summary['descriptor_dimension']}"
    )

    print("\n" + "=" * 60)
    print("       MULTI-SCALE TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()