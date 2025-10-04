"""
Quick ID Card Image Capture Tool
Helps you capture 60 images for YOLO training
"""

import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import json


class ImageCapturer:
    def __init__(self, output_dir="id_card_images", target_count=60):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.target_count = target_count
        self.captured_count = 0
        
        # Load existing count
        self.count_file = self.output_dir / "capture_info.json"
        if self.count_file.exists():
            with open(self.count_file, 'r') as f:
                data = json.load(f)
                self.captured_count = data.get('count', 0)
    
    def save_count(self):
        with open(self.count_file, 'w') as f:
            json.dump({
                'count': self.captured_count,
                'target': self.target_count,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    
    def draw_overlay(self, frame):
        """Draw helpful overlay on frame"""
        h, w = frame.shape[:2]
        overlay = frame.copy()
        
        # Progress bar
        progress = self.captured_count / self.target_count
        bar_width = int(w * 0.8)
        bar_height = 30
        bar_x = int(w * 0.1)
        bar_y = h - 60
        
        # Background
        cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                     (0, 0, 0), -1)
        
        # Progress
        progress_width = int(bar_width * progress)
        color = (0, 255, 0) if progress < 1.0 else (0, 255, 255)
        cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + progress_width, bar_y + bar_height),
                     color, -1)
        
        # Text
        text = f"{self.captured_count}/{self.target_count} images"
        cv2.putText(overlay, text, (bar_x + 10, bar_y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Instructions
        instructions = [
            "SPACE = Capture | Q = Quit | R = Reset Count",
            "Tips: Different angles, lighting, backgrounds",
        ]
        
        for i, text in enumerate(instructions):
            cv2.putText(overlay, text, (10, 30 + i*30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Guide box (where to place ID card)
        guide_x = int(w * 0.3)
        guide_y = int(h * 0.3)
        guide_w = int(w * 0.4)
        guide_h = int(h * 0.4)
        
        cv2.rectangle(overlay, (guide_x, guide_y), (guide_x + guide_w, guide_y + guide_h),
                     (0, 255, 255), 2)
        cv2.putText(overlay, "Place ID card here", (guide_x, guide_y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Blend
        alpha = 0.7
        result = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        return result
    
    def capture(self, camera_index=0):
        """Start capturing images"""
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"❌ Failed to open camera {camera_index}")
            return
        
        print("="*70)
        print("📸 ID CARD IMAGE CAPTURE TOOL")
        print("="*70)
        print(f"\n✅ Camera opened. Target: {self.target_count} images")
        print(f"📁 Saving to: {self.output_dir}")
        print(f"📊 Already captured: {self.captured_count}")
        print("\nControls:")
        print("  - SPACE: Capture image")
        print("  - Q: Quit")
        print("  - R: Reset count")
        print("\nTips for good dataset:")
        print("  1. Capture from different angles (straight, tilted, rotated)")
        print("  2. Different distances (close, medium, far)")
        print("  3. Different lighting (bright, dim, natural, artificial)")
        print("  4. Different backgrounds (desk, wall, hand)")
        print("  5. Get 20-30 different people's ID cards")
        print("="*70)
        
        try:
            while self.captured_count < self.target_count:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                # Draw overlay
                display_frame = self.draw_overlay(frame)
                
                # Show
                cv2.imshow('ID Card Capture Tool', display_frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord(' '):
                    # Capture
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"id_card_{self.captured_count:03d}_{timestamp}.jpg"
                    filepath = self.output_dir / filename
                    
                    cv2.imwrite(str(filepath), frame)
                    self.captured_count += 1
                    self.save_count()
                    
                    print(f"✅ Captured: {filename} ({self.captured_count}/{self.target_count})")
                    
                    # Flash effect
                    white = np.ones_like(frame) * 255
                    cv2.imshow('ID Card Capture Tool', white)
                    cv2.waitKey(50)
                
                elif key == ord('q'):
                    print("\n⚠️  Quitting early...")
                    break
                
                elif key == ord('r'):
                    response = input("\n⚠️  Reset count to 0? (y/n): ")
                    if response.lower() == 'y':
                        self.captured_count = 0
                        self.save_count()
                        print("✅ Count reset to 0")
            
            if self.captured_count >= self.target_count:
                print("\n" + "="*70)
                print("🎉 TARGET REACHED!")
                print("="*70)
                print(f"\n✅ Captured {self.captured_count} images")
                print(f"📁 Saved to: {self.output_dir}")
                print("\n📋 Next Steps:")
                print("  1. Go to https://roboflow.com/")
                print("  2. Create new project: 'ID Card Detection'")
                print(f"  3. Upload all {self.captured_count} images")
                print("  4. Draw boxes around ID cards")
                print("  5. Generate dataset with 3x augmentation")
                print("  6. Export as YOLOv8 format")
                print("  7. Run: python train_id_card_model.py")
                print("="*70)
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print(f"\n✅ Session complete. Total images: {self.captured_count}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Capture images for YOLO training')
    parser.add_argument('--output', type=str, default='id_card_images',
                       help='Output directory (default: id_card_images)')
    parser.add_argument('--count', type=int, default=60,
                       help='Target number of images (default: 60)')
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera index (default: 0)')
    
    args = parser.parse_args()
    
    capturer = ImageCapturer(output_dir=args.output, target_count=args.count)
    capturer.capture(camera_index=args.camera)


if __name__ == "__main__":
    main()
