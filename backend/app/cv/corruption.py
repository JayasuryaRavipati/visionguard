import cv2
import numpy as np

def analyze_corruption(image):
    """
    Estimate severe degradation/corruption using simple
    image statistics.

    This does not detect every possible corrupted file.
    Completely unreadable files are already rejected
    during image decoding.

    Here we detect suspiciously low-information images.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    mean_intensity = float(np.mean(gray))
    std_intensity = float(np.std(gray))

    unique_values = len(np.unique(gray))

    severely_degraded = False
    severity = "none"

    # Extremely little pixel variation
    if std_intensity < 3 or unique_values < 10:
        severely_degraded = True
        severity = "high"

    elif std_intensity < 8 or unique_values < 25:
        severely_degraded = True
        severity = "medium"

    elif std_intensity < 15 or unique_values < 50:
        severely_degraded = True
        severity = "low"

    return {
        "detected": severely_degraded,
        "severity": severity,
        "intensity_mean": round(mean_intensity, 2),
        "intensity_std": round(std_intensity, 2),
        "unique_intensity_values": int(unique_values)
    }
