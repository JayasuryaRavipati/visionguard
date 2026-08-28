from pathlib import Path

import cv2
import pandas as pd

from backend.app.cv.blur import calculate_sharpness
from backend.app.cv.exposure import (
    calculate_brightness,
    calculate_contrast,
)
from backend.app.cv.noise import estimate_noise
from backend.app.cv.corruption import analyze_corruption


BASE_DIR = Path(__file__).resolve().parent

TRAIN_DIR = BASE_DIR / "dataset" / "generated" / "train"
TEST_DIR = BASE_DIR / "dataset" / "generated" / "test"

TRAIN_CSV = BASE_DIR / "train_features.csv"
TEST_CSV = BASE_DIR / "test_features.csv"

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

LABELS = [
    "acceptable",
    "degraded",
    "defective",
]


def extract_features(image):
    sharpness = calculate_sharpness(image)

    brightness = calculate_brightness(image)

    contrast = calculate_contrast(image)

    noise = estimate_noise(image)

    corruption = analyze_corruption(image)

    height, width = image.shape[:2]

    return {
        "width": int(width),
        "height": int(height),
        "aspect_ratio": round(
            float(width / height),
            4
        ),

        "sharpness": sharpness,

        "brightness": brightness,

        "contrast": contrast,

        "noise": noise,

        "intensity_std":
            corruption["intensity_std"],

        "unique_intensity_values":
            corruption[
                "unique_intensity_values"
            ],
    }


def process_dataset(dataset_dir):
    rows = []

    for label in LABELS:
        class_dir = dataset_dir / label

        if not class_dir.exists():
            print(
                f"Warning: folder not found: "
                f"{class_dir}"
            )
            continue

        files = [
            file
            for file in class_dir.iterdir()
            if (
                file.is_file()
                and file.suffix.lower()
                in SUPPORTED_EXTENSIONS
            )
        ]

        print(
            f"\nProcessing {label}: "
            f"{len(files)} images"
        )

        for index, image_path in enumerate(
            files,
            start=1
        ):
            image = cv2.imread(
                str(image_path)
            )

            if image is None:
                print(
                    f"Skipping unreadable file: "
                    f"{image_path.name}"
                )
                continue

            features = extract_features(image)

            features["filename"] = (
                image_path.name
            )

            features["label"] = label.upper()

            rows.append(features)

            if (
                index % 50 == 0
                or index == len(files)
            ):
                print(
                    f"  {index}/{len(files)} "
                    f"completed"
                )

    return pd.DataFrame(rows)


def save_dataframe(
    dataframe,
    output_path
):
    dataframe.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nSaved: {output_path}"
    )

    print(
        f"Rows: {len(dataframe)}"
    )


def main():
    print(
        "\n=========================="
    )
    print(
        "VISIONGUARD FEATURE EXTRACTION"
    )
    print(
        "=========================="
    )

    print(
        "\nExtracting TRAIN features..."
    )

    train_df = process_dataset(
        TRAIN_DIR
    )

    save_dataframe(
        train_df,
        TRAIN_CSV
    )


    print(
        "\nExtracting TEST features..."
    )

    test_df = process_dataset(
        TEST_DIR
    )

    save_dataframe(
        test_df,
        TEST_CSV
    )


    print(
        "\n--------------------------"
    )
    print(
        "FEATURE EXTRACTION SUMMARY"
    )
    print(
        "--------------------------"
    )

    print(
        f"Training rows: "
        f"{len(train_df)}"
    )

    print(
        f"Testing rows: "
        f"{len(test_df)}"
    )

    print(
        "\nTraining label counts:"
    )

    if not train_df.empty:
        print(
            train_df["label"]
            .value_counts()
        )

    print(
        "\nTesting label counts:"
    )

    if not test_df.empty:
        print(
            test_df["label"]
            .value_counts()
        )

    print(
        "\nFeature extraction completed."
    )


if __name__ == "__main__":
    main()