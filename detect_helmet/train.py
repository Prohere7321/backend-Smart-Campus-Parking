from ultralytics import YOLO
model = YOLO("yolov8n.pt")
model.train(
    data="Helmet-Detector-7/data.yaml",
    epochs=10,
    imgsz=640
)