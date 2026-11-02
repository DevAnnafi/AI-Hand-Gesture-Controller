import time
from collections import deque

import cv2

from hand_tracker import HandTracker, INDEX_MCP, INDEX_TIP, THUMB_TIP
from gesture import PinchDetector
from mouse_controller import MouseController
from smoothing import PointFilter

GREEN = (0, 255, 0)
RED = (0, 0, 255)
BLUE = (255, 0, 0)
FONT = cv2.FONT_HERSHEY_SIMPLEX
CURSOR_POINT = INDEX_MCP


def spread(points):
    """Range of x and y over a set of points: how far they wander."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return max(xs) - min(xs), max(ys) - min(ys)


cap = cv2.VideoCapture(0)
frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

tracker = HandTracker()
pinch_detector = PinchDetector()
mouse = MouseController(frame_size)
cursor_filter = PointFilter(min_cutoff=0.3, beta=0.02)
control_enabled = False

raw_history = deque(maxlen=60)
smooth_history = deque(maxlen=60)
prev_time = time.monotonic()

try:
    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.flip(frame, 1)
        landmarks = tracker.find_landmarks(frame)

        curr_time = time.monotonic()
        elapsed_time = curr_time - prev_time
        fps = 1 / elapsed_time if elapsed_time > 0 else 0
        prev_time = curr_time

        region_start, region_end = mouse.active_region()
        cv2.rectangle(frame, region_start, region_end, BLUE, 2)

        if landmarks is not None:
            is_pinched, ratio, extended = pinch_detector.update(landmarks)
            line_color = RED if is_pinched else GREEN

            raw = mouse.to_screen(landmarks[CURSOR_POINT])
            smoothed = cursor_filter(raw, curr_time)
            raw_history.append(raw)
            smooth_history.append(smoothed)

            if control_enabled:
                mouse.update(smoothed, is_pinched)
            else:
                mouse.release()

            for point in landmarks:
                cv2.circle(frame, point, 4, RED, -1)
            cv2.line(frame, landmarks[THUMB_TIP], landmarks[INDEX_TIP], line_color, 3)
            cv2.circle(frame, landmarks[CURSOR_POINT], 10, BLUE, -1)

            cv2.putText(frame, f"Ratio: {ratio:.2f}", (10, 60), FONT, 0.9, line_color, 2)
            cv2.putText(frame, f"Extended: {extended}/3", (10, 90), FONT, 0.9, line_color, 2)

            if len(raw_history) == raw_history.maxlen:
                rx, ry = spread(raw_history)
                sx, sy = spread(smooth_history)
                cv2.putText(frame, f"Jitter raw {rx}x{ry}  smooth {sx}x{sy}",
                            (10, 150), FONT, 0.7, GREEN, 2)
        else:
            pinch_detector.reset()
            mouse.release()
            cursor_filter.reset()
            raw_history.clear()
            smooth_history.clear()

        status = "Mouse: ON" if control_enabled else "Mouse: OFF (press m)"
        cv2.putText(frame, f"FPS: {fps:.0f}", (10, 30), FONT, 0.9, GREEN, 2)
        cv2.putText(frame, status, (10, 120), FONT, 0.9, GREEN if control_enabled else RED, 2)

        cv2.imshow("Gesture Controller", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("m"):
            control_enabled = not control_enabled
finally:
    mouse.release()
    cap.release()
    tracker.close()
    cv2.destroyAllWindows()