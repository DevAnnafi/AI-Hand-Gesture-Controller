import time

import cv2

from hand_tracker import HandTracker, INDEX_TIP, THUMB_TIP
from gesture import PinchDetector

GREEN = (0, 255, 0)
RED = (0, 0, 255)
FONT = cv2.FONT_HERSHEY_SIMPLEX

cap = cv2.VideoCapture(0)
tracker = HandTracker()
pinch_detector = PinchDetector()
prev_time = time.monotonic()

while cap.isOpened():
    ok, frame = cap.read()
    if not ok:
        break

    frame = cv2.flip(frame, 1)                      # mirror view
    landmarks = tracker.find_landmarks(frame)       # list of 21 (x, y) or None

    curr_time = time.monotonic()
    elapsed_time = curr_time - prev_time
    fps = 1 / elapsed_time if elapsed_time > 0 else 0
    prev_time = curr_time

    if landmarks is not None:
        is_pinched, ratio, extended = pinch_detector.update(landmarks)
        line_color = RED if is_pinched else GREEN

        for point in landmarks:
            cv2.circle(frame, point, 4, RED, -1)
        cv2.line(frame, landmarks[THUMB_TIP], landmarks[INDEX_TIP], line_color, 3)
        cv2.circle(frame, landmarks[INDEX_TIP], 10, GREEN, -1)

        cv2.putText(frame, f"Ratio: {ratio:.2f}", (10, 60), FONT, 0.9, line_color, 2)
        cv2.putText(frame, f"Extended: {extended}/3", (10, 90), FONT, 0.9, line_color, 2)
    else:
        pinch_detector.reset()                      # never keep a stale pinch

    cv2.putText(frame, f"FPS: {fps:.0f}", (10, 30), FONT, 0.9, GREEN, 2)

    cv2.imshow("Gesture Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
tracker.close()
cv2.destroyAllWindows()