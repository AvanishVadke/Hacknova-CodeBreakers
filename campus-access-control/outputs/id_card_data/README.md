# Batch ID Card Processing Results

## 📋 Overview

This directory contains the results from batch processing **60 ID card images** from the `data/training_data` folder.

## 📊 Processing Statistics

- **Total Images**: 60
- **Successfully Processed**: 58 (96.7%)
- **Failed**: 2 (3.3%)

### Field Extraction Success Rates:
- 🆔 **Moodle ID**: 44/60 (73.3%)
- 👤 **Name**: 58/60 (96.7%)
- 🏢 **Department**: 16/60 (26.7%)
- ✨ **Complete Records** (all 3 fields): 16/60 (26.7%)

### Average Confidence Scores:
- 🆔 **Moodle ID**: 86.95%
- 👤 **Name**: 81.82%
- 🏢 **Department**: 82.92%

## 📁 Files Generated

### 1. `batch_results.json`
Complete JSON output with all extracted data for each image.

**Structure**:
```json
{
  "image_path": "data/training_data/avanish.jpg",
  "filename": "avanish.jpg",
  "moodle_id": "22102003",
  "name": "AVANISH VADKE",
  "department": "COMPUTER ENGINEERING",
  "card_detected": false,
  "all_text_found": [
    {
      "text": "AVANISH VADKE",
      "confidence": 0.84
    }
  ],
  "confidence_scores": {
    "moodle_id": 0.66,
    "name": 0.84,
    "department": 1.00
  },
  "timestamp": "2025-10-04T09:58:13.878506",
  "success": true
}
```

### 2. `batch_results_summary.csv`
Easy-to-view spreadsheet format with key fields.

**Columns**:
- Filename
- Moodle ID
- Name
- Department
- Card Detected (Yes/No)
- Success (Yes/No)
- ID Confidence
- Name Confidence
- Dept Confidence

## 🎯 Complete Records (All 3 Fields)

The following 16 images have **complete data** (Moodle ID + Name + Department):

1. **avanish.jpg**: 22102003 - AVANISH VADKE - COMPUTER ENGINEERING
2. **harsh.jpg**: 24102107 - HARSH DORLE - COMPUTER ENGINEERING
3. **ishan.jpg**: 24102083 - ISHAN YELVANKAR - COMPUTER ENGINEERING
4. **lucky.jpg**: 22102121 - THAKE - COMPUTER ENGINEERING
5. **manthan.jpg**: 22102124 - MANTHAN SHINDE - COMPUTER ENGINEERING
6. **mohika.jpg**: 22102164 - MOHIKA SONDKAR - COMPUTER ENGINEERING
7. **WhatsApp Image...35fef6d0.jpg**: 22102052 - VISHESH YADAV - COMPUTER ENGINEERING
8. **WhatsApp Image...4f84dabb.jpg**: 23102215 - VEDANT SHINDE - COMPUTER ENGINEERING
9. **WhatsApp Image...39f98e96.jpg**: 25202015 - [NAME] - COMPUTER ENGINEERING
10. **WhatsApp Image...f6a0a1f6.jpg**: 24102142 - AJINKYA PATIL - COMPUTER ENGINEERING
11. **WhatsApp Image...4cfbd1da.jpg**: 24102020 - AVINASH YADAV - COMPUTER ENGINEERING
12. **WhatsApp Image...1dcfef36.jpg**: 23102058 - ARPIT CHOPDA - COMPUTER ENGINEERING
13. **WhatsApp Image...acbacee5.jpg**: 24105012 - ARJAV PATIL - MECHANICAL ENGINEERING
14. **WhatsApp Image...b58a230b.jpg**: 24102155 - ANURAG BIDGAR - COMPUTER ENGINEERING
15. **WhatsApp Image...26f7161a.jpg**: 24102027 - AADESH VISHWASRAO - COMPUTER ENGINEERING
16. **WhatsApp Image...ac68851a.jpg**: 24102098 - DAKSHVAGRECHA - COMPUTER ENGINEERING

## 🔍 Viewing Results

### Method 1: CSV File (Excel/Spreadsheet)
Open `batch_results_summary.csv` in Excel or any spreadsheet application.

### Method 2: JSON Viewer Script
```bash
# View full details
python view_batch_results.py

# View summary only
python view_batch_results.py --summary
```

### Method 3: Direct JSON Access
```python
import json

with open('outputs/id_card_data/batch_results.json', 'r') as f:
    results = json.load(f)

# Access specific image
avanish_data = next(r for r in results if r['filename'] == 'avanish.jpg')
print(avanish_data['moodle_id'])  # 22102003
```

## 📝 Fields Extracted

### ✅ Extracted Fields (Wanted):
- **Moodle ID**: 8-digit number starting with 2 (e.g., 22102003)
- **Name**: Student's full name (e.g., AVANISH VADKE)
- **Department**: Department name (e.g., COMPUTER ENGINEERING)

### ❌ Filtered Fields (Unwanted):
- Institute name (A.P. Shah Institute)
- Academic year (2025-26)
- Principal name/signature
- "Photo", "ID NO::", "Signature"
- Charitable trust information

## 🎨 Processing Details

### OCR Engine
- **EasyOCR** with GPU acceleration (CUDA)
- RTX 3050 6GB GPU utilized

### Detection Methods
1. **YOLO Model** (if available): `models/id_card_best.pt`
2. **OpenCV Fallback**: Edge detection + contour analysis

### Text Parsing
- **Moodle ID**: Regex pattern `\b2\d{7}\b`
- **Name**: Alphabetic text with 4-30 characters, excluding unwanted keywords
- **Department**: Keywords matching "engineering" + department type

## 🚀 Reprocessing

To reprocess all images:
```bash
python batch_process_id_cards.py --input "data/training_data" --output "outputs/id_card_data/batch_results.json"
```

To process a different folder:
```bash
python batch_process_id_cards.py --input "path/to/images" --output "path/to/output.json"
```

## 🐛 Known Issues

### Low Department Detection (26.7%)
**Reason**: Many images have poor quality or the department text is on the back of the ID card.

**Solutions**:
1. Capture both sides of ID cards
2. Improve image quality (better lighting, higher resolution)
3. Manual annotation for training data

### OCR Name Errors
Some names are misread due to:
- Poor image quality
- Glare/reflections
- Unusual fonts

**Example Errors**:
- "MNINCINUL" instead of actual name (abhishek.jpg)
- "BHUBHAMSHELAKE" (missing spaces)
- "COMP" extracted as name (truncated text)

## 📈 Improvement Recommendations

1. **Recapture Low-Quality Images**: Images with confidence < 50%
2. **Scan Both Sides**: Some cards have department on back
3. **Better Lighting**: Reduce glare and shadows
4. **Higher Resolution**: 1080p or higher for clearer text
5. **Manual Verification**: Review the 2 failed images and low-confidence results

## 📞 Support

For issues or questions, refer to:
- Main project: `campus-access-control/README.md`
- Training guide: `campus-access-control/ID_CARD_TRAINING_GUIDE.md`
- Batch processor: `campus-access-control/batch_process_id_cards.py`
