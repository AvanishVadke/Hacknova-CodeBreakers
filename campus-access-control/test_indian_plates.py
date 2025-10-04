"""
Indian License Plate Recognition Test
Tests vehicle plate recognition on Indian videos using dedicated license plate YOLO model
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
import os

class IndianLicensePlateRecognizer:
    def __init__(self, model_path, use_gpu=True):
        """Initialize the license plate recognizer"""
        self.device = 'cuda' if (use_gpu and torch.cuda.is_available()) else 'cpu'
        
        print("=" * 70)
        print("🇮🇳 INDIAN LICENSE PLATE RECOGNITION SYSTEM")
        print("=" * 70)
        print(f"🔧 Device: {self.device.upper()}")
        
        if self.device == 'cuda':
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
            print(f"🔥 CUDA Version: {torch.version.cuda}")
        
        # Load YOLO model
        print(f"\n📦 Loading License Plate YOLO model: {model_path}")
        self.model = YOLO(str(model_path))
        self.model.to(self.device)
        print("✅ YOLO model loaded successfully")
        
        # Initialize EasyOCR for Indian plates
        print(f"\n📝 Initializing EasyOCR...")
        self.reader = easyocr.Reader(['en'], gpu=(self.device == 'cuda'), verbose=False)
        print("✅ EasyOCR ready")
        print("=" * 70)
        
        # Indian license plate patterns
        self.indian_patterns = [
            r'[A-Z]{2}\s*\d{1,2}\s*[A-Z]{1,2}\s*\d{4}',  # MH 12 AB 1234
            r'[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}',  # MH12AB1234
        ]
        
        self.detected_plates = {}
    
    def clean_plate_text(self, text):
        """Clean and validate Indian license plate text"""
        # Remove special characters
        text = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # Replace common OCR mistakes
        replacements = {
            'O': '0', 'I': '1', 'S': '5', 'B': '8', 
            'G': '6', 'Z': '2', 'T': '7'
        }
        
        for old, new in replacements.items():
            # Only replace in number positions (last 4 chars)
            if len(text) > 4:
                text = text[:-4] + text[-4:].replace(old, new)
        
        return text
    
    def format_indian_plate(self, text):
        """Format text as Indian license plate"""
        text = self.clean_plate_text(text)
        
        # Try to match Indian patterns
        # Format: XX00XX0000 (e.g., MH12AB1234)
        if len(text) >= 8:
            # Extract components
            state = text[:2] if text[:2].isalpha() else ""
            rest = text[2:]
            
            # Try to find district code (2 digits)
            district = ""
            series = ""
            number = ""
            
            for i, char in enumerate(rest):
                if char.isdigit() and len(district) < 2:
                    district += char
                elif char.isalpha() and len(district) == 2 and len(series) < 2:
                    series += char
                elif char.isdigit() and len(series) >= 1:
                    number += char
            
            if state and district and series and number:
                formatted = f"{state} {district} {series} {number}"
                return formatted
        
        return text
    
    def extract_plate_text(self, frame, x1, y1, x2, y2):
        """Extract text from license plate region"""
        # Extract ROI
        roi = frame[y1:y2, x1:x2]
        
        if roi.size == 0:
            return None
        
        # Preprocess ROI
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        # OCR
        results = self.reader.readtext(denoised, detail=1)
        
        # Combine text with high confidence
        text_parts = []
        for (bbox, text, confidence) in results:
            if confidence > 0.3:  # Lower threshold for Indian plates
                text_parts.append(text.strip())
        
        if not text_parts:
            return None
        
        # Combine and format
        full_text = "".join(text_parts)
        formatted = self.format_indian_plate(full_text)
        
        return formatted if len(formatted) >= 6 else None
    
    def process_video(self, video_path, save_video=False, max_frames=None):
        """Process video for license plate detection"""
        print(f"\n📹 Processing video: {Path(video_path).name}")
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"❌ Error opening video: {video_path}")
            return
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if max_frames:
            total_frames = min(total_frames, max_frames)
        
        print(f"📊 Video: {width}x{height} @ {fps}fps, {total_frames} frames")
        
        # Video writer
        output_video = None
        if save_video:
            output_dir = Path("outputs/vehicle_data")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            video_name = Path(video_path).stem
            output_path = output_dir / f"{video_name}_indian_plates.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            output_video = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            print(f"💾 Saving annotated video to: {output_path}")
        
        # Stats
        frame_count = 0
        plates_detected = 0
        plates_extracted = 0
        self.detected_plates = {}
        
        print("\n🔄 Processing frames...")
        
        start_time = datetime.now()
        
        while cap.isOpened() and (max_frames is None or frame_count < max_frames):
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # YOLO detection
            results = self.model(frame, conf=0.25, verbose=False)
            
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Get coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    
                    if conf > 0.25:
                        plates_detected += 1
                        
                        # Draw bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        # Extract text
                        plate_text = self.extract_plate_text(frame, x1, y1, x2, y2)
                        
                        if plate_text:
                            plates_extracted += 1
                            
                            # Store plate
                            if plate_text not in self.detected_plates:
                                self.detected_plates[plate_text] = {
                                    'count': 1,
                                    'first_frame': frame_count,
                                    'confidence': conf
                                }
                            else:
                                self.detected_plates[plate_text]['count'] += 1
                            
                            # Draw text
                            cv2.putText(frame, plate_text, (x1, y1 - 10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            
                            print(f"  ✅ Frame {frame_count}: {plate_text} (conf: {conf:.2f})")
                        else:
                            cv2.putText(frame, f"Plate (conf: {conf:.2f})", (x1, y1 - 10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            # Write frame
            if output_video:
                output_video.write(frame)
            
            # Progress update
            if frame_count % 30 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"  ⏳ Progress: {frame_count}/{total_frames} ({progress:.1f}%) - "
                      f"Plates: {plates_detected}, Extracted: {plates_extracted}")
        
        # Cleanup
        cap.release()
        if output_video:
            output_video.release()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Save results
        output_dir = Path("outputs/vehicle_data")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        video_name = Path(video_path).stem
        json_path = output_dir / f"{video_name}_indian_plates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        results_data = {
            'video': str(video_path),
            'frames_processed': frame_count,
            'plates_detected': plates_detected,
            'plates_extracted': plates_extracted,
            'unique_plates': len(self.detected_plates),
            'processing_time_seconds': duration,
            'detected_plates': self.detected_plates,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(json_path, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ PROCESSING COMPLETE!")
        print("=" * 70)
        print(f"⏱️  Time: {duration:.2f}s")
        print(f"📊 Frames: {frame_count}")
        print(f"🚗 Plates detected: {plates_detected}")
        print(f"📝 Plates extracted: {plates_extracted}")
        print(f"🎯 Unique plates: {len(self.detected_plates)}")
        print(f"💾 Results saved to: {json_path}")
        
        if self.detected_plates:
            print("\n📋 Detected License Plates:")
            sorted_plates = sorted(self.detected_plates.items(), 
                                  key=lambda x: x[1]['count'], reverse=True)
            for plate, info in sorted_plates[:10]:  # Top 10
                print(f"  • {plate}: {info['count']} times (first: frame {info['first_frame']})")
        
        print("=" * 70)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Indian License Plate Recognition')
    parser.add_argument('--video', type=str, required=True, help='Path to video file')
    parser.add_argument('--model', type=str, 
                       default='../License-Plate-Extraction-Save-Data-to-SQL-Database/weights/best.pt',
                       help='Path to license plate YOLO model')
    parser.add_argument('--save-video', action='store_true', help='Save annotated video')
    parser.add_argument('--max-frames', type=int, help='Maximum frames to process')
    
    args = parser.parse_args()
    
    # Initialize recognizer
    recognizer = IndianLicensePlateRecognizer(model_path=args.model)
    
    # Process video
    recognizer.process_video(args.video, save_video=args.save_video, max_frames=args.max_frames)


if __name__ == "__main__":
    main()
