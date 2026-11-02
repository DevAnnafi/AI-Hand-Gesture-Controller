import math

from hand_tracker import (
    WRIST, THUMB_TIP, INDEX_TIP, MIDDLE_MCP,
    MIDDLE_TIP, RING_TIP, PINKY_TIP,
    MIDDLE_PIP, RING_PIP, PINKY_PIP,
)

SUPPORT_FINGERS = (
    (MIDDLE_TIP, MIDDLE_PIP),
    (RING_TIP, RING_PIP),
    (PINKY_TIP, PINKY_PIP),
)


def distance(p1, p2):
    """Euclidean distance between two (x, y) points, in pixels."""
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def hand_scale(landmarks):
    """Palm length (wrist to middle knuckle): a reference size that doesn't change as fingers move."""
    return distance(landmarks[WRIST], landmarks[MIDDLE_MCP])


def is_finger_extended(landmarks, tip, pip):
    """True if the finger's tip is farther from the wrist than its middle joint."""
    wrist = landmarks[WRIST]
    return distance(wrist, landmarks[tip]) > distance(wrist, landmarks[pip])


def count_extended(landmarks, fingers=SUPPORT_FINGERS):
    """How many of the given fingers are extended."""
    return sum(is_finger_extended(landmarks, tip, pip) for tip, pip in fingers)


class PinchDetector:
    def __init__(self, press_ratio=0.25, release_ratio=0.35, min_extended=2):
        self.press_ratio = press_ratio
        self.release_ratio = release_ratio
        self.min_extended = min_extended
        self.is_pinched = False

    def update(self, landmarks):
        """Return (is_pinched, ratio, extended_count) for the current frame."""
        extended = count_extended(landmarks)
        scale = hand_scale(landmarks)
        if scale == 0:
            return self.is_pinched, 0.0, extended

        ratio = distance(landmarks[THUMB_TIP], landmarks[INDEX_TIP]) / scale

        if self.is_pinched:
            if ratio > self.release_ratio:
                self.is_pinched = False
        else:
            if ratio < self.press_ratio and extended >= self.min_extended:
                self.is_pinched = True

        return self.is_pinched, ratio, extended

    def reset(self):
        """Forget the pinch state, e.g. when the hand leaves the frame."""
        self.is_pinched = False