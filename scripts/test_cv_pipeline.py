"""
Test CV Pipeline
Test ANPR, OCR, and Face Recognition modules
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from cv_pipeline.anpr.detector import ANPRDetector
from cv_pipeline.ocr.id_card_reader import IDCardOCR
from cv_pipeline.face_recognition.recognizer import FaceRecognition

def test_anpr():
    """Test ANPR detector"""
    print("\n🚗 Testing ANPR...")
    detector = ANPRDetector()
    
    # Test with sample image (if exists)
    test_image = "data/temp/test_vehicle.jpg"
    if os.path.exists(test_image):
        result = detector.detect_plate(test_image)
        print(f"Result: {result}")
    else:
        print("⚠️  Sample vehicle image not found")

def test_ocr():
    """Test ID card OCR"""
    print("\n🪪 Testing ID Card OCR...")
    ocr = IDCardOCR()
    
    # Test with sample ID card
    test_id = "data/id_cards/student_id_STU001.jpg"
    if os.path.exists(test_id):
        result = ocr.extract_info(test_id)
        print(f"Result: {result}")
    else:
        print("⚠️  Sample ID card not found")

def test_face_recognition():
    """Test face recognition"""
    print("\n👤 Testing Face Recognition...")
    fr = FaceRecognition()
    
    # Generate sample embeddings
    import numpy as np
    embedding1 = np.random.rand(128)
    embedding2 = np.random.rand(128)
    
    match, similarity = fr.compare_faces(embedding1, embedding2)
    print(f"Match: {match}, Similarity: {similarity:.4f}")

if __name__ == "__main__":
    print("🧪 Testing CV Pipeline Components")
    print("=" * 50)
    
    test_anpr()
    test_ocr()
    test_face_recognition()
    
    print("\n✅ Testing completed!")
