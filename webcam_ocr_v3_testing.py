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

    big = cv2.resize(frame, None, fx=3, fy=3)
    gray = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    results = reader.readtext(gray)

    cleaned_texts = []

    for bbox, text, confidence in results:
        if confidence > 0.4:
            cleaned = clean_text(text)
            if cleaned:
                cleaned_texts.append(cleaned)

    print("Raw OCR:", cleaned_texts)

    plate = extract_plate(cleaned_texts)

    if plate:
        recent_detections.append(plate)
        recent_detections = recent_detections[-10:]

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