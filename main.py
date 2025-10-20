# --- archivo: main.py (Versión final con todas las mejoras) ---

import pygame
import cv2
import numpy as np
import time
from djitellopy import Tello
from horizonte_artificial import HorizonteArtificial

# --- Constantes de configuración ---
FRAME_WIDTH = 800
FRAME_HEIGHT = 600
FPS = 60  # Puedes ajustarlo si tu sistema lo soporta bien
VELOCIDAD = 60  # Velocidad de movimiento del dron


class TelloApp:
    def __init__(self):
        # 1. Inicializar Pygame
        pygame.init()
        pygame.display.set_caption("Tello Control Center")
        self.screen = pygame.display.set_mode([FRAME_WIDTH, FRAME_HEIGHT])

        # 2. Conectar con el Tello
        self.tello = Tello()
        self.tello.connect()
        self.tello.set_speed(VELOCIDAD)
        self.tello.streamon()
        self.frame_read = self.tello.get_frame_read()

        # 3. Inicializar el Horizonte Artificial
        self.horizonte = HorizonteArtificial(width=FRAME_WIDTH, height=FRAME_HEIGHT)

        # 4. Variables de control
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.send_rc_control = False

        # Timer para enviar comandos de forma continua
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // FPS)

    def run(self):
        """ Bucle principal de la aplicación """
        should_stop = False
        while not should_stop:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.update()
                elif event.type == pygame.QUIT:
                    should_stop = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        should_stop = True
                    else:
                        self.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)

            if self.frame_read.stopped:
                should_stop = True
                continue

            # --- Procesamiento de video y dibujo ---
            self.screen.fill([0, 0, 0])
            frame = self.frame_read.frame

            # Redimensionar frame
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

            # Obtener telemetría para el horizonte
            roll = self.tello.get_roll()
            pitch = self.tello.get_pitch()

            # Dibujar el horizonte artificial
            self.horizonte.draw(frame, roll, pitch)

            # --- Obtener y mostrar la temperatura ---
            temp_text = f"Temperatura: {self.tello.get_temperature()} C"
            cv2.putText(frame, temp_text, (10, FRAME_HEIGHT - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Mostrar información de batería
            battery_text = f"Bateria: {self.tello.get_battery()}%"
            cv2.putText(frame, battery_text, (10, FRAME_HEIGHT - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Preparar y mostrar el frame en la ventana de Pygame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pygame = np.rot90(frame_rgb)
            frame_pygame = np.flipud(frame_pygame)
            surface = pygame.surfarray.make_surface(frame_pygame)

            self.screen.blit(surface, (0, 0))
            pygame.display.update()

            time.sleep(1 / FPS)

        # --- Limpieza al salir ---
        self.tello.end()
        pygame.quit()

    def keydown(self, key):
        """Maneja el evento de presionar una tecla."""
        if key == pygame.K_w:
            self.for_back_velocity = VELOCIDAD
        elif key == pygame.K_s:
            self.for_back_velocity = -VELOCIDAD
        elif key == pygame.K_a:
            self.left_right_velocity = -VELOCIDAD
        elif key == pygame.K_d:
            self.left_right_velocity = VELOCIDAD
        elif key == pygame.K_r:
            self.up_down_velocity = VELOCIDAD
        elif key == pygame.K_f:
            self.up_down_velocity = -VELOCIDAD
        elif key == pygame.K_q:
            self.yaw_velocity = -VELOCIDAD
        elif key == pygame.K_e:
            self.yaw_velocity = VELOCIDAD

    def keyup(self, key):
        """Maneja el evento de soltar una tecla con manejo de errores."""
        if key in [pygame.K_w, pygame.K_s]:
            self.for_back_velocity = 0
        elif key in [pygame.K_a, pygame.K_d]:
            self.left_right_velocity = 0
        elif key in [pygame.K_r, pygame.K_f]:
            self.up_down_velocity = 0
        elif key in [pygame.K_q, pygame.K_e]:
            self.yaw_velocity = 0
        elif key == pygame.K_t:  # Despegar
            try:
                print("Intentando despegar...")
                self.tello.takeoff()
                self.send_rc_control = True
                print("¡Despegue exitoso!")
            except Exception as e:
                print(f"Error al despegar: {e}")
                print(
                    "Posibles causas: sobrecalentamiento, batería baja o mala conexión. Intenta de nuevo en un momento.")
                self.send_rc_control = False
        elif key == pygame.K_l:  # Aterrizar
            try:
                print("Intentando aterrizar...")
                self.tello.land()
                self.send_rc_control = False
                print("Aterrizaje completado.")
            except Exception as e:
                print(f"Ocurrió un error al aterrizar: {e}")

    def update(self):
        """Envía los comandos de control al dron si está en modo de vuelo."""
        if self.send_rc_control:
            self.tello.send_rc_control(
                self.left_right_velocity,
                self.for_back_velocity,
                self.up_down_velocity,
                self.yaw_velocity
            )
def main():
    app = TelloApp()
    app.run()


if __name__ == '__main__':
    main()