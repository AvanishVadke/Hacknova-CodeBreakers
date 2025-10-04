"""
Configuration file for Campus Access Control System
Handles settings for Indian license plate recognition and ID card verification
"""

import os
from pathlib import Path

# ========================
# PROJECT PATHS
# ========================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "outputs"

# Input directories
VIDEO_DIR = DATA_DIR / "videos"
ID_CARD_DIR = DATA_DIR / "id_cards"

# Output directories
VEHICLE_OUTPUT_DIR = OUTPUT_DIR / "vehicle_data"
ID_CARD_OUTPUT_DIR = OUTPUT_DIR / "id_card_data"
ACCESS_LOG_DIR = OUTPUT_DIR / "access_logs"
CAPTURED_FRAMES_DIR = OUTPUT_DIR / "captured_frames"

# Ensure all directories exist
for directory in [VIDEO_DIR, ID_CARD_DIR, VEHICLE_OUTPUT_DIR, 
                  ID_CARD_OUTPUT_DIR, ACCESS_LOG_DIR, CAPTURED_FRAMES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ========================
# MODEL CONFIGURATIONS
# ========================

# YOLO Model Settings
YOLO_MODEL_PATH = MODEL_DIR / "best.pt"  # Path to trained YOLO model
YOLO_CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for detection
YOLO_IOU_THRESHOLD = 0.45  # IoU threshold for NMS

# EasyOCR Settings
OCR_LANGUAGES = ['en']  # Languages for OCR
OCR_CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence for text recognition
OCR_GPU = True  # Use GPU for OCR

# ========================
# INDIAN LICENSE PLATE PATTERNS
# ========================

# Indian license plate formats:
# Old format: XX-00-XX-0000 (e.g., MH-12-AB-1234)
# New format: XX-00-XX-0000 (e.g., MH-20-BH-0001)
# BH Series: XX-00-BH-0000-X (e.g., 22-BH-1234-A)

INDIAN_PLATE_PATTERNS = [
    r'[A-Z]{2}[-\s]?\d{2}[-\s]?[A-Z]{1,2}[-\s]?\d{4}',  # Standard format
    r'\d{2}[-\s]?BH[-\s]?\d{4}[-\s]?[A-Z]',  # BH Series (Bharat Series)
    r'[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}',  # Without separators
]

# Character corrections for Indian plates
PLATE_CHAR_CORRECTIONS = {
    'O': '0',  # Letter O to number 0
    'I': '1',  # Letter I to number 1
    'S': '5',  # Letter S to number 5 (in numeric sections)
    'Z': '2',  # Letter Z to number 2
    'B': '8',  # Letter B to number 8 (in numeric sections)
    'G': '6',  # Letter G to number 6
}

# Valid state codes for Indian license plates
VALID_STATE_CODES = [
    'AP', 'AR', 'AS', 'BR', 'CG', 'GA', 'GJ', 'HR', 'HP', 'JK', 'JH', 'KA',
    'KL', 'MP', 'MH', 'MN', 'ML', 'MZ', 'NL', 'OD', 'PB', 'RJ', 'SK', 'TN',
    'TS', 'TR', 'UP', 'UK', 'WB', 'AN', 'CH', 'DN', 'DD', 'DL', 'LD', 'PY'
]

# ========================
# ID CARD CONFIGURATIONS
# ========================

# ID Card Region Definitions (percentage of image dimensions)
ID_CARD_REGIONS = {
    'photo': (0.25, 0.15, 0.75, 0.50),      # Photo region (center-top)
    'name': (0.1, 0.52, 0.9, 0.62),         # Name below photo
    'department': (0.1, 0.63, 0.9, 0.73),   # Department below name
    'moodle_id': (0.1, 0.80, 0.7, 0.92),    # Moodle ID at bottom
}

# Moodle ID Pattern (8 digits starting with 2)
MOODLE_ID_PATTERN = r'2\d{7}'

# Valid departments (customize as needed)
VALID_DEPARTMENTS = [
    'Computer Engineering',
    'Information Technology',
    'Electronics and Telecommunication',
    'Mechanical Engineering',
    'Civil Engineering',
    'Electrical Engineering',
    'Artificial Intelligence and Data Science',
    'Computer Science',
]

# ========================
# VIDEO PROCESSING SETTINGS
# ========================

# Frame sampling settings
FRAME_SKIP = 5  # Process every Nth frame (for performance)
MAX_FRAMES_TO_PROCESS = None  # None = process all frames

# Video output settings
SAVE_ANNOTATED_VIDEO = True  # Save video with bounding boxes
VIDEO_OUTPUT_CODEC = 'mp4v'  # Video codec
VIDEO_OUTPUT_FPS = 30  # Output video FPS

# ========================
# CAMERA SETTINGS
# ========================

# Camera configuration
CAMERA_INDEX = 0  # Default camera (0 = built-in webcam)
CAMERA_WIDTH = 1280  # Camera resolution width
CAMERA_HEIGHT = 720  # Camera resolution height
CAMERA_FPS = 30  # Camera FPS

# Capture settings
AUTO_CAPTURE_DELAY = 3  # Seconds between auto-captures
CAPTURE_ON_DETECTION = True  # Auto-capture when object detected

# ========================
# DATABASE SETTINGS
# ========================

# Database file paths
VEHICLE_DB_PATH = OUTPUT_DIR / "vehicle_records.db"
ID_CARD_DB_PATH = OUTPUT_DIR / "student_records.db"
ACCESS_LOG_DB_PATH = OUTPUT_DIR / "access_logs.db"

# ========================
# PERFORMANCE SETTINGS
# ========================

# GPU Settings
USE_GPU = True  # Enable GPU acceleration
GPU_DEVICE = 'cuda'  # CUDA device
CPU_DEVICE = 'cpu'

# Processing settings
BATCH_SIZE = 1  # Batch size for inference
NUM_WORKERS = 2  # Number of worker threads

# ========================
# LOGGING SETTINGS
# ========================

LOG_LEVEL = 'INFO'  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = OUTPUT_DIR / "system.log"

# ========================
# ACCESS CONTROL SETTINGS
# ========================

# Verification thresholds
MIN_PLATE_CONFIDENCE = 0.7  # Minimum confidence for plate detection
MIN_ID_CARD_CONFIDENCE = 0.6  # Minimum confidence for ID card detection
MIN_OCR_CONFIDENCE = 0.6  # Minimum confidence for OCR

# Access decision settings
REQUIRE_BOTH_VERIFICATIONS = True  # Both vehicle and ID must match
ACCESS_TIME_WINDOW = 30  # Seconds within which both verifications must occur
MAX_RETRY_ATTEMPTS = 3  # Maximum verification attempts

# Alert settings
SEND_ALERTS = True  # Enable alert system
ALERT_UNAUTHORIZED_ACCESS = True  # Alert on unauthorized access attempts
ALERT_MULTIPLE_FAILURES = True  # Alert on multiple failed attempts

# ========================
# SYSTEM PARAMETERS
# ========================

# Performance targets (as per problem statement)
TARGET_ACCURACY = 0.95  # 95% accuracy requirement
TARGET_RESPONSE_TIME = 2.0  # 2 seconds max response time
MAX_RECORDS = 5000  # Scalability target: 5000+ records

# Environmental robustness settings
ADAPTIVE_BRIGHTNESS = True  # Adjust for lighting conditions
MOTION_BLUR_THRESHOLD = 50  # Skip frames with high motion blur
MIN_IMAGE_QUALITY = 0.5  # Minimum image quality score

# ========================
# HELPER FUNCTIONS
# ========================

def get_timestamp():
    """Get current timestamp in ISO format"""
    from datetime import datetime
    return datetime.now().isoformat()

def get_date_string():
    """Get current date as string (YYYY-MM-DD)"""
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d')

def get_output_filename(prefix, extension='json'):
    """Generate output filename with timestamp"""
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.{extension}"

# ========================
# PRINT CONFIGURATION
# ========================

if __name__ == "__main__":
    print("=" * 60)
    print("CAMPUS ACCESS CONTROL SYSTEM - CONFIGURATION")
    print("=" * 60)
    print(f"\n📁 Base Directory: {BASE_DIR}")
    print(f"📁 Model Directory: {MODEL_DIR}")
    print(f"📁 Output Directory: {OUTPUT_DIR}")
    print(f"\n🚗 Vehicle Output: {VEHICLE_OUTPUT_DIR}")
    print(f"🎴 ID Card Output: {ID_CARD_OUTPUT_DIR}")
    print(f"📊 Access Logs: {ACCESS_LOG_DIR}")
    print(f"\n🎯 YOLO Confidence: {YOLO_CONFIDENCE_THRESHOLD}")
    print(f"📝 OCR Confidence: {OCR_CONFIDENCE_THRESHOLD}")
    print(f"🔧 GPU Enabled: {USE_GPU}")
    print(f"⚡ Frame Skip: {FRAME_SKIP}")
    print(f"\n✅ Target Accuracy: {TARGET_ACCURACY * 100}%")
    print(f"⏱️  Target Response Time: {TARGET_RESPONSE_TIME}s")
    print("=" * 60)
