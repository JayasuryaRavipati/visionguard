from pathlib import Path
import random
import shutil

import cv2
import numpy as np

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

# CHANGE THIS to the folder containing your extracted
# Caltech-101 category folders.
SOURCE_DIR = Path(
    r"C:\Users\surya\Downloads\caltech-101\caltech-101\101_ObjectCategories"
)

BASE_DIR = Path(__file__).resolve().parent

TRAIN_DIR = BASE_DIR / "dataset" / "clean" / "train"
TEST_DIR = BASE_DIR / "dataset" / "clean" / "test"

TARGET_TOTAL = 100
TRAIN_RATIO = 0.80

RANDOM_SEED = 42

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

# ---------------------------------------------------------
# QUALITY FUNCTIONS
# ---------------------------------------------------------

def calculate_sharpness(image):
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return float(
        cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()
    )

def calculate_brightness(image):
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return float(
        np.mean(gray)
    )

def calculate_contrast(image):
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return float(
        np.std(gray)
    )

def estimate_noise(image):
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    residual = (
        gray.astype(np.float32)
        - blurred.astype(np.float32)
    )

    return float(
        np.std(residual)
    )

def check_image_quality(image):
    """
    Screen source images for obvious quality problems.

    These thresholds are intentionally permissive.
    They are preprocessing rules, not our final ML model.
    """

    height, width = image.shape[:2]

    sharpness = calculate_sharpness(image)
    brightness = calculate_brightness(image)
    contrast = calculate_contrast(image)
    noise = estimate_noise(image)

    reasons = []

    # Reject very tiny images
    if width < 100 or height < 100:
        reasons.append("too_small")

    # Reject obviously blurry images
    if sharpness < 80:
        reasons.append("too_blurry")

    # Reject nearly black images
    if brightness < 35:
        reasons.append("too_dark")

    # Reject nearly white images
    if brightness > 225:
        reasons.append("too_bright")

    # Reject images with extremely little variation
    if contrast < 15:
        reasons.append("very_low_contrast")

    # Reject extremely noisy candidates
    if noise > 30:
        reasons.append("very_noisy")

    return {
        "accepted": len(reasons) == 0,
        "reasons": reasons,
        "sharpness": round(sharpness, 2),
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "noise": round(noise, 2),
        "width": width,
        "height": height,
    }

# ---------------------------------------------------------
# DIRECTORY SETUP
# ---------------------------------------------------------

def prepare_output_directories():
    TRAIN_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    TEST_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

def clear_old_images(directory):
    for file in directory.iterdir():
        if (
            file.is_file()
            and file.suffix.lower()
            in SUPPORTED_EXTENSIONS
        ):
            file.unlink()

# ---------------------------------------------------------
# FIND CALTECH IMAGES
# ---------------------------------------------------------

def find_category_directories():
    """
    Find directories that directly contain images.

    This allows the script to work even if the ZIP
    contains another top-level folder.
    """

    categories = []

    for directory in SOURCE_DIR.rglob("*"):

        if not directory.is_dir():
            continue

        image_files = [
            file
            for file in directory.iterdir()
            if (
                file.is_file()
                and file.suffix.lower()
                in SUPPORTED_EXTENSIONS
            )
        ]

        if image_files:
            categories.append(
                (directory, image_files)
            )

    return categories

# ---------------------------------------------------------
# SCREEN IMAGES
# ---------------------------------------------------------

def screen_dataset(categories):
    accepted_by_category = {}

    total_checked = 0
    total_rejected = 0

    rejection_counts = {}

    for category_dir, image_files in categories:

        category_name = category_dir.name

        accepted = []

        random.shuffle(image_files)

        for image_path in image_files:

            total_checked += 1

            image = cv2.imread(
                str(image_path)
            )

            if image is None:
                total_rejected += 1

                rejection_counts[
                    "unreadable"
                ] = (
                    rejection_counts.get(
                        "unreadable",
                        0
                    )
                    + 1
                )

                continue

            quality = check_image_quality(
                image
            )

            if quality["accepted"]:

                accepted.append(
                    {
                        "path": image_path,
                        "quality": quality
                    }
                )

            else:

                total_rejected += 1

                for reason in quality["reasons"]:

                    rejection_counts[
                        reason
                    ] = (
                        rejection_counts.get(
                            reason,
                            0
                        )
                        + 1
                    )

        if accepted:

            accepted_by_category[
                category_name
            ] = accepted

    return (
        accepted_by_category,
        total_checked,
        total_rejected,
        rejection_counts
    )

