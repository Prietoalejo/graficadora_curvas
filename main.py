
"""
Archivo principal de arranque de la aplicación.
Inicializa la interfaz gráfica y lanza la ventana principal.
Este es el punto de entrada del programa: solo ejecuta main.py para usar la graficadora.
"""

import sys
from PyQt5.QtWidgets import QApplication
from gui import MainWindow

def main():
    """
    Función principal que crea la aplicación Qt y muestra la ventana principal.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()