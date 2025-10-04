"""
Offline ID Card Recognition System
No API calls - 100% local processing
Uses YOLO for detection + EasyOCR for text extraction
"""

import cv2
import torch
import easyocr
import numpy as np
import json
import re
from datetime import datetime
from pathlib import Path
from ultralytics import YOLO
import sys

# Add config to path
sys.path.append(str(Path(__file__).resolve().parent))
from config.config import *

# Detection constants
YOLO_CONFIDENCE = 0.25  # YOLO detection confidence threshold
YOLO_IOU = 0.45         # YOLO IoU threshold for NMS
ID_CARD_SAVE_COOLDOWN = 3.0  # Cooldown between saves (seconds)

# Output directories
OUTPUT_ID_CARD_DATA = Path("outputs/id_card_data")
OUTPUT_CAPTURED_FRAMES = Path("outputs/captured_frames")
OUTPUT_ID_CARD_DATA.mkdir(parents=True, exist_ok=True)
OUTPUT_CAPTURED_FRAMES.mkdir(parents=True, exist_ok=True)


class OfflineIDCardRecognizer:
    """
    Complete offline ID card recognition system
    Uses local YOLO + EasyOCR - no API calls
    """
    
    def __init__(self, yolo_model_path=None, use_gpu=True):
        """
        Initialize offline ID card recognizer
        
        Args:
            yolo_model_path (str): Path to YOLO model (optional)
            use_gpu (bool): Use GPU acceleration
        """
        self.use_gpu = use_gpu
        self.device = 'cuda' if (use_gpu and torch.cuda.is_available()) else 'cpu'
        
        print("=" * 70)
        print("🎴 OFFLINE ID CARD RECOGNITION SYSTEM")
        print("=" * 70)
        print(f"🔧 Device: {self.device.upper()}")
        
        if self.device == 'cuda':
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
            print(f"🔥 CUDA Version: {torch.version.cuda}")
        
        # Initialize YOLO for ID card detection
        self.yolo_model_path = yolo_model_path or YOLO_MODEL_PATH
        print(f"\n📦 Loading YOLO model: {self.yolo_model_path}")
        
        try:
            self.yolo_model = YOLO(str(self.yolo_model_path))
            self.yolo_model.to(self.device)
            print("✅ YOLO model loaded successfully")
        except Exception as e:
            print(f"⚠️  YOLO model not found: {e}")
            print("   Using OpenCV fallback for detection")
            self.yolo_model = None
        
        # Initialize EasyOCR for text extraction
        print(f"\n📝 Initializing EasyOCR (GPU: {OCR_GPU})...")
        self.reader = easyocr.Reader(
            OCR_LANGUAGES,
            gpu=OCR_GPU,
            verbose=False
        )
        print("✅ EasyOCR initialized successfully")
        
        # Invalid name patterns (cannot be names)
        self.invalid_name_patterns = [
            'apsit', 'engineering', 'comp', 'engineer', 'technology',
            'institute', 'department', 'mech', 'civil', 'elect',
            'principal', 'charitable', 'trust', 'address', 'addross',
            'shah', 'parshvanalh'
        ]
        
        # Valid department mappings (correct spelling)
        self.valid_departments = {
            'computer': 'COMPUTER ENGINEERING',
            'mechanical': 'MECHANICAL ENGINEERING', 
            'civil': 'CIVIL ENGINEERING',
            'electrical': 'ELECTRICAL ENGINEERING',
            'electronics': 'ELECTRONICS ENGINEERING',
            'information': 'INFORMATION TECHNOLOGY',
            'it': 'INFORMATION TECHNOLOGY'
        }
        
        print("=" * 70)
        
        # Statistics
        self.stats = {
            'frames_processed': 0,
            'cards_detected': 0,
            'cards_recognized': 0,
            'ids_extracted': 0
        }
        
        # Last save time
        self.last_save_time = datetime.min
    
    def detect_id_card_opencv(self, frame):
        """
        Fallback: Detect ID card using OpenCV (if YOLO not available)
        
        Args:
            frame: Input frame
            
        Returns:
            list: Detected card bounding boxes [(x, y, w, h), ...]
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cards = []
        frame_area = frame.shape[0] * frame.shape[1]
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            aspect_ratio = w / h if h > 0 else 0
            
            if (0.05 * frame_area < area < 0.6 * frame_area and
                1.3 < aspect_ratio < 2.0 and
                w > 200 and h > 150):
                
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                
                if len(approx) >= 4:
                    cards.append((x, y, w, h, area, 0.8))  # confidence = 0.8
        
        cards.sort(key=lambda x: x[4], reverse=True)
        return [(x, y, w, h, conf) for x, y, w, h, _, conf in cards[:3]]
    
    def detect_id_card_yolo(self, frame):
        """
        Detect ID card using YOLO model
        
        Args:
            frame: Input frame
            
        Returns:
            list: Detected card bounding boxes [(x, y, w, h, confidence), ...]
        """
        results = self.yolo_model(frame, conf=YOLO_CONFIDENCE, iou=YOLO_IOU, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                
                x, y = int(x1), int(y1)
                w, h = int(x2 - x1), int(y2 - y1)
                
                detections.append((x, y, w, h, conf))
        
        return detections
    
    def preprocess_for_ocr(self, image):
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image: Input image (BGR)
            
        Returns:
            numpy.ndarray: Preprocessed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Increase contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        # Sharpen
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        return sharpened
    
    def is_valid_name(self, text):
        """Validate if text is a proper person's name"""
        text_clean = text.strip().upper()
        text_lower = text_clean.lower()
        
        # Must be alphabetic (allow spaces)
        if not all(c.isalpha() or c.isspace() for c in text_clean):
            return False
        
        # Length check (names are typically 6-30 characters)
        if len(text_clean) < 6 or len(text_clean) > 30:
            return False
        
        # Check for invalid name patterns (APSIT, COMP, ENGINEERING, etc.)
        for invalid_pattern in self.invalid_name_patterns:
            if invalid_pattern in text_lower:
                return False
        
        # Must contain at least one space (first + last name) OR be > 8 chars
        if ' ' not in text_clean and len(text_clean) < 8:
            return False
        
        # Additional check: if it's all one word, it should look like a proper name
        words = text_clean.split()
        if len(words) == 1:
            # Single word - must be at least 8 chars
            if len(words[0]) < 8:
                return False
        
        # Check vowel proportion (names typically have vowels)
        vowel_count = sum(1 for c in text_lower if c in 'aeiou')
        if len(text_clean) > 0 and vowel_count / len(text_clean) < 0.2:
            return False
        
        return True
    
    def normalize_department(self, text):
        """Normalize department name to standard format"""
        text_lower = text.lower()
        
        # Check each department keyword and return standardized name
        for keyword, standard_name in self.valid_departments.items():
            if keyword in text_lower:
                return standard_name
        
        # If no match found, check if it has "engineering" and try to fix typos
        if 'engineer' in text_lower or 'engin' in text_lower:
            # Try to detect department type
            if 'compu' in text_lower or 'comp' in text_lower:
                return 'COMPUTER ENGINEERING'
            elif 'mech' in text_lower:
                return 'MECHANICAL ENGINEERING'
            elif 'civil' in text_lower:
                return 'CIVIL ENGINEERING'
            elif 'elect' in text_lower:
                return 'ELECTRICAL ENGINEERING'
            elif 'electron' in text_lower:
                return 'ELECTRONICS ENGINEERING'
            elif 'info' in text_lower or 'it' in text_lower:
                return 'INFORMATION TECHNOLOGY'
        
        return None
    
    def extract_text_with_ocr(self, image):
        """
        Extract all text from image using EasyOCR
        
        Args:
            image: Input image
            
        Returns:
            list: OCR results [(bbox, text, confidence), ...]
        """
        # Preprocess
        preprocessed = self.preprocess_for_ocr(image)
        
        # Run OCR
        try:
            results = self.reader.readtext(preprocessed, detail=1)
            return results
        except Exception as e:
            print(f"⚠️  OCR error: {e}")
            return []
    
    def parse_id_card_data(self, ocr_results, card_image):
        """
        Parse structured data from OCR results
        
        Args:
            ocr_results: List of OCR results from EasyOCR
            card_image: Full ID card image
            
        Returns:
            dict: Parsed ID card data
        """
        # Combine all text
        all_text = " ".join([text for (_, text, _) in ocr_results])
        
        # Initialize data structure
        card_data = {
            'moodle_id': None,
            'name': None,
            'department': None,
            'institute': None,
            'academic_year': None,
            'raw_text': all_text,
            'confidence': 0.0,
            'photo_extracted': False,
            'timestamp': datetime.now().isoformat()
        }
        
        # Extract Moodle ID (8 digits starting with 2)
        moodle_patterns = [
            r'ID\s*NO[:\s]*(\d{8})',  # ID NO: 22102003
            r'ID[:\s]*(\d{8})',        # ID: 22102003
            r'\b(2\d{7})\b',           # Just the number 22102003
        ]
        
        for pattern in moodle_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                card_data['moodle_id'] = match.group(1)
                break
        
        # If no Moodle ID found, try any 8-digit number
        if not card_data['moodle_id']:
            match = re.search(r'\b(\d{8})\b', all_text)
            if match:
                card_data['moodle_id'] = match.group(1)
        
        # Extract Name (usually all caps, multiple words)
        name_patterns = [
            r'([A-Z][A-Z\s]{10,50})',  # Long uppercase text
            r'Name[:\s]+([A-Z][A-Za-z\s]+)',  # After "Name:"
        ]
        
        name_candidates = []
        for pattern in name_patterns:
            matches = re.finditer(pattern, all_text)
            for match in matches:
                potential_name = match.group(1).strip()
                # Validate using smart validation
                if self.is_valid_name(potential_name):
                    name_candidates.append(potential_name)
        
        # Pick the longest valid name (likely the actual name)
        if name_candidates:
            card_data['name'] = max(name_candidates, key=len)
        
        # Extract Department with normalization
        dept_keywords = [
            'COMPUTER ENGINEERING',
            'MECHANICAL ENGINEERING',
            'CIVIL ENGINEERING',
            'ELECTRICAL ENGINEERING',
            'ELECTRONICS ENGINEERING',
            'INFORMATION TECHNOLOGY',
            'IT',
            'CSE',
            'ECE',
            'EEE',
            'COMPUTER', 'MECHANICAL', 'CIVIL', 'ELECTRICAL', 'ELECTRONICS'
        ]
        
        for keyword in dept_keywords:
            if keyword in all_text.upper():
                # Normalize the department name
                normalized = self.normalize_department(keyword)
                if normalized:
                    card_data['department'] = normalized
                    break
        
        # Extract Institute Name
        institute_keywords = ['INSTITUTE', 'COLLEGE', 'UNIVERSITY', 'TECHNOLOGY']
        for keyword in institute_keywords:
            if keyword in all_text.upper():
                pattern = rf'([A-Z\s]*{keyword}[A-Z\s]*)'
                match = re.search(pattern, all_text.upper())
                if match:
                    card_data['institute'] = match.group(1).strip()
                    break
        
        # Extract Academic Year
        year_match = re.search(r'20\d{2}[-/]20\d{2}|20\d{2}', all_text)
        if year_match:
            card_data['academic_year'] = year_match.group(0)
        
        # Calculate average confidence
        if ocr_results:
            card_data['confidence'] = sum([conf for (_, _, conf) in ocr_results]) / len(ocr_results)
        
        # Extract photo region
        photo = self.extract_photo_region(card_image)
        card_data['photo_extracted'] = photo is not None and photo.size > 0
        
        return card_data, photo
    
    def extract_photo_region(self, card_image):
        """
        Extract photo region from ID card
        
        Args:
            card_image: Cropped ID card image
            
        Returns:
            numpy.ndarray: Photo region
        """
        try:
            h, w = card_image.shape[:2]
            
            # Standard ID card photo location (left side)
            x1 = int(w * ID_CARD_REGIONS['photo']['x'])
            y1 = int(h * ID_CARD_REGIONS['photo']['y'])
            x2 = int(w * (ID_CARD_REGIONS['photo']['x'] + ID_CARD_REGIONS['photo']['width']))
            y2 = int(h * (ID_CARD_REGIONS['photo']['y'] + ID_CARD_REGIONS['photo']['height']))
            
            photo = card_image[y1:y2, x1:x2]
            return photo
        except Exception as e:
            print(f"⚠️  Photo extraction error: {e}")
            return None
    
    def recognize_id_card(self, frame):
        """
        Complete pipeline: detect + extract + parse ID card
        
        Args:
            frame: Input frame
            
        Returns:
            tuple: (list of card_data dicts, annotated_frame)
        """
        self.stats['frames_processed'] += 1
        annotated_frame = frame.copy()
        recognized_cards = []
        
        # Step 1: Detect ID cards
        if self.yolo_model:
            detections = self.detect_id_card_yolo(frame)
        else:
            detections = self.detect_id_card_opencv(frame)
        
        self.stats['cards_detected'] += len(detections)
        
        # Step 2: Process each detected card
        for (x, y, w, h, conf) in detections:
            # Extract card region
            card_image = frame[y:y+h, x:x+w]
            
            # Step 3: Run OCR
            ocr_results = self.extract_text_with_ocr(card_image)
            
            # Step 4: Parse structured data
            card_data, photo = self.parse_id_card_data(ocr_results, card_image)
            
            # Add detection info
            card_data['detection_bbox'] = {'x': x, 'y': y, 'w': w, 'h': h}
            card_data['detection_confidence'] = conf
            
            # Check if card is valid
            is_valid = card_data['moodle_id'] is not None
            
            if is_valid:
                self.stats['cards_recognized'] += 1
                self.stats['ids_extracted'] += 1
            
            # Draw bounding box
            color = (0, 255, 0) if is_valid else (0, 165, 255)
            cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), color, 2)
            
            # Add labels
            label_y = y - 10
            if card_data['moodle_id']:
                cv2.putText(annotated_frame, f"ID: {card_data['moodle_id']}", 
                           (x, label_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                label_y += 25
            
            if card_data['name']:
                name_display = card_data['name'][:25]
                cv2.putText(annotated_frame, f"Name: {name_display}", 
                           (x, label_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                label_y += 22
            
            if card_data['department']:
                dept_display = card_data['department'][:20]
                cv2.putText(annotated_frame, f"Dept: {dept_display}", 
                           (x, label_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            recognized_cards.append({
                'data': card_data,
                'image': card_image,
                'photo': photo
            })
        
        return recognized_cards, annotated_frame
    
    def save_card_data(self, card_data, card_image, photo):
        """
        Save card data to JSON and images
        
        Args:
            card_data: Card data dictionary
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
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(card_data, f, indent=2, ensure_ascii=False)
        
        # Save card image
        card_img_path = OUTPUT_CAPTURED_FRAMES / f"{timestamp}_{moodle_id}_card.jpg"
        cv2.imwrite(str(card_img_path), card_image)
        
        # Save photo if available
        if photo is not None and photo.size > 0:
            photo_path = OUTPUT_ID_CARD_DATA / f"{timestamp}_{moodle_id}_photo.jpg"
            cv2.imwrite(str(photo_path), photo)
        
        print(f"💾 Saved: {moodle_id} -> {json_path.name}")
        
        # Print extracted data
        print(f"\n📋 Extracted Data:")
        print(f"   Moodle ID: {card_data.get('moodle_id', 'N/A')}")
        print(f"   Name: {card_data.get('name', 'N/A')}")
        print(f"   Department: {card_data.get('department', 'N/A')}")
        print(f"   Institute: {card_data.get('institute', 'N/A')}")
        print(f"   Confidence: {card_data.get('confidence', 0):.2f}")
    
    def process_camera_stream(self, camera_index=0, save_auto=True):
        """
        Process live camera stream
        
        Args:
            camera_index: Camera index
            save_auto: Auto-save valid detections
        """
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"❌ Failed to open camera {camera_index}")
            return
        
        print(f"\n📷 Starting camera stream (index: {camera_index})")
        print("✅ Camera opened. Press 'q' to quit, 's' to save detection")
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                frame_count += 1
                
                # Process every 5th frame for performance
                if frame_count % 5 == 0:
                    recognized_cards, annotated_frame = self.recognize_id_card(frame)
                    
                    # Auto-save
                    if save_auto and recognized_cards:
                        for card_info in recognized_cards:
                            if card_info['data'].get('moodle_id'):
                                self.save_card_data(
                                    card_info['data'],
                                    card_info['image'],
                                    card_info['photo']
                                )
                    
                    display_frame = annotated_frame
                else:
                    display_frame = frame
                
                # Display stats
                stats_text = f"Frames: {frame_count} | Detected: {self.stats['cards_detected']} | Recognized: {self.stats['cards_recognized']}"
                cv2.putText(display_frame, stats_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Show frame
                cv2.imshow('Offline ID Card Recognition', display_frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Manual save
                    recognized_cards, _ = self.recognize_id_card(frame)
                    if recognized_cards:
                        for card_info in recognized_cards:
                            self.save_card_data(
                                card_info['data'],
                                card_info['image'],
                                card_info['photo']
                            )
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print(f"\n✅ Session complete!")
            print(f"📊 Stats:")
            print(f"   Frames processed: {self.stats['frames_processed']}")
            print(f"   Cards detected: {self.stats['cards_detected']}")
            print(f"   Cards recognized: {self.stats['cards_recognized']}")
            print(f"   IDs extracted: {self.stats['ids_extracted']}")
    
    def process_single_image(self, image_path):
        """
        Process a single image file
        
        Args:
            image_path: Path to image file
        """
        print(f"\n📄 Processing image: {image_path}")
        
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"❌ Failed to load image: {image_path}")
            return
        
        recognized_cards, annotated = self.recognize_id_card(image)
        
        if recognized_cards:
            print(f"\n✅ Found {len(recognized_cards)} ID card(s)")
            
            for i, card_info in enumerate(recognized_cards, 1):
                print(f"\n📋 Card {i}:")
                card_data = card_info['data']
                print(json.dumps(card_data, indent=2, ensure_ascii=False))
                
                # Save
                self.save_card_data(
                    card_info['data'],
                    card_info['image'],
                    card_info['photo']
                )
        else:
            print("❌ No ID cards detected or recognized")
        
        # Display result
        cv2.imshow('Result', annotated)
        print("\nPress any key to close...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Offline ID Card Recognition System')
    parser.add_argument('--camera', action='store_true', help='Use camera stream')
    parser.add_argument('--camera-index', type=int, default=0, help='Camera index (default: 0)')
    parser.add_argument('--image', type=str, help='Path to ID card image')
    parser.add_argument('--model', type=str, help='Path to YOLO model')
    parser.add_argument('--no-gpu', action='store_true', help='Disable GPU acceleration')
    
    args = parser.parse_args()
    
    # Initialize recognizer
    recognizer = OfflineIDCardRecognizer(
        yolo_model_path=args.model,
        use_gpu=not args.no_gpu
    )
    
    if args.camera:
        # Camera mode
        recognizer.process_camera_stream(camera_index=args.camera_index)
    elif args.image:
        # Single image mode
        recognizer.process_single_image(args.image)
    else:
        print("❌ Please specify --camera or --image")
        print("\nExamples:")
        print("  python offline_id_card_recognizer.py --camera")
        print("  python offline_id_card_recognizer.py --image test.jpg")


if __name__ == "__main__":
    main()
