# --- archivo: main.py (Adaptado para Pygame) ---

import cv2
import pygame
from controlador_dron import ControladorDron
from horizonte_artificial import HorizonteArtificial

FRAME_WIDTH = 960
FRAME_HEIGHT = 720


def main():
    # 1. Inicializar Pygame para capturar eventos de teclado
    pygame.init()
    # No necesitamos una ventana grande, solo la necesitamos para que Pygame funcione
    screen = pygame.display.set_mode((200, 200))
    pygame.display.set_caption("Tello Keyboard Input")

    # 2. Inicializar los componentes del dron
    dron = ControladorDron()
    horizonte = HorizonteArtificial(width=FRAME_WIDTH, height=FRAME_HEIGHT)

    running = True
    try:
        while running:
            # 3. Bucle de eventos de Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # Si se presiona ESC, salimos
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        dron.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    dron.keyup(event.key)

            # --- El resto del código es casi igual ---

            frame = dron.get_frame()
            if frame is None or frame.size == 0:
                continue

            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            telemetry = dron.get_telemetry()

            # 4. Actualizar el estado del dron continuamente
            dron.update()

            # 5. Dibujar los elementos visuales
            horizonte.draw(frame, telemetry['roll'], telemetry['pitch'])
            cv2.putText(frame, f"Roll: {telemetry['roll']:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0),
                        2)
            cv2.putText(frame, f"Pitch: {telemetry['pitch']:.1f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0),
                        2)

            # 6. Mostrar el frame con OpenCV
            cv2.imshow("Tello Control Center", frame)

            # Pequeña pausa para evitar sobrecargar la CPU y para que OpenCV procese la ventana
            cv2.waitKey(1)

    except Exception as e:
        print(f"Ocurrió un error en el bucle principal: {e}")
    finally:
        # 7. Limpiar los recursos al salir
        dron.cleanup()
        cv2.destroyAllWindows()
        pygame.quit()


if __name__ == "__main__":
    main()