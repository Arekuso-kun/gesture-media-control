# Gesture Media Control

Control media playback and volume with hand gestures using a webcam, OpenCV, and MediaPipe.

## Features

- `Open Palm` -> Play / Pause
- `Thumb Right` -> Next track
- `Thumb Left` -> Previous track
- `Index Up` -> Windows volume up
- `Index Down` -> Windows volume down
- `Two Fingers` -> Mute
- `Pinch`, then `index highest + thumb furthest sideways` -> app-aware fullscreen
- `Four fingers extended` dynamic gesture -> multi-step active-app volume control based on finger tilt

## Requirements

- Python `3.10`, `3.11`, or `3.12`
- A webcam
- MediaPipe version that still exposes `mp.solutions`

This project currently uses the classic `mp.solutions.hands` API, so `mediapipe==0.10.14` is recommended.

## Installation

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run

```powershell
python .\gesture_media_control.py
```

Press `q` to close the camera window.

## Enable Media Key Actions

The app can either:

- detect gestures and show them in the overlay
- detect gestures and send media key presses to the OS

To enable real media key actions, open [gesture_constants.py](C:\workspace\gesture-media-control\gesture_constants.py) and set:

```python
USE_PYAUTOGUI = True
```

When it is `False`, the app still detects gestures and logs actions, but it does not press system keys.

The dynamic app-volume gesture first tries to change the actual Windows audio session volume of the currently focused application. That works much better across apps such as:

- Spotify
- YouTube in a browser
- VLC
- other apps that expose a normal Windows audio session

If session-based volume control is not available, it falls back to keyboard shortcuts:

```python
DEFAULT_APP_VOLUME_UP_BINDING = "up"
DEFAULT_APP_VOLUME_DOWN_BINDING = "down"
```

The per-step volume delta is configurable in [gesture_constants.py](C:\workspace\gesture-media-control\gesture_constants.py):

```python
APP_VOLUME_STEP = 0.05
```

Fullscreen is also app-aware:

- on YouTube in a browser, it sends `F` to the player
- in VLC, it sends `F`
- in other apps, it sends `F11`

You can change those bindings in [gesture_constants.py](C:\workspace\gesture-media-control\gesture_constants.py):

```python
DEFAULT_FULLSCREEN_BINDING = "f11"
```

## Project Structure

- [gesture_media_control.py](C:\workspace\gesture-media-control\gesture_media_control.py): entrypoint
- [gesture_app.py](C:\workspace\gesture-media-control\gesture_app.py): webcam loop and overlay
- [gesture_detection.py](C:\workspace\gesture-media-control\gesture_detection.py): gesture classification
- [gesture_helpers.py](C:\workspace\gesture-media-control\gesture_helpers.py): finger and geometry helpers
- [gesture_actions.py](C:\workspace\gesture-media-control\gesture_actions.py): media command execution
- [gesture_constants.py](C:\workspace\gesture-media-control\gesture_constants.py): thresholds and configuration

## Notes

- If MediaPipe installs correctly but `mp.solutions` is missing, make sure you are not using Python `3.14`.
- If gestures feel too sensitive or too strict, tune the thresholds in [gesture_constants.py](C:\workspace\gesture-media-control\gesture_constants.py).
