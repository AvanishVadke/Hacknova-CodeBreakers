"""
Test your trained YOLO model
Quick validation to see if the model can detect your ID card
"""

import cv2
import torch
from ultralytics import YOLO
from pathlib import Path
import argparse


def test_model_camera(model_path, confidence=0.5):
    """
    Test model with camera feed
    
    Args:
        model_path: Path to trained model
        confidence: Detection confidence threshold
    """
    print("="*70)
    print("🧪 TESTING YOLO MODEL")
    print("="*70)
    print(f"📦 Model: {model_path}")
    print(f"🎯 Confidence threshold: {confidence}")
    
    # Load model
    model = YOLO(str(model_path))
    
    if torch.cuda.is_available():
        print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        model.to('cuda')
    else:
        print("💻 Using CPU")
    
    print("\n✅ Model loaded successfully")
    print("="*70)
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Failed to open camera")
        return
    
    print("\n📷 Camera opened. Press 'q' to quit")
    print("\nHold your ID card in front of the camera...")
    
    frame_count = 0
    detection_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Run detection
            results = model(frame, conf=confidence, verbose=False)
            
            # Draw results
            annotated_frame = results[0].plot()
            
            # Count detections
            if len(results[0].boxes) > 0:
                detection_count += 1
            
            # Display stats
            detection_rate = (detection_count / frame_count * 100) if frame_count > 0 else 0
            stats_text = f"Frames: {frame_count} | Detections: {detection_count} | Rate: {detection_rate:.1f}%"
            cv2.putText(annotated_frame, stats_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Show detections info
            if len(results[0].boxes) > 0:
                for i, box in enumerate(results[0].boxes):
                    conf = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                    info_text = f"ID Card {i+1}: {conf*100:.1f}%"
                    y_pos = 60 + i*30
                    cv2.putText(annotated_frame, info_text, (10, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            cv2.imshow('YOLO Model Test', annotated_frame)
            
            # Quit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        print("\n" + "="*70)
        print("📊 TEST RESULTS")
        print("="*70)
        print(f"Total frames processed: {frame_count}")
        print(f"Frames with detection: {detection_count}")
        print(f"Detection rate: {detection_rate:.1f}%")
        
        if detection_rate > 80:
            print("\n✅ EXCELLENT! Model is working very well!")
        elif detection_rate > 60:
            print("\n👍 GOOD! Model is working well.")
        elif detection_rate > 40:
            print("\n⚠️  MODERATE. Consider:")
            print("   - Training for more epochs")
            print("   - Adding more training images")
            print("   - Checking label quality")
        else:
            print("\n❌ LOW detection rate. Recommendations:")
            print("   - Verify labels are correct")
            print("   - Add more diverse training images")
            print("   - Train for 200+ epochs")
            print("   - Check if training loss converged")


def test_model_image(model_path, image_path, confidence=0.5):
    """
    Test model with single image
    
    Args:
        model_path: Path to trained model
        image_path: Path to test image
        confidence: Detection confidence threshold
    """
    print("="*70)
    print("🧪 TESTING YOLO MODEL ON IMAGE")
    print("="*70)
    print(f"📦 Model: {model_path}")
    print(f"🖼️  Image: {image_path}")
    print(f"🎯 Confidence threshold: {confidence}")
    
    # Load model
    model = YOLO(str(model_path))
    
    if torch.cuda.is_available():
        print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        model.to('cuda')
    else:
        print("💻 Using CPU")
    
    # Load image
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"❌ Failed to load image: {image_path}")
        return
    
    print("\n✅ Running detection...")
    
    # Run detection
    results = model(image, conf=confidence, verbose=True)
    
    # Display results
    annotated = results[0].plot()
    
    print("\n" + "="*70)
    print("📊 RESULTS")
    print("="*70)
    print(f"Detections found: {len(results[0].boxes)}")
    
    if len(results[0].boxes) > 0:
        print("\n✅ ID Cards detected:")
        for i, box in enumerate(results[0].boxes):
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            print(f"  {i+1}. Confidence: {conf*100:.1f}% | Bbox: ({x1:.0f}, {y1:.0f}) to ({x2:.0f}, {y2:.0f})")
    else:
        print("\n❌ No ID cards detected")
        print("Try:")
        print("  - Lower confidence: --confidence 0.3")
        print("  - Check if image has ID card")
        print("  - Verify model training completed successfully")
    
    # Show image
    cv2.imshow('Detection Result', annotated)
    print("\nPress any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description='Test trained YOLO model')
    parser.add_argument('--model', type=str, default='models/id_card_best.pt',
                       help='Path to trained model (default: models/id_card_best.pt)')
    parser.add_argument('--camera', action='store_true',
                       help='Test with camera')
    parser.add_argument('--image', type=str,
                       help='Test with single image')
    parser.add_argument('--confidence', type=float, default=0.5,
                       help='Detection confidence threshold (default: 0.5)')
    
    args = parser.parse_args()
    
    model_path = Path(args.model)
    
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        print("\nTrain a model first:")
        print("  python train_id_card_model.py --epochs 150")
        return
    
    if args.camera:
        test_model_camera(model_path, args.confidence)
    elif args.image:
        test_model_image(model_path, args.image, args.confidence)
    else:
        print("❌ Please specify --camera or --image")
        print("\nExamples:")
        print("  python test_model.py --camera")
        print("  python test_model.py --image test.jpg")


if __name__ == "__main__":
    main()
