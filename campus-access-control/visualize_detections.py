"""
Visualize which ID cards were auto-detected in the training data
"""

import cv2
import numpy as np
from pathlib import Path
import json


def detect_and_visualize(image_path):
    """
    Detect ID card and draw bounding box
    """
    image = cv2.imread(str(image_path))
    if image is None:
        return None
    
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
                best_bbox = (x, y, w_box, h_box)
    
    if best_bbox:
        x, y, w_box, h_box = best_bbox
        cv2.rectangle(image, (x, y), (x + w_box, y + h_box), (0, 255, 0), 3)
        cv2.putText(image, "ID CARD DETECTED", (x, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    return image


def main():
    """
    Process all training images and show detections
    """
    training_dir = Path("data/training_data")
    output_dir = Path("id_card_dataset/detections_preview")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("📸 ID CARD DETECTION VISUALIZER")
    print("=" * 70)
    
    image_files = list(training_dir.glob("*.jpg")) + \
                 list(training_dir.glob("*.png")) + \
                 list(training_dir.glob("*.jpeg"))
    
    print(f"\n✅ Found {len(image_files)} images")
    print(f"📁 Output: {output_dir}")
    
    detected = 0
    not_detected = 0
    
    for img_path in image_files:
        result = detect_and_visualize(img_path)
        
        if result is not None:
            output_path = output_dir / img_path.name
            cv2.imwrite(str(output_path), result)
            
            # Check if detected
            has_detection = "ID CARD" in str(result)
            if has_detection:
                detected += 1
                status = "✅"
            else:
                not_detected += 1
                status = "❌"
            
            print(f"{status} {img_path.name}")
    
    print(f"\n📊 Detection Summary:")
    print(f"   Detected: {detected}")
    print(f"   Not detected: {not_detected}")
    print(f"   Success rate: {detected / len(image_files) * 100:.1f}%")
    print(f"\n💾 Visualizations saved to: {output_dir}")


if __name__ == "__main__":
    main()
