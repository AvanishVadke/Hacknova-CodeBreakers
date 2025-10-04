"""
ID Card Verification Module using Roboflow Inference SDK
Uses Roboflow's OCR model for ID card detection and text extraction
"""

import cv2
import numpy as np
import json
import re
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv
from inference_sdk import InferenceHTTPClient
import sys

# Load environment variables
load_dotenv()

# Add config to path
sys.path.append(str(Path(__file__).resolve().parent))
from config.config import *


class IDCardVerifierRoboflow:
    """
    ID Card verification system using Roboflow Inference SDK
    """
    
    def __init__(self, api_key=None, model_id=None):
        """
        Initialize the ID card verifier with Roboflow
        
        Args:
            api_key (str): Roboflow API key (optional, reads from .env)
            model_id (str): Roboflow model ID (optional, reads from .env)
        """
        print("=" * 70)
        print("🎴 ID CARD VERIFICATION SYSTEM (ROBOFLOW)")
        print("=" * 70)
        
        # Get API credentials
        self.api_key = api_key or os.getenv('ROBOFLOW_API_KEY')
        self.model_id = model_id or os.getenv('ROBOFLOW_MODEL_ID', 'ocr-recognition-id/5')
        self.api_url = os.getenv('ROBOFLOW_API_URL', 'https://serverless.roboflow.com')
        
        if not self.api_key:
            raise ValueError(
                "❌ Roboflow API key not found!\n"
                "   Please set ROBOFLOW_API_KEY in .env file or pass as argument"
            )
        
        print(f"🔧 API URL: {self.api_url}")
        print(f"🔑 API Key: {'***' + self.api_key[-4:] if len(self.api_key) > 4 else '***'}")
        print(f"📦 Model ID: {self.model_id}")
        
        # Initialize Roboflow client
        try:
            self.client = InferenceHTTPClient(
                api_url=self.api_url,
                api_key=self.api_key
            )
            print("✅ Roboflow client initialized successfully")
        except Exception as e:
            raise RuntimeError(f"❌ Failed to initialize Roboflow client: {e}")
        
        print("=" * 70)
        
        # Stats
        self.stats = {
            'frames_processed': 0,
            'cards_detected': 0,
            'cards_verified': 0,
            'ids_extracted': 0,
            'api_calls': 0
        }
        
        # Last save time for cooldown
        self.last_save_time = datetime.min
    
    def detect_and_extract_id_card(self, frame):
        """
        Detect ID card and extract information using Roboflow
        
        Args:
            frame: Input frame (numpy array)
            
        Returns:
            tuple: (detected_cards_data, annotated_frame)
        """
        self.stats['frames_processed'] += 1
        annotated_frame = frame.copy()
        detected_cards = []
        
        try:
            # Save frame temporarily for inference
            temp_path = "temp_frame.jpg"
            cv2.imwrite(temp_path, frame)
            
            # Run inference
            result = self.client.infer(temp_path, model_id=self.model_id)
            self.stats['api_calls'] += 1
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Process predictions
            predictions = result.get('predictions', [])
            
            if not predictions:
                return detected_cards, annotated_frame
            
            self.stats['cards_detected'] += len(predictions)
            
            # Process each detected ID card
            for pred in predictions:
                try:
                    # Extract bounding box
                    x = int(pred.get('x', 0))
                    y = int(pred.get('y', 0))
                    width = int(pred.get('width', 0))
                    height = int(pred.get('height', 0))
                    
                    # Convert center coordinates to corner coordinates
                    x1 = int(x - width / 2)
                    y1 = int(y - height / 2)
                    x2 = int(x + width / 2)
                    y2 = int(y + height / 2)
                    
                    # Ensure coordinates are within frame bounds
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(frame.shape[1], x2)
                    y2 = min(frame.shape[0], y2)
                    
                    confidence = pred.get('confidence', 0)
                    detected_class = pred.get('class', 'id_card')
                    
                    # Extract OCR text if available
                    ocr_text = pred.get('ocr_text', '')
                    detected_text = pred.get('detected_text', '')
                    
                    # Parse ID card information
                    card_data = self.parse_id_card_data(
                        ocr_text or detected_text,
                        pred
                    )
                    
                    card_data.update({
                        'timestamp': datetime.now().isoformat(),
                        'bbox': {'x': x1, 'y': y1, 'w': x2-x1, 'h': y2-y1},
                        'confidence': confidence,
                        'class': detected_class
                    })
                    
                    # Extract card image
                    card_image = frame[y1:y2, x1:x2]
                    
                    # Extract photo region (approximate location)
                    photo = self.extract_photo_region(card_image)
                    
                    card_data['photo_extracted'] = photo is not None and photo.size > 0
                    
                    # Draw bounding box
                    color = (0, 255, 0) if card_data.get('moodle_id') else (0, 165, 255)
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                    
                    # Add labels
                    label_y = y1 - 10
                    if card_data.get('moodle_id'):
                        cv2.putText(annotated_frame, f"ID: {card_data['moodle_id']}", 
                                   (x1, label_y),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        label_y += 25
                        self.stats['ids_extracted'] += 1
                    
                    if card_data.get('name'):
                        cv2.putText(annotated_frame, f"Name: {card_data['name'][:20]}", 
                                   (x1, label_y),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        label_y += 25
                    
                    if card_data.get('department'):
                        cv2.putText(annotated_frame, f"Dept: {card_data['department'][:15]}", 
                                   (x1, label_y),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    # Mark as verified if has Moodle ID
                    if card_data.get('moodle_id'):
                        self.stats['cards_verified'] += 1
                    
                    detected_cards.append((card_data, card_image, photo))
                    
                except Exception as e:
                    print(f"⚠️  Error processing prediction: {e}")
                    continue
        
        except Exception as e:
            print(f"⚠️  Roboflow inference error: {e}")
        
        return detected_cards, annotated_frame
    
    def parse_id_card_data(self, text, prediction):
        """
        Parse ID card information from OCR text
        
        Args:
            text (str): OCR extracted text
            prediction (dict): Full prediction dictionary
            
        Returns:
            dict: Parsed card data
        """
        card_data = {
            'name': '',
            'department': '',
            'moodle_id': '',
            'raw_text': text
        }
        
        if not text:
            return card_data
        
        # Extract Moodle ID (8 digits starting with 2)
        moodle_match = re.search(r'2\d{7}', text)
        if moodle_match:
            card_data['moodle_id'] = moodle_match.group(0)
        else:
            # Try to find any 8-digit number
            id_match = re.search(r'\d{8}', text)
            if id_match:
                card_data['moodle_id'] = id_match.group(0)
        
        # Extract name (usually in capital letters)
        name_patterns = [
            r'([A-Z][A-Z\s]{5,})',  # Multiple capital letters
            r'Name[:\s]+([A-Z][A-Za-z\s]+)',  # After "Name:"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                card_data['name'] = match.group(1).strip()
                break
        
        # Extract department
        dept_keywords = ['ENGINEERING', 'COMPUTER', 'MECHANICAL', 'CIVIL', 
                        'ELECTRICAL', 'ELECTRONICS', 'IT', 'CSE', 'ECE']
        
        for keyword in dept_keywords:
            if keyword in text.upper():
                # Extract surrounding words
                pattern = rf'([A-Z\s]*{keyword}[A-Z\s]*)'
                match = re.search(pattern, text.upper())
                if match:
                    card_data['department'] = match.group(1).strip()
                    break
        
        return card_data
    
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
            
            # Approximate photo location (left side, 25-75% width, 15-50% height)
            x1 = int(w * 0.05)
            y1 = int(h * 0.15)
            x2 = int(w * 0.40)
            y2 = int(h * 0.65)
            
            photo = card_image[y1:y2, x1:x2]
            return photo
        except Exception as e:
            print(f"⚠️  Photo extraction error: {e}")
            return None
    
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
        print("⚠️  Note: Processing 1 frame every 2 seconds to save API calls")
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                frame_count += 1
                
                # Process every 60th frame (~2 seconds at 30fps) to save API calls
                if frame_count % 60 == 0:
                    detected_cards, annotated_frame = self.detect_and_extract_id_card(frame)
                    
                    # Auto-save
                    if save_auto and detected_cards:
                        for card_data, card_image, photo in detected_cards:
                            if card_data.get('moodle_id'):  # Only save if ID extracted
                                self.save_card_data(card_data, card_image, photo)
                                
                                # Print extracted data
                                print(f"\n✅ ID Card Detected:")
                                print(f"   Moodle ID: {card_data.get('moodle_id')}")
                                print(f"   Name: {card_data.get('name')}")
                                print(f"   Department: {card_data.get('department')}")
                                print(f"   Confidence: {card_data.get('confidence', 0):.2f}")
                    
                    display_frame = annotated_frame
                else:
                    display_frame = frame
                
                # Display stats
                stats_text = f"Frames: {frame_count} | API Calls: {self.stats['api_calls']} | Detected: {self.stats['cards_detected']} | Verified: {self.stats['cards_verified']}"
                cv2.putText(display_frame, stats_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Show frame
                cv2.imshow('ID Card Verification (Roboflow)', display_frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Manual save
                    detected_cards, _ = self.detect_and_extract_id_card(frame)
                    if detected_cards:
                        for card_data, card_image, photo in detected_cards:
                            self.save_card_data(card_data, card_image, photo)
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print(f"\n✅ Session complete!")
            print(f"📊 Stats: {self.stats['frames_processed']} frames, "
                  f"{self.stats['api_calls']} API calls, "
                  f"{self.stats['cards_detected']} cards detected, "
                  f"{self.stats['cards_verified']} cards verified, "
                  f"{self.stats['ids_extracted']} IDs extracted")
    
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
        
        detected_cards, annotated = self.detect_and_extract_id_card(image)
        
        if detected_cards:
            print(f"\n✅ Found {len(detected_cards)} ID card(s)")
            for i, (card_data, card_image, photo) in enumerate(detected_cards, 1):
                print(f"\nCard {i}:")
                print(f"   Moodle ID: {card_data.get('moodle_id', 'N/A')}")
                print(f"   Name: {card_data.get('name', 'N/A')}")
                print(f"   Department: {card_data.get('department', 'N/A')}")
                print(f"   Confidence: {card_data.get('confidence', 0):.2f}")
                
                # Save
                self.save_card_data(card_data, card_image, photo)
        else:
            print("❌ No ID cards detected")
        
        # Display result
        cv2.imshow('Result', annotated)
        print("\nPress any key to close...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ID Card Verification System (Roboflow)')
    parser.add_argument('--camera', action='store_true', help='Use camera stream')
    parser.add_argument('--camera-index', type=int, default=0, help='Camera index (default: 0)')
    parser.add_argument('--image', type=str, help='Path to ID card image')
    parser.add_argument('--api-key', type=str, help='Roboflow API key (optional, reads from .env)')
    parser.add_argument('--model-id', type=str, help='Roboflow model ID (optional, reads from .env)')
    
    args = parser.parse_args()
    
    try:
        # Initialize verifier
        verifier = IDCardVerifierRoboflow(
            api_key=args.api_key,
            model_id=args.model_id
        )
        
        if args.camera:
            # Camera mode
            verifier.process_camera_stream(camera_index=args.camera_index)
        elif args.image:
            # Single image mode
            verifier.process_single_image(args.image)
        else:
            print("❌ Please specify --camera or --image")
            print("\nExamples:")
            print("  python id_card_verifier_roboflow.py --camera")
            print("  python id_card_verifier_roboflow.py --image test.jpg")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease ensure:")
        print("  1. ROBOFLOW_API_KEY is set in .env file")
        print("  2. inference-sdk is installed: pip install inference-sdk")
        print("  3. Camera is connected (if using --camera)")


if __name__ == "__main__":
    main()
