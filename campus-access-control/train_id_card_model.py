"""
Train YOLO Model for ID Card Detection with Data Augmentation
Works with as few as 60 images by using aggressive augmentation
"""

import os
import shutil
from pathlib import Path
import yaml
from ultralytics import YOLO
import argparse


def setup_training_directories():
    """Create necessary directories for training"""
    base_dir = Path("id_card_training")
    
    dirs = [
        base_dir / "images" / "train",
        base_dir / "images" / "val",
        base_dir / "labels" / "train",
        base_dir / "labels" / "val",
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Training directories created")
    return base_dir


def create_dataset_yaml(base_dir):
    """Create dataset YAML configuration"""
    yaml_content = {
        'path': str(base_dir.absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'names': {
            0: 'id_card'
        }
    }
    
    yaml_path = base_dir / "dataset.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False)
    
    print(f"✅ Dataset YAML created: {yaml_path}")
    return yaml_path


def train_with_augmentation(yaml_path, epochs=150, batch_size=8):
    """
    Train YOLO model with aggressive data augmentation
    
    Args:
        yaml_path: Path to dataset YAML
        epochs: Number of training epochs (default 150)
        batch_size: Batch size (default 8)
    """
    print("\n" + "="*70)
    print("🚀 STARTING YOLO TRAINING WITH DATA AUGMENTATION")
    print("="*70)
    
    # Load YOLOv8 nano model (smallest, fastest for RTX 3050)
    model = YOLO('yolov8n.pt')
    
    # Training with aggressive augmentation for small datasets
    results = model.train(
        data=str(yaml_path),
        epochs=epochs,
        imgsz=640,
        batch=batch_size,
        
        # Data Augmentation Parameters (AGGRESSIVE for small dataset)
        hsv_h=0.015,        # Hue variation (0-1)
        hsv_s=0.7,          # Saturation variation (0-1)
        hsv_v=0.4,          # Value/brightness variation (0-1)
        degrees=10,         # Rotation (±degrees)
        translate=0.2,      # Translation (0-1)
        scale=0.9,          # Scale variation (>0)
        shear=0.0,          # Shear (±degrees)
        perspective=0.0005, # Perspective transformation
        flipud=0.0,         # Vertical flip probability
        fliplr=0.5,         # Horizontal flip probability (50%)
        mosaic=1.0,         # Mosaic augmentation (4 images combined)
        mixup=0.15,         # MixUp augmentation
        copy_paste=0.3,     # Copy-paste augmentation
        
        # Training parameters
        patience=50,        # Early stopping patience
        save=True,
        save_period=10,     # Save checkpoint every 10 epochs
        cache=True,         # Cache images for faster training
        device=0,           # Use GPU 0
        workers=4,          # Data loading workers
        project='runs/id_card',
        name='train',
        exist_ok=True,
        pretrained=True,
        optimizer='AdamW',
        verbose=True,
        seed=42,
        deterministic=False,
        single_cls=True,    # Single class detection
        rect=False,
        cos_lr=True,        # Cosine learning rate scheduler
        close_mosaic=10,    # Disable mosaic in last 10 epochs
        amp=True,           # Automatic Mixed Precision
        fraction=1.0,       # Use 100% of dataset
        profile=False,
        freeze=None,
        lr0=0.01,           # Initial learning rate
        lrf=0.01,           # Final learning rate
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3.0,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        box=7.5,            # Box loss gain
        cls=0.5,            # Class loss gain
        dfl=1.5,            # DFL loss gain
        label_smoothing=0.0,
        nbs=64,
        overlap_mask=True,
        mask_ratio=4,
        dropout=0.0,
    )
    
    print("\n" + "="*70)
    print("✅ TRAINING COMPLETE!")
    print("="*70)
    
    # Get best model path
    best_model = Path('runs/id_card/train/weights/best.pt')
    
    if best_model.exists():
        print(f"\n📦 Best model saved at: {best_model}")
        
        # Copy to models directory
        model_dest = Path('models/id_card_best.pt')
        shutil.copy(best_model, model_dest)
        print(f"📋 Model copied to: {model_dest}")
        
        # Show results
        print("\n📊 Training Results:")
        print(f"   - Results: runs/id_card/train/")
        print(f"   - Confusion Matrix: runs/id_card/train/confusion_matrix.png")
        print(f"   - Training Curves: runs/id_card/train/results.png")
        
        return model_dest
    else:
        print("❌ Training failed - best model not found")
        return None


def validate_model(model_path, yaml_path):
    """Validate the trained model"""
    print("\n" + "="*70)
    print("🔍 VALIDATING MODEL")
    print("="*70)
    
    model = YOLO(str(model_path))
    results = model.val(data=str(yaml_path))
    
    print("\n📊 Validation Metrics:")
    print(f"   - mAP50: {results.box.map50:.3f}")
    print(f"   - mAP50-95: {results.box.map:.3f}")
    print(f"   - Precision: {results.box.mp:.3f}")
    print(f"   - Recall: {results.box.mr:.3f}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Train YOLO for ID Card Detection')
    parser.add_argument('--epochs', type=int, default=150, 
                       help='Number of training epochs (default: 150)')
    parser.add_argument('--batch', type=int, default=8,
                       help='Batch size (default: 8)')
    parser.add_argument('--validate', action='store_true',
                       help='Validate model after training')
    
    args = parser.parse_args()
    
    print("="*70)
    print("🎓 YOLO ID CARD DETECTION - TRAINING SETUP")
    print("="*70)
    print("\n📋 INSTRUCTIONS:")
    print("\n1. Prepare your dataset:")
    print("   - Place 60 ID card images in: id_card_training/images/train/")
    print("   - Create YOLO format labels (.txt files) in: id_card_training/labels/train/")
    print("   - Use 80% for training, 20% for validation")
    print("\n2. Label Format (YOLO):")
    print("   Each .txt file should have: <class> <x_center> <y_center> <width> <height>")
    print("   Example: 0 0.5 0.5 0.8 0.9")
    print("   (All values normalized 0-1)")
    print("\n3. Use Roboflow for easy labeling:")
    print("   - Go to https://roboflow.com/")
    print("   - Upload 60 images")
    print("   - Draw boxes around ID cards")
    print("   - Export as 'YOLOv8' format")
    print("   - Download and extract to id_card_training/")
    print("\n" + "="*70)
    
    response = input("\n✅ Have you prepared your dataset? (y/n): ")
    
    if response.lower() != 'y':
        print("\n⚠️  Please prepare your dataset first!")
        print("\n📚 Quick Guide:")
        print("   1. Collect 60 ID card images")
        print("   2. Go to https://roboflow.com/ (free)")
        print("   3. Create new project: 'ID Card Detection'")
        print("   4. Upload images")
        print("   5. Draw boxes around cards")
        print("   6. Export as YOLOv8 format")
        print("   7. Extract to: id_card_training/")
        print("   8. Run this script again")
        return
    
    # Setup directories
    base_dir = setup_training_directories()
    
    # Check if images exist
    train_images = list((base_dir / "images" / "train").glob("*.jpg")) + \
                   list((base_dir / "images" / "train").glob("*.png"))
    
    if len(train_images) == 0:
        print(f"\n❌ No images found in {base_dir / 'images' / 'train'}")
        print("Please add your labeled images first!")
        return
    
    print(f"\n✅ Found {len(train_images)} training images")
    
    # Create dataset YAML
    yaml_path = create_dataset_yaml(base_dir)
    
    # Start training
    print(f"\n🚀 Starting training with {args.epochs} epochs...")
    print(f"📦 Batch size: {args.batch}")
    print(f"🎮 Using GPU: {os.environ.get('CUDA_VISIBLE_DEVICES', '0')}")
    
    model_path = train_with_augmentation(yaml_path, args.epochs, args.batch)
    
    if model_path and args.validate:
        validate_model(model_path, yaml_path)
    
    print("\n" + "="*70)
    print("🎉 ALL DONE!")
    print("="*70)
    print("\n📋 Next Steps:")
    print("   1. Check training results: runs/id_card/train/results.png")
    print("   2. Test model:")
    print("      python id_card_verifier.py --camera --model models/id_card_best.pt")
    print("   3. If accuracy is low, try:")
    print("      - Collect more images (aim for 100+)")
    print("      - Train for more epochs (--epochs 200)")
    print("      - Check label quality")
    print("="*70)


if __name__ == "__main__":
    main()
