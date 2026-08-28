import cv2


def calculate_sharpness(image):
    """
    Calculate image sharpness using the variance of the Laplacian.

    Higher value  -> sharper image
    Lower value   -> blurrier image
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    sharpness_score = cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()

    return round(float(sharpness_score), 2)


def analyze_blur(image):
    sharpness_score = calculate_sharpness(image)

    if sharpness_score < 50:
        severity = "high"
        is_blurry = True

    elif sharpness_score < 100:
        severity = "medium"
        is_blurry = True

    elif sharpness_score < 150:
        severity = "low"
        is_blurry = True

    else:
        severity = "none"
        is_blurry = False

    return {
        "sharpness_score": sharpness_score,
        "is_blurry": is_blurry,
        "severity": severity
    }