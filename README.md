# License Plate Demo – Smart Parking System

Prototype AI system for the Smart Campus Parking Management System project.

## Current Features

- Thai and English license plate recognition using EasyOCR
- Support for car and motorcycle license plates
- Motorcycle helmet detection using a custom YOLO model
- Stable license plate and helmet detection using multiple-frame results
- Thai Unicode license plate display on the camera feed
- Real-time webcam processing

## Main Program

The current combined prototype is:

`smart_parking_v1.py`

It combines license plate recognition and helmet detection.

## Requirements

- Python 3.11
- OpenCV
- EasyOCR
- Ultralytics YOLO
- Pillow
- NumPy

## Setup

Create a Python 3.11 virtual environment:

```bash
python3.11 -m venv venv
```

Activate the virtual environment on macOS/Linux:

```bash
source venv/bin/activate
```

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

## macOS Apple Silicon Note

If Python 3.11 produces a `pyexpat` / Expat library error, run:

```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/opt/expat/lib:$DYLD_LIBRARY_PATH"
```

This environment variable applies to the current Terminal session.

## Run

Run the current combined prototype:

```bash
python smart_parking_v1.py
```

Press `q` to close the camera window.

## Models

`helmet_model.pt` is the custom YOLO helmet detection model used by the current smart parking prototype.

`yolov8n.pt` is the base YOLOv8 Nano model used by some earlier/training scripts.

## Notes

The `runs/` directory, Python virtual environment, cache files, and generated prediction/training output are excluded from Git.

The Thai license plate overlay currently uses the macOS Thonburi font. The font path may need to be changed when running the project on Windows or Linux.
