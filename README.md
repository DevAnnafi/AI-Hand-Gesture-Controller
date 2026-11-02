# AI Hand Gesture Controller

Control your computer with hand gestures through a webcam. Built from scratch in Python with **OpenCV** and **MediaPipe Hand Landmarker**.

>**Status: In development.** Step 1 (camera feed + hand landmark tracking) is complete. Gesture recognition and OS input control are in progress — see the [Roadmap](#roadmap).

---

## How It Works

1. **Capture** — OpenCV reads frames from the webcam and mirrors them so on-screen movement matches your hand.
2. **Detect** — MediaPipe's Hand Landmarker finds the hand and returns **21 landmarks** (wrist, knuckles, fingertips) per frame.
3. **Convert** — Landmarks arrive as normalized coordinates (0–1) and are converted to pixel coordinates for drawing and geometry.
4. **Interpret** *(planned)* — Distances and angles between landmarks are turned into gestures (e.g. a thumb–index pinch).
5. **Act** *(planned)* — Gestures are mapped to operating-system input such as mouse movement and clicks.

---

## Current Features

- Real-time webcam capture with a mirrored view
- Hand landmark detection using the MediaPipe Tasks API (`HandLandmarker`, video mode)
- Index fingertip tracking, drawn as a live overlay
- Normalized → pixel coordinate conversion
- On-screen FPS counter

---

## Requirements

- Python 3.12+ (developed on 3.14)
- A webcam
- Windows, macOS, or Linux with a desktop display

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/DevAnnafi/AI_Hand_Gesture_Controller.git
cd AI_Hand_Gesture_Controller
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install mediapipe opencv-contrib-python
```

> **Note:** If you see `The function is not implemented. Rebuild the library with Windows, GTK+ 2.x or Cocoa support`, a *headless* OpenCV build is installed. Remove every OpenCV variant and reinstall the GUI build:
>
> ```bash
> pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless opencv-contrib-python-headless
> pip install opencv-contrib-python
> ```

### 4. Download the hand landmark model

The model file is not stored in this repository. Download it into the project folder:

```bash
# macOS / Linux
curl -L -o hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
```

```powershell
# Windows (PowerShell)
Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task" -OutFile "hand_landmarker.task"
```

The file should be a few megabytes. If it is only a few kilobytes, the download returned an error page — try again.

---

## Usage

Run from the project folder:

```bash
python capture.py
```

- A window opens showing your mirrored webcam feed.
- A green dot follows your index fingertip.
- Fingertip coordinates (normalized and pixel) print to the terminal.
- The FPS counter is shown in the top-left corner.

Press **`q`** with the video window focused to quit.

---

## Coordinate System

MediaPipe returns each landmark as `(x, y, z)`:

| Value | Meaning |
|---|---|
| `x` | Horizontal position as a fraction of image width (`0` = left, `1` = right) |
| `y` | Vertical position as a fraction of image height (`0` = **top**, `1` = bottom) |
| `z` | Depth relative to the wrist; more negative = closer to the camera |

Pixel coordinates are computed as:

```
pixel_x = int(x × frame_width)
pixel_y = int(y × frame_height)
```

Because `x` and `y` are scaled by different dimensions, distances are calculated in **pixel space** to avoid aspect-ratio distortion.

### Landmark indices

| Index | Landmark |
|---|---|
| 0 | Wrist |
| 4 | Thumb tip |
| 8 | Index fingertip |
| 12 | Middle fingertip |
| 16 | Ring fingertip |
| 20 | Pinky tip |

---

## Roadmap

- [x] **Step 1** — Camera feed, hand landmark detection, fingertip overlay, FPS counter
- [x] **Step 2** — Landmark extraction module (all 21 points in pixel space)
- [x] **Step 3** — Geometric distance calculations and gesture detection
- [x] **Step 4** — OS input mapping (cursor movement, clicks)
- [x] **Step 5** — Smoothing and jitter reduction

---

## Project Structure

```
AI_Hand_Gesture_Controller/
├── capture.py            # Camera loop + landmark detection
├── hand_landmarker.task  # MediaPipe model (downloaded, not committed)
├── hand_tracker.py
├── .gitignore
└── README.md
```

---

## Tech Stack

- [Python](https://www.python.org/)
- [OpenCV](https://opencv.org/) — video capture and drawing
- [MediaPipe Hand Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker) — hand landmark detection

---

## Author

**Annafi Islam** — [GitHub](https://github.com/DevAnnafi) · [Portfolio](https://annafiislam.com) · [LinkedIn](https://linkedin.com/in/annafi-islam)