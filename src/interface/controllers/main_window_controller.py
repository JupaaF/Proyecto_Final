
import shutil
from pathlib import Path

from PySide6.QtWidgets import (QMainWindow, QDialog, QMessageBox, QVBoxLayout, QFileDialog, QPlainTextEdit)
from PySide6.QtCore import QUrl, QTimer, Slot
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QDesktopServices
import json

from config import RUTA_LOCAL, create_dir
from docker_handler.dockerHandler import DockerHandler
from file_handler.file_handler import FileHandler

from .widget_geometria import GeometryView
from .simulation_wizard_controller import SimulationWizardController
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
        self.ui = loader.load(str(ui_path), self)
        self.setCentralWidget(self.ui)

        self.vtk_layout = QVBoxLayout(self.ui.vtkContainer)
        self.vtk_layout.setContentsMargins(0, 0, 0, 0)

        # The .ui file already contains the logPlainTextEdit, so we can use it directly.
        # If it didn't, we would create and add it here.
        # self.log_view = QPlainTextEdit()
        # self.log_view.setReadOnly(True)
        # self.ui.logDock.setWidget(self.log_view)

        self.setup_view_menu()

    def setup_view_menu(self):
        """Configura el menú 'Ver' para mostrar/ocultar los docks."""
        self.ui.menuVer.addAction(self.ui.fileBrowserDock.toggleViewAction())
        self.ui.menuVer.addAction(self.ui.parameterEditorDock.toggleViewAction())
        self.ui.menuVer.addAction(self.ui.logDock.toggleViewAction())

    def _connect_signals(self):
        """Conecta las señales de los widgets a los slots correspondientes."""
        self.ui.actionDocumentacion.triggered.connect(self.open_documentation)
        self.ui.actionNueva_Simulacion.triggered.connect(self.open_new_simulation_wizard)
        self.ui.actionCargar_Simulacion.triggered.connect(self.open_load_simulation_dialog)
        self.ui.actionEjecutar_Simulacion.triggered.connect(self.execute_simulation)
        self.ui.actionGuardar_Parametros.triggered.connect(self.save_all_parameters_action)

    def open_documentation(self):
        """Abre la documentación en el navegador web."""
        QDesktopServices.openUrl(QUrl(DOCUMENTATION_URL))

    def open_new_simulation_wizard(self):
        """Abre el asistente para crear una nueva simulación."""
        if not self._prompt_save_changes():
            return  # Abort if user cancels

        temp_docker_handler = DockerHandler(Path("."))
        if not temp_docker_handler.is_docker_running():
            QMessageBox.critical(self, "Docker Status", "El servicio de Docker no está en ejecución o no se encontró. Por favor, inicia Docker Desktop para crear una nueva simulación. ❌")
            return

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

        self._setup_case_handlers(case_name, data["template"])
        self._setup_managers()
        self._setup_case_environment(Path(data["mesh_file"]))
        self.file_handler.create_case_files()

    def open_load_simulation_dialog(self):
        """Abre un diálogo para cargar una simulación existente."""
        if not self._prompt_save_changes():
            return  # Abort if user cancels

        temp_docker_handler = DockerHandler(Path("."))
        if not temp_docker_handler.is_docker_running():
            QMessageBox.critical(self, "Docker Status", "El servicio de Docker no está en ejecución o no se encontró. Por favor, inicia Docker Desktop.")
            return

        case_dir_path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Simulación", str(RUTA_LOCAL))
        if not case_dir_path:
            return

        case_path = Path(case_dir_path)
        json_path = case_path / FileHandler.JSON_PARAMS_FILE
        if not json_path.exists():
            QMessageBox.warning(self, "Error al Cargar", "La carpeta seleccionada no contiene un archivo de parámetros válido (parameters.json).")
            return

        try:
            with open(json_path, 'r') as f:
                saved_data = json.load(f)
            loaded_template = saved_data.get("template")
            if not loaded_template:
                QMessageBox.warning(self, "Error al Cargar", "El archivo parameters.json no especifica un template.")
                return

            self.setWindowTitle(f"{DEFAULT_WINDOW_TITLE} - {case_path.name}")
            self._setup_case_handlers(case_path.name, loaded_template)
            self._setup_managers()
            self.file_handler.load_all_parameters_from_json()
            self.file_handler.create_case_files()
            QMessageBox.information(self, "Cargar Simulación", "Simulación cargada exitosamente.")

            if self.parameter_editor_manager and self.parameter_editor_manager.current_file_path:
                self.parameter_editor_manager.open_parameters_view(self.parameter_editor_manager.current_file_path)
            else:
                self.file_browser_manager.update_root_path()
        except Exception as e:
            QMessageBox.critical(self, "Error al Cargar", f"Error al cargar la simulación: {e}")

    def _setup_case_handlers(self, case_name: str, template: str):
        """Inicializa y conecta los manejadores de archivos y Docker."""
        self.file_handler = FileHandler(RUTA_LOCAL / case_name, template)
        self.docker_handler = DockerHandler(self.file_handler.get_case_path())

        # Connect DockerHandler signals to main window slots
        self.docker_handler.process_started.connect(self._on_docker_process_started)
        self.docker_handler.new_log_line.connect(self._on_docker_process_log)
        self.docker_handler.process_finished.connect(self._on_docker_process_finished)

    def _setup_managers(self):
        """Configura los manejadores de la interfaz (navegador de archivos y editor)."""
        self.file_browser_manager = FileBrowserManager(self.ui.fileBrowserDock, self.file_handler)
        self.file_browser_manager.file_clicked.connect(self.open_parameters_view)
        self.ui.fileBrowserDock.setWidget(self.file_browser_manager.get_widget())

        self.parameter_editor_manager = ParameterEditorManager(self.ui.parameterEditorDock, self.file_handler, self._get_vtk_patch_names)

    def _setup_case_environment(self, mesh_file_path: Path):
        """Copia la geometría y ejecuta la transformación de malla."""
        if not self.docker_handler:
            QMessageBox.critical(self, "Error", "Docker handler no inicializado.")
            return

        if self._copy_geometry_file(mesh_file_path):
            script_name = "run_transform_UNV.sh" if mesh_file_path.suffix == '.unv' else "run_transform_blockMeshDict.sh"
            self.docker_handler.execute_script_in_docker(script_name)

    def _check_mesh_and_visualize(self):
        """Verifica si la malla existe y la visualiza."""
        vtk_path = self.file_handler.get_case_path() / "VTK" / "case_0" / "boundary"
        if vtk_path.exists():
            self.show_geometry_visualizer(vtk_path)
        else:
            QMessageBox.warning(self, "Error de Malla/Docker", "No se pudo generar la malla. Revisa la configuración, el archivo de geometría y los logs.")

    def _copy_geometry_file(self, mesh_file_path: Path) -> bool:
        """Copia el archivo de malla al directorio del caso."""
        try:
            case_path = self.file_handler.get_case_path()
            if mesh_file_path.suffix == '.unv':
                destination_path = case_path / 'malla.unv'
            elif mesh_file_path.name == 'blockMeshDict':
                system_path = case_path / 'system'
                system_path.mkdir(exist_ok=True)
                destination_path = system_path / 'blockMeshDict'
            else:
                QMessageBox.critical(self, "Error de Archivo", "Tipo de archivo de malla no soportado.")
                return False

            shutil.copy(mesh_file_path, destination_path)
            return True
        except (FileNotFoundError, IOError) as e:
            QMessageBox.critical(self, "Error de Archivo", f"No se pudo copiar el archivo de malla: {e}")
            return False

    def execute_simulation(self):
        """Ejecuta la simulación si la configuración es válida."""
        if not self.docker_handler:
            QMessageBox.warning(self, "Error de Simulación", "No hay una simulación configurada. Cree un nuevo caso primero.")
            return

        if self.parameter_editor_manager and not self.parameter_editor_manager.save_parameters():
            return

        self.docker_handler.execute_script_in_docker("run_openfoam.sh")

    @Slot(str)
    def _on_docker_process_started(self, script_name: str):
        """Slot para manejar el inicio de un proceso Docker."""
        self.ui.logPlainTextEdit.clear()
        self.ui.logPlainTextEdit.appendPlainText(f"--- Iniciando: {script_name} ---\n")
        self._set_ui_busy(True)

    @Slot(str)
    def _on_docker_process_log(self, line: str):
        """Slot para mostrar los logs del proceso Docker."""
        self.ui.logPlainTextEdit.appendPlainText(line)

    @Slot(str, int)
    def _on_docker_process_finished(self, script_name: str, return_code: int):
        """Slot para manejar la finalización de un proceso Docker."""
        self.ui.logPlainTextEdit.appendPlainText(f"\n--- Proceso finalizado: {script_name} (Código de salida: {return_code}) ---")
        self._set_ui_busy(False)

        # Si la transformación de malla fue exitosa, visualiza la malla.
        if "run_transform" in script_name and return_code == 0:
            self._check_mesh_and_visualize()

    def _set_ui_busy(self, busy: bool):
        """Activa o desactiva los controles de la UI durante la ejecución."""
        self.ui.actionEjecutar_Simulacion.setEnabled(not busy)
        self.ui.actionNueva_Simulacion.setEnabled(not busy)
        self.ui.actionCargar_Simulacion.setEnabled(not busy)
        self.ui.parameterEditorDock.setEnabled(not busy)
        self.ui.fileBrowserDock.setEnabled(not busy)

    def save_all_parameters_action(self):
        """Guarda todos los parámetros editables en un archivo JSON."""

        if self.parameter_editor_manager:
            if not self.parameter_editor_manager.save_parameters():
                return

        if self.file_handler:
            self.file_handler.save_all_parameters_to_json()
            QMessageBox.information(self, "Guardar Parámetros", "¡Parámetros guardados exitosamente!")
        else:
            QMessageBox.warning(self, "Guardar Parámetros", "No hay una simulación activa para guardar parámetros.")

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
        while self.vtk_layout.count():
            item = self.vtk_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
        
        visualizer = GeometryView(geom_file_path)
        self.vtk_layout.addWidget(visualizer)
        """Crea o actualiza el visualizador de geometría."""

    def _prompt_save_changes(self) -> bool:
        """ 
        Prompts the user to save changes if there are any. 
        Returns True if the action should continue, False if it should be aborted.
        """
        if self.parameter_editor_manager and self.parameter_editor_manager.current_file_path:
            reply = QMessageBox.question(self,
                                         "Guardar Cambios",
                                         "¿Desea guardar los cambios en los parámetros actuales?",
                                         QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                                         QMessageBox.Cancel)

            if reply == QMessageBox.Save:
                if not self.parameter_editor_manager.save_parameters():
                    return False
            elif reply == QMessageBox.Cancel:
                return False
            # If Discard, proceed without saving
        
        return True

    def setup_view_menu(self):
        """Configura el menú 'Ver' para mostrar/ocultar los docks."""
        self.ui.menuVer.addAction(self.ui.fileBrowserDock.toggleViewAction())
        self.ui.menuVer.addAction(self.ui.parameterEditorDock.toggleViewAction())
        self.ui.menuVer.addAction(self.ui.logDock.toggleViewAction())