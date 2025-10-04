"""
Quick test to verify GPU setup
"""
import torch
from ultralytics import YOLO
import cv2

print("=" * 60)
print("Testing License Plate Detection Setup")
print("=" * 60)

# Test 1: PyTorch GPU
print("\n[1] PyTorch GPU Test:")
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"   Device: {device}")
if device == 'cuda':
    print(f"   GPU: {torch.cuda.get_device_name(0)}")

# Test 2: YOLO Model
print("\n[2] Loading YOLO Model:")
try:
    model = YOLO("weights/best.pt")
    model.to(device)
    print(f"   ✅ Model loaded successfully on {device}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Test Video
print("\n[3] Testing Video Input:")
try:
    cap = cv2.VideoCapture("data/carLicence1.mp4")
    ret, frame = cap.read()
    if ret:
        print(f"   ✅ Video loaded: {frame.shape}")
        cap.release()
    else:
        print("   ❌ Could not read video")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: PaddleOCR (this might take a while first time)
print("\n[4] Testing PaddleOCR:")
try:
    from paddleocr import PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, use_gpu=True, gpu_mem=2000, show_log=False)
    print("   ✅ PaddleOCR initialized with GPU")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ All tests completed!")
print("=" * 60)
print("\nYou can now run: python main.py")
