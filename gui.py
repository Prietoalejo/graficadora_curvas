# gui.py
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QDoubleSpinBox, QCheckBox, QPushButton, QGridLayout, QGroupBox, QMessageBox
from PyQt5.QtCore import Qt

from function_parse import parse_function # Importa tu parser
from plotter import CurvePlotter # Importa tu plotter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gratificadora de Curvas de Nivel 2D")
        self.setGeometry(100, 100, 800, 600) # x, y, ancho, alto inicial

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # AHORA SÍ: Instanciar el plotter
        self.plotter = CurvePlotter(self) # Pasa self como parent

        self.init_ui()

    def init_ui(self):
        self.controls_group_box = QGroupBox("Define tu Curva de Nivel")
        control_layout = QGridLayout()

        # Fila 0: Función f(x, y)
        control_layout.addWidget(QLabel("Función f(x, y):"), 0, 0)
        self.function_input = QLineEdit("x**2 + y**2")
        self.function_input.setPlaceholderText("Ej: x**2 + y**2")
        control_layout.addWidget(self.function_input, 0, 1)

        # Fila 1: Valor constante para N
        control_layout.addWidget(QLabel("Valor constante N:"), 1, 0)
        self.n_value_input = QDoubleSpinBox()
        self.n_value_input.setRange(-1000.0, 1000.0)
        self.n_value_input.setValue(0.0)
        control_layout.addWidget(self.n_value_input, 1, 1)

        # Fila 2: Checkbox Mantener Rastro
        self.leave_trace_checkbox = QCheckBox("Mantener rastro (para animación)")
        self.leave_trace_checkbox.setChecked(True)
        control_layout.addWidget(self.leave_trace_checkbox, 2, 0, 1, 2)

        # Fila 3: Control de velocidad de animación
        from PyQt5.QtWidgets import QComboBox
        control_layout.addWidget(QLabel("Velocidad animación:"), 3, 0)
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["x0.5", "x1", "x1.5", "x2"])
        self.speed_combo.setCurrentIndex(1)
        control_layout.addWidget(self.speed_combo, 3, 1)

        # Fila 4: Botón de Graficar y Animar
        self.plot_button = QPushButton("Graficar")
        self.plot_button.clicked.connect(self.on_plot_button_clicked)
        self.animate_button = QPushButton("Animar")
        self.animate_button.clicked.connect(self.on_animate_button_clicked)
        control_layout.addWidget(self.plot_button, 4, 0)
        control_layout.addWidget(self.animate_button, 4, 1)

        # Fila 5: Botón de Detener animación
        self.stop_button = QPushButton("Detener animación")
        self.stop_button.clicked.connect(self.on_stop_button_clicked)
        control_layout.addWidget(self.stop_button, 5, 0, 1, 2)

        # Asignar el layout al group box
        self.controls_group_box.setLayout(control_layout)

        # Limpiar el layout principal antes de agregar widgets (por si se reinicializa)
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Agregar los widgets al layout principal
        self.main_layout.addWidget(self.controls_group_box)
        self.main_layout.addWidget(self.plotter, stretch=1)
        # No es necesario addStretch si el plotter tiene stretch
    def on_plot_button_clicked(self):
        func_str = self.function_input.text()
        n_value = self.n_value_input.value()
        parsed_func, error_message = parse_function(func_str)
        if parsed_func:
            try:
                self.plotter.draw_single_curve(parsed_func, n_value)
            except Exception as e:
                print(f"Error al graficar estáticamente: {e}")
        else:
            print(f"Error de parseo: {error_message}")


    def on_stop_button_clicked(self):
        self.plotter.stop_animation()

    def on_animate_button_clicked(self):
        print("--- Botón 'Graficar / Animar' clickeado ---")
        func_str = self.function_input.text()
        n_value = self.n_value_input.value()
        trace_enabled = self.leave_trace_checkbox.isChecked()
        speed_str = self.speed_combo.currentText()
        speed_map = {"x0.5": 200, "x1": 100, "x1.5": 66, "x2": 50}
        interval = speed_map.get(speed_str, 100)

        print(f"Función ingresada: {func_str}")
        print(f"Valor constante de N: {n_value}")
        print(f"Mantener rastro: {'Sí' if trace_enabled else 'No'}")
        print(f"Velocidad animación: {speed_str} ({interval} ms por frame)")

        # --- Lógica de parseo de la función ---
        parsed_func, error_message = parse_function(func_str)

        if parsed_func:
            print("Función parseada correctamente. ¡Graficando curva estática!")
            try:
                # Animar la curva de nivel con los parámetros
                self.plotter.animate_curves(parsed_func, n_value, trace_enabled, interval)

            except Exception as e:
                print(f"Error al intentar graficar: {e}")
                QMessageBox.critical(self, "Error de Graficado", f"Ocurrió un error al intentar dibujar la curva: {e}")

