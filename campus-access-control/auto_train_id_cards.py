"""
Automated ID Card Training System
Auto-detects and labels ID cards from images, then trains YOLO model
No manual labeling required for simple rectangular ID cards
"""

import cv2
import numpy as np
from pathlib import Path
import yaml
import shutil
from ultralytics import YOLO
import json
from datetime import datetime


class AutoIDCardTrainer:
    """
    Automated training system for ID card detection
    """
    
    def __init__(self, source_dir="data/training_data", output_dir="id_card_dataset"):
        """
        Initialize trainer
        
        Args:
            source_dir: Directory containing training images
            output_dir: Directory to save processed dataset
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        
        print("=" * 70)
        print("🤖 AUTOMATED ID CARD TRAINING SYSTEM")
        print("=" * 70)
        print(f"📁 Source: {self.source_dir}")
        print(f"📦 Output: {self.output_dir}")
        
        # Create output structure
        self.train_img_dir = self.output_dir / "images" / "train"
        self.train_lbl_dir = self.output_dir / "labels" / "train"
        self.val_img_dir = self.output_dir / "images" / "val"
        self.val_lbl_dir = self.output_dir / "labels" / "val"
        
        for dir_path in [self.train_img_dir, self.train_lbl_dir, 
                        self.val_img_dir, self.val_lbl_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            'total_images': 0,
            'successfully_labeled': 0,
            'failed': 0,
            'train_images': 0,
            'val_images': 0
        }
    
    def detect_id_card_in_image(self, image):
        """
        Auto-detect ID card in image using OpenCV
        
        Args:
            image: Input image (BGR)
            
        Returns:
            tuple: (x_center, y_center, width, height) normalized 0-1, or None
        """
        h, w = image.shape[:2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Dilate edges
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find largest rectangular contour
        best_bbox = None
        max_area = 0
        frame_area = h * w
        
        for contour in contours:
            x, y, w_box, h_box = cv2.boundingRect(contour)
            area = w_box * h_box
            aspect_ratio = w_box / h_box if h_box > 0 else 0
            
            # ID card criteria
            if (0.1 * frame_area < area < 0.9 * frame_area and
                1.2 < aspect_ratio < 2.2 and
                w_box > 150 and h_box > 100):
                
                # Check if rectangular
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                
                if len(approx) >= 4 and area > max_area:
                    max_area = area
                    # Convert to YOLO format (normalized center x, y, width, height)
                    x_center = (x + w_box / 2) / w
                    y_center = (y + h_box / 2) / h
                    width_norm = w_box / w
                    height_norm = h_box / h
                    best_bbox = (x_center, y_center, width_norm, height_norm)
        
        return best_bbox
    
    def create_yolo_label(self, bbox, output_path):
        """
        Create YOLO format label file
        
        Args:
            bbox: Tuple (x_center, y_center, width, height) normalized
            output_path: Path to save label file
        """
        with open(output_path, 'w') as f:
            # Format: class x_center y_center width height
            # class 0 = id_card
            f.write(f"0 {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n")
    
    def process_images(self, split_ratio=0.8):
        """
        Process all images: detect ID cards and create labels
        
        Args:
            split_ratio: Train/validation split (default 0.8 = 80% train, 20% val)
        """
        print("\n📸 Processing images...")
        
        # Get all images
        image_files = list(self.source_dir.glob("*.jpg")) + \
                     list(self.source_dir.glob("*.png")) + \
                     list(self.source_dir.glob("*.jpeg"))
        
        self.stats['total_images'] = len(image_files)
        print(f"✅ Found {self.stats['total_images']} images")
        
        if self.stats['total_images'] == 0:
            print(f"❌ No images found in {self.source_dir}")
            return False
        
        # Process each image
        processed_data = []
        
        for i, img_path in enumerate(image_files, 1):
            print(f"Processing {i}/{self.stats['total_images']}: {img_path.name}...", end=" ")
            
            # Read image
            image = cv2.imread(str(img_path))
            if image is None:
                print("❌ Failed to read")
                self.stats['failed'] += 1
                continue
            
            # Detect ID card
            bbox = self.detect_id_card_in_image(image)
            
            if bbox is None:
                print("⚠️  No ID card detected")
                self.stats['failed'] += 1
                continue
            
            processed_data.append({
                'path': img_path,
                'image': image,
                'bbox': bbox
            })
            
            self.stats['successfully_labeled'] += 1
            print("✅")
        
        if len(processed_data) == 0:
            print("\n❌ No ID cards detected in any image!")
            print("Tips:")
            print("  - Ensure images contain clear ID cards")
            print("  - ID cards should be well-lit and visible")
            print("  - Try manual labeling with Roboflow")
            return False
        
        # Split into train/val
        num_train = int(len(processed_data) * split_ratio)
        train_data = processed_data[:num_train]
        val_data = processed_data[num_train:]
        
        self.stats['train_images'] = len(train_data)
        self.stats['val_images'] = len(val_data)
        
        # Save training data
        print(f"\n💾 Saving training data ({len(train_data)} images)...")
        for i, data in enumerate(train_data):
            img_name = f"train_{i:04d}.jpg"
            lbl_name = f"train_{i:04d}.txt"
            
            cv2.imwrite(str(self.train_img_dir / img_name), data['image'])
            self.create_yolo_label(data['bbox'], self.train_lbl_dir / lbl_name)
        
        # Save validation data
        print(f"💾 Saving validation data ({len(val_data)} images)...")
        for i, data in enumerate(val_data):
            img_name = f"val_{i:04d}.jpg"
            lbl_name = f"val_{i:04d}.txt"
            
            cv2.imwrite(str(self.val_img_dir / img_name), data['image'])
            self.create_yolo_label(data['bbox'], self.val_lbl_dir / lbl_name)
        
        print("✅ Dataset prepared successfully!")
        return True
    
    def create_dataset_yaml(self):
        """
        Create dataset.yaml for YOLO training
        """
        yaml_content = {
            'path': str(self.output_dir.absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'nc': 1,
            'names': ['id_card']
        }
        
        yaml_path = self.output_dir / "dataset.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_content, f, default_flow_style=False)
        
        print(f"✅ Created dataset.yaml: {yaml_path}")
        return yaml_path
    
    def train_model(self, epochs=150, batch_size=8, img_size=640):
        """
        Train YOLO model on the dataset
        
        Args:
            epochs: Number of training epochs
            batch_size: Batch size
            img_size: Input image size
        """
        print("\n" + "=" * 70)
        print("🚀 STARTING MODEL TRAINING")
        print("=" * 70)
        
        # Create dataset.yaml
        yaml_path = self.create_dataset_yaml()
        
        # Load YOLOv8 nano model
        print("\n📦 Loading YOLOv8n model...")
        model = YOLO('yolov8n.pt')
        
        # Train
        print(f"\n🎓 Training for {epochs} epochs...")
        print(f"📊 Batch size: {batch_size}")
        print(f"📐 Image size: {img_size}x{img_size}")
        print(f"🎮 Using GPU: {'Yes' if cv2.cuda.getCudaEnabledDeviceCount() > 0 else 'No'}")
        
        results = model.train(
            data=str(yaml_path),
            epochs=epochs,
            imgsz=img_size,
            batch=batch_size,
            
            # Aggressive augmentation for small dataset
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            degrees=15,
            translate=0.2,
            scale=0.9,
            shear=0.0,
            perspective=0.0005,
            flipud=0.0,
            fliplr=0.5,
            mosaic=1.0,
            mixup=0.15,
            copy_paste=0.3,
            
            # Training settings
            patience=50,
            save=True,
            save_period=10,
            cache=True,
            device=0,
            workers=4,
            project='runs/id_card_training',
            name='train',
            exist_ok=True,
            pretrained=True,
            optimizer='AdamW',
            verbose=True,
            seed=42,
            single_cls=True,
            cos_lr=True,
            close_mosaic=10,
            amp=True,
            lr0=0.01,
            lrf=0.01,
            momentum=0.937,
            weight_decay=0.0005,
        )
        
        print("\n" + "=" * 70)
        print("✅ TRAINING COMPLETE!")
        print("=" * 70)
        
        # Copy best model to models directory
        best_model_path = Path('runs/id_card_training/train/weights/best.pt')
        
        if best_model_path.exists():
            dest_path = Path('models/id_card_best.pt')
            shutil.copy(best_model_path, dest_path)
            print(f"\n📦 Model saved to: {dest_path}")
            
            # Also update the main model
            main_model_path = Path('models/best.pt')
            shutil.copy(best_model_path, main_model_path)
            print(f"📦 Updated main model: {main_model_path}")
            
            return dest_path
        else:
            print("\n⚠️  Training completed but best model not found")
            return None
    
    def test_model(self, model_path):
        """
        Test the trained model on sample images
        
        Args:
            model_path: Path to trained model
        """
        print("\n" + "=" * 70)
        print("🧪 TESTING TRAINED MODEL")
        print("=" * 70)
        
        model = YOLO(str(model_path))
        
        # Test on validation images
        val_images = list(self.val_img_dir.glob("*.jpg"))
        
        if not val_images:
            print("⚠️  No validation images found to test")
            return
        
        print(f"\n📸 Testing on {len(val_images)} validation images...")
        
        detections = 0
        for img_path in val_images[:5]:  # Test on first 5
            image = cv2.imread(str(img_path))
            results = model(image, conf=0.5)
            
            if len(results[0].boxes) > 0:
                detections += 1
                print(f"✅ {img_path.name}: Detected {len(results[0].boxes)} ID card(s)")
            else:
                print(f"❌ {img_path.name}: No detection")
        
        detection_rate = (detections / min(5, len(val_images))) * 100
        print(f"\n📊 Detection rate: {detection_rate:.1f}% ({detections}/{min(5, len(val_images))})")
        
        if detection_rate >= 80:
            print("✅ EXCELLENT! Model is performing well!")
        elif detection_rate >= 60:
            print("👍 GOOD! Model is working.")
        else:
            print("⚠️  LOW detection rate. Consider:")
            print("   - Training for more epochs (--epochs 200)")
            print("   - Adding more diverse training images")
    
    def generate_report(self):
        """
        Generate training report
        """
        print("\n" + "=" * 70)
        print("📊 TRAINING REPORT")
        print("=" * 70)
        print(f"\n📁 Dataset Statistics:")
        print(f"   Total images: {self.stats['total_images']}")
        print(f"   Successfully labeled: {self.stats['successfully_labeled']}")
        print(f"   Failed: {self.stats['failed']}")
        print(f"   Training images: {self.stats['train_images']}")
        print(f"   Validation images: {self.stats['val_images']}")
        
        success_rate = (self.stats['successfully_labeled'] / self.stats['total_images'] * 100) if self.stats['total_images'] > 0 else 0
        print(f"\n✅ Success rate: {success_rate:.1f}%")
        
        # Save report
        report = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'dataset_path': str(self.output_dir),
            'model_path': 'models/id_card_best.pt'
        }
        
        report_path = self.output_dir / 'training_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📝 Report saved: {report_path}")


def main():
    """
    Main training pipeline
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated ID Card Training System')
    parser.add_argument('--source', type=str, default='data/training_data',
                       help='Source directory with training images')
    parser.add_argument('--output', type=str, default='id_card_dataset',
                       help='Output directory for processed dataset')
    parser.add_argument('--epochs', type=int, default=150,
                       help='Number of training epochs')
    parser.add_argument('--batch', type=int, default=8,
                       help='Batch size')
    parser.add_argument('--test', action='store_true',
                       help='Test model after training')
    parser.add_argument('--skip-training', action='store_true',
                       help='Skip training, only process images')
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = AutoIDCardTrainer(
        source_dir=args.source,
        output_dir=args.output
    )
    
    # Step 1: Process images and create labels
    success = trainer.process_images()
    
    if not success:
        print("\n❌ Dataset preparation failed!")
        return
    
    # Step 2: Train model
    if not args.skip_training:
        model_path = trainer.train_model(
            epochs=args.epochs,
            batch_size=args.batch
        )
        
        # Step 3: Test model
        if args.test and model_path:
            trainer.test_model(model_path)
    
    # Step 4: Generate report
    trainer.generate_report()
    
    print("\n" + "=" * 70)
    print("🎉 ALL DONE!")
    print("=" * 70)
    print("\n📋 Next Steps:")
    print("   1. Test your model:")
    print("      python offline_id_card_recognizer.py --camera")
    print("   2. Use in access control:")
    print("      python access_control_system.py --mode single --vehicle-camera 0")
    print("   3. Check training results:")
    print("      - Model: models/id_card_best.pt")
    print("      - Results: runs/id_card_training/train/")
    print("      - Metrics: runs/id_card_training/train/results.png")


if __name__ == "__main__":
    main()
