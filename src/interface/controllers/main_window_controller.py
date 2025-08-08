
import shutil
from pathlib import Path

from PySide6.QtWidgets import (QMainWindow, QDialog, QMessageBox, QVBoxLayout)
from PySide6.QtCore import QUrl, QTimer
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QDesktopServices

from config import RUTA_LOCAL, create_dir
from docker_handler.dockerHandler import DockerHandler
from file_handler.file_handler import FileHandler

from .widget_geometria import GeometryView
from .simulation_wizard_controller import SimulationWizardController
from .theme_manager import ThemeManager
from .file_browser_manager import FileBrowserManager
from .parameter_editor_manager import ParameterEditorManager

# --- Constantes ---
APP_NAME = "Simulador Hidrosedimentológico"
DOCUMENTATION_URL = "https://github.com/JupaaF/Proyecto_Final"
DEFAULT_WINDOW_TITLE = f"{APP_NAME} by Marti and Jupa"

class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()
        self._initialize_app()
        self._setup_ui()
        self._connect_signals()

        self.file_handler = None
        self.docker_handler = None
        self.file_browser_manager = None
        self.parameter_editor_manager = None

    def _initialize_app(self):
        """Inicializa la configuración básica de la aplicación."""
        create_dir()

    def _setup_ui(self):
        """Configura la interfaz de usuario principal."""
        self.setWindowTitle(DEFAULT_WINDOW_TITLE)
        
        loader = QUiLoader()
        ui_path = Path(__file__).parent.parent / "ui" / "main_window_dock.ui"
        self.ui = loader.load(str(ui_path))
        self.setCentralWidget(self.ui)

        self.theme_manager = ThemeManager(self.ui)
        self.theme_manager.set_theme(dark_mode=False)

        self.vtk_layout = QVBoxLayout(self.ui.vtkContainer)
        self.vtk_layout.setContentsMargins(0, 0, 0, 0)
        
        self.setup_view_menu()

    def _connect_signals(self):
        """Conecta las señales de los widgets a los slots correspondientes."""
        self.ui.actionModo_Oscuro.triggered.connect(self.toggle_theme)
        self.ui.actionNueva_Simulacion.triggered.connect(self.open_new_simulation_wizard)
        self.ui.actionDocumentacion.triggered.connect(self.open_documentation)
        self.ui.actionEjecutar_Simulacion.triggered.connect(self.execute_simulation)

    def open_documentation(self):
        """Abre la documentación en el navegador web."""
        QDesktopServices.openUrl(QUrl(DOCUMENTATION_URL))

    def open_new_simulation_wizard(self):
        """Abre el asistente para crear una nueva simulación."""
        wizard = SimulationWizardController(self)
        if wizard.exec() == QDialog.Accepted:
            self._handle_wizard_accepted(wizard.get_data())
        

    def _handle_wizard_accepted(self, data: dict):
        """Procesa los datos del asistente y configura la simulación."""
        case_name = data.get("case_name")
        if not case_name:
            QMessageBox.warning(self, "Error de Creación", "El nombre del caso no puede estar vacío.")
            return

        self.setWindowTitle(f"{DEFAULT_WINDOW_TITLE} - {case_name}")

        self._initialize_file_handler(case_name, data["template"])
        self._setup_managers()
        self._setup_case_environment(Path(data["mesh_file"]))


    def _initialize_file_handler(self, case_name: str, template: str):
        """Inicializa el manejador de archivos para el caso."""
        self.file_handler = FileHandler(RUTA_LOCAL / case_name, template)

    def _setup_managers(self):
        """Configura los manejadores de la interfaz (navegador de archivos y editor)."""
        if not self.file_browser_manager:
            self.file_browser_manager = FileBrowserManager(self.ui.fileBrowserDock, self.file_handler)
            self.file_browser_manager.file_clicked.connect(self.open_parameters_view)
            self.ui.fileBrowserDock.setWidget(self.file_browser_manager.get_widget())
        else:
            self.file_browser_manager.update_root_path()

        if not self.parameter_editor_manager:
            self.parameter_editor_manager = ParameterEditorManager(self.ui.parameterEditorDock, self.file_handler, self._get_vtk_patch_names)

    def _setup_case_environment(self, mesh_file_path: Path):
        """Copia la geometría, inicializa Docker y muestra la malla."""
        self._copy_geometry_file(mesh_file_path)
        
        self.docker_handler = DockerHandler(self.file_handler.get_case_path())
         
        self.docker_handler.transformar_malla()
        
        QTimer.singleShot(1000, self._check_mesh_and_visualize)

    def _check_mesh_and_visualize(self):
        """Verifica si la malla existe y la visualiza."""
        vtk_path = self.file_handler.get_case_path() / "VTK" / "case_0" / "boundary"
        if vtk_path.exists():
            self.show_geometry_visualizer(vtk_path)

        else:
            QMessageBox.warning(self, "Error de Malla", "No se pudo generar la malla. Revisa la configuración y el archivo de geometría.")

    def _copy_geometry_file(self, mesh_file_path: Path):
        """Copia el archivo de malla al directorio del caso."""
        try:
            destination_path = self.file_handler.get_case_path() / 'malla.unv'
            shutil.copy(mesh_file_path, destination_path)
        except IOError as e:
            QMessageBox.critical(self, "Error de Archivo", f"No se pudo copiar el archivo de malla: {e}")

    def execute_simulation(self):
        """Ejecuta la simulación si la configuración es válida."""
        if not self.docker_handler:
            QMessageBox.warning(self, "Error de Simulación", "No hay una simulación configurada. Por favor, cree un nuevo caso primero.")
            return
        
        self.docker_handler.ejecutar_simulacion()

    def open_parameters_view(self, file_path: Path):
        """Abre la vista de parámetros para un archivo específico."""
        if self.parameter_editor_manager:
            self.parameter_editor_manager.open_parameters_view(file_path)

    def _get_vtk_patch_names(self) -> list[str]:
        """Obtiene los nombres de los patches de VTK del directorio boundary."""
        if not self.file_handler:
            return []
            
        vtk_boundary_path = self.file_handler.get_case_path() / "VTK" / "case_0" / "boundary"
        if vtk_boundary_path.is_dir():
            return [item.stem for item in vtk_boundary_path.iterdir()]
        return []

    def show_geometry_visualizer(self, geom_file_path: Path):
        """Crea o actualiza el visualizador de geometría."""
        while self.vtk_layout.count():
            item = self.vtk_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
        
        visualizer = GeometryView(geom_file_path)
        self.vtk_layout.addWidget(visualizer)

    def toggle_theme(self):
        """Cambia entre el tema claro y oscuro."""
        self.theme_manager.set_theme(self.ui.actionModo_Oscuro.isChecked())

    def setup_view_menu(self):
        """Configura el menú 'Ver' para mostrar/ocultar los docks."""
        self.ui.menuVer.addAction(self.ui.fileBrowserDock.toggleViewAction())
        self.ui.menuVer.addAction(self.ui.parameterEditorDock.toggleViewAction())
        self.ui.menuVer.addAction(self.ui.logDock.toggleViewAction())