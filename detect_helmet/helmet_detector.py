from ultralytics import YOLO

helmet_model = YOLO("helmet_model.pt")

last_helmet = ""
def detect_helmet(frame):
    global last_helmet
    results = helmet_model(frame, conf=0.5)
    annotated = results[0].plot()

    helmet_status = None

    for box in results[0].boxes:

        cls = int(box.cls[0])

        helmet_status = helmet_model.names[cls]

        if helmet_status != last_helmet:

            print("Detected Helmet:", helmet_status)

            last_helmet = helmet_status

    return annotated, helmet_status