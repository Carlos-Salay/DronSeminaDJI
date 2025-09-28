# --- archivo: controlador_dron.py ---

from djitellopy import Tello
import time
import threading  # <-- 1. Importamos las librerías necesarias
import queue


class ControladorDron:
    def __init__(self):
        self.tello = Tello()
        print("ControladorDron: Conectando con el Tello...")
        self.tello.connect()
        print("ControladorDron: Conexión exitosa!")
        print(f"Batería: {self.tello.get_battery()}%")
        self.tello.streamon()
        print("ControladorDron: Flujo de video activado.")

        self.velocidad = 50
        self.tiempo_ultimo_comando = 0
        self.intervalo_comando = 0.04

        # --- 2. Novedad: Creamos una cola para los comandos bloqueantes ---
        self.command_queue = queue.Queue()

        # --- 3. Novedad: Creamos y arrancamos el hilo "asistente" ---
        self.worker_thread = threading.Thread(target=self._command_worker, daemon=True)
        self.worker_thread.start()

    def _command_worker(self):
        """
        Este es el "asistente". Se ejecuta en segundo plano, esperando tareas.
        """
        while True:
            # Espera hasta que llegue un comando a la cola
            command = self.command_queue.get()
            if command == "takeoff":
                print("Worker: Recibido comando de despegue.")
                self.tello.takeoff()
                print("Worker: Despegue completado.")
            elif command == "land":
                print("Worker: Recibido comando de aterrizaje.")
                self.tello.land()
                print("Worker: Aterrizaje completado.")

            # Avisa que la tarea ha terminado
            self.command_queue.task_done()

    def get_frame(self):
        return self.tello.get_frame_read().frame

    def get_telemetry(self):
        return {
            'roll': self.tello.get_roll(),
            'pitch': self.tello.get_pitch(),
            'height': self.tello.get_height()
        }

    def manejar_teclado(self, key):
        adelante_atras, izquierda_derecha, arriba_abajo, rotacion = 0, 0, 0, 0

        if key == ord('w'):
            adelante_atras = self.velocidad
        elif key == ord('s'):
            adelante_atras = -self.velocidad
        if key == ord('a'):
            izquierda_derecha = -self.velocidad
        elif key == ord('d'):
            izquierda_derecha = self.velocidad
        if key == ord('e'):
            rotacion = self.velocidad
        elif key == ord('q'):
            rotacion = -self.velocidad
        if key == ord('r'):
            arriba_abajo = self.velocidad
        elif key == ord('f'):
            arriba_abajo = -self.velocidad

        tiempo_actual = time.time()
        if tiempo_actual - self.tiempo_ultimo_comando > self.intervalo_comando:
            self.tello.send_rc_control(izquierda_derecha, adelante_atras, arriba_abajo, rotacion)
            self.tiempo_ultimo_comando = tiempo_actual

        # --- 4. Novedad: En lugar de ejecutar los comandos, los enviamos a la cola ---
        if key == ord('t'):
            print("Main: Enviando comando 'takeoff' a la cola.")
            self.command_queue.put("takeoff")
        elif key == ord('l'):
            print("Main: Enviando comando 'land' a la cola.")
            self.command_queue.put("land")

    def cleanup(self):
        print("ControladorDron: Realizando limpieza...")
        # Aseguramos que el dron aterrice de forma segura al salir
        if self.tello.is_flying:
            self.command_queue.put("land")
            # Damos un momento para que el comando se procese
            time.sleep(4)

        self.tello.streamoff()
        self.tello.end()
        print("ControladorDron: Conexión cerrada.")