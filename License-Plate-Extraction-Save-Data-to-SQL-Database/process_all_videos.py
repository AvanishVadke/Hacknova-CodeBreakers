"""
Process all videos in the data folder and save output to output/videos
"""
import os
import json
import cv2
from ultralytics import YOLO
import numpy as np
import math
import re
import sqlite3
from datetime import datetime
import easyocr
import torch
import glob

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Check GPU availability
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"🚀 Using device: {device}")
if device == 'cuda':
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print(f"   CUDA Version: {torch.version.cuda}")

# Create output folder
output_folder = "output/videos"
os.makedirs(output_folder, exist_ok=True)
os.makedirs("json", exist_ok=True)

# Initialize models once
print("⏳ Initializing YOLO model...")
model = YOLO("weights/best.pt")
model.to(device)

print("⏳ Initializing EasyOCR...")
reader = easyocr.Reader(['en'], gpu=True if device == 'cuda' else False)
print(f"✅ Models initialized with GPU: {device == 'cuda'}")

# Class Names
className = ["License"]

def extract_text(frame, x1, y1, x2, y2):
    """Extract text from license plate region using EasyOCR"""
    roi = frame[y1:y2, x1:x2]
    results = reader.readtext(roi, detail=1)
    
    text = ""
    for (bbox, detected_text, confidence) in results:
        if confidence > 0.6:
            text += detected_text + " "
    
    text = text.strip()
    pattern = re.compile('[\W_]')
    text = pattern.sub('', text)
    text = text.replace("O", "0")
    
    return str(text)

def save_json(license_plates, startTime, endTime, video_name):
    """Save detected plates to JSON"""
    interval_data = {
        "Video": video_name,
        "Start Time": startTime.isoformat(),
        "End Time": endTime.isoformat(),
        "License Plates": list(license_plates)
    }
    
    interval_file = f"json/output_{video_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    with open(interval_file, 'w') as f:
        json.dump(interval_data, f, indent=2)
    
    cumulative_file = "json/LicensePlateData.json"
    if os.path.exists(cumulative_file):
        with open(cumulative_file, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []
    
    existing_data.append(interval_data)
    
    with open(cumulative_file, 'w') as f:
        json.dump(existing_data, f, indent=2)

def save_to_database(license_plates, start_time, end_time, video_name):
    """Save to SQLite database"""
    conn = sqlite3.connect('licensePlatesDatabase.db')
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS LicensePlates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_name TEXT,
            start_time TEXT,
            end_time TEXT,
            license_plate TEXT
        )
    ''')
    
    for plate in license_plates:
        cursor.execute('''
            INSERT INTO LicensePlates(video_name, start_time, end_time, license_plate)
            VALUES (?, ?, ?, ?)
        ''', (video_name, start_time.isoformat(), end_time.isoformat(), plate))
    
    conn.commit()
    conn.close()

def process_video(video_path):
    """Process a single video file"""
    video_name = os.path.basename(video_path)
    print(f"\n{'='*60}")
    print(f"📹 Processing: {video_name}")
    print(f"{'='*60}")
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Error: Could not open video {video_path}")
        return
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Create video writer
    output_name = video_name.replace('.mp4', '_processed.mp4')
    output_path = os.path.join(output_folder, output_name)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"   Resolution: {width}x{height}")
    print(f"   FPS: {fps}")
    print(f"   Total Frames: {total_frames}")
    print(f"   Output: {output_path}")
    
    startTime = datetime.now()
    license_plates = set()
    count = 0
    
    while True:
        ret, frame = cap.read()
        if ret:
            currentTime = datetime.now()
            count += 1
            
            if count % 30 == 0:  # Print every 30 frames
                progress = (count / total_frames) * 100 if total_frames > 0 else 0
                print(f"   Progress: {count}/{total_frames} frames ({progress:.1f}%)")
            
            # Run YOLO detection
            results = model.predict(frame, conf=0.45, device=device, verbose=False)
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # Draw rectangle
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    
                    # Extract text
                    label = extract_text(frame, x1, y1, x2, y2)
                    if label:
                        license_plates.add(label)
                    
                    # Draw label
                    textSize = cv2.getTextSize(label, 0, fontScale=0.5, thickness=2)[0]
                    c2 = x1 + textSize[0], y1 - textSize[1] - 3
                    cv2.rectangle(frame, (x1, y1), c2, (255, 0, 0), -1)
                    cv2.putText(frame, label, (x1, y1 - 2), 0, 0.5, [255, 255, 255], 
                               thickness=1, lineType=cv2.LINE_AA)
            
            # Save every 20 seconds
            if (currentTime - startTime).seconds >= 20:
                endTime = currentTime
                save_json(license_plates, startTime, endTime, video_name)
                save_to_database(license_plates, startTime, endTime, video_name)
                startTime = currentTime
                license_plates.clear()
            
            # Write frame to output video
            out.write(frame)
        else:
            break
    
    # Save any remaining plates
    if license_plates:
        endTime = datetime.now()
        save_json(license_plates, startTime, endTime, video_name)
        save_to_database(license_plates, startTime, endTime, video_name)
    
    cap.release()
    out.release()
    
    print(f"   ✅ Complete! Processed {count} frames")
    print(f"   💾 Output saved to: {output_path}")

def main():
    """Process all videos in data folder"""
    video_files = glob.glob("data/*.mp4") + glob.glob("data/*.avi") + glob.glob("data/*.mov")
    
    if not video_files:
        print("❌ No video files found in data/ folder")
        return
    
    print(f"\n🎬 Found {len(video_files)} video(s) to process")
    
    for video_path in video_files:
        try:
            process_video(video_path)
        except Exception as e:
            print(f"❌ Error processing {video_path}: {str(e)}")
            continue
    
    print(f"\n{'='*60}")
    print("🎉 All videos processed!")
    print(f"{'='*60}")
    print(f"📁 Processed videos saved to: {output_folder}/")
    print(f"💾 Database: licensePlatesDatabase.db")
    print(f"📄 JSON files: json/")

if __name__ == "__main__":
    main()
