from pathlib import Path
import random

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent

CLEAN_TRAIN_DIR = BASE_DIR / "dataset" / "clean" / "train"
CLEAN_TEST_DIR = BASE_DIR / "dataset" / "clean" / "test"

GENERATED_TRAIN_DIR = BASE_DIR / "dataset" / "generated" / "train"
GENERATED_TEST_DIR = BASE_DIR / "dataset" / "generated" / "test"

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

RANDOM_SEED = 42


def add_gaussian_noise(image, sigma):
    noise = np.random.normal(
        0,
        sigma,
        image.shape
    ).astype(np.float32)

    noisy = image.astype(np.float32) + noise

    return np.clip(
        noisy,
        0,
        255
    ).astype(np.uint8)


def adjust_brightness(image, factor):
    adjusted = image.astype(np.float32) * factor

    return np.clip(
        adjusted,
        0,
        255
    ).astype(np.uint8)


def apply_blur(image, kernel_size):
    if kernel_size % 2 == 0:
        kernel_size += 1

    return cv2.GaussianBlur(
        image,
        (kernel_size, kernel_size),
        0
    )


def apply_jpeg_compression(image, quality):
    success, encoded = cv2.imencode(
        ".jpg",
        image,
        [
            int(cv2.IMWRITE_JPEG_QUALITY),
            quality
        ]
    )

    if not success:
        return image

    return cv2.imdecode(
        encoded,
        cv2.IMREAD_COLOR
    )


def resize_if_needed(image, max_dimension=1200):
    height, width = image.shape[:2]

    largest = max(height, width)

    if largest <= max_dimension:
        return image

    scale = max_dimension / largest

    new_width = int(width * scale)
    new_height = int(height * scale)

    return cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_AREA
    )


def save_image(directory, filename, image):
    directory.mkdir(
        parents=True,
        exist_ok=True
    )

    cv2.imwrite(
        str(directory / filename),
        image
    )


def generate_acceptable(image, stem, output_dir):
    mild_brightness = adjust_brightness(
        image,
        random.uniform(0.9, 1.1)
    )

    save_image(
        output_dir / "acceptable",
        f"{stem}_clean.jpg",
        image
    )

    save_image(
        output_dir / "acceptable",
        f"{stem}_mild_brightness.jpg",
        mild_brightness
    )


def generate_degraded(image, stem, output_dir):
    moderate_blur = apply_blur(
        image,
        random.choice([5, 7, 9])
    )

    save_image(
        output_dir / "degraded",
        f"{stem}_moderate_blur.jpg",
        moderate_blur
    )

    moderate_noise = add_gaussian_noise(
        image,
        random.uniform(10, 20)
    )

    save_image(
        output_dir / "degraded",
        f"{stem}_moderate_noise.jpg",
        moderate_noise
    )

    underexposed = adjust_brightness(
        image,
        random.uniform(0.45, 0.7)
    )

    save_image(
        output_dir / "degraded",
        f"{stem}_underexposed.jpg",
        underexposed
    )

    overexposed = adjust_brightness(
        image,
        random.uniform(1.3, 1.7)
    )

    save_image(
        output_dir / "degraded",
        f"{stem}_overexposed.jpg",
        overexposed
    )

    compressed = apply_jpeg_compression(
        image,
        random.randint(25, 50)
    )

    save_image(
        output_dir / "degraded",
        f"{stem}_compressed.jpg",
        compressed
    )


