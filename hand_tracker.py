from pathlib import Path
import time

import cv2
import mediapipe as mp

MODEL_PATH = Path(__file__).parent / "hand_landmarker.task"

WRIST = 0
THUMB_TIP = 4
INDEX_PIP = 6
INDEX_TIP = 8
INDEX_MCP = 5
MIDDLE_MCP = 9
MIDDLE_PIP = 10
MIDDLE_TIP = 12
RING_PIP = 14
RING_TIP = 16
PINKY_PIP = 18
PINKY_TIP = 20



class HandTracker:
    def __init__(self, max_hands=1, detection_conf=0.5, tracking_conf=0.5):
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL_PATH)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_conf,
            min_hand_presence_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )
        self._landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self._last_ts = -1

    def find_landmarks(self, frame):
        """Return 21 (x, y) pixel tuples for the first hand, or None."""
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        ts = int(time.monotonic() * 1000)
        if ts <= self._last_ts:          # MediaPipe rejects repeated timestamps
            ts = self._last_ts + 1
        self._last_ts = ts

        result = self._landmarker.detect_for_video(mp_image, ts)
        if not result.hand_landmarks:
            return None

        hand = result.hand_landmarks[0]
        return [(int(lm.x * w), int(lm.y * h)) for lm in hand]

    def close(self):
        self._landmarker.close()