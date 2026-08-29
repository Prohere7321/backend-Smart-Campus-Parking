import cv2
from ultralytics import YOLO

model = YOLO("helmet_model.pt")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

last_status = ""

while True:
    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame, conf=0.5, verbose=False)

    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls]

            if label not in ["with_helmet", "no_helmet"]:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if label == "with_helmet":
                status = "Helmet: YES"
                color = (0, 255, 0)
            else:
                status = "Helmet: NO"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            cv2.putText(
                frame,
                f"{status} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
            )

            if status != last_status:
                print(status)
                last_status = status

    cv2.imshow("Member Helmet Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
