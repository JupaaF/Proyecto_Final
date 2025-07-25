
# main.py
import sys
from PySide6.QtWidgets import QApplication
from interfaz.controllers.main_window_controller import MainWindowController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Crea una instancia del controlador principal
    main_controller = MainWindowController()
    
    # Le pide al controlador que muestre la ventana que gestiona
    main_controller.show()
    
    sys.exit(app.exec())
