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

    # ---------- Motorcycle Plates ----------
    # Example OCR:
    # ["1กก", "สมทรปรกร", "2048"]
    for i in range(len(texts)):
        if re.fullmatch(r"[0-9]{1,2}[ก-ฮ]{1,3}", texts[i]):
            for j in range(i + 1, len(texts)):
                if re.fullmatch(r"[0-9]{3,4}", texts[j]):
                    return texts[i] + texts[j]

    # ---------- Car Plates ----------
    # Example:
    # กท2058
    # 9ฒฒ9999
    # 1B961

    for text in texts:

        if re.fullmatch(r"[0-9]{1,2}[ก-ฮ]{1,3}[0-9]{3,4}", text):
            return text

        if re.fullmatch(r"[ก-ฮ]{1,3}[0-9]{3,4}", text):
            return text

        if re.fullmatch(r"[0-9]{1,2}[A-Z]{1,3}[0-9]{1,4}", text):
            return text

    # ---------- Adjacent OCR Combination ----------
    # Handles OCR splitting a car plate into two pieces.
    for i in range(len(texts) - 1):

        candidate = texts[i] + texts[i + 1]

        if re.fullmatch(r"[0-9]{1,2}[ก-ฮ]{1,3}[0-9]{3,4}", candidate):
            return candidate

        if re.fullmatch(r"[ก-ฮ]{1,3}[0-9]{3,4}", candidate):
            return candidate

        if re.fullmatch(r"[0-9]{1,2}[A-Z]{1,3}[0-9]{1,4}", candidate):
            return candidate

    return ""


while True:

    ret, frame = cap.read()

    if not ret:
        break

    # ---------- Image Pre-processing ----------
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

        # Keep latest 10 detections
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
            2,
        )

    cv2.imshow("Thai License Plate OCR Demo", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()