# --- archivo: display_controles.py ---

import cv2


class DisplayControles:
    def __init__(self):
        self.COLOR_FONDO = (50, 50, 50)
        self.COLOR_LETRA = (255, 255, 255)
        self.COLOR_PRESIONADO = (0, 255, 0)

        # --- Novedad: Actualizamos el layout con R y F ---
        # (x, y, ancho, alto)
        self.layout = {
            ord('w'): ("Adelante", (100, 430, 60, 60)),
            ord('s'): ("Atras", (100, 500, 60, 60)),
            ord('a'): ("Izquierda", (30, 500, 60, 60)),
            ord('d'): ("Derecha", (170, 500, 60, 60)),
            ord('q'): ("Girar Iz.", (30, 430, 60, 60)),
            ord('e'): ("Girar Der.", (170, 430, 60, 60)),
            ord('r'): ("Subir", (300, 430, 60, 60)),
            ord('f'): ("Bajar", (300, 500, 60, 60)),
            ord('t'): ("Despegar", (450, 500, 120, 60)),
            ord('l'): ("Aterrizar", (600, 500, 120, 60)),
        }

    def _dibujar_tecla(self, frame, texto_tecla, texto_accion, rect, presionado):
        x, y, w, h = rect
        color_fondo = self.COLOR_PRESIONADO if presionado else self.COLOR_FONDO

        cv2.rectangle(frame, (x, y), (x + w, y + h), color_fondo, -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), self.COLOR_LETRA, 2)

        (text_w, text_h), _ = cv2.getTextSize(texto_tecla, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        cv2.putText(frame, texto_tecla, (x + (w - text_w) // 2, y + (h + text_h) // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.COLOR_LETRA, 2)

        (text_w, _), _ = cv2.getTextSize(texto_accion, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.putText(frame, texto_accion, (x + (w - text_w) // 2, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_LETRA, 1)

    def draw(self, frame, tecla_presionada):
        self._dibujar_tecla(frame, "W", "Adelante", self.layout[ord('w')][1], tecla_presionada == ord('w'))
        self._dibujar_tecla(frame, "S", "Atras", self.layout[ord('s')][1], tecla_presionada == ord('s'))
        self._dibujar_tecla(frame, "A", "Izquierda", self.layout[ord('a')][1], tecla_presionada == ord('a'))
        self._dibujar_tecla(frame, "D", "Derecha", self.layout[ord('d')][1], tecla_presionada == ord('d'))
        self._dibujar_tecla(frame, "Q", "Girar Iz.", self.layout[ord('q')][1], tecla_presionada == ord('q'))
        self._dibujar_tecla(frame, "E", "Girar Der.", self.layout[ord('e')][1], tecla_presionada == ord('e'))
        # --- Novedad: Dibujamos las nuevas teclas R y F ---
        self._dibujar_tecla(frame, "R", "Subir", self.layout[ord('r')][1], tecla_presionada == ord('r'))
        self._dibujar_tecla(frame, "F", "Bajar", self.layout[ord('f')][1], tecla_presionada == ord('f'))
        self._dibujar_tecla(frame, "T", "Despegar", self.layout[ord('t')][1], tecla_presionada == ord('t'))
        self._dibujar_tecla(frame, "L", "Aterrizar", self.layout[ord('l')][1], tecla_presionada == ord('l'))