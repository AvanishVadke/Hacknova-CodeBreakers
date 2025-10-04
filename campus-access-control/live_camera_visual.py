"""
Live ID Card Recognition with Visual Annotations
Saves annotated frames showing:
- Detected card region (green box)
- Name, Department, Moodle ID overlays
- All OCR text regions
- Confidence scores
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


class VisualIDCardTester:
    """
    Visual ID card tester - saves annotated frames
    """
    
    def __init__(self):
        """Initialize tester"""
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        print("=" * 70)
        print("📹 VISUAL ID CARD RECOGNITION (Saves Annotated Frames)")
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
        
        # Output directory
        self.output_dir = Path("outputs/live_captures")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print("=" * 70)
        print(f"📁 Saving frames to: {self.output_dir}")
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
        
        for bbox, text, conf in text_results:
            if conf > 0.5:
                matches = re.findall(pattern, text)
                if matches:
                    return matches[0], conf, bbox
        
        return None, 0.0, None
    
    def extract_name(self, text_results):
        """Extract name (2-3 words, high confidence, all caps)"""
        for bbox, text, conf in text_results:
            if conf > 0.6 and self.filter_text(text):
                words = text.split()
                if 2 <= len(words) <= 3:
                    if sum(c.isupper() or c.isspace() for c in text) / len(text) > 0.7:
                        if not any(dept in text.upper() for dept in ['ENGINEERING', 'TECHNOLOGY']):
                            return text.upper(), conf, bbox
        
        return None, 0.0, None
    
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
        
        for bbox, text, conf in text_results:
            if conf > 0.7:
                text_upper = text.upper()
                for dept in departments:
                    if dept in text_upper:
                        if 'ENGINEERING' in text_upper:
                            return text_upper, conf, bbox
                        else:
                            return f"{text_upper} ENGINEERING", conf, bbox
        
        return None, 0.0, None
    
    def draw_text_with_background(self, img, text, pos, font_scale=0.6, thickness=2, 
                                  text_color=(255, 255, 255), bg_color=(0, 128, 0)):
        """Draw text with background rectangle"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        x, y = pos
        
        # Draw background rectangle
        cv2.rectangle(img, 
                     (x - 5, y - text_height - 5),
                     (x + text_width + 5, y + baseline + 5),
                     bg_color, -1)
        
        # Draw text
        cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness)
        
        return y + text_height + baseline + 10
    
    def process_frame(self, frame):
        """
        Process frame and create annotated visualization
        
        Returns:
            tuple: (annotated_frame, info_dict)
        """
        annotated = frame.copy()
        h, w = annotated.shape[:2]
        
        # Detect card
        bbox = None
        detection_method = "None"
        
        # Try YOLO first
        if self.yolo_model:
            try:
                results = self.yolo_model(frame, conf=0.25, verbose=False)
                if len(results[0].boxes) > 0:
                    box = results[0].boxes[0]
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    bbox = (x1, y1, x2, y2)
                    detection_method = "YOLO"
            except:
                pass
        
        # Fallback to OpenCV
        if bbox is None:
            bbox = self.detect_card_opencv(frame)
            if bbox:
                detection_method = "OpenCV"
        
        # Draw card bounding box
        if bbox:
            x1, y1, x2, y2 = bbox
            # Draw thick green rectangle
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 3)
            # Draw label
            label = f"ID CARD ({detection_method})"
            cv2.putText(annotated, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Extract text
        info = {
            'moodle_id': None,
            'name': None,
            'department': None,
            'confidence': {},
            'detected': bbox is not None,
            'method': detection_method
        }
        
        try:
            # OCR on card region or full frame
            if bbox:
                x1, y1, x2, y2 = bbox
                # Add padding
                pad = 10
                x1 = max(0, x1 - pad)
                y1 = max(0, y1 - pad)
                x2 = min(w, x2 + pad)
                y2 = min(h, y2 + pad)
                roi = frame[y1:y2, x1:x2]
                offset_x, offset_y = x1, y1
            else:
                roi = frame
                offset_x, offset_y = 0, 0
            
            # Run OCR
            ocr_results = self.reader.readtext(roi)
            
            # Draw ALL OCR text regions (light blue boxes)
            for bbox_ocr, text, conf in ocr_results:
                # Draw bounding box for each text region
                pts = np.array(bbox_ocr, dtype=np.int32)
                pts[:, 0] += offset_x
                pts[:, 1] += offset_y
                cv2.polylines(annotated, [pts], True, (255, 200, 100), 1)
                
                # Draw text label (small)
                x_min = int(min(pt[0] for pt in bbox_ocr))
                y_min = int(min(pt[1] for pt in bbox_ocr))
                cv2.putText(annotated, f"{conf:.2f}", 
                           (x_min + offset_x, y_min + offset_y - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 200, 100), 1)
            
            # Extract key info
            moodle_id, mid_conf, mid_bbox = self.extract_moodle_id(ocr_results)
            name, name_conf, name_bbox = self.extract_name(ocr_results)
            dept, dept_conf, dept_bbox = self.extract_department(ocr_results)
            
            info['moodle_id'] = moodle_id
            info['name'] = name
            info['department'] = dept
            info['confidence'] = {
                'moodle_id': mid_conf,
                'name': name_conf,
                'department': dept_conf
            }
            
            # Draw highlighted boxes for extracted fields
            if mid_bbox and moodle_id:
                pts = np.array(mid_bbox, dtype=np.int32)
                pts[:, 0] += offset_x
                pts[:, 1] += offset_y
                cv2.polylines(annotated, [pts], True, (0, 255, 255), 3)  # Yellow
            
            if name_bbox and name:
                pts = np.array(name_bbox, dtype=np.int32)
                pts[:, 0] += offset_x
                pts[:, 1] += offset_y
                cv2.polylines(annotated, [pts], True, (255, 0, 255), 3)  # Magenta
            
            if dept_bbox and dept:
                pts = np.array(dept_bbox, dtype=np.int32)
                pts[:, 0] += offset_x
                pts[:, 1] += offset_y
                cv2.polylines(annotated, [pts], True, (255, 128, 0), 3)  # Orange
            
            # Draw info overlay panel (top-left)
            y_pos = 30
            
            # Title
            y_pos = self.draw_text_with_background(
                annotated, "ID CARD DETECTION", (10, y_pos), 
                font_scale=0.8, thickness=2, bg_color=(50, 50, 50)
            )
            
            # Card detection status
            if info['detected']:
                status_text = f"Card: YES ({detection_method})"
                status_color = (0, 200, 0)
            else:
                status_text = "Card: NO (Full Frame OCR)"
                status_color = (0, 128, 200)
            
            y_pos = self.draw_text_with_background(
                annotated, status_text, (10, y_pos),
                font_scale=0.6, thickness=2, bg_color=status_color
            )
            
            # Moodle ID
            if moodle_id:
                text = f"ID: {moodle_id} ({mid_conf:.2f})"
                y_pos = self.draw_text_with_background(
                    annotated, text, (10, y_pos),
                    font_scale=0.7, thickness=2, bg_color=(0, 200, 200)  # Yellow
                )
            else:
                y_pos = self.draw_text_with_background(
                    annotated, "ID: Not found", (10, y_pos),
                    font_scale=0.6, thickness=2, bg_color=(100, 100, 100)
                )
            
            # Name
            if name:
                text = f"Name: {name}"
                y_pos = self.draw_text_with_background(
                    annotated, text, (10, y_pos),
                    font_scale=0.6, thickness=2, bg_color=(200, 0, 200)  # Magenta
                )
                text = f"Conf: {name_conf:.2f}"
                y_pos = self.draw_text_with_background(
                    annotated, text, (10, y_pos),
                    font_scale=0.5, thickness=1, bg_color=(150, 0, 150)
                )
            else:
                y_pos = self.draw_text_with_background(
                    annotated, "Name: Not found", (10, y_pos),
                    font_scale=0.6, thickness=2, bg_color=(100, 100, 100)
                )
            
            # Department
            if dept:
                text = f"Dept: {dept}"
                y_pos = self.draw_text_with_background(
                    annotated, text, (10, y_pos),
                    font_scale=0.6, thickness=2, bg_color=(200, 100, 0)  # Orange
                )
                text = f"Conf: {dept_conf:.2f}"
                y_pos = self.draw_text_with_background(
                    annotated, text, (10, y_pos),
                    font_scale=0.5, thickness=1, bg_color=(150, 75, 0)
                )
            else:
                y_pos = self.draw_text_with_background(
                    annotated, "Dept: Not found", (10, y_pos),
                    font_scale=0.6, thickness=2, bg_color=(100, 100, 100)
                )
            
            # Legend (bottom)
            legend_y = h - 80
            cv2.putText(annotated, "LEGEND:", (10, legend_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            legend_y += 20
            cv2.rectangle(annotated, (10, legend_y), (30, legend_y + 10), (0, 255, 0), -1)
            cv2.putText(annotated, "ID Card", (35, legend_y + 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            legend_y += 15
            cv2.rectangle(annotated, (10, legend_y), (30, legend_y + 10), (0, 255, 255), -1)
            cv2.putText(annotated, "Moodle ID", (35, legend_y + 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            legend_y += 15
            cv2.rectangle(annotated, (10, legend_y), (30, legend_y + 10), (255, 0, 255), -1)
            cv2.putText(annotated, "Name", (35, legend_y + 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            legend_y += 15
            cv2.rectangle(annotated, (10, legend_y), (30, legend_y + 10), (255, 128, 0), -1)
            cv2.putText(annotated, "Department", (35, legend_y + 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        except Exception as e:
            cv2.putText(annotated, f"Error: {str(e)[:50]}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        return annotated, info
    
    def run(self, camera_index=0, interval=3.0, resolution=(1920, 1080), fps=30):
        """
        Run live camera feed with visual annotations
        
        Args:
            camera_index: Camera index
            interval: Seconds between captures
            resolution: Tuple (width, height) - default 1080p
            fps: Target frames per second - default 30
        """
        print(f"📷 Opening camera {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"❌ Failed to open camera {camera_index}")
            return
        
        # Set camera properties for higher resolution and FPS
        width, height = resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps)
        
        # Enable camera buffer optimizations
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer lag
        
        # Verify settings
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        print(f"✅ Camera configured:")
        print(f"   📐 Resolution: {actual_width}x{actual_height} (requested: {width}x{height})")
        print(f"   ⚡ FPS: {actual_fps} (requested: {fps})")
        
        print(f"🎯 Processing every {interval} seconds")
        print("=" * 70)
        print("\n⏳ Starting capture loop...\n")
        
        frame_count = 0
        last_capture_time = 0
        detections = []
        
        # FPS measurement
        fps_start_time = time.time()
        fps_frame_count = 0
        current_fps = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                frame_count += 1
                fps_frame_count += 1
                current_time = time.time()
                
                # Calculate FPS every second
                if current_time - fps_start_time >= 1.0:
                    current_fps = fps_frame_count / (current_time - fps_start_time)
                    fps_frame_count = 0
                    fps_start_time = current_time
                
                # Process frame at interval for OCR (heavy operation)
                if current_time - last_capture_time >= interval:
                    last_capture_time = current_time
                    
                    print(f"🔍 Processing frame {frame_count} | FPS: {current_fps:.1f}...")
                    annotated, info = self.process_frame(frame)
                    
                    # Save annotated frame
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"frame_{timestamp}.jpg"
                    filepath = self.output_dir / filename
                    cv2.imwrite(str(filepath), annotated)
                    
                    # Console output
                    print(f"\n📋 Frame saved: {filename}")
                    print("   " + "-" * 60)
                    print(f"   📦 Card Detected: {'✅ YES' if info['detected'] else '⚠️  NO'}")
                    print(f"   🔧 Method: {info['method']}")
                    
                    if info['moodle_id']:
                        conf = info['confidence']['moodle_id']
                        print(f"   🆔 Moodle ID: {info['moodle_id']} (conf: {conf:.2f})")
                    else:
                        print("   🆔 Moodle ID: ❌ Not found")
                    
                    if info['name']:
                        conf = info['confidence']['name']
                        print(f"   👤 Name: {info['name']} (conf: {conf:.2f})")
                    else:
                        print("   👤 Name: ❌ Not found")
                    
                    if info['department']:
                        conf = info['confidence']['department']
                        print(f"   🏢 Department: {info['department']} (conf: {conf:.2f})")
                    else:
                        print("   🏢 Department: ❌ Not found")
                    
                    print("   " + "-" * 60)
                    
                    # Track valid detections
                    if info['moodle_id'] and info['name']:
                        detections.append(info)
                        print(f"   ✅ Valid! Total: {len(detections)}\n")
                    else:
                        print()
                
                # NO delay - run as fast as possible for high FPS
                # (OCR only runs at interval, so camera runs at max speed)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Stopped by user (Ctrl+C)")
        
        finally:
            cap.release()
            
            print("\n" + "=" * 70)
            print("📊 SESSION SUMMARY")
            print("=" * 70)
            print(f"Frames captured: {frame_count}")
            print(f"Average FPS: {current_fps:.1f}")
            print(f"Valid detections: {len(detections)}")
            print(f"Saved to: {self.output_dir}")
            
            if detections:
                print("\n📋 Successful Detections:")
                for i, det in enumerate(detections, 1):
                    print(f"\n   Detection {i}:")
                    print(f"      ID: {det['moodle_id']}")
                    print(f"      Name: {det['name']}")
                    print(f"      Dept: {det['department']}")
            
            print("\n✅ Live feed stopped")
            print(f"\n📁 Check annotated frames in: {self.output_dir.absolute()}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Visual ID Card Recognition')
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera index (default: 0)')
    parser.add_argument('--interval', type=float, default=3.0,
                       help='Seconds between OCR captures (default: 3.0)')
    parser.add_argument('--width', type=int, default=1920,
                       help='Camera width resolution (default: 1920)')
    parser.add_argument('--height', type=int, default=1080,
                       help='Camera height resolution (default: 1080)')
    parser.add_argument('--fps', type=int, default=30,
                       help='Target FPS (default: 30)')
    
    args = parser.parse_args()
    
    tester = VisualIDCardTester()
    tester.run(
        camera_index=args.camera, 
        interval=args.interval,
        resolution=(args.width, args.height),
        fps=args.fps
    )


if __name__ == "__main__":
    main()
