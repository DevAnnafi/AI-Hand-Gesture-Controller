import numpy as np
import pyautogui

pyautogui.PAUSE = 0        # default sleeps 0.1 s after EVERY call, which would cap you at ~10 FPS
pyautogui.FAILSAFE = True  # mouse in a screen corner raises an exception as an emergency stop


class MouseController:
    def __init__(self, frame_size, margin=100):
        self.frame_w, self.frame_h = frame_size
        self.screen_w, self.screen_h = pyautogui.size()
        self.margin = margin
        self.button_down = False

    def active_region(self):
        """Top-left and bottom-right corners of the camera area mapped to the screen."""
        return (self.margin, self.margin), (self.frame_w - self.margin, self.frame_h - self.margin)

    def to_screen(self, point):
        """Map a camera-pixel point inside the active region to screen pixels (clamped)."""
        x, y = point
        (x1, y1), (x2, y2) = self.active_region()
        sx = np.interp(x, [x1, x2], [1, self.screen_w - 2])
        sy = np.interp(y, [y1, y2], [1, self.screen_h - 2])
        return int(sx), int(sy)

    def update(self, screen_point, is_pinched):
        """Move the cursor to an (x, y) screen point and turn pinch changes into down/up events."""
        pyautogui.moveTo(*screen_point)

        if is_pinched and not self.button_down:      # rising edge
            pyautogui.mouseDown()
            self.button_down = True
        elif not is_pinched and self.button_down:    # falling edge
            pyautogui.mouseUp()
            self.button_down = False

    def release(self):
        """Make sure the button is up, e.g. when the hand is lost or the program exits."""
        if self.button_down:
            pyautogui.mouseUp()
            self.button_down = False