# plotter.py
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib
matplotlib.use('Qt5Agg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, QObject

# Clase worker para animación en hilo separado
class AnimationWorker(QObject):
    update_signal = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, num_frames, interval, parent=None):
        super().__init__(parent)
        self.num_frames = num_frames
        self.interval = interval
        self._running = True

    def run(self):
        import time
        for frame in range(self.num_frames):
            if not self._running:
                break
            self.update_signal.emit(frame)
            time.sleep(self.interval / 1000.0)
        self.finished.emit()

    def stop(self):
        self._running = False

# Clase principal para graficar curvas
class CurvePlotter(QWidget):
    def stop_animation(self):
        if hasattr(self, 'worker') and self.worker:
            self.worker.stop()
            self.worker = None
        if hasattr(self, 'worker_thread') and self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None
        self.animation = None
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111) # 1x1 grid, first subplot

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        # Configuracion inicial del eje
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True)
        # Establecer límites fijos para X e Y (ya que el usuario no los controla)
        self.x_min, self.x_max = -10.0, 10.0
        self.y_min, self.y_max = -10.0, 10.0
        self.ax.set_xlim(self.x_min, self.x_max)
        self.ax.set_ylim(self.y_min, self.y_max)
        self.ax.set_aspect('equal', adjustable='box') # Para que las escalas X e Y sean iguales

        self.animation = None # Para almacenar la referencia a la animación

    def draw_single_curve(self, func_callable, n_value):
        """
        Dibuja una única curva de nivel f(x, y) = n_value.

        Args:
            func_callable (callable): La función parseada f(x, y).
            n_value (float): El valor constante de la curva de nivel.
        """
        # Limpiar los ejes antes de dibujar una nueva curva
        self.ax.clear()
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True)
        self.ax.set_xlim(self.x_min, self.x_max)
        self.ax.set_ylim(self.y_min, self.y_max)
        self.ax.set_aspect('equal', adjustable='box') # Mantener aspecto igual

        # Crear malla de puntos
        x = np.linspace(self.x_min, self.x_max, 400) # 400 puntos en X
        y = np.linspace(self.y_min, self.y_max, 400) # 400 puntos en Y
        X, Y = np.meshgrid(x, y)

        try:
            # Evaluar la función sobre la malla
            Z = func_callable(X, Y)

            # Dibujar la curva de nivel para el valor de N
            # Se usa .collections[0] si solo esperas una línea y quieres acceder a ella,
            # pero contour devuelve un objeto ContourSet.
            # Para una única línea, 'levels=[n_value]' es la clave.
            self.ax.contour(X, Y, Z, levels=[n_value], colors='blue') # Dibujar la curva

            self.ax.set_title(f"Curva de Nivel: N = {n_value:.2f}")

        except Exception as e:
            # Manejar errores durante la evaluación o graficado
            self.ax.text(0.5, 0.5, f"Error al graficar:\n{e}",
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax.transAxes, color='red', fontsize=12)
            print(f"Error en draw_single_curve: {e}")

        # Dibujar (actualizar) el canvas de Matplotlib en la GUI
        self.canvas.draw()

    def animate_curves(self, func_callable, n_value, leave_trace, interval):
        import matplotlib.animation as animation
        self.ax.clear()
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True)
        self.ax.set_xlim(self.x_min, self.x_max)
        self.ax.set_ylim(self.y_min, self.y_max)
        self.ax.set_aspect('equal', adjustable='box')

        x = np.linspace(self.x_min, self.x_max, 400)
        y = np.linspace(self.y_min, self.y_max, 400)
        X, Y = np.meshgrid(x, y)

        n_start = -abs(n_value)
        n_end = abs(n_value)
        num_frames = 50
        n_values = np.linspace(n_start, n_end, num_frames)

        def update(frame):
            if not leave_trace:
                self.ax.clear()
                self.ax.set_xlabel("X")
                self.ax.set_ylabel("Y")
                self.ax.grid(True)
                self.ax.set_xlim(self.x_min, self.x_max)
                self.ax.set_ylim(self.y_min, self.y_max)
                self.ax.set_aspect('equal', adjustable='box')
            try:
                Z = func_callable(X, Y)
                if leave_trace:
                    for i in range(frame + 1):
                        self.ax.contour(X, Y, Z, levels=[n_values[i]], colors='blue', alpha=0.5)
                else:
                    self.ax.contour(X, Y, Z, levels=[n_values[frame]], colors='blue')
                self.ax.set_title(f"Animación Curva de Nivel: N = {n_values[frame]:.2f}")
            except Exception as e:
                self.ax.text(0.5, 0.5, f"Error al graficar:\n{e}",
                             horizontalalignment='center', verticalalignment='center',
                             transform=self.ax.transAxes, color='red', fontsize=12)
            self.canvas.draw()

        self.animation = animation.FuncAnimation(self.figure, update, frames=num_frames, interval=interval, repeat=False)
        self.canvas.draw()