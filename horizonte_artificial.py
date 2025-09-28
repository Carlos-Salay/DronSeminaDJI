# --- archivo: horizonte_artificial.py ---

import cv2
import numpy as np


class HorizonteArtificial:
    """
    Dibuja un horizonte artificial realista y un mensaje de arranque.
    """

    def __init__(self, width, height, size=300, margin=20):
        self.HORIZON_SIZE = size
        self.PITCH_SCALE = 3.0

        self.COLOR_SKY = (255, 127, 0)
        self.COLOR_GROUND = (0, 85, 170)
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_YELLOW = (0, 255, 255)

        self.START_X = width - self.HORIZON_SIZE - margin
        self.START_Y = height - self.HORIZON_SIZE - margin
        self.END_X = self.START_X + self.HORIZON_SIZE
        self.END_Y = self.START_Y + self.HORIZON_SIZE
        self.CENTER_X = self.START_X + self.HORIZON_SIZE // 2
        self.CENTER_Y = self.START_Y + self.HORIZON_SIZE // 2

        self.boot_up_frame_counter = 120  # Durará aprox. 4 segundos (a 30fps)

    def draw(self, frame, roll, pitch):
        """
        Dibuja todos los componentes del horizonte sobre el frame.
        """
        bg_size = int(self.HORIZON_SIZE * 1.5)
        horizon_bg = np.zeros((bg_size, bg_size, 3), dtype=np.uint8)

        pitch_displacement = int(pitch * self.PITCH_SCALE)
        center_y_bg = bg_size // 2 + pitch_displacement

        cv2.rectangle(horizon_bg, (0, 0), (bg_size, bg_size), self.COLOR_SKY, -1)
        cv2.rectangle(horizon_bg, (0, center_y_bg), (bg_size, bg_size), self.COLOR_GROUND, -1)
        cv2.line(horizon_bg, (0, center_y_bg), (bg_size, center_y_bg), self.COLOR_WHITE, 2)

        for angle in range(-90, 91, 5):
            if angle == 0: continue
            y_pos = center_y_bg - int(angle * self.PITCH_SCALE)
            if 0 < y_pos < bg_size:
                line_len = 50 if angle % 10 == 0 else 25
                cv2.line(horizon_bg, (bg_size // 2 - line_len, y_pos), (bg_size // 2 + line_len, y_pos),
                         self.COLOR_WHITE, 1)
                if angle % 10 == 0:
                    cv2.putText(horizon_bg, str(abs(angle)), (bg_size // 2 - line_len - 30, y_pos + 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_WHITE, 1, cv2.LINE_AA)

        M = cv2.getRotationMatrix2D((bg_size // 2, bg_size // 2), -roll, 1)
        rotated_bg = cv2.warpAffine(horizon_bg, M, (bg_size, bg_size))

        crop_start = (bg_size - self.HORIZON_SIZE) // 2
        final_horizon = rotated_bg[
            crop_start: crop_start + self.HORIZON_SIZE, crop_start: crop_start + self.HORIZON_SIZE]

        roi = frame[self.START_Y:self.END_Y, self.START_X:self.END_X]
        cv2.addWeighted(final_horizon, 1.0, roi, 0.0, 0, roi)

        radius = self.HORIZON_SIZE // 2 - 10
        cv2.line(frame, (self.CENTER_X, self.START_Y), (self.CENTER_X, self.START_Y + 15), self.COLOR_WHITE, 2)
        for angle in [10, 20, 30, 45, 60]:
            rad = np.deg2rad(angle)
            for sign in [-1, 1]:
                start_pt = (int(self.CENTER_X + sign * radius * np.sin(rad)), int(self.CENTER_Y - radius * np.cos(rad)))
                end_pt = (int(self.CENTER_X + sign * (radius - 10) * np.sin(rad)),
                          int(self.CENTER_Y - (radius - 10) * np.cos(rad)))
                cv2.line(frame, start_pt, end_pt, self.COLOR_WHITE, 2)

        cv2.rectangle(frame, (self.START_X, self.START_Y), (self.END_X, self.END_Y), self.COLOR_WHITE, 2)
        cv2.line(frame, (self.CENTER_X - 40, self.CENTER_Y), (self.CENTER_X - 20, self.CENTER_Y), self.COLOR_YELLOW, 2)
        cv2.line(frame, (self.CENTER_X + 20, self.CENTER_Y), (self.CENTER_X + 40, self.CENTER_Y), self.COLOR_YELLOW, 2)
        cv2.circle(frame, (self.CENTER_X, self.CENTER_Y), 5, self.COLOR_YELLOW, -1)

        if self.boot_up_frame_counter > 0:
            text = "HUD SYSTEM ONLINE"
            (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            text_x = self.START_X + (self.HORIZON_SIZE - text_w) // 2
            text_y = self.START_Y - 15
            cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
            self.boot_up_frame_counter -= 1