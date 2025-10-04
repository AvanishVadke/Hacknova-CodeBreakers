"""
ID Card Verification Module (Without YOLO)
Uses OpenCV for ID card detection and EasyOCR for text extraction
Extracts Photo, Name, Department, and Moodle ID
"""

import cv2
import torch
import easyocr
import numpy as np
import json
import re
from datetime import datetime
from pathlib import Path
import sys

# Add config to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import *


class IDCardVerifier:
    """
    ID Card verification system using OpenCV detection instead of YOLO
    """
    
    def __init__(self, use_gpu=True):
        """
        Initialize the ID card verifier
        
        Args:
            use_gpu (bool): Whether to use GPU acceleration for OCR
        """
        self.use_gpu = use_gpu
        self.device = 'cuda' if (use_gpu and torch.cuda.is_available()) else 'cpu'
        
        print("=" * 70)
        print("🎴 ID CARD VERIFICATION SYSTEM (OpenCV Detection)")
        print("=" * 70)
        print(f"🔧 Device: {self.device.upper()}")
        
        if self.device == 'cuda':
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
            print(f"🔥 CUDA Version: {torch.version.cuda}")
        
        # Initialize EasyOCR
        print(f"\n📝 Initializing EasyOCR (GPU: {OCR_GPU})...")
        self.reader = easyocr.Reader(
            OCR_LANGUAGES, 
            gpu=OCR_GPU,
            verbose=False
        )
        print("✅ EasyOCR initialized successfully")
        print("=" * 70)
        
        # Stats
        self.stats = {
            'frames_processed': 0,
            'cards_detected': 0,
            'cards_verified': 0,
            'ids_extracted': 0
        }
        
        # Last save time for cooldown
        self.last_save_time = datetime.min
        
    def detect_id_card_opencv(self, frame):
        """
        Detect ID card using OpenCV edge detection and contour finding
        
        Args:
            frame: Input frame
            
        Returns:
            list: List of detected card bounding boxes (x, y, w, h)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Dilate edges to connect nearby edges
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cards = []
        frame_area = frame.shape[0] * frame.shape[1]
        
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate area and aspect ratio
            area = w * h
            aspect_ratio = w / h if h > 0 else 0
            
            # Filter based on:
            # 1. Area (5% to 60% of frame)
            # 2. Aspect ratio (typical ID card: 1.4 to 1.8)
            # 3. Minimum size
            if (0.05 * frame_area < area < 0.6 * frame_area and
                1.3 < aspect_ratio < 2.0 and
                w > 200 and h > 150):
                
                # Approximate the contour to check if it's rectangular
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                
                # If it has 4 corners (rectangle), it's likely an ID card
                if len(approx) >= 4:
                    cards.append((x, y, w, h, area))
        
        # Sort by area (largest first) and return top 3
        cards.sort(key=lambda x: x[4], reverse=True)
        return [(x, y, w, h) for x, y, w, h, _ in cards[:3]]
    
    def extract_region(self, image, region_name):
        """
        Extract a specific region from the ID card image
        
        Args:
            image: ID card image
            region_name: Name of region ('photo', 'name', 'department', 'moodle_id')
            
        Returns:
            numpy.ndarray: Cropped region image
        """
        if region_name not in ID_CARD_REGIONS:
            raise ValueError(f"Unknown region: {region_name}")
        
        region = ID_CARD_REGIONS[region_name]
        h, w = image.shape[:2]
        
        # Calculate pixel coordinates from percentages
        x1 = int(w * region['x'])
        y1 = int(h * region['y'])
        x2 = int(w * (region['x'] + region['width']))
        y2 = int(h * (region['y'] + region['height']))
        
        # Ensure coordinates are within bounds
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        return image[y1:y2, x1:x2]
    
    def preprocess_for_ocr(self, region_image):
        """
        Preprocess region image for better OCR
        
        Args:
            region_image: Region to preprocess
            
        Returns:
            numpy.ndarray: Preprocessed image
        """
        if len(region_image.shape) == 3:
            gray = cv2.cvtColor(region_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = region_image
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            denoised, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return binary
    
    def extract_text_from_region(self, region_image, region_name=""):
        """
        Extract text from a region using EasyOCR
        
        Args:
            region_image: Region to extract text from
            region_name: Name of the region (for debugging)
            
        Returns:
            str: Extracted text
        """
        if region_image.size == 0:
            return ""
        
        # Preprocess
        preprocessed = self.preprocess_for_ocr(region_image)
        
        # OCR
        try:
            results = self.reader.readtext(preprocessed, detail=1)
            
            # Filter by confidence and combine
            texts = [text for (bbox, text, conf) in results if conf > OCR_CONFIDENCE_THRESHOLD]
            combined_text = " ".join(texts).strip()
            
            return combined_text
        except Exception as e:
            print(f"⚠️  OCR error on {region_name}: {e}")
            return ""
    
    def extract_photo(self, id_card_image):
        """
        Extract photo region from ID card
        
        Args:
            id_card_image: Full ID card image
            
        Returns:
            numpy.ndarray: Photo region
        """
        return self.extract_region(id_card_image, 'photo')
    
    def extract_name(self, id_card_image):
        """
        Extract name from ID card
        
        Args:
            id_card_image: Full ID card image
            
        Returns:
            str: Extracted name
        """
        name_region = self.extract_region(id_card_image, 'name')
        return self.extract_text_from_region(name_region, "name")
    
    def extract_department(self, id_card_image):
        """
        Extract department from ID card
        
        Args:
            id_card_image: Full ID card image
            
        Returns:
            str: Extracted department
        """
        dept_region = self.extract_region(id_card_image, 'department')
        return self.extract_text_from_region(dept_region, "department")
    
    def extract_moodle_id(self, id_card_image):
        """
        Extract Moodle ID from ID card
        
        Args:
            id_card_image: Full ID card image
            
        Returns:
            str: Extracted Moodle ID
        """
        id_region = self.extract_region(id_card_image, 'moodle_id')
        text = self.extract_text_from_region(id_region, "moodle_id")
        
        # Look for pattern: 2XXXXXXX (8 digits starting with 2)
        match = re.search(MOODLE_ID_PATTERN, text)
        if match:
            return match.group(0)
        
        # Fallback: look for any 8-digit number
        match = re.search(r'\d{8}', text)
        if match:
            return match.group(0)
        
        return ""
    
    def detect_and_extract_id_card(self, frame):
        """
        Detect ID card in frame and extract all information
        
        Args:
            frame: Input frame
            
        Returns:
            tuple: (detected_cards_data, annotated_frame)
        """
        self.stats['frames_processed'] += 1
        annotated_frame = frame.copy()
        detected_cards = []
        
        # Detect cards using OpenCV
        card_boxes = self.detect_id_card_opencv(frame)
        
        for (x, y, w, h) in card_boxes:
            self.stats['cards_detected'] += 1
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(annotated_frame, "ID Card Detected", (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Extract card region
            card_image = frame[y:y+h, x:x+w]
            
            # Extract information
            try:
                name = self.extract_name(card_image)
                department = self.extract_department(card_image)
                moodle_id = self.extract_moodle_id(card_image)
                photo = self.extract_photo(card_image)
                
                # Validate: Must have at least Moodle ID
                if moodle_id:
                    self.stats['cards_verified'] += 1
                    self.stats['ids_extracted'] += 1
                    
                    card_data = {
                        'timestamp': datetime.now().isoformat(),
                        'moodle_id': moodle_id,
                        'name': name,
                        'department': department,
                        'bbox': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
                        'photo_extracted': photo is not None and photo.size > 0
                    }
                    
                    detected_cards.append((card_data, card_image, photo))
                    
                    # Display extracted info
                    y_offset = y + h + 30
                    if moodle_id:
                        cv2.putText(annotated_frame, f"ID: {moodle_id}", (x, y_offset),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        y_offset += 25
                    if name:
                        cv2.putText(annotated_frame, f"Name: {name[:20]}", (x, y_offset),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        y_offset += 25
                    if department:
                        cv2.putText(annotated_frame, f"Dept: {department[:20]}", (x, y_offset),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
            except Exception as e:
                print(f"⚠️  Error extracting card data: {e}")
                continue
        
        return detected_cards, annotated_frame
    
    def save_card_data(self, card_data, card_image, photo):
        """
        Save extracted card data to JSON and images
        
        Args:
            card_data: Dictionary with card information
            card_image: Full card image
            photo: Extracted photo
        """
        # Check cooldown
        now = datetime.now()
        if (now - self.last_save_time).total_seconds() < ID_CARD_SAVE_COOLDOWN:
            return
        
        self.last_save_time = now
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        moodle_id = card_data.get('moodle_id', 'unknown')
        
        # Save JSON
        json_path = OUTPUT_ID_CARD_DATA / f"{timestamp}_{moodle_id}.json"
        with open(json_path, 'w') as f:
            json.dump(card_data, f, indent=2)
        
        # Save card image
        card_img_path = OUTPUT_CAPTURED_FRAMES / f"{timestamp}_{moodle_id}_card.jpg"
        cv2.imwrite(str(card_img_path), card_image)
        
        # Save photo if available
        if photo is not None and photo.size > 0:
            photo_path = OUTPUT_ID_CARD_DATA / f"{timestamp}_{moodle_id}_photo.jpg"
            cv2.imwrite(str(photo_path), photo)
        
        print(f"💾 Saved: {moodle_id} -> {json_path.name}")
    
    def process_camera_stream(self, camera_index=0, save_auto=True):
        """
        Process live camera stream
        
        Args:
            camera_index: Camera index (default 0)
            save_auto: Auto-save valid detections
        """
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"❌ Failed to open camera {camera_index}")
            return
        
        print(f"\n📷 Starting camera stream (index: {camera_index})")
        print("✅ Camera opened. Press 'q' to quit, 's' to save detection")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                # Detect and extract
                detected_cards, annotated_frame = self.detect_and_extract_id_card(frame)
                
                # Auto-save
                if save_auto and detected_cards:
                    for card_data, card_image, photo in detected_cards:
                        self.save_card_data(card_data, card_image, photo)
                
                # Display stats
                stats_text = f"Frames: {self.stats['frames_processed']} | Detected: {self.stats['cards_detected']} | Verified: {self.stats['cards_verified']}"
                cv2.putText(annotated_frame, stats_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Show frame
                cv2.imshow('ID Card Verification (OpenCV)', annotated_frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s') and detected_cards:
                    for card_data, card_image, photo in detected_cards:
                        self.save_card_data(card_data, card_image, photo)
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print(f"\n✅ Session complete!")
            print(f"📊 Stats: {self.stats['frames_processed']} frames, "
                  f"{self.stats['cards_detected']} cards detected, "
                  f"{self.stats['cards_verified']} cards verified, "
                  f"{self.stats['ids_extracted']} IDs extracted")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ID Card Verification System (OpenCV Detection)')
    parser.add_argument('--camera', action='store_true', help='Use camera stream')
    parser.add_argument('--camera-index', type=int, default=0, help='Camera index (default: 0)')
    parser.add_argument('--image', type=str, help='Path to ID card image')
    parser.add_argument('--no-gpu', action='store_true', help='Disable GPU acceleration')
    
    args = parser.parse_args()
    
    # Initialize verifier
    verifier = IDCardVerifier(use_gpu=not args.no_gpu)
    
    if args.camera:
        # Camera mode
        verifier.process_camera_stream(camera_index=args.camera_index)
    elif args.image:
        # Single image mode
        image = cv2.imread(args.image)
        if image is None:
            print(f"❌ Failed to load image: {args.image}")
            return
        
        detected_cards, annotated = verifier.detect_and_extract_id_card(image)
        
        if detected_cards:
            for card_data, card_image, photo in detected_cards:
                print(f"\n✅ Card Data: {json.dumps(card_data, indent=2)}")
                verifier.save_card_data(card_data, card_image, photo)
        else:
            print("❌ No ID cards detected")
        
        cv2.imshow('Result', annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("❌ Please specify --camera or --image")


if __name__ == "__main__":
    main()
