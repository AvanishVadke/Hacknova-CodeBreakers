"""
OCR Module for ID Card Recognition
Extract text from student ID cards
"""

import cv2
import numpy as np
from typing import Dict, Optional

class IDCardOCR:
    """
    ID Card OCR using Tesseract/EasyOCR
    Extracts student information from ID cards
    """
    
    def __init__(self):
        # TODO: Initialize OCR engine (Tesseract or EasyOCR)
        pass
    
    def extract_info(self, image_path: str) -> Optional[Dict]:
        """
        Extract information from ID card
        
        Args:
            image_path: Path to ID card image
            
        Returns:
            dict with moodle_id, name, department
        """
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # Preprocess image
        preprocessed = self.preprocess_id_card(image)
        
        # TODO: Run OCR
        # 1. Detect text regions
        # 2. Extract text using OCR
        # 3. Parse and structure data
        
        return {
            "moodle_id": "EXTRACTED_ID",
            "name": "EXTRACTED_NAME",
            "department": "EXTRACTED_DEPT",
            "confidence": 0.9
        }
    
    def preprocess_id_card(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess ID card image
        """
        # Resize
        scale_percent = 200
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)
        
        # Convert to grayscale
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return thresh
    
    def validate_id_format(self, moodle_id: str) -> bool:
        """
        Validate Moodle ID format
        """
        # TODO: Implement ID format validation
        return len(moodle_id) > 0

if __name__ == "__main__":
    # Test OCR
    ocr = IDCardOCR()
    result = ocr.extract_info("../../data/id_cards/sample_id_1.jpg")
    print(f"Extracted info: {result}")
