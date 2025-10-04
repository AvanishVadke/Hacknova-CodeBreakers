"""
ID Card Verification Module
Uses YOLO for ID card detection and EasyOCR for text extraction
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
from ultralytics import YOLO
import sys

# Add config to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import *


class IDCardVerifier:
    """
    ID Card verification system for college/campus ID cards
    """
    
    def __init__(self, model_path=None, use_gpu=True):
        """
        Initialize the ID card verifier
        
        Args:
            model_path (str): Path to YOLO model weights
            use_gpu (bool): Whether to use GPU acceleration
        """
        self.use_gpu = use_gpu
        self.device = 'cuda' if (use_gpu and torch.cuda.is_available()) else 'cpu'
        
        print("=" * 70)
        print("🎴 ID CARD VERIFICATION SYSTEM")
        print("=" * 70)
        print(f"🔧 Device: {self.device.upper()}")
        
        if self.device == 'cuda':
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
            print(f"🔥 CUDA Version: {torch.version.cuda}")
        
        # Load YOLO model
        if model_path is None:
            model_path = YOLO_MODEL_PATH
        
        print(f"\n📦 Loading YOLO model from: {model_path}")
        self.model = YOLO(str(model_path))
        self.model.to(self.device)
        print("✅ YOLO model loaded successfully")
        
        # Initialize EasyOCR
        print(f"\n📝 Initializing EasyOCR (GPU: {OCR_GPU})...")
        self.reader = easyocr.Reader(
            OCR_LANGUAGES, 
            gpu=OCR_GPU if self.device == 'cuda' else False
        )
        print("✅ EasyOCR initialized successfully")
        
        # Statistics
        self.stats = {
            'frames_processed': 0,
            'cards_detected': 0,
            'cards_verified': 0,
            'moodle_ids_extracted': 0
        }
        
        print("=" * 70)
    
    def extract_region(self, image, region_coords):
        """
        Extract region from image based on percentage coordinates
        
        Args:
            image: Input image
            region_coords: Tuple (x1, y1, x2, y2) as percentages
            
        Returns:
            Extracted region
        """
        h, w = image.shape[:2]
        x1, y1, x2, y2 = region_coords
        
        # Convert percentage to pixels
        x1_px = int(x1 * w)
        y1_px = int(y1 * h)
        x2_px = int(x2 * w)
        y2_px = int(y2 * h)
        
        # Ensure coordinates are within bounds
        x1_px = max(0, min(x1_px, w))
        y1_px = max(0, min(y1_px, h))
        x2_px = max(0, min(x2_px, w))
        y2_px = max(0, min(y2_px, h))
        
        return image[y1_px:y2_px, x1_px:x2_px]
    
    def preprocess_for_ocr(self, img):
        """
        Preprocess image region for better OCR results
        
        Args:
            img: Input image region
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # Resize if too small
        if gray.shape[1] < 200:
            scale = 200 / gray.shape[1]
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, h=10)
        
        return denoised
    
    def extract_text_from_region(self, region):
        """
        Extract text from image region using EasyOCR
        
        Args:
            region: Image region
            
        Returns:
            str: Extracted text
        """
        if region.size == 0 or region.shape[0] < 10 or region.shape[1] < 10:
            return ""
        
        # Preprocess
        preprocessed = self.preprocess_for_ocr(region)
        
        # Run OCR
        try:
            results = self.reader.readtext(preprocessed, detail=1)
            
            text = ""
            for (bbox, detected_text, confidence) in results:
                if confidence > OCR_CONFIDENCE_THRESHOLD:
                    text += detected_text + " "
            
            return text.strip()
            
        except Exception as e:
            print(f"⚠️  OCR Error: {e}")
            return ""
    
    def extract_photo(self, id_card_image, save_path=None):
        """
        Extract student photo from ID card
        
        Args:
            id_card_image: Full ID card image
            save_path: Path to save extracted photo
            
        Returns:
            Extracted photo image
        """
        photo_region = self.extract_region(id_card_image, ID_CARD_REGIONS['photo'])
        
        if save_path:
            cv2.imwrite(str(save_path), photo_region)
        
        return photo_region
    
    def extract_name(self, id_card_image):
        """
        Extract name from ID card
        
        Args:
            id_card_image: Full ID card image
            
        Returns:
            str: Extracted name
        """
        name_region = self.extract_region(id_card_image, ID_CARD_REGIONS['name'])
        name = self.extract_text_from_region(name_region)
        
        # Clean name
        name = ' '.join(name.split())
        name = re.sub(r'[^A-Za-z\s]', '', name)
        
        return name.strip()
    
    def extract_department(self, id_card_image):
        """
        Extract department from ID card
        
        Args:
            id_card_image: Full ID card image
            
        Returns:
            str: Extracted department
        """
        dept_region = self.extract_region(id_card_image, ID_CARD_REGIONS['department'])
        department = self.extract_text_from_region(dept_region)
        
        # Clean department
        department = ' '.join(department.split())
        
        # Try to match with valid departments
        for valid_dept in VALID_DEPARTMENTS:
            if valid_dept.lower() in department.lower():
                return valid_dept
        
        return department.strip()
    
    def extract_moodle_id(self, id_card_image):
        """
        Extract Moodle ID from ID card
        
        Args:
            id_card_image: Full ID card image
            
        Returns:
            str: Extracted Moodle ID (8 digits starting with 2)
        """
        moodle_region = self.extract_region(id_card_image, ID_CARD_REGIONS['moodle_id'])
        text = self.extract_text_from_region(moodle_region)
        
        # Find Moodle ID pattern
        match = re.search(MOODLE_ID_PATTERN, text)
        if match:
            return match.group(0)
        
        # Try without any formatting
        digits = re.sub(r'\D', '', text)
        if len(digits) >= 8:
            # Find 8-digit sequence starting with 2
            for i in range(len(digits) - 7):
                if digits[i] == '2':
                    candidate = digits[i:i+8]
                    if len(candidate) == 8:
                        return candidate
        
        return None
    
    def detect_and_extract_id_card(self, frame, frame_number, timestamp):
        """
        Detect ID card in frame and extract all information
        
        Args:
            frame: Input video frame
            frame_number (int): Frame number
            timestamp (str): Timestamp
            
        Returns:
            dict: Extraction results
        """
        results_data = {
            'frame_number': frame_number,
            'timestamp': timestamp,
            'id_cards': []
        }
        
        # Run YOLO detection
        results = self.model(frame, conf=YOLO_CONFIDENCE_THRESHOLD, verbose=False)
        
        # Process detections
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Get coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                
                # Skip low confidence detections
                if confidence < MIN_ID_CARD_CONFIDENCE:
                    continue
                
                # Extract ID card region
                id_card_roi = frame[y1:y2, x1:x2]
                
                # Extract information
                name = self.extract_name(id_card_roi)
                department = self.extract_department(id_card_roi)
                moodle_id = self.extract_moodle_id(id_card_roi)
                
                # Save photo
                photo_filename = None
                if moodle_id:
                    photo_filename = f"photo_{moodle_id}_{frame_number}.jpg"
                    photo_path = CAPTURED_FRAMES_DIR / photo_filename
                    self.extract_photo(id_card_roi, photo_path)
                
                # Validation
                is_valid = bool(moodle_id and name)
                
                id_card_data = {
                    'bbox': [x1, y1, x2, y2],
                    'confidence': round(confidence, 3),
                    'moodle_id': moodle_id,
                    'name': name,
                    'department': department,
                    'photo_file': photo_filename,
                    'is_valid': is_valid
                }
                
                results_data['id_cards'].append(id_card_data)
                
                # Update statistics
                self.stats['cards_detected'] += 1
                if is_valid:
                    self.stats['cards_verified'] += 1
                if moodle_id:
                    self.stats['moodle_ids_extracted'] += 1
                
                # Draw on frame
                color = (0, 255, 0) if is_valid else (0, 165, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Add label
                label = f"{name if name else 'Unknown'}"
                if moodle_id:
                    label += f" | ID: {moodle_id}"
                label += f" ({confidence:.2f})"
                
                cv2.putText(frame, label, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        self.stats['frames_processed'] += 1
        return results_data, frame
    
    def process_camera_stream(self, camera_index=0, duration=None, auto_save=True):
        """
        Process live camera stream for ID card verification
        
        Args:
            camera_index (int): Camera index
            duration (int): Duration in seconds (None = infinite)
            auto_save (bool): Auto-save when valid ID detected
        """
        print(f"\n📷 Starting camera stream (index: {camera_index})")
        
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"❌ Failed to open camera: {camera_index}")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
        
        print("✅ Camera opened. Press 'q' to quit, 's' to save detection")
        
        frame_count = 0
        verifications_log = []
        start_time = datetime.now()
        last_save_time = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame")
                break
            
            frame_count += 1
            timestamp = get_timestamp()
            
            # Process frame
            results, annotated_frame = self.detect_and_extract_id_card(frame, frame_count, timestamp)
            
            # Auto-save valid detections
            if auto_save and results['id_cards']:
                for card in results['id_cards']:
                    if card['is_valid'] and card['moodle_id']:
                        # Avoid duplicate saves (wait 3 seconds between saves)
                        current_time = datetime.now()
                        if last_save_time is None or (current_time - last_save_time).seconds >= AUTO_CAPTURE_DELAY:
                            output_path = ID_CARD_OUTPUT_DIR / f"{card['moodle_id']}.json"
                            with open(output_path, 'w', encoding='utf-8') as f:
                                json.dump(card, f, indent=2, ensure_ascii=False)
                            print(f"💾 ID Card saved: {card['moodle_id']} - {card['name']}")
                            verifications_log.append(results)
                            last_save_time = current_time
            
            # Display
            cv2.imshow('ID Card Verification', annotated_frame)
            
            # Handle key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s') and results['id_cards']:
                # Manual save
                for card in results['id_cards']:
                    if card['moodle_id']:
                        output_path = ID_CARD_OUTPUT_DIR / f"{card['moodle_id']}_manual.json"
                        with open(output_path, 'w', encoding='utf-8') as f:
                            json.dump(card, f, indent=2, ensure_ascii=False)
                        print(f"💾 Manual save: {card['moodle_id']}")
            
            # Check duration
            if duration and (datetime.now() - start_time).total_seconds() > duration:
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Save session log
        if verifications_log:
            output_path = ID_CARD_OUTPUT_DIR / get_output_filename('id_card_session')
            session_data = {
                'session_started': start_time.isoformat(),
                'session_ended': get_timestamp(),
                'total_verifications': len(verifications_log),
                'verifications': verifications_log,
                'statistics': self.stats
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Session log saved: {output_path}")
        
        print(f"\n✅ Session complete!")
        print(f"📊 Stats: {self.stats['frames_processed']} frames, "
              f"{self.stats['cards_detected']} cards detected, "
              f"{self.stats['cards_verified']} cards verified, "
              f"{self.stats['moodle_ids_extracted']} IDs extracted")
    
    def process_single_image(self, image_path, output_json_path=None):
        """
        Process single ID card image
        
        Args:
            image_path (str): Path to ID card image
            output_json_path (str): Path to save JSON output
            
        Returns:
            dict: Extraction results
        """
        image_path = Path(image_path)
        if not image_path.exists():
            print(f"❌ Image not found: {image_path}")
            return None
        
        print(f"\n🎴 Processing image: {image_path.name}")
        
        # Read image
        frame = cv2.imread(str(image_path))
        if frame is None:
            print(f"❌ Failed to read image: {image_path}")
            return None
        
        # Process
        timestamp = get_timestamp()
        results, annotated_frame = self.detect_and_extract_id_card(frame, 1, timestamp)
        
        # Save annotated image
        output_img_path = CAPTURED_FRAMES_DIR / f"{image_path.stem}_annotated{image_path.suffix}"
        cv2.imwrite(str(output_img_path), annotated_frame)
        
        # Save JSON
        if output_json_path is None and results['id_cards']:
            for card in results['id_cards']:
                if card['moodle_id']:
                    output_json_path = ID_CARD_OUTPUT_DIR / f"{card['moodle_id']}.json"
                    with open(output_json_path, 'w', encoding='utf-8') as f:
                        json.dump(card, f, indent=2, ensure_ascii=False)
                    print(f"💾 Results saved to: {output_json_path}")
        
        print(f"✅ Processing complete!")
        print(f"📊 Found {len(results['id_cards'])} ID card(s)")
        
        return results


def main():
    """Main function to test the module"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ID Card Verification System')
    parser.add_argument('--image', type=str, help='Path to ID card image')
    parser.add_argument('--camera', action='store_true', help='Use camera stream')
    parser.add_argument('--model', type=str, help='Path to YOLO model')
    parser.add_argument('--duration', type=int, help='Camera duration in seconds')
    
    args = parser.parse_args()
    
    # Initialize verifier
    verifier = IDCardVerifier(model_path=args.model)
    
    if args.camera:
        # Process camera stream
        verifier.process_camera_stream(duration=args.duration)
    elif args.image:
        # Process single image
        verifier.process_single_image(args.image)
    else:
        print("❌ Please specify --image or --camera")


if __name__ == "__main__":
    main()
