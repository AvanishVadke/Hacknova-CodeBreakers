# Output Directory

This folder contains the extracted data and photos.

## Generated Files

### Extracted Photos
- `[original_filename]_photo.jpg` - Individual student photos

### Data Files
- `id_card_data.csv` - All extracted information in CSV format
- `id_card_data.json` - All extracted information in JSON format
- `extracted_data.csv` - Temporary extraction results

## CSV Format
```csv
image_name,name,department,moodle_id,photo_path
id_card_1.jpg,John Doe,Computer Engineering,23456789,output/id_card_1_photo.jpg
```

Files are automatically generated when you run the notebook.
