"""
Batch ID Card Processor
Processes all images in training_data folder and generates comprehensive JSON output
Extracts: Moodle ID, Name, Department (filters out unwanted text)
"""

import cv2
import numpy as np
import easyocr
import re
import json
import os
from pathlib import Path
from datetime import datetime
import torch

class BatchIDCardProcessor:
    def __init__(self):
        """Initialize the batch processor"""
        print("=" * 70)
        print("📦 BATCH ID CARD PROCESSOR")
        print("=" * 70)
        
        # Device setup
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🔧 Device: {self.device.upper()}")
        
        if self.device == 'cuda':
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        
        # Initialize EasyOCR
        print("📝 Initializing EasyOCR...")
        self.reader = easyocr.Reader(['en'], gpu=True if self.device == 'cuda' else False)
        print("✅ EasyOCR ready")
        
        # Unwanted text patterns (case-insensitive)
        self.unwanted_keywords = [
            'parshvanalh', 'charitable', 'trust', 'shah', 'institute', 
            'technology', 'thane', 'academic', 'year', '2025', '2026',
            'principal', 'photo', 'id no', 'signature', ':', 'a.p.'
        ]
        
        # Invalid name patterns (cannot be names)
        self.invalid_name_patterns = [
            'apsit', 'engineering', 'comp', 'engineer', 'technology',
            'institute', 'department', 'mech', 'civil', 'elect',
            'principal', 'charitable', 'trust', 'address', 'addross'
        ]
        
        # Valid department mappings (correct spelling)
        self.valid_departments = {
            'computer': 'COMPUTER ENGINEERING',
            'mechanical': 'MECHANICAL ENGINEERING', 
            'civil': 'CIVIL ENGINEERING',
            'electrical': 'ELECTRICAL ENGINEERING',
            'electronics': 'ELECTRONICS ENGINEERING',
            'information': 'INFORMATION TECHNOLOGY',
            'it': 'INFORMATION TECHNOLOGY'
        }
        
        # Department keywords
        self.department_keywords = [
            'computer', 'mechanical', 'civil', 'electrical', 
            'electronics', 'information', 'engineering'
        ]
        
        print("=" * 70)
    
    def is_unwanted_text(self, text):
        """Check if text should be filtered out"""
        text_lower = text.lower().strip()
        
        # Empty or too short
        if len(text_lower) < 2:
            return True
        
        # Check unwanted keywords
        for keyword in self.unwanted_keywords:
            if keyword in text_lower:
                return True
        
        # Single characters or digits only
        if len(text_lower) <= 2 and (text_lower.isdigit() or text_lower.isalpha()):
            return True
        
        return False
    
    def normalize_department(self, text):
        """Normalize department name to standard format"""
        text_lower = text.lower()
        
        # Check each department keyword and return standardized name
        for keyword, standard_name in self.valid_departments.items():
            if keyword in text_lower:
                return standard_name
        
        # If no match found, check if it has "engineering" and try to fix typos
        if 'engineer' in text_lower or 'engin' in text_lower:
            # Try to detect department type
            if 'compu' in text_lower or 'comp' in text_lower:
                return 'COMPUTER ENGINEERING'
            elif 'mech' in text_lower:
                return 'MECHANICAL ENGINEERING'
            elif 'civil' in text_lower:
                return 'CIVIL ENGINEERING'
            elif 'elect' in text_lower:
                return 'ELECTRICAL ENGINEERING'
            elif 'electron' in text_lower:
                return 'ELECTRONICS ENGINEERING'
            elif 'info' in text_lower or 'it' in text_lower:
                return 'INFORMATION TECHNOLOGY'
        
        # Return None if cannot normalize
        return None
    
    def is_department(self, text):
        """Check if text is a department name"""
        text_lower = text.lower()
        
        # Must contain engineering-related keywords
        if 'engineering' in text_lower or 'engineer' in text_lower or 'engin' in text_lower:
            # Check for specific departments
            for dept in self.department_keywords:
                if dept in text_lower:
                    return True
        
        return False
    
    def extract_moodle_id(self, text):
        """Extract Moodle ID (8 digits starting with 2)"""
        # Pattern: 2 followed by 7 digits
        pattern = r'\b2\d{7}\b'
        matches = re.findall(pattern, text)
        
        if matches:
            return matches[0]
        
        return None
    
    def is_likely_name(self, text):
        """Check if text is likely a person's name"""
        text_clean = text.strip().upper()
        text_lower = text_clean.lower()
        
        # Must be alphabetic (allow spaces)
        if not all(c.isalpha() or c.isspace() for c in text_clean):
            return False
        
        # Length check (names are typically 6-30 characters)
        if len(text_clean) < 6 or len(text_clean) > 30:
            return False
        
        # Must not be unwanted text
        if self.is_unwanted_text(text_clean):
            return False
        
        # Must not be a department
        if self.is_department(text_clean):
            return False
        
        # Check for invalid name patterns (APSIT, COMP, ENGINEERING, etc.)
        for invalid_pattern in self.invalid_name_patterns:
            if invalid_pattern in text_lower:
                return False
        
        # Must contain at least one space (first + last name) OR be > 8 chars
        # This filters out single words like "COMP", "APSIT"
        if ' ' not in text_clean and len(text_clean) < 8:
            return False
        
        # Additional check: if it's all one word, it should look like a proper name
        # (not abbreviations like "COMP" or institutional names like "APSIT")
        words = text_clean.split()
        if len(words) == 1:
            # Single word - must be at least 8 chars and not contain numbers
            if len(words[0]) < 8:
                return False
        
        # Check if it contains common name patterns
        # Names typically have vowels in reasonable proportions
        vowel_count = sum(1 for c in text_lower if c in 'aeiou')
        if len(text_clean) > 0 and vowel_count / len(text_clean) < 0.2:
            # Less than 20% vowels - likely not a name (e.g., "COMP", "MECH")
            return False
        
        return True
    
    def detect_card_opencv(self, image):
        """Detect ID card using OpenCV edge detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Blur and edge detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Find largest rectangular contour
        best_contour = None
        max_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 5000:  # Minimum area threshold
                continue
            
            # Approximate contour to polygon
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            # Check if it's roughly rectangular (4-6 vertices)
            if len(approx) >= 4 and area > max_area:
                max_area = area
                best_contour = contour
        
        if best_contour is not None:
            x, y, w, h = cv2.boundingRect(best_contour)
            
            # Aspect ratio check (ID cards are typically 1.5:1 to 1.8:1)
            aspect_ratio = w / h if h > 0 else 0
            if 1.3 <= aspect_ratio <= 2.0:
                return (x, y, w, h)
        
        return None
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        # Sharpen
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        return sharpened
    
    def process_single_image(self, image_path):
        """Process a single ID card image"""
        result = {
            'image_path': str(image_path),
            'filename': os.path.basename(image_path),
            'moodle_id': None,
            'name': None,
            'department': None,
            'card_detected': False,
            'all_text_found': [],
            'confidence_scores': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Read image
            image = cv2.imread(str(image_path))
            if image is None:
                result['error'] = 'Failed to read image'
                return result
            
            # Try to detect card
            card_bbox = self.detect_card_opencv(image)
            
            if card_bbox:
                result['card_detected'] = True
                x, y, w, h = card_bbox
                result['card_bbox'] = {'x': x, 'y': y, 'width': w, 'height': h}
                
                # Crop to card region
                card_region = image[y:y+h, x:x+w]
            else:
                # Use full image if card not detected
                card_region = image
            
            # Preprocess for OCR
            preprocessed = self.preprocess_image(card_region)
            
            # Perform OCR
            ocr_results = self.reader.readtext(preprocessed)
            
            # Parse OCR results
            all_text = []
            filtered_text = []
            name_candidates = []
            department_candidates = []
            moodle_id = None
            
            for (bbox, text, confidence) in ocr_results:
                text_clean = text.strip()
                all_text.append({
                    'text': text_clean,
                    'confidence': float(confidence)
                })
                
                # Skip unwanted text
                if self.is_unwanted_text(text_clean):
                    continue
                
                filtered_text.append(text_clean)
                
                # Check for Moodle ID
                found_id = self.extract_moodle_id(text_clean)
                if found_id:
                    moodle_id = found_id
                    result['confidence_scores']['moodle_id'] = float(confidence)
                
                # Check for department
                if self.is_department(text_clean):
                    department_candidates.append((text_clean.upper(), float(confidence)))
                
                # Check for name
                if self.is_likely_name(text_clean):
                    name_candidates.append((text_clean.upper(), float(confidence)))
            
            # Store all text found
            result['all_text_found'] = all_text
            
            # Assign Moodle ID
            result['moodle_id'] = moodle_id
            
            # Assign department (highest confidence)
            if department_candidates:
                department_candidates.sort(key=lambda x: x[1], reverse=True)
                # Normalize department name to fix typos
                normalized_dept = self.normalize_department(department_candidates[0][0])
                if normalized_dept:
                    result['department'] = normalized_dept
                    result['confidence_scores']['department'] = department_candidates[0][1]
                    result['original_department_text'] = department_candidates[0][0]
            
            # Assign name (highest confidence, but exclude department and invalid patterns)
            if name_candidates:
                # Filter out department from name candidates
                name_candidates = [(name, conf) for name, conf in name_candidates 
                                  if not self.is_department(name)]
                
                # Additional validation: re-check with stricter rules
                valid_names = []
                for name, conf in name_candidates:
                    if self.is_likely_name(name):
                        valid_names.append((name, conf))
                
                if valid_names:
                    valid_names.sort(key=lambda x: x[1], reverse=True)
                    result['name'] = valid_names[0][0]
                    result['confidence_scores']['name'] = valid_names[0][1]
            
            # Success status
            result['success'] = bool(moodle_id or result['name'] or result['department'])
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
        
        return result
    
    def process_directory(self, directory_path):
        """Process all images in a directory"""
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"❌ Directory not found: {directory_path}")
            return None
        
        # Find all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(directory.glob(f'*{ext}'))
            image_files.extend(directory.glob(f'*{ext.upper()}'))
        
        image_files = sorted(set(image_files))
        
        if not image_files:
            print(f"❌ No images found in: {directory_path}")
            return None
        
        print(f"\n📁 Found {len(image_files)} images")
        print("=" * 70)
        
        # Process each image
        results = []
        successful = 0
        
        for idx, image_path in enumerate(image_files, 1):
            print(f"\n[{idx}/{len(image_files)}] Processing: {image_path.name}")
            
            result = self.process_single_image(image_path)
            results.append(result)
            
            # Print summary
            if result.get('success'):
                successful += 1
                print(f"  ✅ Success")
                if result['moodle_id']:
                    print(f"     🆔 Moodle ID: {result['moodle_id']}")
                if result['name']:
                    print(f"     👤 Name: {result['name']}")
                if result['department']:
                    print(f"     🏢 Department: {result['department']}")
            else:
                print(f"  ⚠️  No data extracted")
                if 'error' in result:
                    print(f"     Error: {result['error']}")
        
        # Summary statistics
        print("\n" + "=" * 70)
        print("📊 PROCESSING SUMMARY")
        print("=" * 70)
        print(f"Total images: {len(image_files)}")
        print(f"Successful: {successful} ({successful/len(image_files)*100:.1f}%)")
        print(f"Failed: {len(image_files) - successful}")
        
        # Field extraction statistics
        moodle_count = sum(1 for r in results if r.get('moodle_id'))
        name_count = sum(1 for r in results if r.get('name'))
        dept_count = sum(1 for r in results if r.get('department'))
        
        print(f"\nField Extraction:")
        print(f"  🆔 Moodle ID: {moodle_count}/{len(image_files)} ({moodle_count/len(image_files)*100:.1f}%)")
        print(f"  👤 Name: {name_count}/{len(image_files)} ({name_count/len(image_files)*100:.1f}%)")
        print(f"  🏢 Department: {dept_count}/{len(image_files)} ({dept_count/len(image_files)*100:.1f}%)")
        
        return results
    
    def save_results(self, results, output_path):
        """Save results to JSON file"""
        try:
            # Create output directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Save JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Results saved to: {output_path}")
            
            # Also create a summary CSV
            csv_path = output_path.replace('.json', '_summary.csv')
            self.save_summary_csv(results, csv_path)
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
            return False
    
    def save_summary_csv(self, results, csv_path):
        """Save a summary CSV for easy viewing"""
        try:
            import csv
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow(['Filename', 'Moodle ID', 'Name', 'Department', 
                               'Card Detected', 'Success', 'ID Confidence', 
                               'Name Confidence', 'Dept Confidence'])
                
                # Data rows
                for result in results:
                    writer.writerow([
                        result['filename'],
                        result.get('moodle_id', ''),
                        result.get('name', ''),
                        result.get('department', ''),
                        'Yes' if result.get('card_detected') else 'No',
                        'Yes' if result.get('success') else 'No',
                        f"{result.get('confidence_scores', {}).get('moodle_id', 0):.2f}",
                        f"{result.get('confidence_scores', {}).get('name', 0):.2f}",
                        f"{result.get('confidence_scores', {}).get('department', 0):.2f}"
                    ])
            
            print(f"📊 Summary CSV saved to: {csv_path}")
            
        except Exception as e:
            print(f"⚠️  Could not save CSV: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch Process ID Card Images')
    parser.add_argument('--input', type=str, default='data/training_data',
                       help='Input directory with images (default: data/training_data)')
    parser.add_argument('--output', type=str, default='outputs/id_card_data/batch_results.json',
                       help='Output JSON file (default: outputs/id_card_data/batch_results.json)')
    
    args = parser.parse_args()
    
    # Create processor
    processor = BatchIDCardProcessor()
    
    # Process directory
    results = processor.process_directory(args.input)
    
    if results:
        # Save results
        processor.save_results(results, args.output)
        
        print("\n" + "=" * 70)
        print("✅ BATCH PROCESSING COMPLETE")
        print("=" * 70)
    else:
        print("\n❌ Batch processing failed")


if __name__ == "__main__":
    main()
