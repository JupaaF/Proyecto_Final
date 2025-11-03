import sys
from PySide6.QtWidgets import QApplication
from src.interface.controllers.main_window_controller import MainWindowController

def main():
    """Punto de entrada principal de la aplicación."""
    app = QApplication(sys.argv)
    window = MainWindowController()
    window.show()
    sys.exit(app.exec())