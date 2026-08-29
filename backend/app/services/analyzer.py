import math

from app.cv.visual_defect import (
    analyze_visual_defect,
)
from app.ml.predictor import (
    predict_quality,
)
from app.cv.blur import analyze_blur
from app.cv.exposure import (
    analyze_exposure,
)
from app.cv.noise import analyze_noise
from app.cv.corruption import (
    analyze_corruption,
)
from app.cv.features import (
    get_image_dimensions,
)


# ============================================================
# CONFIGURATION
# ============================================================

SEVERITY_PENALTIES = {
    "none": 0,
    "low": 8,
    "medium": 18,
    "high": 35,
}


QUALITY_CLASS_SCORES = {
    "ACCEPTABLE": 100,
    "DEGRADED": 60,
    "DEFECTIVE": 20,
}


# ============================================================
# OLD INTERPRETABLE SCORE
# ============================================================

def calculate_quality_score(issues):
    """
    Interpretable CV-based score.

    Currently retained for debugging /
    future explainability, while the final
    quality score is produced using the
    trained ML probabilities.
    """

    score = 100

    for issue in issues.values():
        severity = issue.get(
            "severity",
            "none",
        )

        score -= (
            SEVERITY_PENALTIES.get(
                severity,
                0,
            )
        )

    return max(
        0,
        min(
            100,
            score,
        ),
    )


# ============================================================
# QUALITY LABEL
# ============================================================

def get_quality_label(score):
    if score >= 80:
        return "ACCEPTABLE"

    if score >= 50:
        return "DEGRADED"

    return "DEFECTIVE"


# ============================================================
# ISSUE CONFIDENCE
# ============================================================

def severity_confidence(
    severity,
):
    confidence_map = {
        "none": 0.0,
        "low": 0.55,
        "medium": 0.75,
        "high": 0.90,
    }

    return confidence_map.get(
        severity,
        0.0,
    )


# ============================================================
# SCORE UNCERTAINTY
# ============================================================

def calculate_score_uncertainty(
    probabilities,
    quality_score,
):
    """
    Calculate uncertainty in quality-score
    points from the ML probability
    distribution.

    Example:

        quality_score = 74.2
        score_uncertainty = 12.4

    Frontend can display:

        74.2 ± 12.4

    A smaller uncertainty means the model's
    probability distribution is more
    concentrated around one quality class.

    A larger uncertainty means the model is
    less certain between different quality
    classes.
    """

    variance = 0.0

    for (
        label,
        class_score,
    ) in (
        QUALITY_CLASS_SCORES.items()
    ):
        probability = float(
            probabilities.get(
                label,
                0.0,
            )
        )

        difference = (
            class_score -
            quality_score
        )

        variance += (
            probability *
            (
                difference ** 2
            )
        )

    uncertainty = math.sqrt(
        max(
            variance,
            0.0,
        )
    )

    return round(
        uncertainty,
        2,
    )


# ============================================================
# MAIN IMAGE ANALYZER
# ============================================================

