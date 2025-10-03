import os

# Path to dataset YAML (from Roboflow export) or folder containing data.yaml
DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ceit-id-lace", "data.yaml")

# Where to save trained weights
WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
BEST_WEIGHTS = os.path.join(WEIGHTS_DIR, "best.pt")

# Detection settings
DETECT_CLASS_NAME = "id_card_strap"  # Change if your class name is different
CONFIDENCE_THRESHOLD = 0.45

# Webcam settings
WEBCAM_DEVICE_INDEX = 0
