# AP Shah College ID Card Extractor

Extract useful information from AP Shah College ID cards using OCR and image processing.

## 📋 Extracted Information

1. **Photo** - Student photo (usually in the middle of the card)
2. **Name** - Student name (located below photo)
3. **Department** - Department of Engineering (below name)
4. **Moodle ID** - 8-digit code starting with 2 (format: 2XXXXXXX)

## 🚫 Ignored Regions

- Top ribbon (AP Shah college name)
- Bottom right (Principal's signature)
- Placeholder areas

## 📁 Project Structure

```
id-extraction/
├── id_card_extractor.ipynb    # Main Jupyter notebook
├── data/                       # Place ID card images here
├── output/                     # Extracted photos and results
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🛠️ Setup

### 1. Install Python Packages

```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install and add to PATH
- Or set path in notebook: `pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'`

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**Mac:**
```bash
brew install tesseract
```

### 3. Add ID Card Images

Place your ID card images (JPG or PNG format) in the `data/` folder.

## 🚀 Usage

1. Open the Jupyter notebook:
```bash
jupyter notebook id_card_extractor.ipynb
```

2. Run all cells sequentially

3. The notebook will:
   - Load images from `data/` folder
   - Extract information from each card
   - Save extracted photos to `output/` folder
   - Generate CSV/JSON with all extracted data

## 📊 Output

### Extracted Data (CSV/JSON)
- `output/id_card_data.csv` - All extracted information
- `output/id_card_data.json` - JSON format

### Extracted Photos
- `output/[filename]_photo.jpg` - Individual student photos

## 🎯 Features

- **Automatic Region Detection** - Smart detection of photo, name, department, and ID
- **OCR Text Extraction** - Tesseract-based text recognition
- **Moodle ID Validation** - Pattern matching for 8-digit codes
- **Batch Processing** - Process multiple cards at once
- **Visualization** - See detected regions and results
- **Export Options** - CSV and JSON formats

## 🔧 Fine-tuning

If extraction accuracy is low, you can adjust region coordinates in the notebook:

```python
REGIONS = {
    'photo': (0.3, 0.2, 0.7, 0.5),      # (x1, y1, x2, y2) as percentages
    'name': (0.1, 0.52, 0.9, 0.62),
    'department': (0.1, 0.63, 0.9, 0.73),
    'moodle_id': (0.1, 0.85, 0.6, 0.95),
}
```

Use the `test_region_adjustment()` function to visualize and test new coordinates.

## 📝 Example Output

```csv
image_name,name,department,moodle_id,photo_path
id_card_1.jpg,John Doe,Computer Engineering,23456789,output/id_card_1_photo.jpg
id_card_2.jpg,Jane Smith,Electronics Engineering,23456790,output/id_card_2_photo.jpg
```

## 💡 Tips

1. **Image Quality**: Use high-resolution, well-lit images
2. **Consistent Format**: Works best when all cards have similar layout
3. **Batch Processing**: Process multiple cards at once for efficiency
4. **Region Tuning**: Adjust coordinates if layout varies

## 🐛 Troubleshooting

### Tesseract Not Found
- Ensure Tesseract is installed and in PATH
- Or set the path explicitly in the notebook

### Poor OCR Accuracy
- Increase image resolution
- Adjust preprocessing parameters
- Fine-tune region coordinates

### Moodle ID Not Detected
- Check if the ID format matches `2XXXXXXX`
- Adjust the `moodle_id` region coordinates

## 📚 Dependencies

- OpenCV - Image processing
- Pytesseract - OCR engine
- Pillow - Image handling
- NumPy - Array operations
- Pandas - Data management
- Matplotlib - Visualization

## 🎓 Use Cases

- Bulk student data extraction
- Database population
- Identity verification
- Access control systems
- Attendance management

## 📄 License

MIT License

---

**Branch**: `id-card-extraction`  
**Created for**: AP Shah College ID Card Processing
