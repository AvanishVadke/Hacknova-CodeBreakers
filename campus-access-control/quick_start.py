"""
Quick Start Script for Campus Access Control System
Helps users get started quickly with the system
"""

import os
import sys
from pathlib import Path

def print_banner():
    print("=" * 70)
    print("🏛️  SMART CAMPUS ACCESS VERIFICATION SYSTEM")
    print("=" * 70)
    print("Quick Start Setup Wizard")
    print("=" * 70)

def check_dependencies():
    print("\n📦 Checking dependencies...")
    
    try:
        import torch
        print(f"  ✅ PyTorch {torch.__version__}")
        
        if torch.cuda.is_available():
            print(f"  ✅ CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            print("  ⚠️  CUDA not available (CPU mode will be used)")
    except ImportError:
        print("  ❌ PyTorch not installed")
        print("     Install: pip install torch torchvision")
        return False
    
    try:
        import cv2
        print(f"  ✅ OpenCV {cv2.__version__}")
    except ImportError:
        print("  ❌ OpenCV not installed")
        print("     Install: pip install opencv-python")
        return False
    
    try:
        import easyocr
        print("  ✅ EasyOCR installed")
    except ImportError:
        print("  ❌ EasyOCR not installed")
        print("     Install: pip install easyocr")
        return False
    
    try:
        from ultralytics import YOLO
        print("  ✅ Ultralytics YOLO installed")
    except ImportError:
        print("  ❌ Ultralytics not installed")
        print("     Install: pip install ultralytics")
        return False
    
    return True

def check_model():
    print("\n🤖 Checking YOLO model...")
    
    model_path = Path("models/best.pt")
    
    if model_path.exists():
        print(f"  ✅ Model found: {model_path}")
        return True
    else:
        print(f"  ❌ Model not found: {model_path}")
        print("\n  Please do one of the following:")
        print("  1. Copy existing model:")
        print("     Copy-Item ..\\License-Plate-Extraction-Save-Data-to-SQL-Database\\weights\\best.pt models\\best.pt")
        print("  2. Train your own model (see models/README.md)")
        print("  3. Download YOLOv8 base model:")
        print("     yolo download model=yolov8s.pt")
        return False

def setup_directories():
    print("\n📁 Setting up directories...")
    
    dirs = [
        "data/videos",
        "data/id_cards",
        "outputs/vehicle_data",
        "outputs/id_card_data",
        "outputs/access_logs",
        "outputs/captured_frames"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_path}")
    
    return True

def show_usage_examples():
    print("\n" + "=" * 70)
    print("📚 USAGE EXAMPLES")
    print("=" * 70)
    
    examples = [
        ("1. Vehicle Plate Recognition (Video)", 
         "python vehicle_plate_recognizer.py --video data/videos/test.mp4 --save-video"),
        
        ("2. Vehicle Plate Recognition (Camera)", 
         "python vehicle_plate_recognizer.py --camera"),
        
        ("3. ID Card Verification (Image)", 
         "python id_card_verifier.py --image data/id_cards/sample.jpg"),
        
        ("4. ID Card Verification (Camera)", 
         "python id_card_verifier.py --camera"),
        
        ("5. Unified System (Single Camera)", 
         "python access_control_system.py --mode single --vehicle-camera 0"),
        
        ("6. Unified System (Dual Camera)", 
         "python access_control_system.py --mode dual --vehicle-camera 0 --id-card-camera 1"),
    ]
    
    for title, command in examples:
        print(f"\n{title}:")
        print(f"  {command}")

def interactive_mode():
    print("\n" + "=" * 70)
    print("🎯 INTERACTIVE MODE")
    print("=" * 70)
    print("\nWhat would you like to do?")
    print("  1. Test Vehicle Plate Recognition (Camera)")
    print("  2. Test ID Card Verification (Camera)")
    print("  3. Run Unified Access Control System")
    print("  4. View Configuration")
    print("  5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        print("\n🚗 Starting Vehicle Plate Recognition...")
        print("Press 'q' to quit, 's' to save detection\n")
        os.system("python vehicle_plate_recognizer.py --camera")
    
    elif choice == "2":
        print("\n🎴 Starting ID Card Verification...")
        print("Press 'q' to quit, 's' to save detection\n")
        os.system("python id_card_verifier.py --camera")
    
    elif choice == "3":
        print("\n🏛️  Starting Unified Access Control System...")
        print("Using single camera mode")
        print("Press '1' for vehicle mode, '2' for ID card mode, 'q' to quit\n")
        os.system("python access_control_system.py --mode single --vehicle-camera 0")
    
    elif choice == "4":
        print("\n⚙️  Viewing Configuration...")
        os.system("python config/config.py")
    
    elif choice == "5":
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    else:
        print("\n❌ Invalid choice. Please try again.")

def main():
    print_banner()
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Setup failed. Please install missing dependencies.")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Step 2: Check model
    model_exists = check_model()
    
    # Step 3: Setup directories
    setup_directories()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SETUP SUMMARY")
    print("=" * 70)
    print(f"  Dependencies: ✅")
    print(f"  Model: {'✅' if model_exists else '❌ (required)'}")
    print(f"  Directories: ✅")
    
    if not model_exists:
        print("\n⚠️  Warning: Model not found. System cannot run without a YOLO model.")
        print("Please follow the instructions above to add a model.")
        sys.exit(1)
    
    print("\n✅ Setup complete! System is ready to use.")
    
    # Show usage examples
    show_usage_examples()
    
    # Ask if user wants interactive mode
    print("\n" + "=" * 70)
    response = input("\nWould you like to try the system now? (y/n): ").strip().lower()
    
    if response == 'y':
        interactive_mode()
    else:
        print("\n📚 Great! Check the README.md for detailed usage instructions.")
        print("💡 Tip: Run this script again to use interactive mode: python quick_start.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting...")
        sys.exit(0)
