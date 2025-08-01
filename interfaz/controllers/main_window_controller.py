import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QFile, QTextStream
from PySide6.QtUiTools import QUiLoader

class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()

        # Cargar la interfaz desde el archivo .ui
        loader = QUiLoader()
        self.ui = loader.load("interfaz/ui/main_window_dock.ui", self)

        # Cargar los estilos QSS
        self.load_styles()

        # Conectar la acción del menú
        self.ui.actionModo_Oscuro.triggered.connect(self.toggle_theme)

        # Establecer el tema inicial (claro por defecto)
        self.set_theme(dark_mode=False)

        # Conectar los docks al menú "Ver"
        self.setup_view_menu()

    def load_styles(self):
        # Cargar tema claro
        light_theme_file = QFile("interfaz/resources/light_theme.qss")
        light_theme_file.open(QFile.ReadOnly | QFile.Text)
        self.light_theme = QTextStream(light_theme_file).readAll()
        light_theme_file.close()

        # Cargar tema oscuro
        dark_theme_file = QFile("interfaz/resources/dark_theme.qss")
        dark_theme_file.open(QFile.ReadOnly | QFile.Text)
        self.dark_theme = QTextStream(dark_theme_file).readAll()
        dark_theme_file.close()

    def set_theme(self, dark_mode):
        if dark_mode:
            self.ui.setStyleSheet(self.dark_theme)
            self.ui.actionModo_Oscuro.setChecked(True)
        else:
            self.ui.setStyleSheet(self.light_theme)
            self.ui.actionModo_Oscuro.setChecked(False)

    def toggle_theme(self):
        # Cambiar al tema opuesto del estado actual del menú
        self.set_theme(self.ui.actionModo_Oscuro.isChecked())

    def setup_view_menu(self):
        # Permite mostrar/ocultar los docks desde el menú "Ver"
        self.ui.menuVer.addAction(self.ui.fileBrowserDock.toggleViewAction())
        self.ui.menuVer.addAction(self.ui.parameterEditorDock.toggleViewAction())
        self.ui.menuVer.addAction(self.ui.logDock.toggleViewAction())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindowController()
    window.ui.show()
    sys.exit(app.exec())