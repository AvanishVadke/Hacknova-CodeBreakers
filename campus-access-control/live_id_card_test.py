"""
Live ID Card Recognition - Camera Feed Test
Shows real-time detection with filtered output:
- Name (below photo)
- Department (below name)
- Moodle ID (8 digits starting with 2)
"""

import cv2
import torch
import easyocr
import numpy as np
import re
from datetime import datetime
from pathlib import Path
from ultralytics import YOLO


class LiveIDCardTester:
    """
    Live camera testing for ID card recognition
    """
    
    def __init__(self):
        """Initialize camera tester"""
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        print("=" * 70)
        print("📹 LIVE ID CARD RECOGNITION TEST")
        print("=" * 70)
        print(f"🔧 Device: {self.device.upper()}")
        
        if self.device == 'cuda':
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        
        # Initialize YOLO (optional - will use OpenCV fallback if no detection)
        try:
            self.yolo_model = YOLO("models/id_card_best.pt")
            print("✅ YOLO model loaded")
        except:
            self.yolo_model = None
            print("⚠️  YOLO model not loaded - using OpenCV fallback")
        
        # Initialize EasyOCR
        print("📝 Initializing EasyOCR...")
        self.reader = easyocr.Reader(['en'], gpu=(self.device == 'cuda'), verbose=False)
        print("✅ EasyOCR initialized")
        
        # Filters for unwanted text
        self.ignore_keywords = [
            'parshvanalh', 'charitable', 'trust', 'shah', 'institute',
            'technology', 'thane', 'academic', 'year', '2025', '2026',
            'principal', 'photo', 'id no', 'signature', '4', '202'
        ]
        
        # Department keywords
        self.departments = [
            'COMPUTER ENGINEERING', 'COMPUTER', 'COMP',
            'MECHANICAL ENGINEERING', 'MECHANICAL', 'MECH',
            'CIVIL ENGINEERING', 'CIVIL',
            'ELECTRICAL ENGINEERING', 'ELECTRICAL', 'ELECT',
            'ELECTRONICS', 'EXTC', 'E&TC',
            'INFORMATION TECHNOLOGY', 'IT',
            'CHEMICAL ENGINEERING', 'CHEMICAL', 'CHEM'
        ]
        
        print("=" * 70)
        print("\n📷 Controls:")
        print("   SPACE = Capture and analyze")
        print("   Q     = Quit")
        print("   S     = Save current frame")
        print("\n🎯 Processing: Every frame (real-time)")
        print("=" * 70)
    
    def detect_card_opencv(self, frame):
        """
        Detect ID card using OpenCV edge detection
        
        Returns:
            bbox or None: [x1, y1, x2, y2] of detected card
        """
        h, w = frame.shape[:2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Blur and edge detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        # Dilate edges
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        frame_area = h * w
        best_bbox = None
        max_area = 0
        
        for contour in contours:
            x, y, w_box, h_box = cv2.boundingRect(contour)
            area = w_box * h_box
            aspect_ratio = w_box / h_box if h_box > 0 else 0
            
            # ID card criteria
            if (0.1 * frame_area < area < 0.9 * frame_area and
                1.2 < aspect_ratio < 2.5 and
                w_box > 150 and h_box > 80):
                
                # Check if rectangular
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                
                if len(approx) >= 4 and area > max_area:
                    max_area = area
                    best_bbox = (x, y, x + w_box, y + h_box)
        
        return best_bbox
    
    def filter_text(self, text):
        """
        Check if text should be ignored
        
        Returns:
            bool: True if text should be kept
        """
        text_lower = text.lower().strip()
        
        # Ignore if too short
        if len(text_lower) < 3:
            return False
        
        # Ignore if contains any keyword
        for keyword in self.ignore_keywords:
            if keyword in text_lower:
                return False
        
        return True
    
    def extract_moodle_id(self, text_results):
        """
        Extract 8-digit Moodle ID starting with 2
        
        Returns:
            str or None: Moodle ID
        """
        pattern = r'\b2\d{7}\b'
        
        for _, text, conf in text_results:
            if conf > 0.5:  # Only high confidence
                matches = re.findall(pattern, text)
                if matches:
                    return matches[0]
        
        return None
    
    def extract_name(self, text_results):
        """
        Extract name (high confidence text with 2-3 words, all caps)
        
        Returns:
            str or None: Name
        """
        for _, text, conf in text_results:
            if conf > 0.6 and self.filter_text(text):
                # Check if it's a name (2-3 words, mostly alphabetic)
                words = text.split()
                if 2 <= len(words) <= 3:
                    # Check if mostly uppercase and alphabetic
                    if sum(c.isupper() or c.isspace() for c in text) / len(text) > 0.7:
                        # Not a department
                        if not any(dept.upper() in text.upper() for dept in ['ENGINEERING', 'TECHNOLOGY']):
                            return text.upper()
        
        return None
    
    def extract_department(self, text_results):
        """
        Extract department using keyword matching
        
        Returns:
            str or None: Department
        """
        for _, text, conf in text_results:
            if conf > 0.7:
                text_upper = text.upper()
                for dept in self.departments:
                    if dept in text_upper:
                        # Return full "X ENGINEERING" format
                        if 'ENGINEERING' in text_upper:
                            return text_upper
                        else:
                            # Add ENGINEERING if missing
                            return f"{text_upper} ENGINEERING"
        
        return None
    
    def process_frame(self, frame):
        """
        Process single frame: detect card and extract info
        
        Returns:
            tuple: (annotated_frame, info_dict)
        """
        annotated = frame.copy()
        h, w = annotated.shape[:2]
        
        # Detect card
        bbox = None
        
        # Try YOLO first
        if self.yolo_model:
            try:
                results = self.yolo_model(frame, conf=0.25, verbose=False)
                if len(results[0].boxes) > 0:
                    box = results[0].boxes[0]
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    bbox = (x1, y1, x2, y2)
            except:
                pass
        
        # Fallback to OpenCV
        if bbox is None:
            bbox = self.detect_card_opencv(frame)
        
        # Draw bounding box
        if bbox:
            x1, y1, x2, y2 = bbox
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated, "ID CARD", (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Extract text
        info = {
            'moodle_id': None,
            'name': None,
            'department': None,
            'detected': bbox is not None
        }
        
        try:
            # Run OCR on full frame (or just card region if detected)
            if bbox:
                x1, y1, x2, y2 = bbox
                # Add padding
                pad = 10
                x1 = max(0, x1 - pad)
                y1 = max(0, y1 - pad)
                x2 = min(w, x2 + pad)
                y2 = min(h, y2 + pad)
                roi = frame[y1:y2, x1:x2]
            else:
                roi = frame
            
            # OCR
            ocr_results = self.reader.readtext(roi)
            
            # Extract info
            info['moodle_id'] = self.extract_moodle_id(ocr_results)
            info['name'] = self.extract_name(ocr_results)
            info['department'] = self.extract_department(ocr_results)
            
            # Display extracted info on frame
            y_offset = 30
            font = cv2.FONT_HERSHEY_SIMPLEX
            
            if info['moodle_id']:
                cv2.putText(annotated, f"Moodle ID: {info['moodle_id']}",
                           (10, y_offset), font, 0.7, (0, 255, 0), 2)
                y_offset += 35
            
            if info['name']:
                cv2.putText(annotated, f"Name: {info['name']}",
                           (10, y_offset), font, 0.7, (0, 255, 0), 2)
                y_offset += 35
            
            if info['department']:
                cv2.putText(annotated, f"Dept: {info['department']}",
                           (10, y_offset), font, 0.6, (0, 255, 0), 2)
        
        except Exception as e:
            cv2.putText(annotated, f"OCR Error: {str(e)[:30]}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        return annotated, info
    
    def run(self, camera_index=0):
        """
        Run live camera feed
        
        Args:
            camera_index: Camera index (0 = default)
        """
        print(f"\n📷 Opening camera {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"❌ Failed to open camera {camera_index}")
            return
        
        print("✅ Camera opened!")
        print("\n🎬 Starting live feed...")
        print("=" * 70)
        
        frame_count = 0
        process_every = 30  # Process every 30 frames for speed
        last_info = None
        
        # Create output directory
        output_dir = Path("outputs/live_captures")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                frame_count += 1
                
                # Process frame
                if frame_count % process_every == 0:
                    annotated, info = self.process_frame(frame)
                    last_info = info
                    
                    # Print to console
                    if info['moodle_id'] or info['name'] or info['department']:
                        print(f"\n📋 Detection at frame {frame_count}:")
                        if info['moodle_id']:
                            print(f"   🆔 Moodle ID: {info['moodle_id']}")
                        if info['name']:
                            print(f"   👤 Name: {info['name']}")
                        if info['department']:
                            print(f"   🏢 Department: {info['department']}")
                else:
                    annotated = frame
                
                # Add instructions overlay
                cv2.putText(annotated, "SPACE=Analyze | S=Save | Q=Quit",
                           (10, frame.shape[0] - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Show frame (will fail on headless, but we'll catch it)
                try:
                    cv2.imshow('Live ID Card Recognition', annotated)
                except cv2.error:
                    # Headless mode - just print to console
                    pass
                
                # Handle keyboard
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\n👋 Quitting...")
                    break
                
                elif key == ord(' '):
                    # Force process current frame
                    print("\n🔍 Analyzing current frame...")
                    annotated, info = self.process_frame(frame)
                    last_info = info
                    
                    print(f"\n📋 Analysis Result:")
                    print(f"   🆔 Moodle ID: {info['moodle_id'] or 'Not found'}")
                    print(f"   👤 Name: {info['name'] or 'Not found'}")
                    print(f"   🏢 Department: {info['department'] or 'Not found'}")
                    print(f"   📦 Card Detected: {info['detected']}")
                
                elif key == ord('s'):
                    # Save current frame
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_path = output_dir / f"capture_{timestamp}.jpg"
                    cv2.imwrite(str(save_path), frame)
                    print(f"\n💾 Frame saved: {save_path}")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        
        finally:
            cap.release()
            try:
                cv2.destroyAllWindows()
            except:
                pass
            
            print("\n" + "=" * 70)
            print("✅ Live feed stopped")
            print("=" * 70)
            
            if last_info:
                print("\n📊 Last Detection:")
                print(f"   🆔 Moodle ID: {last_info['moodle_id'] or 'N/A'}")
                print(f"   👤 Name: {last_info['name'] or 'N/A'}")
                print(f"   🏢 Department: {last_info['department'] or 'N/A'}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Live ID Card Recognition Test')
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera index (default: 0)')
    
    args = parser.parse_args()
    
    tester = LiveIDCardTester()
    tester.run(camera_index=args.camera)


if __name__ == "__main__":
    main()
