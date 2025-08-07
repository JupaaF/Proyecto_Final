import sys
from pathlib import Path

# Añade el directorio raíz del proyecto a sys.path
# Esto permite importar módulos de scripts/ y otros directorios hermanos de src/
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from PySide6.QtWidgets import QApplication
from interface.controllers.main_window_controller import MainWindowController

def main():
    """Punto de entrada principal de la aplicación."""
    app = QApplication(sys.argv)
    window = MainWindowController()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()