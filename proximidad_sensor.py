# --- archivo: proximidad_sensor.py ---

import cv2
import numpy as np


class ProximitySensor:
    def __init__(self, frame_width, frame_height, danger_threshold=0.30):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.roi_w = int(frame_width / 3)
        self.roi_h = int(frame_height / 3)
        self.roi_x = (frame_width - self.roi_w) // 2
        self.roi_y = (frame_height - self.roi_h) // 2
        self.DANGER_THRESHOLD = danger_threshold
        self.WARNING_THRESHOLD = danger_threshold * 0.5
        self.roi_area = self.roi_w * self.roi_h
        self.BAR_WIDTH = 200
        self.BAR_HEIGHT = 20
        self.BAR_X = 10
        self.BAR_Y = 100
        self.CORNER_INDICATOR_SIZE = 30
        self.CORNER_MARGIN = 10

    def detect(self, frame):
        roi = frame[self.roi_y: self.roi_y + self.roi_h, self.roi_x: self.roi_x + self.roi_w]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        occupied_area = sum(cv2.contourArea(cnt) for cnt in contours)
        danger_level = np.clip(occupied_area / self.roi_area, 0, 1)

        if danger_level > self.DANGER_THRESHOLD:
            current_alert_color = (0, 0, 255)
        elif danger_level > self.WARNING_THRESHOLD:
            current_alert_color = (0, 255, 255)
        else:
            current_alert_color = (0, 255, 0)

        cv2.rectangle(frame, (self.BAR_X, self.BAR_Y), (self.BAR_X + self.BAR_WIDTH, self.BAR_Y + self.BAR_HEIGHT),
                      (50, 50, 50), -1)
        bar_fill_color = (0, int(255 * (1 - danger_level)), int(255 * danger_level))
        fill_width = int(self.BAR_WIDTH * danger_level)
        cv2.rectangle(frame, (self.BAR_X, self.BAR_Y), (self.BAR_X + fill_width, self.BAR_Y + self.BAR_HEIGHT),
                      bar_fill_color, -1)
        cv2.rectangle(frame, (self.BAR_X, self.BAR_Y), (self.BAR_X + self.BAR_WIDTH, self.BAR_Y + self.BAR_HEIGHT),
                      (200, 200, 200), 1)
        cv2.putText(frame, f"Proximidad: {int(danger_level * 100)}%", (self.BAR_X, self.BAR_Y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        h, w, _ = frame.shape
        indicator_color = current_alert_color if danger_level > self.WARNING_THRESHOLD else (50, 50, 50)

        pts1 = np.array([[self.CORNER_MARGIN, self.CORNER_MARGIN + self.CORNER_INDICATOR_SIZE],
                         [self.CORNER_MARGIN, self.CORNER_MARGIN],
                         [self.CORNER_MARGIN + self.CORNER_INDICATOR_SIZE, self.CORNER_MARGIN]], np.int32)
        pts2 = np.array([[w - self.CORNER_MARGIN - self.CORNER_INDICATOR_SIZE, self.CORNER_MARGIN],
                         [w - self.CORNER_MARGIN, self.CORNER_MARGIN],
                         [w - self.CORNER_MARGIN, self.CORNER_MARGIN + self.CORNER_INDICATOR_SIZE]], np.int32)
        pts3 = np.array([[self.CORNER_MARGIN, h - self.CORNER_MARGIN - self.CORNER_INDICATOR_SIZE],
                         [self.CORNER_MARGIN, h - self.CORNER_MARGIN],
                         [self.CORNER_MARGIN + self.CORNER_INDICATOR_SIZE, h - self.CORNER_MARGIN]], np.int32)
        pts4 = np.array([[w - self.CORNER_MARGIN - self.CORNER_INDICATOR_SIZE, h - self.CORNER_MARGIN],
                         [w - self.CORNER_MARGIN, h - self.CORNER_MARGIN],
                         [w - self.CORNER_MARGIN, h - self.CORNER_MARGIN - self.CORNER_INDICATOR_SIZE]], np.int32)
        cv2.fillPoly(frame, [pts1, pts2, pts3, pts4], indicator_color)

        is_critical_danger = danger_level > self.DANGER_THRESHOLD
        if is_critical_danger:
            alert_text = "¡ALERTA CRÍTICA!"
            (text_w, text_h), _ = cv2.getTextSize(alert_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)
            box_start_x = w // 2 - text_w // 2 - 20
            box_start_y = h // 2 + 50 - text_h - 20
            overlay = frame.copy()
            cv2.rectangle(overlay, (box_start_x, box_start_y), (box_start_x + text_w + 40, box_start_y + text_h + 40),
                          (0, 0, 0), -1)
            frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
            cv2.putText(frame, alert_text, (w // 2 - text_w // 2, h // 2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                        (0, 0, 255), 3, cv2.LINE_AA)
        return is_critical_danger