# ---------------------------------------------------------
# BALANCED SELECTION
# ---------------------------------------------------------

def select_diverse_images(
    accepted_by_category,
    target
):
    """
    Select images across categories instead of taking
    100 images from only a few object classes.
    """

    categories = list(
        accepted_by_category.keys()
    )

    random.shuffle(categories)

    selected = []

    index = 0

    while (
        len(selected) < target
        and categories
    ):

        category = categories[
            index % len(categories)
        ]

        available = (
            accepted_by_category[
                category
            ]
        )

        if available:

            item = available.pop()

            selected.append(
                {
                    "category": category,
                    **item
                }
            )

        else:

            categories.remove(
                category
            )

            if not categories:
                break

        index += 1

    return selected

# ---------------------------------------------------------
# TRAIN / TEST SPLIT
# ---------------------------------------------------------

def split_and_copy(selected):
    random.shuffle(selected)

    train_count = int(
        len(selected)
        * TRAIN_RATIO
    )

    train_items = selected[
        :train_count
    ]

    test_items = selected[
        train_count:
    ]

    for index, item in enumerate(
        train_items,
        start=1
    ):

        source = item["path"]

        filename = (
            f"{index:03d}_"
            f"{item['category']}_"
            f"{source.name}"
        )

        shutil.copy2(
            source,
            TRAIN_DIR / filename
        )

    for index, item in enumerate(
        test_items,
        start=1
    ):

        source = item["path"]

        filename = (
            f"{index:03d}_"
            f"{item['category']}_"
            f"{source.name}"
        )

        shutil.copy2(
            source,
            TEST_DIR / filename
        )

    return train_items, test_items

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    random.seed(
        RANDOM_SEED
    )

    prepare_output_directories()

    clear_old_images(
        TRAIN_DIR
    )

    clear_old_images(
        TEST_DIR
    )

    if not SOURCE_DIR.exists():

        print(
            "\nERROR: Caltech-101 folder "
            "was not found."
        )

        print(
            f"Current SOURCE_DIR:\n"
            f"{SOURCE_DIR}"
        )

        print(
            "\nEdit SOURCE_DIR at the top "
            "of prepare_clean_dataset.py."
        )

        return

    print(
        "\nScanning Caltech-101..."
    )

    categories = (
        find_category_directories()
    )

    print(
        f"Found {len(categories)} "
        f"image categories."
    )

    if not categories:

        print(
            "\nNo image folders were found."
        )

        print(
            "Check SOURCE_DIR."
        )

        return

    (
        accepted_by_category,
        total_checked,
        total_rejected,
        rejection_counts
    ) = screen_dataset(
        categories
    )

    total_accepted = sum(
        len(images)
        for images
        in accepted_by_category.values()
    )

    print("\n--------------------------")
    print("QUALITY SCREENING SUMMARY")
    print("--------------------------")

    print(
        f"Images checked: {total_checked}"
    )

    print(
        f"Accepted candidates: "
        f"{total_accepted}"
    )

    print(
        f"Rejected candidates: "
        f"{total_rejected}"
    )

    if rejection_counts:

        print("\nRejection reasons:")

        for reason, count in sorted(
            rejection_counts.items()
        ):

            print(
                f"  {reason}: {count}"
            )

    if total_accepted < TARGET_TOTAL:

        print(
            f"\nWARNING: Only "
            f"{total_accepted} acceptable "
            f"images were found."
        )

        target = total_accepted

    else:

        target = TARGET_TOTAL

    selected = select_diverse_images(
        accepted_by_category,
        target
    )

    train_items, test_items = (
        split_and_copy(
            selected
        )
    )

    print("\n--------------------------")
    print("DATASET PREPARATION DONE")
    print("--------------------------")

    print(
        f"Selected originals: "
        f"{len(selected)}"
    )

    print(
        f"Training originals: "
        f"{len(train_items)}"
    )

    print(
        f"Testing originals: "
        f"{len(test_items)}"
    )

    print(
        f"\nTrain folder:\n"
        f"{TRAIN_DIR}"
    )

    print(
        f"\nTest folder:\n"
        f"{TEST_DIR}"
    )

if __name__ == "__main__":
    main()
