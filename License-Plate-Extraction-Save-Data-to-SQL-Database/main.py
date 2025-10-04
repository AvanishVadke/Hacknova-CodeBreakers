#Import All the Required Libraries
import json
import cv2
from ultralytics import YOLO  # Changed from YOLOv10 to YOLO
import numpy as np
import math
import re
import os
import sqlite3
from datetime import datetime
import easyocr
import torch

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Check GPU availability
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"🚀 Using device: {device}")
if device == 'cuda':
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print(f"   CUDA Version: {torch.version.cuda}")

# Create output folder for processed videos
output_folder = "output/videos"
os.makedirs(output_folder, exist_ok=True)

#Create a Video Capture Object
video_path = "data/carLicence1.mp4"
cap = cv2.VideoCapture(video_path)

# Get video properties for output
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Create video writer
video_name = os.path.basename(video_path).replace('.mp4', '_processed.mp4')
output_path = os.path.join(output_folder, video_name)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

print(f"📹 Processing video: {video_path}")
print(f"💾 Output will be saved to: {output_path}")

#Initialize the YOLO Model with GPU (works with both YOLOv8 and YOLOv10 weights)
model = YOLO("weights/best.pt")
model.to(device)  # Move model to GPU

#Initialize the frame count
count = 0

#Class Names
className = ["License"]

#Initialize EasyOCR with GPU support
print("⏳ Initializing EasyOCR (this may take a minute first time)...")
reader = easyocr.Reader(['en'], gpu=True if device == 'cuda' else False)
print(f"✅ EasyOCR initialized with GPU: {device == 'cuda'}")



def paddle_ocr(frame, x1, y1, x2, y2):
    """Extract text from license plate region using EasyOCR"""
    roi = frame[y1:y2, x1:x2]
    results = reader.readtext(roi, detail=1)
    
    text = ""
    for (bbox, detected_text, confidence) in results:
        if confidence > 0.6:  # Only accept high confidence results
            text += detected_text + " "
    
    # Clean up text
    text = text.strip()
    pattern = re.compile('[\W_]')
    text = pattern.sub('', text)
    text = text.replace("O", "0")
    
    return str(text)



def save_json(license_plates, startTime, endTime):
    #Generate individual JSON files for each 20-second interval
    interval_data = {
        "Start Time": startTime.isoformat(),
        "End Time": endTime.isoformat(),
        "License Plate": list(license_plates)
    }
    interval_file_path = "json/output_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".json"
    with open(interval_file_path, 'w') as f:
        json.dump(interval_data, f, indent = 2)

    #Cummulative JSON File
    cummulative_file_path = "json/LicensePlateData.json"
    if os.path.exists(cummulative_file_path):
        with open(cummulative_file_path, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    #Add new intervaal data to cummulative data
    existing_data.append(interval_data)

    with open(cummulative_file_path, 'w') as f:
        json.dump(existing_data, f, indent = 2)

    #Save data to SQL database
    save_to_database(license_plates, startTime, endTime)



def save_to_database(license_plates, start_time, end_time):
    conn = sqlite3.connect('licensePlatesDatabase.db')
    cursor = conn.cursor()
    for plate in license_plates:
        cursor.execute('''
            INSERT INTO LicensePlates(start_time, end_time, license_plate)
            VALUES (?, ?, ?)
        ''', (start_time.isoformat(), end_time.isoformat(), plate))
    conn.commit()
    conn.close()



startTime = datetime.now()
license_plates = set()


while True:
    ret, frame = cap.read()
    if ret:
        currentTime = datetime.now()
        count += 1
        if count % 10 == 0:  # Print every 10 frames to reduce console spam
            print(f"Frame Number: {count}")
        
        # Run prediction on GPU with optimized settings
        results = model.predict(frame, conf=0.45, device=device, verbose=False)
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                classNameInt = int(box.cls[0])
                clsName = className[classNameInt]
                conf = math.ceil(box.conf[0]*100)/100
                #label = f'{clsName}:{conf}'
                label = paddle_ocr(frame, x1, y1, x2, y2)
                if label:
                    license_plates.add(label)
                textSize = cv2.getTextSize(label, 0, fontScale=0.5, thickness=2)[0]
                c2 = x1 + textSize[0], y1 - textSize[1] - 3
                cv2.rectangle(frame, (x1, y1), c2, (255, 0, 0), -1)
                cv2.putText(frame, label, (x1, y1 - 2), 0, 0.5, [255,255,255], thickness=1, lineType=cv2.LINE_AA)
        if (currentTime - startTime).seconds >= 20:
            endTime = currentTime
            save_json(license_plates, startTime, endTime)
            startTime = currentTime
            license_plates.clear()
        
        # Write frame to output video
        out.write(frame)
        
        # Display (optional - comment out if running headless)
        try:
            cv2.imshow("Video", frame)
            if cv2.waitKey(1) & 0xFF == ord('1'):
                break
        except:
            # Headless mode - just process without display
            pass
    else:
        break


    
cap.release()
out.release()  # Release video writer
print("\n✅ Processing complete!")
print(f"📊 Total frames processed: {count}")
print(f"💾 Results saved to: licensePlatesDatabase.db")
print(f"📁 JSON output: json/LicensePlateData.json")
print(f"🎬 Processed video saved to: {output_path}")
