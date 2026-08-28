import cv2
import numpy as np

def decode_image(file_bytes):
    """
    Convert uploaded image bytes into an OpenCV image.
    """

    image_array = np.frombuffer(file_bytes, np.uint8)

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    return image

def get_image_dimensions(image):
    height, width = image.shape[:2]

    return {
        "width": int(width),
        "height": int(height)
    }
