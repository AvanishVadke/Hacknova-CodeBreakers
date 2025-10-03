"""
Image preprocessing utilities
Common image operations for CV pipeline
"""

import cv2
import numpy as np
from typing import Tuple

def resize_image(image: np.ndarray, width: int = None, height: int = None) -> np.ndarray:
    """
    Resize image while maintaining aspect ratio
    """
    (h, w) = image.shape[:2]
    
    if width is None and height is None:
        return image
    
    if width is None:
        ratio = height / float(h)
        dimensions = (int(w * ratio), height)
    else:
        ratio = width / float(w)
        dimensions = (width, int(h * ratio))
    
    return cv2.resize(image, dimensions, interpolation=cv2.INTER_AREA)

def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize image pixel values to [0, 1]
    """
    return image.astype(np.float32) / 255.0

def enhance_contrast(image: np.ndarray) -> np.ndarray:
    """
    Enhance image contrast using CLAHE
    """
    if len(image.shape) == 3:
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge and convert back
        enhanced = cv2.merge([l, a, b])
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    else:
        # Grayscale image
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        return clahe.apply(image)

def crop_region(image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
    """
    Crop region from image using bounding box
    
    Args:
        image: Input image
        bbox: (x, y, width, height)
    """
    x, y, w, h = bbox
    return image[y:y+h, x:x+w]
