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
        if hasattr(self, 'animation') and self.animation:
            try:
                self.animation.event_source.stop()
            except Exception:
                pass
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
        self.ax.set_xlabel(f"X  [{self.x_min}, {self.x_max}]")
        self.ax.set_ylabel(f"Y  [{self.y_min}, {self.y_max}]")
        self.ax.grid(True, which='both', color='gray', linestyle='--', linewidth=0.7, alpha=0.5)
        self.ax.set_xlim(self.x_min, self.x_max)
        self.ax.set_ylim(self.y_min, self.y_max)
        self.ax.set_aspect('equal', adjustable='box') # Mantener aspecto igual
        # Mostrar los valores de los ticks en los ejes
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        self.ax.yaxis.set_major_locator(plt.MaxNLocator(10))

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

            self.ax.set_title(f"Curva de Nivel: N = {n_value:.2f} | X:[{self.x_min},{self.x_max}] Y:[{self.y_min},{self.y_max}]")

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
        self.ax.set_xlabel(f"X  [{self.x_min}, {self.x_max}]")
        self.ax.set_ylabel(f"Y  [{self.y_min}, {self.y_max}]")
        self.ax.grid(True, which='both', color='gray', linestyle='--', linewidth=0.7, alpha=0.5)
        self.ax.set_xlim(self.x_min, self.x_max)
        self.ax.set_ylim(self.y_min, self.y_max)
        self.ax.set_aspect('equal', adjustable='box')

        x = np.linspace(self.x_min, self.x_max, 400)
        y = np.linspace(self.y_min, self.y_max, 400)
        X, Y = np.meshgrid(x, y)

        # Definir rango de N: de 0 a n_value, luego de n_value a -n_value, ida y vuelta
        num_frames = 20  # Menos frames para mayor separación
        n_max = abs(n_value)
        n_min = -abs(n_value)
        # Usar un paso mayor para N
        step = (n_max - n_min) / num_frames if num_frames > 0 else 1
        n_values_forward = np.arange(0, n_max + step, step)
        n_values_backward = np.arange(n_max, n_min - step, -step)
        n_values_return = np.arange(n_min, 0 + step, step)
        n_values = np.concatenate([n_values_forward, n_values_backward, n_values_return])

        # Filtrar valores de N donde sí existe curva (no da error al graficar)

        valid_n_values = []
        seen = set()
        for n in n_values:
            n_rounded = round(n, 3)  # Redondear para evitar duplicados por precisión
            if n_rounded in seen:
                continue
            try:
                Z = func_callable(X, Y)
                cs = self.ax.contour(X, Y, Z, levels=[n])
                if len(cs.allsegs[0]) > 0:
                    valid_n_values.append(n_rounded)
                    seen.add(n_rounded)
                plt.close(cs.figure)
            except Exception:
                continue
        valid_n_values = sorted(valid_n_values)
        # Generar ciclo completo: origen -> max -> min -> origen
        if 0 not in valid_n_values:
            valid_n_values.append(0)
        valid_n_values = sorted(set(valid_n_values))
        ciclo = valid_n_values + valid_n_values[::-1][1:]  # ida y vuelta, sin repetir el origen
        self.ax.clear()

        def update(frame):
            if frame >= len(ciclo):
                return
            self.ax.clear()
            n_actual = ciclo[frame]
            try:
                Z = func_callable(X, Y)
                if leave_trace:
                    # Dibujar todas las curvas anteriores con color tenue
                    levels_rastro = sorted(set(ciclo[:frame]))
                    if levels_rastro:
                        self.ax.contour(X, Y, Z, levels=levels_rastro, colors='blue', alpha=0.3, linewidths=1)
                    # Dibujar la curva actual con color normal
                    self.ax.contour(X, Y, Z, levels=[n_actual], colors='blue', alpha=1.0, linewidths=2)
                    self.ax.set_title(f"Animación Curva de Nivel: N = {n_actual:.2f}")
                else:
                    self.ax.contour(X, Y, Z, levels=[n_actual], colors='blue', alpha=1.0, linewidths=2)
                    self.ax.set_title(f"Animación Curva de Nivel: N = {n_actual:.2f}")
            except Exception:
                self.ax.text(0.5, 0.5, f"No existe curva para N = {n_actual:.2f}",
                             horizontalalignment='center', verticalalignment='center',
                             transform=self.ax.transAxes, color='red', fontsize=12)
            self.canvas.draw()

        self.animation = animation.FuncAnimation(self.figure, update, frames=len(ciclo), interval=interval, repeat=False)
        self.canvas.draw()