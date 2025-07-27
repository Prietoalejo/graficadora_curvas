
Proyecto: Gratificadora de Curvas de Nivel 2D (Tipo GeoGebra)
Este proyecto desarrolla una aplicación de escritorio en Python para visualizar curvas de nivel. Permite a los usuarios ingresar una función f(x,y), definir rangos de visualización y un parámetro de animación (n), y generar un GIF animado del desplazamiento de las curvas. Incluye una opción para dejar un "rastro" visual de las curvas anteriores.

Stack Tecnológico
GUI: PyQt6

Manejo de Función: Python nativo (eval() seguro)

Cálculo Numérico: NumPy

Visualización y Animación: Matplotlib

Exportación de GIFs: Pillow (dependencia de Matplotlib)

Fases de Desarrollo
El proyecto se construirá en las siguientes fases, cada una con objetivos claros y pasos específicos.

Fase 1: Configuración Inicial y GUI Mínima
Objetivo: La ventana principal con todos los elementos de entrada listos, sin funcionalidad matemática.

1.1. Configuración del Entorno:

Crear la carpeta del proyecto (gratificadora_curvas/).

Crear y activar un entorno virtual.

Instalar PyQt6, matplotlib, numpy, pillow.

Crear requirements.txt.

Crear archivos vacíos: main.py, gui.py, plotter.py, function_parser.py.

1.2. Ventana Principal y Widgets:

En gui.py, definir MainWindow (heredando de QtWidgets.QMainWindow).

Añadir:

QLabel y QLineEdit para la función f(x,y).

QDoubleSpinBox para rangos de n (n_start, n_end) y num_steps.

QDoubleSpinBox para rangos de visualización (x_min, x_max, y_min, y_max).

QCheckBox para "Mantener Rastro".

QPushButton para "Graficar/Animar".

Organizar widgets con QVBoxLayout o QGridLayout.

En main.py, inicializar QApplication y MainWindow para mostrarla.

Prueba: Ejecutar main.py y verificar que la ventana y todos los campos son visibles.

Fase 2: Parseo Seguro de la Función
Objetivo: La aplicación debe entender y evaluar la función ingresada por el usuario de forma segura.

2.1. Implementación de function_parser.py:

Definir una función que reciba la cadena de la función (func_str).

Implementar eval() seguro: crear un safe_dict con funciones matemáticas de numpy (ej., np.sin, np.cos, np.sqrt, np.pi, etc.).

Usar try-except para capturar errores de sintaxis.

Devolver una función callable (ej., lambda) que acepte arrays x, y de NumPy y retorne f(x, y).

2.2. Conexión Básica con GUI (Prueba):

Modificar el botón "Graficar/Animar" en gui.py: al clickear, debe tomar el texto de la función, pasarlo al function_parser, e imprimir en consola el éxito o error del parseo.

Prueba: Ingresar funciones válidas e inválidas para confirmar que el parser las maneja correctamente.

Fase 3: Graficado Estático de una Curva de Nivel
Objetivo: Incrustar Matplotlib en la GUI y mostrar una única curva de nivel.

3.1. Configuración de Matplotlib en plotter.py:

En la clase CurvePlotter, inicializar una figura y ejes de Matplotlib.

Aprender a incrustar FigureCanvasQTAgg de Matplotlib en un widget de PyQt.

3.2. Dibujo de una Única Curva:

En plotter.py, añadir el método draw_single_curve(self, func_callable, x_range, y_range, n_value).

Dentro del método:

Crear malla X, Y con np.meshgrid (usando x_range, y_range).

Evaluar func_callable para obtener Z = f(X, Y).

Usar self.ax.contour(X, Y, Z, levels=[n_value]) para dibujar la curva.

Limpiar ejes (self.ax.clear()) antes de dibujar.

Llamar a self.canvas.draw() para actualizar la GUI.

3.3. Conexión GUI - Plotter:

Modificar el botón "Graficar/Animar" en gui.py: después del parseo, llamar a self.plotter.draw_single_curve() usando n_start como valor fijo.

Prueba: Ejecutar la aplicación, ingresar una función y rangos, y verificar que una curva de nivel se dibuja en la ventana.

Fase 4: Animación y Rastro
Objetivo: Implementar la animación de curvas de nivel a través de n y la funcionalidad de "rastro".

4.1. Implementación de Animación en plotter.py:

Implementar animate_curves(self, func_callable, x_range, y_range, n_start, n_end, num_steps, leave_trace).

Calcular la secuencia de valores de n para la animación.

Definir la función update_frame(frame_index):

Obtener n_value para el frame_index actual.

Evaluar Z = f(X, Y).

Lógica de Rastro:

Si leave_trace es False, limpiar el eje.

Si leave_trace es True, NO limpiar el eje; dibujar todas las curvas desde el inicio hasta el n_value actual.

Dibujar curvas de nivel con self.ax.contour(...).

Actualizar el título del eje con el n_value actual.

Usar matplotlib.animation.FuncAnimation para crear la animación.

Almacenar referencia a la animación (self.animation = ...) para evitar que se detenga.

4.2. Conexión Completa GUI - Plotter:

Modificar el botón "Graficar/Animar" en gui.py: llamar a self.plotter.animate_curves() con todos los parámetros necesarios.

Añadir manejo de errores y mensajes de estado en la GUI (ej., "Generando animación...").

Prueba: Ejecutar, ingresar datos, y experimentar la animación con y sin la opción de rastro.

Fase 5: Exportación a GIF y Pulido
Objetivo: Permitir guardar la animación como GIF y mejorar la experiencia de usuario final.

5.1. Guardar Animación como GIF:

Dentro de animate_curves en plotter.py, usar anim.save('animation.gif', writer='pillow', fps=10). Considerar un diálogo de guardado.

5.2. Mejoras de Interfaz y Usabilidad:

Añadir QLabels claras para todos los campos de entrada.

Implementar QMessageBox para errores (ej., "Función inválida") y mensajes de éxito (ej., "GIF guardado").

Asegurar un diseño de ventana limpio y profesional.

Opcional: añadir un botón "Exportar GIF" separado para mayor control del usuario.