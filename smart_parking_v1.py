import cv2
import easyocr
import re
import numpy as np
from collections import Counter
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont

# Load OCR and helmet model
reader = easyocr.Reader(['th', 'en'])
helmet_model = YOLO("helmet_model.pt")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

print("Smart Parking v1 started")
print("Press q to quit")

# Helmet stability
recent_helmet_detections = []
last_helmet_status = ""

# Plate stability
recent_plate_detections = []
last_plate = ""

# OCR every 10 frames to reduce lag
frame_count = 0
OCR_INTERVAL = 10

thai_font = ImageFont.truetype(
    "/System/Library/Fonts/Supplemental/Thonburi.ttc",
    32
)

def clean_text(text):
    text = text.upper()
    text = text.replace(" ", "")
    text = re.sub(r"[^ก-ฮ0-9A-Z-]", "", text)
    return text


def extract_plate(texts):
    # Motorcycle: 1กก + 2048
    for i in range(len(texts)):
        if re.fullmatch(r"[0-9]{1,2}[ก-ฮ]{1,3}", texts[i]):
            for j in range(i + 1, len(texts)):
                if re.fullmatch(r"[0-9]{3,4}", texts[j]):
                    return texts[i] + texts[j]

    # International: 1B9 + 61
    for i in range(len(texts) - 1):
        candidate = texts[i] + texts[i + 1]
        if re.fullmatch(r"[0-9]{1,2}[A-Z]{1,3}[0-9]{2,4}", candidate):
            return candidate

    # Thai car plates
    for text in texts:
        if re.fullmatch(r"[0-9]{1,2}[ก-ฮ]{1,3}-?[0-9]{3,4}", text):
            return text.replace("-", "")

        if re.fullmatch(r"[ก-ฮ]{1,3}[0-9]{3,4}", text):
            return text

    # Private truck: 82-4728
    for text in texts:
        if re.fullmatch(r"[0-9]{2}-?[0-9]{4}", text):
            if "-" in text:
                return text
            return text[:2] + "-" + text[2:]

    # Split Thai car plate: ภบ + 9503
    for i in range(len(texts) - 1):
        candidate = texts[i] + texts[i + 1]

        if re.fullmatch(r"[0-9]{1,2}[ก-ฮ]{1,3}-?[0-9]{3,4}", candidate):
            return candidate.replace("-", "")

        if re.fullmatch(r"[ก-ฮ]{1,3}[0-9]{3,4}", candidate):
            return candidate

    return ""


while True:
    ret, frame = cap.read()

    if not ret:
        break

    frame_count += 1

    # ---------- Plate OCR ----------
    if frame_count % OCR_INTERVAL == 0:
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

        plate = extract_plate(cleaned_texts)

        if plate:
            recent_plate_detections.append(plate)
            recent_plate_detections = recent_plate_detections[-10:]

            stable_plate = Counter(recent_plate_detections).most_common(1)[0][0]

            if stable_plate != last_plate and recent_plate_detections.count(stable_plate) >= 3:
                print("Detected Plate:", stable_plate)
                last_plate = stable_plate

    # ---------- Helmet Detection ----------
    helmet_results = helmet_model(frame, conf=0.5, verbose=False)

    for result in helmet_results:
        for box in result.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            label = helmet_model.names[cls]

            if label not in ["with_helmet", "no_helmet"]:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if label == "with_helmet":
                helmet_text = "Helmet: YES"
            else:
                helmet_text = "Helmet: NO"

            recent_helmet_detections.append(helmet_text)
            recent_helmet_detections = recent_helmet_detections[-10:]

            stable_helmet = Counter(recent_helmet_detections).most_common(1)[0][0]

            if stable_helmet == "Helmet: YES":
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)

            if stable_helmet != last_helmet_status and recent_helmet_detections.count(stable_helmet) >= 3:
                print(stable_helmet)
                last_helmet_status = stable_helmet

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            cv2.putText(
                frame,
                f"{stable_helmet} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
            )

    # ---------- Display Status ----------
    plate_display = last_plate if last_plate else "Detecting..."

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(frame_rgb)
    draw = ImageDraw.Draw(pil_image)

    draw.text(
        (30, 15),
        f"Plate: {plate_display}",
        font=thai_font,
        fill=(255, 255, 0)
    )

    frame = cv2.cvtColor(
        np.array(pil_image),
        cv2.COLOR_RGB2BGR
    )

    cv2.putText(
        frame,
        f"Helmet: {last_helmet_status.replace('Helmet: ', '') if last_helmet_status else 'Detecting...'}",
        (30, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 255),
        2,
    )

    cv2.imshow("Smart Parking v1", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()