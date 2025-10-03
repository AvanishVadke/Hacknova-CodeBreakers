# ID Card Extraction Project - Quick Start

## ✅ Project Created Successfully!

Branch: `id-card-extraction`  
Location: `id-extraction/`

## 📁 Project Structure

```
id-extraction/
├── id_card_extractor.ipynb    # Main Jupyter notebook with full implementation
├── requirements.txt            # Python dependencies
├── README.md                   # Detailed documentation
├── .gitignore                 # Git ignore rules (protects sensitive data)
├── data/                      # Place ID card images here
│   └── README.md
└── output/                    # Extracted photos and CSV/JSON results
    └── README.md
```

## 🎯 What It Does

Extracts from AP Shah College ID Cards:
1. ✅ **Photo** (middle of card)
2. ✅ **Name** (below photo)
3. ✅ **Department** (below name)
4. ✅ **Moodle ID** (8-digit code: 2XXXXXXX at bottom)

Intelligently **ignores**:
- Top ribbon (college name)
- Bottom right (principal's signature)
- Placeholder areas

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd id-extraction
pip install -r requirements.txt
```

### 2. Install Tesseract OCR
**Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki  
**Linux**: `sudo apt-get install tesseract-ocr`  
**Mac**: `brew install tesseract`

### 3. Add ID Card Images
Place your ID card images (JPG/PNG) in the `data/` folder

### 4. Run the Notebook
```bash
jupyter notebook id_card_extractor.ipynb
```

Run all cells sequentially!

## 📊 Features

✅ **Automatic Extraction** - Smart region detection  
✅ **Batch Processing** - Process multiple cards at once  
✅ **OCR with Tesseract** - Accurate text extraction  
✅ **Moodle ID Validation** - Pattern matching (2XXXXXXX)  
✅ **Visualization** - See detected regions  
✅ **Multiple Exports** - CSV, JSON formats  
✅ **Photo Extraction** - Individual student photos saved  

## 📈 Workflow

```
1. Load ID card images from data/
     ↓
2. Detect and extract regions
     ↓
3. Apply OCR to text regions
     ↓
4. Extract and validate Moodle ID
     ↓
5. Save photos to output/
     ↓
6. Generate CSV/JSON with all data
```

## 🔧 Customization

The notebook includes a **region adjustment tool** to fine-tune coordinates:

```python
# Adjust these percentages based on your card layout
REGIONS = {
    'photo': (0.3, 0.2, 0.7, 0.5),
    'name': (0.1, 0.52, 0.9, 0.62),
    'department': (0.1, 0.63, 0.9, 0.73),
    'moodle_id': (0.1, 0.85, 0.6, 0.95),
}
```

## 📦 Output Files

After processing, you'll get:

### In `output/` folder:
- `id_card_data.csv` - All extracted information
- `id_card_data.json` - JSON format
- `[filename]_photo.jpg` - Individual student photos

### Example CSV:
```csv
image_name,name,department,moodle_id,photo_path
card1.jpg,John Doe,Computer Engineering,23456789,output/card1_photo.jpg
card2.jpg,Jane Smith,Electronics,23456790,output/card2_photo.jpg
```

## 🎨 Notebook Features

1. **Setup and Imports** - Install packages and configure
2. **Helper Functions** - Image processing and OCR utilities
3. **Visualization** - See detected regions on cards
4. **Single Card Processing** - Test on one image
5. **Batch Processing** - Process all cards at once
6. **Fine-tuning Tool** - Adjust region coordinates
7. **Export Results** - Save to CSV/JSON

## 💡 Tips

✅ Use **high-resolution** images for best results  
✅ Ensure **good lighting** (no shadows)  
✅ Keep cards **flat** (not tilted)  
✅ Process a **test card first** to verify regions  
✅ Adjust coordinates if layout varies  

## 🐛 Troubleshooting

**Tesseract not found?**
- Set path in notebook: `pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'`

**Poor OCR accuracy?**
- Increase image resolution
- Adjust preprocessing parameters
- Fine-tune region coordinates

**Moodle ID not detected?**
- Verify format is `2XXXXXXX` (8 digits)
- Adjust `moodle_id` region coordinates

## 🔒 Privacy & Security

✅ `.gitignore` configured to **exclude**:
- ID card images in `data/`
- Extracted photos in `output/`
- CSV/JSON files with personal data

Your sensitive data won't be committed to git!

## 📚 Technologies Used

- **OpenCV** - Image processing
- **Pytesseract** - OCR text extraction
- **Pillow** - Image handling
- **NumPy** - Array operations
- **Pandas** - Data management
- **Matplotlib** - Visualization
- **Regex** - Pattern matching for Moodle ID

## 🎓 Use Cases

- Bulk student data extraction
- Database population
- Automated data entry
- Identity verification systems
- Access control integration

## 📞 Support

- Full documentation in `id-extraction/README.md`
- Example code in the Jupyter notebook
- Inline comments explaining each function

---

## Next Steps

1. ✅ Switch to branch: `git checkout id-card-extraction`
2. ✅ Navigate to folder: `cd id-extraction`
3. ✅ Install dependencies: `pip install -r requirements.txt`
4. ✅ Add ID cards to `data/` folder
5. ✅ Open notebook: `jupyter notebook id_card_extractor.ipynb`
6. ✅ Run all cells and extract data!

---

**Branch**: `id-card-extraction`  
**Commit**: `37cf182`  
**Status**: ✅ Ready to use!

Happy extracting! 🎉
