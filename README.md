# Smart Campus Parking – Backend

Backend AI prototype for the Smart Campus Parking Management System project.

## Current Features

- Thai and English license plate recognition using EasyOCR
- Support for car and motorcycle license plates
- Motorcycle helmet detection using a custom YOLO model
- Stable license plate and helmet detection using multiple-frame results
- Thai Unicode license plate display on the camera feed
- Real-time webcam processing

## Main Program

The current combined prototype is:

```text
smart_parking_v1.py
```

It combines license plate recognition and motorcycle helmet detection.

## Requirements

- Python 3.11
- OpenCV
- EasyOCR
- Ultralytics YOLO
- Pillow
- NumPy
- Webcam

Python packages are listed in:

```text
requirements.txt
```

## Clone the Repository

Clone the repository:

```bash
git clone https://github.com/Prohere7321/backend-Smart-Campus-Parking.git
```

Enter the project directory:

```bash
cd backend-Smart-Campus-Parking
```

## Setup

### 1. Create a Python 3.11 Virtual Environment

On macOS/Linux:

```bash
python3.11 -m venv venv
```

On Windows, depending on the Python installation:

```bash
py -3.11 -m venv venv
```

### 2. Activate the Virtual Environment

macOS/Linux:

```bash
source venv/bin/activate
```

Windows Command Prompt:

```bat
venv\Scripts\activate
```

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install Required Packages

```bash
python -m pip install -r requirements.txt
```

## macOS Apple Silicon / Homebrew Expat Issue

Some macOS Apple Silicon systems using Homebrew Python 3.11 may encounter a `pyexpat` / Expat library error.

This can occur while creating the virtual environment.

If this happens, delete the incomplete virtual environment:

```bash
rm -rf venv
```

Then set the Homebrew Expat library path:

```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/opt/expat/lib:$DYLD_LIBRARY_PATH"
```

Verify that Expat works:

```bash
python3.11 -c "import xml.parsers.expat; print('Expat OK')"
```

The expected output is:

```text
Expat OK
```

Then create the virtual environment again:

```bash
python3.11 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

The `DYLD_LIBRARY_PATH` environment variable applies to the current Terminal session. If the Expat error appears again in a new Terminal session, run the export command again.

## Run the Program

Make sure the virtual environment is activated.

Then run:

```bash
python smart_parking_v1.py
```

The program should display:

```text
Smart Parking v1 started
Press q to quit
```

A webcam window should open.

The system will perform:

- License plate recognition
- Motorcycle helmet detection
- License plate stabilization across multiple frames
- Helmet detection stabilization across multiple frames

Example terminal output:

```text
Detected Plate: 1กก2048
Helmet: YES
```

Press:

```text
q
```

to close the camera window.

## AI Models

### helmet_model.pt

`helmet_model.pt` is the custom YOLO helmet detection model used by the current Smart Parking prototype.

The model contains the following classes:

- `driver`
- `no_helmet`
- `pillion`
- `with_helmet`

The current program uses the `with_helmet` and `no_helmet` detections to determine helmet status.

### yolov8n.pt

`yolov8n.pt` is the base YOLOv8 Nano model used by some earlier and training scripts.

## License Plate Recognition

License plate recognition is performed using EasyOCR with Thai and English language support.

The current prototype supports several plate formats used during development, including:

- Thai car plates
- Thai motorcycle plates
- Private truck plates
- English/alphanumeric plate formats

Province text detected from Thai motorcycle plates is currently ignored when constructing the final plate number.

## Thai Text Display

OpenCV's default fonts do not support Thai Unicode correctly.

The current prototype therefore uses Pillow to display Thai license plate text on the camera feed.

On macOS, the current program uses the Thonburi font located at:

```text
/System/Library/Fonts/Supplemental/Thonburi.ttc
```

This path is specific to macOS.

If the program is run on Windows or Linux, the font configuration in `smart_parking_v1.py` may need to be changed to a Thai-compatible font available on that operating system.

## Apple Silicon MPS Warning

On Apple Silicon Macs, PyTorch may display a warning similar to:

```text
'pin_memory' argument is set as true but not supported on MPS
```

This warning is non-fatal and does not prevent the current prototype from running.

## Repository Structure

Important files include:

```text
backend-Smart-Campus-Parking/
├── smart_parking_v1.py
├── helmet_model.pt
├── yolov8n.pt
├── requirements.txt
├── README.md
├── detect_helmet/
├── helmet_detection_v1.py
├── helmet_detection_v2.py
├── helmet_detection_v3.py
├── webcam_ocr_v1.py
├── webcam_ocr_v2.py
├── webcam_ocr_v3_testing.py
├── webcam_ocr_v4_testing.py
├── webcam_ocr_v4.1_testing.py
├── webcam_ocr_v4.2_debug.py
└── webcam_ocr_v4.2.py
```

The exact repository contents may change as development continues.

## Files Excluded from Git

The following types of files are excluded using `.gitignore`:

- Python virtual environments (`venv/`)
- Python cache files
- macOS `.DS_Store`
- Ultralytics generated `runs/` output
- VS Code and IDE settings
- Old helmet model (`helmet_best.pt`)

Each group member should create their own local virtual environment after cloning the repository.

Do not copy or commit the `venv` directory.

## Updating the Repository

Before starting work, get the latest version:

```bash
git pull
```

After making changes:

```bash
git add .
git commit -m "Describe the changes"
git push
```

Group members should always run `git pull` before starting new work to reduce the chance of conflicts.

## Current Project Status

The current backend prototype successfully combines:

1. Real-time webcam input
2. Thai/English license plate recognition
3. Motorcycle license plate recognition
4. Custom YOLO motorcycle helmet detection
5. Multi-frame result stabilization
6. Thai Unicode camera overlay

Further backend integration and communication with the Smart Campus Parking frontend will be developed as the project progresses.
