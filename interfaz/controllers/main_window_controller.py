import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog
from PySide6.QtCore import QFile, QTextStream
from PySide6.QtUiTools import QUiLoader
from file_handler.file_handler import fileHandler

# Importar el controlador del asistente
from .simulation_wizard_controller import SimulationWizardController

class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()

        # Cargar la interfaz desde el archivo .ui
        loader = QUiLoader()
        self.ui = loader.load("interfaz/ui/main_window_dock.ui")
        self.setCentralWidget(self.ui)

        # Cargar los estilos QSS
        self.load_styles()

        # Conectar acciones del menú
        self.ui.actionModo_Oscuro.triggered.connect(self.toggle_theme)
        self.ui.actionNueva_Simulacion.triggered.connect(self.open_new_simulation_wizard)

        # Establecer el tema inicial (claro por defecto)
        self.set_theme(dark_mode=False)

        # Conectar los docks al menú "Ver"
        self.setup_view_menu()

    def open_new_simulation_wizard(self):
        """Abre el asistente para crear una nueva simulación."""
        wizard = SimulationWizardController(self)
        # Usamos exec() para abrir el wizard como un diálogo modal
        if wizard.exec() == QDialog.Accepted:
            data = wizard.get_data()
            file_handler = fileHandler(data["case_name"],data["template"])
            # Aquí es donde se llamaría a file_handler para crear los archivos del caso
        else:
            print("Asistente cancelado por el usuario.")

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
