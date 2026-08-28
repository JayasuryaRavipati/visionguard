def analyze_visual_defect(
    blur_result,
    exposure_result,
    noise_result,
    corruption_result,
):
    score = 0

    severity_weights = {
        "none": 0,
        "low": 1,
        "medium": 2,
        "high": 3,
    }

    score += severity_weights.get(
        blur_result.get("severity", "none"),
        0,
    )

    score += severity_weights.get(
        exposure_result["underexposure"].get(
            "severity",
            "none",
        ),
        0,
    )

    score += severity_weights.get(
        exposure_result["overexposure"].get(
            "severity",
            "none",
        ),
        0,
    )

    score += severity_weights.get(
        noise_result.get("severity", "none"),
        0,
    )

    score += severity_weights.get(
        corruption_result.get(
            "severity",
            "none",
        ),
        0,
    )

    if score >= 8:
        severity = "high"
        detected = True

    elif score >= 5:
        severity = "medium"
        detected = True

    elif score >= 3:
        severity = "low"
        detected = True

    else:
        severity = "none"
        detected = False

    return {
        "detected": detected,
        "severity": severity,
        "defect_score": score,
    }