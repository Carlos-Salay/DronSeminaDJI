# --- archivo: main.py (Modificado) ---

import cv2
from djitellopy import Tello
import time

# Importamos las clases que hemos creado
from horizonte_artificial import HorizonteArtificial



def main():
    # --- 1. CONFIGURACIÓN ---
    FRAME_WIDTH, FRAME_HEIGHT = 960, 720

    # Conectar al Dron
    drone = Tello()
    drone.connect()
    print(f"Batería: {drone.get_battery()}%")
    drone.streamon()
    frame_read = drone.get_frame_read()

    # Crear instancias de nuestros módulos
    controlador = ControladorVuelo(drone)
    horizonte = HorizonteArtificial(width=FRAME_WIDTH, height=FRAME_HEIGHT)

    running = True

    # --- 2. BUCLE PRINCIPAL ---
    try:
        while running:
            # La lógica de control ahora está encapsulada en esta simple llamada.
            # Si retorna False, salimos del bucle.
            running = controlador.manejar_eventos_teclado()

            # Obtener y mostrar el video
            frame = frame_read.frame
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

            # Dibujar el horizonte artificial
            roll = drone.get_roll()
            pitch = drone.get_pitch()
            horizonte.draw(frame, roll, pitch)

            # Mostrar telemetría en pantalla
            cv2.putText(frame, f"Roll: {roll:.1f} Pitch: {pitch:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.imshow("Tello Main Display", frame)
            cv2.waitKey(1)

            # Limitar la velocidad del bucle para no sobrecargar la CPU
            time.sleep(1 / 60)  # Apuntar a 60 FPS

    finally:
        # --- 3. LIMPIEZA ---
        print("Cerrando el programa...")
        controlador.cleanup()
        drone.streamoff()
        drone.end()
        cv2.destroyAllWindows()
        print("Programa cerrado correctamente.")


if __name__ == "__main__":
    main()