def analyze_image(image):
    # --------------------------------------------------------
    # Image dimensions
    # --------------------------------------------------------

    dimensions = (
        get_image_dimensions(
            image
        )
    )

    # --------------------------------------------------------
    # Computer vision detectors
    # --------------------------------------------------------

    blur_result = (
        analyze_blur(
            image
        )
    )

    exposure_result = (
        analyze_exposure(
            image
        )
    )

    noise_result = (
        analyze_noise(
            image
        )
    )

    corruption_result = (
        analyze_corruption(
            image
        )
    )

    visual_defect_result = (
        analyze_visual_defect(
            blur_result,
            exposure_result,
            noise_result,
            corruption_result,
        )
    )

    # ========================================================
    # EXPLAINABLE CV ISSUE DETECTION
    # ========================================================

    issues = {
        "blur": {
            "detected": (
                blur_result[
                    "is_blurry"
                ]
            ),

            "severity": (
                blur_result[
                    "severity"
                ]
            ),

            "confidence":
                severity_confidence(
                    blur_result[
                        "severity"
                    ]
                ),
        },

        "underexposure": {
            **exposure_result[
                "underexposure"
            ],

            "confidence":
                severity_confidence(
                    exposure_result[
                        "underexposure"
                    ][
                        "severity"
                    ]
                ),
        },

        "overexposure": {
            **exposure_result[
                "overexposure"
            ],

            "confidence":
                severity_confidence(
                    exposure_result[
                        "overexposure"
                    ][
                        "severity"
                    ]
                ),
        },

        "noise": {
            "detected": (
                noise_result[
                    "detected"
                ]
            ),

            "severity": (
                noise_result[
                    "severity"
                ]
            ),

            "confidence":
                severity_confidence(
                    noise_result[
                        "severity"
                    ]
                ),
        },

        "severe_degradation": {
            "detected": (
                corruption_result[
                    "detected"
                ]
            ),

            "severity": (
                corruption_result[
                    "severity"
                ]
            ),

            "confidence":
                severity_confidence(
                    corruption_result[
                        "severity"
                    ]
                ),
        },

        "potential_visual_defect": {
            "detected": (
                visual_defect_result[
                    "detected"
                ]
            ),

            "severity": (
                visual_defect_result[
                    "severity"
                ]
            ),

            "confidence":
                severity_confidence(
                    visual_defect_result[
                        "severity"
                    ]
                ),

            "defect_score": (
                visual_defect_result[
                    "defect_score"
                ]
            ),
        },
    }

    # ========================================================
    # FEATURES SENT TO TRAINED ML MODEL
    # ========================================================

    height = (
        dimensions[
            "height"
        ]
    )

    width = (
        dimensions[
            "width"
        ]
    )

    aspect_ratio = (
        round(
            width / height,
            4,
        )
        if height
        else 0.0
    )

    ml_features = {
        "width": width,

        "height": height,

        "aspect_ratio":
            aspect_ratio,

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
            ],
    }

    # ========================================================
    # MACHINE LEARNING PREDICTION
    # ========================================================

    ml_prediction = (
        predict_quality(
            ml_features
        )
    )

    quality_label = (
        ml_prediction[
            "label"
        ]
    )

    confidence = float(
        ml_prediction[
            "confidence"
        ]
    )

    probabilities = (
        ml_prediction[
            "probabilities"
        ]
    )

    # --------------------------------------------------------
    # Read probabilities safely
    # --------------------------------------------------------

    acceptable_probability = float(
        probabilities.get(
            "ACCEPTABLE",
            0.0,
        )
    )

    degraded_probability = float(
        probabilities.get(
            "DEGRADED",
            0.0,
        )
    )

    defective_probability = float(
        probabilities.get(
            "DEFECTIVE",
            0.0,
        )
    )

    # ========================================================
    # QUALITY SCORE
    # ========================================================

    quality_score = (
        acceptable_probability
        * QUALITY_CLASS_SCORES[
            "ACCEPTABLE"
        ]

        +

        degraded_probability
        * QUALITY_CLASS_SCORES[
            "DEGRADED"
        ]

        +

        defective_probability
        * QUALITY_CLASS_SCORES[
            "DEFECTIVE"
        ]
    )

    quality_score = round(
        max(
            0,
            min(
                100,
                quality_score,
            ),
        ),
        2,
    )

    # ========================================================
    # SCORE UNCERTAINTY
    # ========================================================

    score_uncertainty = (
        calculate_score_uncertainty(
            probabilities,
            quality_score,
        )
    )

    # ========================================================
    # API RESPONSE
    # ========================================================

    return {
        "quality_score":
            quality_score,

        "quality_label":
            quality_label,

        # Real model confidence.
        #
        # Example:
        # 0.824 = 82.4%
        "confidence":
            round(
                confidence,
                4,
            ),

        # Quality-score uncertainty.
        #
        # Example:
        # 9.7 = ±9.7 score points
        "score_uncertainty":
            score_uncertainty,

        "ml_prediction":
            ml_prediction,

        "image_statistics": {
            "width":
                width,

            "height":
                height,

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
                ],
        },

        "issues":
            issues,
    }