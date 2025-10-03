import torch
import cv2
import numpy as np

def load_model(weights_path):
    """
    Load YOLOv8 model from weights_path.
    """
    model = torch.hub.load("ultralytics/yolov8", "custom", path=str(weights_path))
    return model

def run_inference_on_frame(model, frame):
    """
    Run inference on a single frame and return annotated frame, detection status, and raw detections.
    """
    results = model(frame)
    annotated_frame = np.copy(frame)
    found = False
    detections = []

    for det in results.xyxy[0]:  # x1, y1, x2, y2, confidence, class
        x1, y1, x2, y2, conf, cls = det.cpu().numpy()
        if conf >= 0.45:  # Threshold
            found = True
            detections.append(det.cpu().numpy())
            # Draw bounding box
            cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(
                annotated_frame,
                f"{int(cls)} {conf:.2f}",
                (int(x1), int(y1) - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )

    return annotated_frame, found, detections
