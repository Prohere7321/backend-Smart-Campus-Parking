import cv2
import easyocr
import re
from collections import Counter

reader = easyocr.Reader(['th', 'en'])
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

last_printed = ""
recent_detections = []

def clean_text(text):
    text = text.upper()
    text = text.replace(" ", "")
    text = re.sub(r"[^ก-ฮ0-9A-Z]", "", text)
    return text

def extract_plate(texts):
    combined = "".join(texts)

    matches = re.findall(
        r"(?:[0-9]{1,2}[ก-ฮ]{1,3}[0-9]{3,4}|[ก-ฮ]{1,3}[0-9]{3,4}|[0-9]{1,2}[A-Z]{1,3}[0-9]{1,4})",
        combined
    )

    if matches:
        return matches[0]

    return ""

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = reader.readtext(frame)

    cleaned_texts = []

    for bbox, text, confidence in results:
        if confidence > 0.4:
            cleaned = clean_text(text)
            if cleaned:
                cleaned_texts.append(cleaned)

                top_left = tuple(map(int, bbox[0]))
                bottom_right = tuple(map(int, bbox[2]))
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

    plate = extract_plate(cleaned_texts)

    if plate:
        recent_detections.append(plate)

        # Keep only latest 10 detections
        recent_detections = recent_detections[-10:]

        # Use most common result to reduce OCR noise
        stable_plate = Counter(recent_detections).most_common(1)[0][0]

        if stable_plate != last_printed and recent_detections.count(stable_plate) >= 3:
            print("Detected Plate:", stable_plate)
            last_printed = stable_plate

        cv2.putText(
            frame,
            f"Plate: {stable_plate}",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

    cv2.imshow("Thai License Plate OCR Demo", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()