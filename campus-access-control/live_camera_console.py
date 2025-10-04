"""
Live ID Card Recognition - CONSOLE MODE (No GUI)
Perfect for testing without display/headless systems
Shows: Name, Department, Moodle ID
"""

import cv2
import torch
import easyocr
import numpy as np
import re
import time
from datetime import datetime
from pathlib import Path
from ultralytics import YOLO


class ConsoleIDCardTester:
    """
    Console-only ID card tester (no GUI)
    """
    
    def __init__(self):
        """Initialize tester"""
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        print("=" * 70)
        print("📹 LIVE ID CARD RECOGNITION (CONSOLE MODE)")
        print("=" * 70)
        print(f"🔧 Device: {self.device.upper()}")
        
        if self.device == 'cuda':
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        
        # Initialize YOLO
        try:
            self.yolo_model = YOLO("models/id_card_best.pt")
            print("✅ YOLO model loaded")
        except:
            self.yolo_model = None
            print("⚠️  Using OpenCV fallback only")
        
        # Initialize EasyOCR
        print("📝 Initializing EasyOCR...")
        self.reader = easyocr.Reader(['en'], gpu=(self.device == 'cuda'), verbose=False)
        print("✅ EasyOCR ready")
        
        # Filters
        self.ignore_keywords = [
            'parshvanalh', 'charitable', 'trust', 'shah', 'institute',
            'technology', 'thane', 'academic', 'year', '2025', '2026',
            'principal', 'photo', 'id no', 'signature', '4', '202'
        ]
        
        print("=" * 70)
        print("\n📷 Press Ctrl+C to stop\n")
    
    def detect_card_opencv(self, frame):
        """Detect ID card using OpenCV"""
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        frame_area = h * w
        best_bbox = None
        max_area = 0
        
        for contour in contours:
            x, y, w_box, h_box = cv2.boundingRect(contour)
            area = w_box * h_box
            aspect_ratio = w_box / h_box if h_box > 0 else 0
            
            if (0.1 * frame_area < area < 0.9 * frame_area and
                1.2 < aspect_ratio < 2.5 and
                w_box > 150 and h_box > 80):
                
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                
                if len(approx) >= 4 and area > max_area:
                    max_area = area
                    best_bbox = (x, y, x + w_box, y + h_box)
        
        return best_bbox
    
    def filter_text(self, text):
        """Check if text should be kept"""
        text_lower = text.lower().strip()
        
        if len(text_lower) < 3:
            return False
        
        for keyword in self.ignore_keywords:
            if keyword in text_lower:
                return False
        
        return True
    
    def extract_moodle_id(self, text_results):
        """Extract 8-digit Moodle ID starting with 2"""
        pattern = r'\b2\d{7}\b'
        
        for _, text, conf in text_results:
            if conf > 0.5:
                matches = re.findall(pattern, text)
                if matches:
                    return matches[0], conf
        
        return None, 0.0
    
    def extract_name(self, text_results):
        """Extract name (2-3 words, high confidence, all caps)"""
        for _, text, conf in text_results:
            if conf > 0.6 and self.filter_text(text):
                words = text.split()
                if 2 <= len(words) <= 3:
                    if sum(c.isupper() or c.isspace() for c in text) / len(text) > 0.7:
                        if not any(dept in text.upper() for dept in ['ENGINEERING', 'TECHNOLOGY']):
                            return text.upper(), conf
        
        return None, 0.0
    
    def extract_department(self, text_results):
        """Extract department"""
        departments = [
            'COMPUTER ENGINEERING', 'COMPUTER', 'COMP',
            'MECHANICAL ENGINEERING', 'MECHANICAL',
            'CIVIL ENGINEERING', 'CIVIL',
            'ELECTRICAL ENGINEERING', 'ELECTRICAL',
            'ELECTRONICS', 'EXTC', 'E&TC',
            'INFORMATION TECHNOLOGY', 'IT'
        ]
        
        for _, text, conf in text_results:
            if conf > 0.7:
                text_upper = text.upper()
                for dept in departments:
                    if dept in text_upper:
                        if 'ENGINEERING' in text_upper:
                            return text_upper, conf
                        else:
                            return f"{text_upper} ENGINEERING", conf
        
        return None, 0.0
    
    def process_frame(self, frame):
        """Process frame and extract info"""
        # Detect card
        bbox = None
        
        if self.yolo_model:
            try:
                results = self.yolo_model(frame, conf=0.25, verbose=False)
                if len(results[0].boxes) > 0:
                    box = results[0].boxes[0]
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    bbox = (x1, y1, x2, y2)
            except:
                pass
        
        if bbox is None:
            bbox = self.detect_card_opencv(frame)
        
        # Extract text
        info = {
            'moodle_id': None,
            'name': None,
            'department': None,
            'confidence': {},
            'detected': bbox is not None
        }
        
        try:
            # OCR on card region or full frame
            if bbox:
                x1, y1, x2, y2 = bbox
                h, w = frame.shape[:2]
                pad = 10
                x1 = max(0, x1 - pad)
                y1 = max(0, y1 - pad)
                x2 = min(w, x2 + pad)
                y2 = min(h, y2 + pad)
                roi = frame[y1:y2, x1:x2]
            else:
                roi = frame
            
            # Run OCR
            ocr_results = self.reader.readtext(roi)
            
            # Extract info
            moodle_id, mid_conf = self.extract_moodle_id(ocr_results)
            name, name_conf = self.extract_name(ocr_results)
            dept, dept_conf = self.extract_department(ocr_results)
            
            info['moodle_id'] = moodle_id
            info['name'] = name
            info['department'] = dept
            info['confidence'] = {
                'moodle_id': mid_conf,
                'name': name_conf,
                'department': dept_conf
            }
        
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def run(self, camera_index=0, interval=2.0):
        """
        Run live camera feed (console only)
        
        Args:
            camera_index: Camera index
            interval: Seconds between captures (default 2.0)
        """
        print(f"📷 Opening camera {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"❌ Failed to open camera {camera_index}")
            return
        
        print(f"✅ Camera opened!")
        print(f"🎯 Capturing every {interval} seconds")
        print("=" * 70)
        print("\n⏳ Waiting for first capture...\n")
        
        frame_count = 0
        last_capture_time = 0
        detections = []
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                frame_count += 1
                current_time = time.time()
                
                # Process frame at interval
                if current_time - last_capture_time >= interval:
                    last_capture_time = current_time
                    
                    print(f"🔍 Analyzing frame {frame_count}...")
                    info = self.process_frame(frame)
                    
                    # Display results
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"\n📋 [{timestamp}] Detection Result:")
                    print("   " + "-" * 60)
                    
                    if info['detected']:
                        print("   📦 Card Detected: ✅ YES")
                    else:
                        print("   📦 Card Detected: ⚠️  NO (using full frame OCR)")
                    
                    if info['moodle_id']:
                        conf = info['confidence']['moodle_id']
                        print(f"   🆔 Moodle ID:     {info['moodle_id']} (conf: {conf:.2f})")
                    else:
                        print("   🆔 Moodle ID:     ❌ Not found")
                    
                    if info['name']:
                        conf = info['confidence']['name']
                        print(f"   👤 Name:          {info['name']} (conf: {conf:.2f})")
                    else:
                        print("   👤 Name:          ❌ Not found")
                    
                    if info['department']:
                        conf = info['confidence']['department']
                        print(f"   🏢 Department:    {info['department']} (conf: {conf:.2f})")
                    else:
                        print("   🏢 Department:    ❌ Not found")
                    
                    print("   " + "-" * 60)
                    
                    # Save successful detection
                    if info['moodle_id'] and info['name']:
                        detections.append(info)
                        print(f"   ✅ Valid detection saved! (Total: {len(detections)})")
                    
                    print()
                
                # Small delay
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Stopped by user (Ctrl+C)")
        
        finally:
            cap.release()
            
            print("\n" + "=" * 70)
            print("📊 SESSION SUMMARY")
            print("=" * 70)
            print(f"Frames processed: {frame_count}")
            print(f"Valid detections: {len(detections)}")
            
            if detections:
                print("\n📋 Successful Captures:")
                for i, det in enumerate(detections, 1):
                    print(f"\n   Detection {i}:")
                    print(f"      ID: {det['moodle_id']}")
                    print(f"      Name: {det['name']}")
                    print(f"      Dept: {det['department']}")
            
            print("\n✅ Live feed stopped")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Console ID Card Recognition')
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera index (default: 0)')
    parser.add_argument('--interval', type=float, default=2.0,
                       help='Seconds between captures (default: 2.0)')
    
    args = parser.parse_args()
    
    tester = ConsoleIDCardTester()
    tester.run(camera_index=args.camera, interval=args.interval)


if __name__ == "__main__":
    main()
