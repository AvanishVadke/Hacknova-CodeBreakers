# YOLOv8 Model Files

## 📥 Model Download

The YOLOv8 model files are **not included in the repository** due to their large size (130MB+).

### Automatic Download (Recommended)

When you first run the detection functions in `ID_identification.ipynb`, the YOLOv8x model will be **automatically downloaded** from the official Ultralytics repository.

```python
# This cell automatically downloads yolov8x.pt on first run
yolo_model = YOLO('yolov8x.pt')
```

**First run output:**
```
Downloading https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8x.pt
to 'yolov8x.pt': 100% ━━━━━━━━━━━━ 130.5MB 34.5MB/s
```

### Manual Download (Optional)

If automatic download fails, you can manually download the model:

1. **Download YOLOv8x:**
   ```bash
   wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8x.pt
   ```
   
   Or visit: https://github.com/ultralytics/assets/releases/tag/v8.3.0

2. **Place in project directory:**
   - Save `yolov8x.pt` in: `id-extraction/yolov8x.pt`

### Alternative Models (Smaller Size)

If you want faster inference or have limited storage:

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| yolov8n.pt | 6MB | Very Fast | Good |
| yolov8s.pt | 22MB | Fast | Better |
| yolov8m.pt | 50MB | Medium | Very Good |
| yolov8l.pt | 87MB | Slow | Excellent |
| yolov8x.pt | 130MB | Very Slow | **Maximum** ✅ |

**To use a different model:**
```python
# Change this line in the notebook
yolo_model = YOLO('yolov8m.pt')  # Use medium model instead
```

## 📁 Model Storage

```
id-extraction/
├── yolov8x.pt              # Auto-downloaded (not in Git)
├── models/                 # Custom models folder (optional)
│   └── *.pt               # Your custom trained models
└── runs/                   # Training runs (not in Git)
    └── detect/
        └── train/
            └── weights/
                └── best.pt
```

## 🚫 Why Not in Git?

GitHub has a **100MB file size limit**. The YOLOv8x model is 130MB, so:
- ✅ Model is downloaded automatically on first run
- ✅ `.gitignore` excludes all `.pt` model files
- ✅ Reduces repository size
- ✅ Always uses the latest model version

## 🔄 Model Updates

To update to the latest model version:

```bash
# Delete old model
rm yolov8x.pt

# Run the notebook again to download latest version
# Or manually download from: https://github.com/ultralytics/ultralytics/releases
```

## 📚 More Information

- [Ultralytics YOLOv8 Models](https://docs.ultralytics.com/models/yolov8/)
- [Model Zoo](https://github.com/ultralytics/ultralytics#models)
- [Custom Training Guide](https://docs.ultralytics.com/modes/train/)

---

**Note**: The model will be downloaded to the same directory as the notebook on first run. This is normal and expected behavior.
