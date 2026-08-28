from pathlib import Path

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "visionguard_model.joblib"
)

_model_artifact = None

def load_model():
    global _model_artifact

    if _model_artifact is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"ML model not found: {MODEL_PATH}"
            )

        _model_artifact = joblib.load(
            MODEL_PATH
        )

    return _model_artifact

def predict_quality(features):
    artifact = load_model()

    model = artifact["model"]
    feature_names = artifact["features"]

    row = {
        feature: features[feature]
        for feature in feature_names
    }

    dataframe = pd.DataFrame(
        [row],
        columns=feature_names
    )

    predicted_label = model.predict(
        dataframe
    )[0]

    probabilities = model.predict_proba(
        dataframe
    )[0]

    classes = model.classes_

    probability_map = {
        class_name: round(
            float(probability),
            4
        )
        for class_name, probability
        in zip(classes, probabilities)
    }

    confidence = round(
        float(max(probabilities)),
        4
    )

    return {
        "label": predicted_label,
        "confidence": confidence,
        "probabilities": probability_map,
        "model_type": artifact.get(
            "model_type",
            "unknown"
        ),
        "model_version": artifact.get(
            "version",
            "unknown"
        ),
    }
