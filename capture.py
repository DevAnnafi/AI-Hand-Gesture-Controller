import time
import cv2
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
    running_mode=RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)

cap = cv2.VideoCapture(0)
prev_time = time.monotonic()

with HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.flip(frame, 1)                      # mirror view
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)    # OpenCV is BGR
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        timestamp_ms = int(time.monotonic() * 1000)
        result = landmarker.detect_for_video(mp_image, timestamp_ms)

        curr_time = time.monotonic()
        elapsed_time = curr_time - prev_time
        FPS = 1 / elapsed_time if elapsed_time > 0 else 0
        prev_time = curr_time    

        if result.hand_landmarks:
            hand = result.hand_landmarks[0]             # list of 21 landmarks
            tip = hand[8]                               # index fingertip
            pixel_x = int(tip.x * w)
            pixel_y = int(tip.y * h)
            cv2.circle(frame, (pixel_x, pixel_y), 10, (0, 255, 0), -1)
            print(f"index tip  x={tip.x:.3f}  y={tip.y:.3f}  z={tip.z:.3f} | pixel_x={pixel_x:.0f}  pixel_y={pixel_y:.0f}")

        cv2.putText(frame, f"FPS: {FPS:.0f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow("Gesture Controller", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()