def generate_defective(image, stem, output_dir):
    severe_blur = apply_blur(
        image,
        random.choice([15, 21, 31])
    )

    save_image(
        output_dir / "defective",
        f"{stem}_severe_blur.jpg",
        severe_blur
    )

    severe_noise = add_gaussian_noise(
        image,
        random.uniform(35, 60)
    )

    save_image(
        output_dir / "defective",
        f"{stem}_severe_noise.jpg",
        severe_noise
    )

    extreme_dark = adjust_brightness(
        image,
        random.uniform(0.08, 0.25)
    )

    save_image(
        output_dir / "defective",
        f"{stem}_extreme_dark.jpg",
        extreme_dark
    )

    extreme_bright = adjust_brightness(
        image,
        random.uniform(2.0, 3.0)
    )

    save_image(
        output_dir / "defective",
        f"{stem}_extreme_bright.jpg",
        extreme_bright
    )

    heavy_compression = apply_jpeg_compression(
        image,
        random.randint(3, 12)
    )

    save_image(
        output_dir / "defective",
        f"{stem}_heavy_compression.jpg",
        heavy_compression
    )

    combined = apply_blur(
        image,
        21
    )

    combined = add_gaussian_noise(
        combined,
        45
    )

    combined = adjust_brightness(
        combined,
        0.3
    )

    save_image(
        output_dir / "defective",
        f"{stem}_multiple_defects.jpg",
        combined
    )


def clear_generated_images(output_dir):
    if not output_dir.exists():
        return

    for class_name in [
        "acceptable",
        "degraded",
        "defective"
    ]:
        class_dir = output_dir / class_name

        if not class_dir.exists():
            continue

        for file in class_dir.iterdir():
            if (
                file.is_file()
                and file.suffix.lower() in SUPPORTED_EXTENSIONS
            ):
                file.unlink()


def process_split(clean_dir, output_dir, split_name):
    files = [
        path
        for path in clean_dir.iterdir()
        if (
            path.is_file()
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )
    ]

    if not files:
        print(
            f"No clean images found for {split_name}: "
            f"{clean_dir}"
        )

        return {
            "source": 0,
            "acceptable": 0,
            "degraded": 0,
            "defective": 0
        }

    print(
        f"\nGenerating {split_name} dataset "
        f"from {len(files)} source images..."
    )

    processed = 0

    for index, image_path in enumerate(
        files,
        start=1
    ):
        image = cv2.imread(
            str(image_path)
        )

        if image is None:
            print(
                f"Skipping unreadable image: "
                f"{image_path.name}"
            )
            continue

        image = resize_if_needed(image)

        stem = image_path.stem

        generate_acceptable(
            image,
            stem,
            output_dir
        )

        generate_degraded(
            image,
            stem,
            output_dir
        )

        generate_defective(
            image,
            stem,
            output_dir
        )

        processed += 1

        print(
            f"[{index}/{len(files)}] "
            f"{split_name}: {image_path.name}"
        )

    return {
        "source": processed,
        "acceptable": processed * 2,
        "degraded": processed * 5,
        "defective": processed * 6
    }


def main():
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    clear_generated_images(
        GENERATED_TRAIN_DIR
    )

    clear_generated_images(
        GENERATED_TEST_DIR
    )

    train_stats = process_split(
        CLEAN_TRAIN_DIR,
        GENERATED_TRAIN_DIR,
        "TRAIN"
    )

    test_stats = process_split(
        CLEAN_TEST_DIR,
        GENERATED_TEST_DIR,
        "TEST"
    )

    print("\n--------------------------")
    print("DATASET GENERATION SUMMARY")
    print("--------------------------")

    print("\nTRAIN")
    print(
        f"Source images: "
        f"{train_stats['source']}"
    )
    print(
        f"Acceptable: "
        f"{train_stats['acceptable']}"
    )
    print(
        f"Degraded: "
        f"{train_stats['degraded']}"
    )
    print(
        f"Defective: "
        f"{train_stats['defective']}"
    )

    print("\nTEST")
    print(
        f"Source images: "
        f"{test_stats['source']}"
    )
    print(
        f"Acceptable: "
        f"{test_stats['acceptable']}"
    )
    print(
        f"Degraded: "
        f"{test_stats['degraded']}"
    )
    print(
        f"Defective: "
        f"{test_stats['defective']}"
    )

    total_train = (
        train_stats["acceptable"]
        + train_stats["degraded"]
        + train_stats["defective"]
    )

    total_test = (
        test_stats["acceptable"]
        + test_stats["degraded"]
        + test_stats["defective"]
    )

    print(
        f"\nTotal generated training images: "
        f"{total_train}"
    )

    print(
        f"Total generated testing images: "
        f"{total_test}"
    )

    print(
        "\nDataset generation completed."
    )


if __name__ == "__main__":
    main()