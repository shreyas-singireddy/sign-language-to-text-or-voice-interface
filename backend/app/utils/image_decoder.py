import base64
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None


def image_from_base64(data: str):
    if cv2 is None:
        return None

    header, encoded = data.split(',', 1) if ',' in data else ('', data)
    decoded = base64.b64decode(encoded)
    array = np.frombuffer(decoded, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    return image
