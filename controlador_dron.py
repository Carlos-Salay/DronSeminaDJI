# --- archivo: controlador_dron.py (Corregido para control fluido) ---

from djitellopy import Tello
import time
import threading
import queue
import pygame  # Importamos pygame para las constantes de teclas


class ControladorDron:
    def __init__(self):
        self.tello = Tello()
        print("ControladorDron: Conectando con el Tello...")
        self.tello.connect()
        print("ControladorDron: Conexión exitosa!")
        print(f"Batería: {self.tello.get_battery()}%")
        self.tello.streamon()
        print("ControladorDron: Flujo de video activado.")

        self.velocidad = 60
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.send_rc_control = False

        self.command_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._command_worker, daemon=True)
        self.worker_thread.start()

    def _command_worker(self):
        while True:
            command = self.command_queue.get()
            if command == "takeoff":
                print("Worker: Recibido comando de despegue.")
                self.tello.takeoff()
                self.send_rc_control = True
                print("Worker: Despegue completado.")
            elif command == "land":
                print("Worker: Recibido comando de aterrizaje.")
                self.tello.land()
                self.send_rc_control = False
                print("Worker: Aterrizaje completado.")
            self.command_queue.task_done()

    def get_frame(self):
        return self.tello.get_frame_read().frame

    def get_telemetry(self):
        return {
            'roll': self.tello.get_roll(),
            'pitch': self.tello.get_pitch(),
            'height': self.tello.get_height()
        }

    def keydown(self, key):
        """Actualiza las velocidades basado en la tecla PRESIONADA."""
        if key == pygame.K_w:
            self.for_back_velocity = self.velocidad
        elif key == pygame.K_s:
            self.for_back_velocity = -self.velocidad
        elif key == pygame.K_a:
            self.left_right_velocity = -self.velocidad
        elif key == pygame.K_d:
            self.left_right_velocity = self.velocidad
        elif key == pygame.K_r:
            self.up_down_velocity = self.velocidad
        elif key == pygame.K_f:
            self.up_down_velocity = -self.velocidad
        elif key == pygame.K_q:
            self.yaw_velocity = -self.velocidad
        elif key == pygame.K_e:
            self.yaw_velocity = self.velocidad

    def keyup(self, key):
        """Resetea las velocidades basado en la tecla LIBERADA."""
        if key == pygame.K_w or key == pygame.K_s:
            self.for_back_velocity = 0
        elif key == pygame.K_a or key == pygame.K_d:
            self.left_right_velocity = 0
        elif key == pygame.K_r or key == pygame.K_f:
            self.up_down_velocity = 0
        elif key == pygame.K_q or key == pygame.K_e:
            self.yaw_velocity = 0

        # Comandos de despegue y aterrizaje (se ejecutan al soltar la tecla)
        elif key == pygame.K_t:
            self.command_queue.put("takeoff")
        elif key == pygame.K_l:
            self.command_queue.put("land")

    def update(self):
        """ Envía las velocidades actuales al Tello. Debe llamarse continuamente. """
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity,
                                       self.up_down_velocity, self.yaw_velocity)

    def cleanup(self):
        print("ControladorDron: Realizando limpieza...")
        if self.tello.is_flying:
            self.command_queue.put("land")
            time.sleep(4)
        self.tello.streamoff()
        self.tello.end()
        print("ControladorDron: Conexión cerrada.")