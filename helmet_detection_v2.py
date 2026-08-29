import cv2
from ultralytics import YOLO

# Load helmet detection model
model = YOLO("helmet_model.pt")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:

    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame, verbose=False)

    for result in results:

        for box in result.boxes:

            cls = int(box.cls[0])
            conf = float(box.conf[0])

            if conf < 0.5:
                continue

            label = model.names[cls].strip()

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if label == "With helmet":
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                color,
                2
            )

            cv2.putText(
                frame,
                f"{label} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )

    cv2.imshow("Helmet Detection v2", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
