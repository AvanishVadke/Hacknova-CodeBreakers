# ID Strap Detector (YOLOv8 + Streamlit)

This project trains a YOLOv8 detector on your Roboflow-exported dataset and provides a Streamlit UI that uses a webcam to detect an ID strap and mark it as "Authorized" when detected.

Structure

idstrap_detector/
├─ data/ceit-id-lace/       # place Roboflow-exported YOLOv8 dataset here
├─ models/                  # trained weights will be copied to models/best.pt
├─ src/
│  ├─ config.py
│  ├─ utils.py
│  ├─ train.py
│  └─ app.py
├─ requirements.txt
└─ README.md

Quickstart

1. Create virtualenv and install:

   python -m venv env; env\Scripts\Activate.ps1; pip install -r requirements.txt

2. Place your Roboflow-exported dataset into `data/ceit-id-lace/` so it contains `data.yaml` and `train/ valid/ test/` directories.

3. (Optional) To download programmatically, set environment variable `ROBOFLOW_API_KEY` and run a small script to download dataset with the Roboflow client.

4. Train:

   python -m src.train --epochs 30 --batch 8

If your `data.yaml` uses relative paths (typical of Roboflow exports), the training script will resolve them automatically so you can keep the folder structure under `data/ceit-id-lace/`.

Example to download using Roboflow (run from project root; make sure ROBOFLOW_API_KEY is set):

```python
from roboflow import Roboflow
import os

rf = Roboflow(api_key=os.environ.get("ROBOFLOW_API_KEY"))
project = rf.workspace("jason-fml5e").project("ceit-id-lace")
version = project.version(1)
dataset = version.download("yolov8")
```

Using a .env file

1. Copy `.env.example` to `.env` and fill in your values (do NOT check `.env` into git).

2. The project includes `src/secrets.py` which will load `.env` (if python-dotenv is installed) or read environment variables. Example:

```python
from src.secrets import SECRETS
print(SECRETS.ROBOFLOW_API_KEY)
```


5. Run Streamlit UI (desktop):

   streamlit run src/app.py

Notes
- Keep your Roboflow API key secret. Do NOT commit it to source control. Use environment variables.
- If you plan to host the app in the browser (Streamlit Cloud), consider switching to `streamlit-webrtc` for camera capture.
