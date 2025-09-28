# --- archivo: main.py ---

import cv2
# La línea 'import time' se ha eliminado

from controlador_dron import ControladorDron
from horizonte_artificial import HorizonteArtificial
from proximidad_sensor import ProximitySensor
from alerta_suelo import AlertaSuelo
from display_controles import DisplayControles

FRAME_WIDTH = 800
FRAME_HEIGHT = 600


def main():
    dron = ControladorDron()
    horizonte = HorizonteArtificial(width=FRAME_WIDTH, height=FRAME_HEIGHT)
    sensor_proximidad = ProximitySensor(FRAME_WIDTH, FRAME_HEIGHT)
    alerta_suelo = AlertaSuelo(critical_height_dm=3, warning_height_dm=6)
    display_controles = DisplayControles()

    try:
        while True:
            frame = dron.get_frame()
            if frame is None or frame.size == 0:
                continue

            telemetry = dron.get_telemetry()
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

            key = cv2.waitKey(1) & 0xFF

            dron.manejar_teclado(key)

            sensor_proximidad.detect(frame)
            horizonte.draw(frame, telemetry['roll'], telemetry['pitch'])
            alerta_suelo.update_and_draw(frame, telemetry['height'])
            display_controles.draw(frame, key)

            cv2.putText(frame, f"Roll: {telemetry['roll']:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Pitch: {telemetry['pitch']:.1f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0),
                        2)

            cv2.imshow("Tello Control Center", frame)

            # La línea 'time.sleep(0.02)' se ha eliminado

            if key == 27:  # Salir con ESC
                break

    except Exception as e:
        print(f"Ocurrió un error en el bucle principal: {e}")

    finally:
        dron.cleanup()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()