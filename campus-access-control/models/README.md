# YOLO Models for Campus Access Control

This directory should contain the YOLO model weights for:
1. Vehicle license plate detection
2. ID card detection

## 📥 Model Requirements

### Option 1: Use Existing Model (from license-plate project)

If you already have a trained YOLO model from the `License-Plate-Extraction-Save-Data-to-SQL-Database` folder:

```powershell
# Copy the model
Copy-Item ..\License-Plate-Extraction-Save-Data-to-SQL-Database\weights\best.pt models\best.pt
```

### Option 2: Train Your Own Model

#### For Vehicle License Plates:

1. **Collect Dataset**: 
   - Capture 1000+ images of vehicles with visible license plates
   - Include various angles, lighting conditions, distances
   - Indian license plates in different formats

2. **Annotate Dataset**:
   - Use [Roboflow](https://roboflow.com/) or [LabelImg](https://github.com/heartexlabs/labelImg)
   - Draw bounding boxes around license plates
   - Export in YOLO format

3. **Train Model**:
```powershell
# Using Ultralytics YOLOv8
yolo train data=license_plates.yaml model=yolov8n.pt epochs=100 imgsz=640
```

4. **Place Trained Model**:
```powershell
# Copy trained weights
Copy-Item runs\detect\train\weights\best.pt models\best.pt
```

#### For ID Cards:

1. **Collect Dataset**:
   - Capture 500+ images of college/campus ID cards
   - Various angles and orientations
   - Different lighting conditions

2. **Annotate Dataset**:
   - Draw bounding boxes around entire ID card
   - Optionally: Annotate photo region, text regions separately

3. **Train Model**:
```powershell
yolo train data=id_cards.yaml model=yolov8n.pt epochs=100 imgsz=640
```

4. **Place Model**:
```powershell
Copy-Item runs\detect\train2\weights\best.pt models\id_card_best.pt
```

## 📦 Pre-trained Models

If you don't have time to train:

### Option A: Use YOLOv8 Base Model
```powershell
# Download YOLOv8 nano model (smallest, fastest)
yolo download model=yolov8n.pt

# Copy to models folder
Copy-Item yolov8n.pt models\best.pt
```

**Note**: Base model won't work well for specific tasks. Fine-tuning is recommended.

### Option B: Use Pre-trained License Plate Model

Search for publicly available Indian license plate detection models:
- Roboflow Universe: https://universe.roboflow.com/
- GitHub repositories with trained weights

## 🎯 Model Performance Tips

### Choose the Right Model Size:

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| YOLOv8n | 3.2MB | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | Real-time, resource-limited |
| YOLOv8s | 11.2MB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | Balanced speed/accuracy |
| YOLOv8m | 25.9MB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Better accuracy |
| YOLOv8l | 43.7MB | ⚡⚡ | ⭐⭐⭐⭐⭐ | High accuracy |
| YOLOv8x | 68.2MB | ⚡ | ⭐⭐⭐⭐⭐ | Maximum accuracy |

**Recommendation**: Use YOLOv8s or YOLOv8m for campus access control (good balance)

## 🔄 Using Different Models

You can specify different models for vehicle and ID card detection:

```python
# In your code
vehicle_recognizer = VehiclePlateRecognizer(model_path="models/vehicle_best.pt")
id_card_verifier = IDCardVerifier(model_path="models/id_card_best.pt")
```

Or via command line:
```powershell
python vehicle_plate_recognizer.py --model models/vehicle_best.pt --video data/videos/test.mp4
```

## 📊 Model Training Dataset Structure

```
dataset/
├── images/
│   ├── train/
│   │   ├── img001.jpg
│   │   ├── img002.jpg
│   │   └── ...
│   └── val/
│       ├── img100.jpg
│       └── ...
├── labels/
│   ├── train/
│   │   ├── img001.txt
│   │   ├── img002.txt
│   │   └── ...
│   └── val/
│       ├── img100.txt
│       └── ...
└── dataset.yaml
```

### dataset.yaml example:
```yaml
path: ./dataset
train: images/train
val: images/val

names:
  0: license_plate
  # or for ID cards:
  # 0: id_card
```

## ✅ Verify Model

Test your model before deploying:

```powershell
# Test detection on sample image
yolo predict model=models/best.pt source=test_image.jpg

# Check model info
yolo val model=models/best.pt data=dataset.yaml
```

## 🚨 Important Notes

1. **Model Compatibility**: Ensure model is trained with same YOLO version (YOLOv8)
2. **Class Names**: Model class names should match your use case (license_plate, id_card)
3. **GPU Memory**: Larger models need more VRAM (6GB minimum recommended)
4. **Regular Retraining**: Retrain models periodically with new data for better accuracy

## 📚 Resources

- **Ultralytics Docs**: https://docs.ultralytics.com/
- **Training Tutorial**: https://docs.ultralytics.com/modes/train/
- **Model Export**: https://docs.ultralytics.com/modes/export/
- **Roboflow Datasets**: https://universe.roboflow.com/

---

**Need Help?** Check the main README.md or open an issue on GitHub.
