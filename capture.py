import time
import cv2
from hand_tracker import HandTracker, INDEX_TIP

cap = cv2.VideoCapture(0)
tracker = HandTracker()
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
        for point in landmarks:
            cv2.circle(frame, point, 4, (0, 0, 255), -1)
        pixel_x, pixel_y = landmarks[INDEX_TIP]             # index fingertip
        cv2.circle(frame, (pixel_x, pixel_y), 10, (0, 255, 0), -1)
        print(f"index tip  pixel_x={pixel_x:4d}  pixel_y={pixel_y:4d}")

    cv2.putText(frame, f"FPS: {fps:.0f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Gesture Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
tracker.close()
cv2.destroyAllWindows()