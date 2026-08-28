import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    precision_recall_fscore_support,
)


BASE_DIR = Path(__file__).resolve().parent

TRAIN_CSV = BASE_DIR / "train_features.csv"
TEST_CSV = BASE_DIR / "test_features.csv"

MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"

MODEL_PATH = MODEL_DIR / "visionguard_model.joblib"
METRICS_PATH = REPORT_DIR / "metrics.json"

CONFUSION_MATRIX_PATH = (
    REPORT_DIR / "confusion_matrix.png"
)

FEATURE_IMPORTANCE_PATH = (
    REPORT_DIR / "feature_importance.png"
)


FEATURE_COLUMNS = [
    "width",
    "height",
    "aspect_ratio",
    "sharpness",
    "brightness",
    "contrast",
    "noise",
    "intensity_std",
    "unique_intensity_values",
]


CLASS_LABELS = [
    "ACCEPTABLE",
    "DEGRADED",
    "DEFECTIVE",
]


def load_data():
    train_df = pd.read_csv(
        TRAIN_CSV
    )

    test_df = pd.read_csv(
        TEST_CSV
    )

    X_train = train_df[
        FEATURE_COLUMNS
    ]

    y_train = train_df["label"]

    X_test = test_df[
        FEATURE_COLUMNS
    ]

    y_test = test_df["label"]

    return (
        X_train,
        y_train,
        X_test,
        y_test,
    )


def train_model(
    X_train,
    y_train
):
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    print(
        "\nTraining Random Forest model..."
    )

    model.fit(
        X_train,
        y_train
    )

    print(
        "Training completed."
    )

    return model


def evaluate_model(
    model,
    X_test,
    y_test
):
    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    (
        precision,
        recall,
        f1,
        _
    ) = precision_recall_fscore_support(
        y_test,
        predictions,
        average="weighted",
        zero_division=0,
    )

    report = classification_report(
        y_test,
        predictions,
        output_dict=True,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=CLASS_LABELS,
    )

    return {
        "accuracy": float(
            accuracy
        ),
        "precision_weighted": float(
            precision
        ),
        "recall_weighted": float(
            recall
        ),
        "f1_weighted": float(
            f1
        ),
        "classification_report":
            report,
        "confusion_matrix":
            matrix.tolist(),
    }


def get_feature_importance(
    model
):
    importance = {}

    for feature, value in zip(
        FEATURE_COLUMNS,
        model.feature_importances_,
    ):
        importance[
            feature
        ] = round(
            float(value),
            6
        )

    return dict(
        sorted(
            importance.items(),
            key=lambda item:
                item[1],
            reverse=True,
        )
    )


def save_model(
    model,
    feature_importance
):
    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    artifact = {
        "model": model,
        "features":
            FEATURE_COLUMNS,
        "feature_importance":
            feature_importance,
        "model_type":
            "RandomForestClassifier",
        "version":
            "1.0.0",
    }

    joblib.dump(
        artifact,
        MODEL_PATH
    )

    print(
        f"\nModel saved to:\n"
        f"{MODEL_PATH}"
    )


def save_metrics(
    metrics
):
    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        METRICS_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            metrics,
            file,
            indent=4,
        )

    print(
        f"\nMetrics saved to:\n"
        f"{METRICS_PATH}"
    )


def save_confusion_matrix(
    model,
    X_test,
    y_test
):
    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    predictions = model.predict(
        X_test
    )

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=CLASS_LABELS,
    )

    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=CLASS_LABELS,
    )

    fig, ax = plt.subplots(
        figsize=(8, 6)
    )

    display.plot(
        ax=ax,
        cmap="Blues",
        values_format="d",
        colorbar=False,
    )

    ax.set_title(
        "VisionGuard Confusion Matrix"
    )

    ax.set_xlabel(
        "Predicted Label"
    )

    ax.set_ylabel(
        "True Label"
    )

    fig.tight_layout()

    fig.savefig(
        CONFUSION_MATRIX_PATH,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        f"\nConfusion matrix saved to:\n"
        f"{CONFUSION_MATRIX_PATH}"
    )


def save_feature_importance_chart(
    model
):
    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    importance_df = pd.DataFrame(
        {
            "feature":
                FEATURE_COLUMNS,
            "importance":
                model.feature_importances_,
        }
    )

    importance_df = (
        importance_df.sort_values(
            "importance",
            ascending=True,
        )
    )

    fig, ax = plt.subplots(
        figsize=(9, 6)
    )

    ax.barh(
        importance_df[
            "feature"
        ],
        importance_df[
            "importance"
        ],
    )

    ax.set_title(
        "VisionGuard Feature Importance"
    )

    ax.set_xlabel(
        "Random Forest Importance"
    )

    ax.set_ylabel(
        "Feature"
    )

    fig.tight_layout()

    fig.savefig(
        FEATURE_IMPORTANCE_PATH,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        f"\nFeature importance saved to:\n"
        f"{FEATURE_IMPORTANCE_PATH}"
    )


def main():
    print(
        "\n=========================="
    )
    print(
        "VISIONGUARD MODEL TRAINING"
    )
    print(
        "=========================="
    )

    (
        X_train,
        y_train,
        X_test,
        y_test,
    ) = load_data()

    print(
        f"\nTraining samples: "
        f"{len(X_train)}"
    )

    print(
        f"Testing samples: "
        f"{len(X_test)}"
    )

    print(
        f"Number of features: "
        f"{len(FEATURE_COLUMNS)}"
    )

    model = train_model(
        X_train,
        y_train
    )

    metrics = evaluate_model(
        model,
        X_test,
        y_test
    )

    feature_importance = (
        get_feature_importance(
            model
        )
    )

    metrics[
        "feature_importance"
    ] = feature_importance

    save_model(
        model,
        feature_importance
    )

    save_metrics(
        metrics
    )

    save_confusion_matrix(
        model,
        X_test,
        y_test
    )

    save_feature_importance_chart(
        model
    )

    print(
        "\n--------------------------"
    )

    print(
        "MODEL EVALUATION"
    )

    print(
        "--------------------------"
    )

    print(
        f"Accuracy: "
        f"{metrics['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{metrics['precision_weighted']:.4f}"
    )

    print(
        f"Recall: "
        f"{metrics['recall_weighted']:.4f}"
    )

    print(
        f"F1 Score: "
        f"{metrics['f1_weighted']:.4f}"
    )

    print(
        "\nConfusion Matrix:"
    )

    for row in metrics[
        "confusion_matrix"
    ]:
        print(row)

    print(
        "\nFeature Importance:"
    )

    for (
        feature,
        importance
    ) in feature_importance.items():
        print(
            f"  {feature}: "
            f"{importance:.4f}"
        )

    print(
        "\nModel training and "
        "evaluation completed."
    )


if __name__ == "__main__":
    main()