"""
Simple ID Card Tester - No GUI (headless)
Tests the trained YOLO model + EasyOCR
"""

import cv2
import torch
import easyocr
from pathlib import Path
from ultralytics import YOLO
import json


def test_id_card(image_path, model_path="models/id_card_best.pt"):
    """
    Test ID card detection and OCR without GUI
    """
    print("=" * 70)
    print("🧪 ID CARD TESTER (Headless)")
    print("=" * 70)
    
    # Check GPU
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"🔧 Device: {device.upper()}")
    
    if device == 'cuda':
        print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Failed to load image: {image_path}")
        return
    
    print(f"\n📸 Image: {image_path}")
    print(f"📐 Size: {image.shape[1]}x{image.shape[0]}")
    
    # Test 1: YOLO Detection
    print("\n" + "=" * 70)
    print("Test 1: YOLO ID Card Detection")
    print("=" * 70)
    
    try:
        model = YOLO(model_path)
        print(f"✅ YOLO model loaded: {model_path}")
        
        results = model(image, conf=0.25, verbose=False)
        detections = results[0].boxes
        
        print(f"🔍 Detections found: {len(detections)}")
        
        if len(detections) > 0:
            for i, box in enumerate(detections):
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                print(f"   Card {i+1}: [{x1}, {y1}, {x2}, {y2}] confidence={conf:.2f}")
        else:
            print("   ⚠️  No ID cards detected by YOLO")
    except Exception as e:
        print(f"❌ YOLO detection failed: {e}")
    
    # Test 2: OpenCV Fallback Detection
    print("\n" + "=" * 70)
    print("Test 2: OpenCV Edge Detection (Fallback)")
    print("=" * 70)
    
    h, w = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    import numpy as np
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=2)
    
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    frame_area = h * w
    found_opencv = False
    
    for contour in contours:
        x, y, w_box, h_box = cv2.boundingRect(contour)
        area = w_box * h_box
        aspect_ratio = w_box / h_box if h_box > 0 else 0
        
        if (0.1 * frame_area < area < 0.9 * frame_area and
            1.2 < aspect_ratio < 2.2 and
            w_box > 150 and h_box > 100):
            
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            if len(approx) >= 4:
                print(f"✅ OpenCV detected card: [{x}, {y}, {x+w_box}, {y+h_box}]")
                print(f"   Area: {area/frame_area*100:.1f}% of frame")
                print(f"   Aspect ratio: {aspect_ratio:.2f}")
                found_opencv = True
                break
    
    if not found_opencv:
        print("⚠️  OpenCV did not detect rectangular ID card")
    
    # Test 3: OCR
    print("\n" + "=" * 70)
    print("Test 3: EasyOCR Text Extraction")
    print("=" * 70)
    
    try:
        print("📝 Initializing EasyOCR...")
        reader = easyocr.Reader(['en'], gpu=(device == 'cuda'), verbose=False)
        print("✅ EasyOCR initialized")
        
        print("🔍 Extracting text...")
        ocr_results = reader.readtext(image)
        
        print(f"📄 Found {len(ocr_results)} text regions:")
        
        for i, (bbox, text, conf) in enumerate(ocr_results, 1):
            print(f"   {i}. '{text}' (confidence: {conf:.2f})")
        
        # Look for Moodle ID pattern
        import re
        moodle_pattern = r'\b2\d{7}\b'  # 8 digits starting with 2
        
        all_text = ' '.join([text for _, text, _ in ocr_results])
        moodle_ids = re.findall(moodle_pattern, all_text)
        
        if moodle_ids:
            print(f"\n✅ Found Moodle ID(s): {', '.join(moodle_ids)}")
        else:
            print("\n⚠️  No Moodle ID pattern found (8 digits starting with 2)")
    
    except Exception as e:
        print(f"❌ OCR failed: {e}")
    
    print("\n" + "=" * 70)
    print("🎉 Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_id_card_simple.py <image_path>")
        print("\nExample: python test_id_card_simple.py data/training_data/harsh.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    test_id_card(image_path)
