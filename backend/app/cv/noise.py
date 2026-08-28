import cv2
import numpy as np

def estimate_noise(image):
    """
    Estimate image noise using the difference between the
    original grayscale image and a Gaussian-smoothed version.

    Higher score generally indicates more noise.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    noise_residual = gray.astype(np.float32) - blurred.astype(np.float32)

    noise_score = np.std(noise_residual)

    return round(float(noise_score), 2)

def analyze_noise(image):
    noise_score = estimate_noise(image)

    # Initial engineering thresholds.
    # These will later be tuned using evaluation data.

    if noise_score > 25:
        detected = True
        severity = "high"

    elif noise_score > 15:
        detected = True
        severity = "medium"

    elif noise_score > 8:
        detected = True
        severity = "low"

    else:
        detected = False
        severity = "none"

    return {
        "noise_score": noise_score,
        "detected": detected,
        "severity": severity
    }
