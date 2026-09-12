import cv2
import numpy as np

from processing.preprocessing import preprocess_image
from processing.features import extract_features, get_feature_summary


# --------------------------------------------------
# 1. Create a synthetic lunar-like test image
# --------------------------------------------------

image = np.zeros((700, 700), dtype=np.uint8)

# Moon-like circular surface
cv2.circle(image, (350, 350), 300, 150, -1)

# Large craters
cv2.circle(image, (250, 260), 70, 100, 4)
cv2.circle(image, (250, 260), 45, 125, 3)

cv2.circle(image, (470, 300), 55, 95, 4)
cv2.circle(image, (470, 300), 30, 125, 3)

cv2.circle(image, (350, 450), 80, 105, 4)
cv2.circle(image, (350, 450), 45, 130, 3)

# Smaller craters
cv2.circle(image, (180, 420), 25, 110, 3)
cv2.circle(image, (520, 450), 30, 115, 3)
cv2.circle(image, (400, 180), 25, 110, 3)

# Surface lines / geological structures
cv2.line(image, (100, 500), (250, 550), 100, 4)
cv2.line(image, (450, 180), (570, 120), 100, 4)

# Add texture/noise
noise = np.random.normal(0, 12, image.shape).astype(np.int16)

image_with_noise = np.clip(
    image.astype(np.int16) + noise,
    0,
    255
).astype(np.uint8)


# --------------------------------------------------
# 2. Save test image
# --------------------------------------------------

test_path = "data/input/test_lunar.png"

cv2.imwrite(
    test_path,
    image_with_noise
)

print("\nTest lunar image created:")
print(test_path)


# --------------------------------------------------
# 3. Run LunaAlgin preprocessing
# --------------------------------------------------

processed = preprocess_image(test_path)

enhanced = processed["enhanced"]


# --------------------------------------------------
# 4. Run SIFT feature extraction
# --------------------------------------------------

keypoints, descriptors = extract_features(enhanced)


# --------------------------------------------------
# 5. Get feature statistics
# --------------------------------------------------

summary = get_feature_summary(
    keypoints,
    descriptors
)


# --------------------------------------------------
# 6. Print results
# --------------------------------------------------

print("\n========== LUNAALGIN FEATURE TEST ==========")

print("Keypoints detected      :", summary["keypoints"])
print("Descriptors             :", summary["descriptor_count"])
print("Descriptor dimension    :", summary["descriptor_dimension"])

print("============================================")
print("\nSIFT feature extraction completed successfully.")