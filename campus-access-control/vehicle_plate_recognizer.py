"""
Vehicle Number Plate Recognition Module
Uses YOLO for detection and EasyOCR for text extraction
Processes video frame-by-frame and saves to JSON
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


class VehiclePlateRecognizer:
    """
    Vehicle number plate recognition system for Indian license plates
    """
    
    def __init__(self, model_path=None, use_gpu=True):
        """
        Initialize the vehicle plate recognizer
        
        Args:
            model_path (str): Path to YOLO model weights
            use_gpu (bool): Whether to use GPU acceleration
        """
        self.use_gpu = use_gpu
        self.device = 'cuda' if (use_gpu and torch.cuda.is_available()) else 'cpu'
        
        print("=" * 70)
        print("🚗 VEHICLE NUMBER PLATE RECOGNITION SYSTEM")
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
            'plates_detected': 0,
            'plates_extracted': 0,
            'processing_times': []
        }
        
        print("=" * 70)
    
    def extract_text_from_roi(self, frame, x1, y1, x2, y2):
        """
        Extract text from license plate region using EasyOCR
        
        Args:
            frame: Input frame
            x1, y1, x2, y2: Bounding box coordinates
            
        Returns:
            str: Extracted text from plate
        """
        # Extract ROI
        roi = frame[y1:y2, x1:x2]
        
        # Skip if ROI is too small
        if roi.shape[0] < 20 or roi.shape[1] < 20:
            return ""
        
        # Preprocess ROI
        roi = self.preprocess_plate_roi(roi)
        
        # Run OCR
        try:
            results = self.reader.readtext(roi, detail=1)
            
            text = ""
            for (bbox, detected_text, confidence) in results:
                if confidence > OCR_CONFIDENCE_THRESHOLD:
                    text += detected_text + " "
            
            # Clean and format text
            text = self.clean_plate_text(text.strip())
            return text
            
        except Exception as e:
            print(f"⚠️  OCR Error: {e}")
            return ""
    
    def preprocess_plate_roi(self, roi):
        """
        Preprocess plate ROI for better OCR accuracy
        
        Args:
            roi: Region of interest (plate image)
            
        Returns:
            Preprocessed image
        """
        # Resize if too small
        if roi.shape[1] < 200:
            scale = 200 / roi.shape[1]
            roi = cv2.resize(roi, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Convert to grayscale
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, h=10)
        
        return denoised
    
    def clean_plate_text(self, text):
        """
        Clean and format extracted plate text for Indian plates
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned and formatted text
        """
        # Remove special characters except hyphen
        text = re.sub(r'[^A-Z0-9\-\s]', '', text.upper())
        
        # Apply character corrections
        for old_char, new_char in PLATE_CHAR_CORRECTIONS.items():
            # Only apply corrections in numeric sections
            text = text.replace(old_char, new_char)
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        # Try to format as standard Indian plate
        text = self.format_indian_plate(text)
        
        return text
    
    def format_indian_plate(self, text):
        """
        Format text to match Indian license plate pattern
        
        Args:
            text (str): Cleaned text
            
        Returns:
            str: Formatted plate number
        """
        # Remove all spaces and hyphens
        clean = text.replace(' ', '').replace('-', '')
        
        # Try to match standard format: XX00XX0000
        if len(clean) >= 10:
            # Standard format: MH-12-AB-1234
            formatted = f"{clean[0:2]}-{clean[2:4]}-{clean[4:6]}-{clean[6:10]}"
            return formatted
        elif len(clean) >= 9:
            # Short format without full digits
            formatted = f"{clean[0:2]}-{clean[2:4]}-{clean[4:6]}-{clean[6:]}"
            return formatted
        
        return text
    
    def validate_indian_plate(self, plate_text):
        """
        Validate if text matches Indian license plate patterns
        
        Args:
            plate_text (str): Plate text to validate
            
        Returns:
            bool: True if valid Indian plate format
        """
        if not plate_text or len(plate_text) < 8:
            return False
        
        # Check against Indian plate patterns
        for pattern in INDIAN_PLATE_PATTERNS:
            if re.match(pattern, plate_text):
                # Additional check: verify state code
                state_code = plate_text[:2]
                if state_code in VALID_STATE_CODES:
                    return True
        
        return False
    
    def detect_and_extract(self, frame, frame_number, timestamp):
        """
        Detect license plates in frame and extract text
        
        Args:
            frame: Input video frame
            frame_number (int): Frame number
            timestamp (str): Timestamp
            
        Returns:
            dict: Detection results
        """
        results_data = {
            'frame_number': frame_number,
            'timestamp': timestamp,
            'detections': []
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
                if confidence < MIN_PLATE_CONFIDENCE:
                    continue
                
                # Extract text from plate
                plate_text = self.extract_text_from_roi(frame, x1, y1, x2, y2)
                
                # Validate plate
                is_valid = self.validate_indian_plate(plate_text)
                
                detection = {
                    'bbox': [x1, y1, x2, y2],
                    'confidence': round(confidence, 3),
                    'plate_text': plate_text,
                    'is_valid': is_valid,
                }
                
                results_data['detections'].append(detection)
                
                # Update statistics
                self.stats['plates_detected'] += 1
                if plate_text:
                    self.stats['plates_extracted'] += 1
                
                # Draw on frame
                color = (0, 255, 0) if is_valid else (0, 165, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Add label
                label = f"{plate_text} ({confidence:.2f})"
                cv2.putText(frame, label, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        self.stats['frames_processed'] += 1
        return results_data, frame
    
    def process_video(self, video_path, output_json_path=None, save_video=False):
        """
        Process video file and extract license plates
        
        Args:
            video_path (str): Path to input video
            output_json_path (str): Path to save JSON output
            save_video (bool): Whether to save annotated video
            
        Returns:
            dict: All detection results
        """
        video_path = Path(video_path)
        if not video_path.exists():
            print(f"❌ Video not found: {video_path}")
            return None
        
        print(f"\n📹 Processing video: {video_path.name}")
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"❌ Failed to open video: {video_path}")
            return None
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"📊 Video: {width}x{height} @ {fps}fps, {total_frames} frames")
        
        # Video writer (optional)
        out = None
        if save_video:
            output_video_path = CAPTURED_FRAMES_DIR / f"{video_path.stem}_annotated.mp4"
            fourcc = cv2.VideoWriter_fourcc(*VIDEO_OUTPUT_CODEC)
            out = cv2.VideoWriter(str(output_video_path), fourcc, fps, (width, height))
            print(f"💾 Saving annotated video to: {output_video_path}")
        
        # Process frames
        all_results = {
            'video_name': video_path.name,
            'video_properties': {
                'width': width,
                'height': height,
                'fps': fps,
                'total_frames': total_frames
            },
            'processing_started': get_timestamp(),
            'frames': []
        }
        
        frame_count = 0
        start_time = datetime.now()
        
        print("\n🔄 Processing frames...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Skip frames based on FRAME_SKIP
            if frame_count % FRAME_SKIP != 0:
                if out:
                    out.write(frame)
                continue
            
            # Process frame
            timestamp = get_timestamp()
            results, annotated_frame = self.detect_and_extract(frame, frame_count, timestamp)
            
            # Add to results if detections found
            if results['detections']:
                all_results['frames'].append(results)
            
            # Write annotated frame
            if out:
                out.write(annotated_frame)
            
            # Progress indicator
            if frame_count % 30 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"  ⏳ Progress: {frame_count}/{total_frames} ({progress:.1f}%) - "
                      f"Plates detected: {self.stats['plates_detected']}")
        
        # Release resources
        cap.release()
        if out:
            out.release()
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        all_results['processing_completed'] = get_timestamp()
        all_results['processing_time_seconds'] = round(processing_time, 2)
        all_results['statistics'] = {
            'frames_processed': self.stats['frames_processed'],
            'plates_detected': self.stats['plates_detected'],
            'plates_extracted': self.stats['plates_extracted'],
            'avg_fps': round(frame_count / processing_time, 2) if processing_time > 0 else 0
        }
        
        # Save to JSON
        if output_json_path is None:
            output_json_path = VEHICLE_OUTPUT_DIR / get_output_filename(f"vehicle_{video_path.stem}")
        
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Processing complete!")
        print(f"⏱️  Time: {processing_time:.2f}s")
        print(f"📊 Stats: {self.stats['frames_processed']} frames, "
              f"{self.stats['plates_detected']} plates detected, "
              f"{self.stats['plates_extracted']} plates extracted")
        print(f"💾 Results saved to: {output_json_path}")
        
        return all_results
    
    def process_camera_stream(self, camera_index=0, duration=None):
        """
        Process live camera stream
        
        Args:
            camera_index (int): Camera index
            duration (int): Duration in seconds (None = infinite)
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
        detections_log = []
        start_time = datetime.now()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame")
                break
            
            frame_count += 1
            timestamp = get_timestamp()
            
            # Process frame
            results, annotated_frame = self.detect_and_extract(frame, frame_count, timestamp)
            
            # Save detections
            if results['detections']:
                detections_log.append(results)
            
            # Display
            cv2.imshow('Vehicle Plate Recognition', annotated_frame)
            
            # Handle key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s') and results['detections']:
                # Save current detection
                output_path = VEHICLE_OUTPUT_DIR / get_output_filename('camera_detection')
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"💾 Detection saved: {output_path}")
            
            # Check duration
            if duration and (datetime.now() - start_time).total_seconds() > duration:
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Save all detections
        if detections_log:
            output_path = VEHICLE_OUTPUT_DIR / get_output_filename('camera_session')
            session_data = {
                'session_started': start_time.isoformat(),
                'session_ended': get_timestamp(),
                'total_detections': len(detections_log),
                'detections': detections_log
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Session log saved: {output_path}")


def main():
    """Main function to test the module"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Vehicle Number Plate Recognition')
    parser.add_argument('--video', type=str, help='Path to video file')
    parser.add_argument('--camera', action='store_true', help='Use camera stream')
    parser.add_argument('--model', type=str, help='Path to YOLO model')
    parser.add_argument('--save-video', action='store_true', help='Save annotated video')
    
    args = parser.parse_args()
    
    # Initialize recognizer
    recognizer = VehiclePlateRecognizer(model_path=args.model)
    
    if args.camera:
        # Process camera stream
        recognizer.process_camera_stream()
    elif args.video:
        # Process video file
        recognizer.process_video(args.video, save_video=args.save_video)
    else:
        print("❌ Please specify --video or --camera")


if __name__ == "__main__":
    main()
