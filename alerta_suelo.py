# --- archivo: alerta_suelo.py ---

import cv2


class AlertaSuelo:
    """
    Muestra la altitud y una alerta "PULL UP" parpadeante de proximidad al suelo.
    """

    def __init__(self, critical_height_dm=3, warning_height_dm=6):
        self.CRITICAL_HEIGHT_DM = critical_height_dm
        self.WARNING_HEIGHT_DM = warning_height_dm

        self.COLOR_NORMAL = (255, 255, 255)
        self.COLOR_WARNING = (0, 255, 255)
        self.COLOR_CRITICAL = (0, 0, 255)

        self.blink_counter = 0

    def update_and_draw(self, frame, height_dm):
        height_m = height_dm / 10.0
        frame_h, frame_w, _ = frame.shape

        if height_dm <= self.CRITICAL_HEIGHT_DM:
            self.blink_counter += 1
            if self.blink_counter % 20 < 10:
                text = "PULL UP"
                font_scale = 1.8
                thickness = 3
                (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, font_scale, thickness)

                position = ((frame_w - text_w) // 2, (frame_h + text_h) // 2)

                overlay = frame.copy()
                cv2.rectangle(overlay, (position[0] - 20, position[1] + 20),
                              (position[0] + text_w + 20, position[1] - text_h - 20), (0, 0, 0), -1)
                alpha = 0.6
                frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

                cv2.putText(frame, text, position, cv2.FONT_HERSHEY_DUPLEX, font_scale, self.COLOR_CRITICAL, thickness,
                            cv2.LINE_AA)

        elif height_dm <= self.WARNING_HEIGHT_DM:
            text = f"BAJA ALTITUD: {height_m:.1f} m"
            position = (10, frame_h - 20)
            cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLOR_WARNING, 2, cv2.LINE_AA)
        else:
            text = f"Altitud: {height_m:.1f} m"
            position = (10, frame_h - 20)
            cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLOR_NORMAL, 1, cv2.LINE_AA)