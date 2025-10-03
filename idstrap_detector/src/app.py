import streamlit as st
import cv2
import time
import numpy as np
from pathlib import Path
from PIL import Image

# Absolute imports
from config import BEST_WEIGHTS, WEBCAM_DEVICE_INDEX
from utils import load_model, run_inference_on_frame

st.set_page_config(page_title="ID Strap Authenticator")

st.title("🎥 ID Strap Authenticator")
st.markdown("Detects your ID strap from the webcam using YOLOv8")

weights_path = st.text_input("Path to model weights", value=str(BEST_WEIGHTS))

if not Path(weights_path).exists():
    st.warning("Weights not found. Train first or adjust path.")
else:
    st.success("Weights path set. Click 'Load Model' to load the model into memory.")

if st.button("Load Model"):
    try:
        model = load_model(Path(weights_path))
        st.session_state["model_loaded"] = True
        st.session_state["model"] = model
        st.success("Model loaded.")
    except Exception as e:
        st.error(f"Failed to load model: {e}")

if "model_loaded" not in st.session_state:
    st.session_state["model_loaded"] = False

start_btn = st.button("Start Webcam")
stop_btn = st.button("Stop Webcam")

frame_container = st.empty()
status_container = st.empty()

if st.session_state["model_loaded"] and start_btn:
    cap = cv2.VideoCapture(WEBCAM_DEVICE_INDEX)
    if not cap.isOpened():
        st.error("❌ Could not open webcam. Check permissions and device index.")
    else:
        st.session_state["stop_stream"] = False
        model = st.session_state.get("model")
        status_container.info("Streaming... Press Stop Webcam to end.")
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    st.warning("Failed to read frame from camera.")
                    break
                annotated, found, detections = run_inference_on_frame(model, frame)
                annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                frame_container.image(annotated_rgb, channels="RGB", use_column_width=True)
                if found:
                    status_container.success("✅ Authorized — ID strap detected.")
                else:
                    status_container.error("❌ Not authorized — ID strap not detected.")

                if st.session_state.get("stop_stream", False):
                    break
                if stop_btn:
                    st.session_state["stop_stream"] = True
                    break
                time.sleep(0.05)
        except st.script_runner.StopException:
            pass
        finally:
            cap.release()
            status_container.info("Stream stopped.")
elif not st.session_state["model_loaded"]:
    st.info("Load the model first (click 'Load Model').")

# Single image uploader
st.markdown("---")
st.header("Test single image")
img_file = st.file_uploader("Upload image (or use webcam snapshot)", type=["jpg", "jpeg", "png"])
if img_file is not None:
    img = Image.open(img_file).convert("RGB")
    frame = np.array(img)[:, :, ::-1]  # RGB->BGR
    if Path(weights_path).exists():
        model = load_model(Path(weights_path))
        annotated, found, detections = run_inference_on_frame(model, frame)
        annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        st.image(annotated_rgb, use_column_width=True)
        if found:
            st.success("✅ Authorized — ID strap detected.")
        else:
            st.error("❌ Not authorized — ID strap not detected.")
    else:
        st.warning("Weights not found. Cannot run inference.")
