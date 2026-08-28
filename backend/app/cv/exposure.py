import cv2
import numpy as np

def calculate_brightness(image):
    """
    Calculate average image brightness using grayscale intensity.
    Range is approximately 0-255.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    brightness = np.mean(gray)

    return round(float(brightness), 2)

def calculate_contrast(image):
    """
    Estimate image contrast using the standard deviation
    of grayscale pixel intensities.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    contrast = np.std(gray)

    return round(float(contrast), 2)

def analyze_exposure(image):
    brightness = calculate_brightness(image)
    contrast = calculate_contrast(image)

    underexposed = False
    overexposed = False

    underexposure_severity = "none"
    overexposure_severity = "none"

    # Initial engineering thresholds.
    # These will later be evaluated and tuned using our dataset.

    if brightness < 50:
        underexposed = True
        underexposure_severity = "high"

    elif brightness < 80:
        underexposed = True
        underexposure_severity = "medium"

    elif brightness < 100:
        underexposed = True
        underexposure_severity = "low"

    if brightness > 220:
        overexposed = True
        overexposure_severity = "high"

    elif brightness > 200:
        overexposed = True
        overexposure_severity = "medium"

    elif brightness > 180:
        overexposed = True
        overexposure_severity = "low"

    return {
        "brightness": brightness,
        "contrast": contrast,

        "underexposure": {
            "detected": underexposed,
            "severity": underexposure_severity
        },

        "overexposure": {
            "detected": overexposed,
            "severity": overexposure_severity
        }
    }
