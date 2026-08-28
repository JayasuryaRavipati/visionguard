from app.cv.visual_defect import analyze_visual_defect
from app.ml.predictor import predict_quality
from app.cv.blur import analyze_blur
from app.cv.exposure import analyze_exposure
from app.cv.noise import analyze_noise
from app.cv.corruption import analyze_corruption
from app.cv.features import get_image_dimensions


SEVERITY_PENALTIES = {
    "none": 0,
    "low": 8,
    "medium": 18,
    "high": 35
}


def calculate_quality_score(issues):
    """
    Temporary interpretable scoring system.
    """

    score = 100

    for issue in issues.values():
        severity = issue.get("severity", "none")
        score -= SEVERITY_PENALTIES.get(severity, 0)

    return max(0, min(100, score))


def get_quality_label(score):
    if score >= 80:
        return "ACCEPTABLE"

    elif score >= 50:
        return "DEGRADED"

    else:
        return "DEFECTIVE"


def severity_confidence(severity):
    confidence_map = {
        "none": 0.0,
        "low": 0.55,
        "medium": 0.75,
        "high": 0.9
    }

    return confidence_map.get(
        severity,
        0.0
    )


def analyze_image(image):
    dimensions = get_image_dimensions(image)

    blur_result = analyze_blur(image)
    exposure_result = analyze_exposure(image)
    noise_result = analyze_noise(image)
    corruption_result = analyze_corruption(image)
    visual_defect_result = analyze_visual_defect(
    blur_result,
    exposure_result,
    noise_result,
    corruption_result,
)

    # -----------------------------------
    # Explainable CV issue detection
    # -----------------------------------

    issues = {
        "blur": {
            "detected": blur_result["is_blurry"],
            "severity": blur_result["severity"],
            "confidence": severity_confidence(
                blur_result["severity"]
            )
        },

        "underexposure": {
            **exposure_result["underexposure"],
            "confidence": severity_confidence(
                exposure_result[
                    "underexposure"
                ]["severity"]
            )
        },

        "overexposure": {
            **exposure_result["overexposure"],
            "confidence": severity_confidence(
                exposure_result[
                    "overexposure"
                ]["severity"]
            )
        },

        "noise": {
            "detected": noise_result["detected"],
            "severity": noise_result["severity"],
            "confidence": severity_confidence(
                noise_result["severity"]
            )
        },

        "severe_degradation": {
            "detected": corruption_result["detected"],
            "severity": corruption_result["severity"],
            "confidence": severity_confidence(
                corruption_result["severity"]
            )
        },
        "potential_visual_defect": {
    "detected":
        visual_defect_result["detected"],

    "severity":
        visual_defect_result["severity"],

    "confidence":
        severity_confidence(
            visual_defect_result["severity"]
        ),

    "defect_score":
        visual_defect_result[
            "defect_score"
        ],
},
    }

    # -----------------------------------
    # Features sent to trained ML model
    # -----------------------------------

    ml_features = {
        "width": dimensions["width"],
        "height": dimensions["height"],

        "aspect_ratio": round(
            dimensions["width"]
            / dimensions["height"],
            4
        ),

        "sharpness":
            blur_result["sharpness_score"],

        "brightness":
            exposure_result["brightness"],

        "contrast":
            exposure_result["contrast"],

        "noise":
            noise_result["noise_score"],

        "intensity_std":
            corruption_result[
                "intensity_std"
            ],

        "unique_intensity_values":
            corruption_result[
                "unique_intensity_values"
            ]
    }

    # -----------------------------------
    # ML prediction
    # -----------------------------------

    ml_prediction = predict_quality(
        ml_features
    )

    quality_label = ml_prediction["label"]
    confidence = ml_prediction["confidence"]

    probabilities = ml_prediction[
        "probabilities"
    ]

    acceptable_probability = probabilities.get(
        "ACCEPTABLE",
        0
    )

    degraded_probability = probabilities.get(
        "DEGRADED",
        0
    )

    defective_probability = probabilities.get(
        "DEFECTIVE",
        0
    )

    # -----------------------------------
    # Convert probabilities to 0-100 score
    # -----------------------------------

    quality_score = (
        acceptable_probability * 100
        + degraded_probability * 60
        + defective_probability * 20
    )

    quality_score = round(
        max(
            0,
            min(100, quality_score)
        ),
        2
    )

    # -----------------------------------
    # API response
    # -----------------------------------

    return {
        "quality_score": quality_score,

        "quality_label": quality_label,

        "confidence": confidence,

        "ml_prediction": ml_prediction,

        "image_statistics": {
            "width": dimensions["width"],
            "height": dimensions["height"],

            "sharpness":
                blur_result[
                    "sharpness_score"
                ],

            "brightness":
                exposure_result[
                    "brightness"
                ],

            "contrast":
                exposure_result[
                    "contrast"
                ],

            "noise":
                noise_result[
                    "noise_score"
                ],

            "intensity_std":
                corruption_result[
                    "intensity_std"
                ],

            "unique_intensity_values":
                corruption_result[
                    "unique_intensity_values"
                ]
        },

        "issues": issues
    }