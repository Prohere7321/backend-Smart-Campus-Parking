from ultralytics import YOLO
model = YOLO(
    "runs/detect/train/weights/best.pt"
)
model.predict(
    source="Helmet-Detector-7/test/images",
    conf=0.25,
    save=True
)