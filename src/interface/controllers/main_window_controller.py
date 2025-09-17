import shutil
from pathlib import Path

import os
import platform
import subprocess
from PySide6.QtWidgets import QMessageBox
import re

from PySide6.QtWidgets import (QMainWindow, QDialog, QMessageBox, QVBoxLayout, QFileDialog, QPlainTextEdit)
from PySide6.QtCore import QUrl, QTimer,  QObject, QThread, Signal, QRunnable, Slot
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QDesktopServices, QKeySequence
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

class DockerWorker(QObject):
    """
    Worker thread for executing Docker commands in the background.
    """
    finished = Signal(bool, str)  # Signal to indicate completion (success, script_name)
    log_received = Signal(str)

    def __init__(self, docker_handler: DockerHandler, script_name: str):
        super().__init__()
        self.docker_handler = docker_handler
        self.script_name = script_name

    @Slot()
    def run(self):
        """Executes the Docker script and emits the finished signal."""
        try:
            for line in self.docker_handler.execute_script_in_docker(self.script_name):
                self.log_received.emit(line)
            self.finished.emit(True, self.script_name)
        except Exception as e:
            # It's important to catch exceptions in the thread and emit a signal
            # so the main thread can handle them.
            self.log_received.emit(f"Error during Docker execution: {e}")
            self.finished.emit(False, self.script_name)

class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()

        self._initialize_app()
        self._setup_ui()
        self._connect_signals()

        self.file_handler = None ## Modelo
        self.docker_handler = None ## Modelo
        self.file_browser_manager = None ## Controlador
        self.parameter_editor_manager = None ## Controlador
        self.visualizer = None
        self.is_running_task = False

    def _initialize_app(self):
        """Inicializa la configuración básica de la aplicación."""

        ##Por si queremos agregar otras cosas
        create_dir()

    def _setup_ui(self):
        """Configura la interfaz de usuario principal."""
        self.setWindowTitle(DEFAULT_WINDOW_TITLE)
        
        loader = QUiLoader()
        ui_path = Path(__file__).parent.parent / "ui" / "main_window_dock.ui"
        self.ui = loader.load(str(ui_path))
        self.setCentralWidget(self.ui)

        self.vtk_layout = QVBoxLayout(self.ui.vtkContainer)
        self.vtk_layout.setContentsMargins(0, 0, 0, 0)
        
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
        self.ui.actionLimpiar_Resultados.triggered.connect(self.clean_simulation_results)
        self.ui.actionVisualizarEnParaview.triggered.connect(self.launch_paraview_action)
        self.ui.actionCrear_Extrude.triggered.connect(self.open_new_extrude_dialog)
        self.ui.actionGuardar_Parametros.triggered.connect(self.save_all_parameters_action)
        self.ui.actionGuardar_Parametros.setShortcut(QKeySequence.Save)
        self.ui.actionDetener_Simulacion.triggered.connect(self.stop_simulation)

    def clean_simulation_results(self):
        """
        Limpia los resultados de la simulación actual, eliminando las carpetas
        de resultados numéricos, excepto la carpeta '0'.
        """
        if not self.file_handler:
            QMessageBox.warning(self, "Acción Requerida", "Por favor, cargue o cree una simulación primero.")
            return

        case_path = self.file_handler.get_case_path()
        
        # Preguntar al usuario si está seguro
        reply = QMessageBox.question(self, "Confirmar Limpieza",
                                     f"¿Está seguro de que desea eliminar los resultados de la simulación en '{case_path.name}'?\n"
                                     "Esta acción no se puede deshacer.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.No:
            return

        deleted_folders = []
        error_folders = []

        for item in case_path.iterdir():
            if item.is_dir():
                # Intentar convertir el nombre de la carpeta a un número
                try:
                    # Permite números con decimales, como '0.1' o '0.5'
                    float(item.name)
                    is_numeric = True
                except ValueError:
                    is_numeric = False

                if is_numeric and item.name != "0":
                    try:
                        shutil.rmtree(item)
                        deleted_folders.append(item.name)
                    except OSError as e:
                        error_folders.append(item.name)
                        print(f"Error deleting folder {item.name}: {e}")

        if deleted_folders:
            QMessageBox.information(self, "Limpieza Exitosa",
                                    f"Se eliminaron las siguientes carpetas de resultados:\n\n"
                                    f"{', '.join(deleted_folders)}")
        elif not error_folders:
            QMessageBox.information(self, "Sin Resultados", "No se encontraron carpetas de resultados para limpiar.")

        if error_folders:
            QMessageBox.critical(self, "Error de Limpieza",
                                 f"No se pudieron eliminar las siguientes carpetas:\n\n"
                                 f"{', '.join(error_folders)}")

    def open_documentation(self):
        """Abre la documentación en el navegador web."""
        QDesktopServices.openUrl(QUrl(DOCUMENTATION_URL))

    def open_new_simulation_wizard(self):
        """Abre el asistente para crear una nueva simulación."""
        if not self._prompt_save_changes():
            return # Abort if user cancels
        
        # Se crea una instancia temporal del DockerHandler para la verificación
        docker_handler = DockerHandler(Path("."))
        
        if not docker_handler.is_docker_running():
            QMessageBox.critical(self, "Docker Status", "El servicio de Docker no está en ejecución o no se encontró. Por favor, inicia Docker Desktop para crear una nueva simulación.")
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

        # Si el caso existe, se borra para empezar de cero.
        # El usuario ya dio su confirmación en el wizard.
        case_path = RUTA_LOCAL / case_name
        if case_path.exists():
            try:
                shutil.rmtree(case_path)
            except OSError as e:
                QMessageBox.critical(self, "Error de Borrado", f"No se pudo eliminar la carpeta del caso existente: {e}")
                return

        self.setWindowTitle(f"{DEFAULT_WINDOW_TITLE} - {case_name}")

        self._initialize_file_handler(case_name, data["template"])
        self._setup_managers()
        self._setup_case_environment(Path(data["mesh_file"]))

    def open_load_simulation_dialog(self):
        """Abre un diálogo para cargar una simulación existente."""
        if not self._prompt_save_changes():
            return # Abort if user cancels
        
        # Se crea una instancia temporal del DockerHandler para la verificación
        docker_handler = DockerHandler(Path("."))
        
        if not docker_handler.is_docker_running():
            QMessageBox.critical(self, "Docker Status", "El servicio de Docker no está en ejecución o no se encontró. Por favor, inicia Docker Desktop para crear una nueva simulación.")
            return
        
        case_dir_path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Simulación", str(RUTA_LOCAL))

        if case_dir_path:
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

                # Initialize FileHandler with the loaded template
                self._initialize_file_handler(case_path.name, loaded_template)
                self._setup_managers() # Re-setup managers with the new file_handler
                
                #Search for VTK directory
                self._check_mesh_and_visualize()

                self.file_handler.load_all_parameters_from_json() # Load parameters from the JSON
                self.file_handler.create_case_files()

                self.setWindowTitle(f"{DEFAULT_WINDOW_TITLE} - {case_path.name}")
                self.docker_handler = DockerHandler(self.file_handler.get_case_path())
                QMessageBox.information(self, "Cargar Simulación", "Simulación cargada exitosamente.")

                # Refresh UI elements
                if self.parameter_editor_manager and self.parameter_editor_manager.current_file_path:
                    self.parameter_editor_manager.open_parameters_view(self.parameter_editor_manager.current_file_path)
                else:
                    # If no file was previously open, open a default one or just refresh the file browser
                    self.file_browser_manager.update_root_path()


            except Exception as e:
                QMessageBox.critical(self, "Error al Cargar", f"Error al cargar la simulación: {e}")
        
    def open_new_extrude_dialog(self):
        """
        Abre un diálogo para cargar un archivo extrudeMeshDict, verificando
        primero si hay una simulación y una malla cargadas.
        """
        if not self.file_handler:
            QMessageBox.warning(self, "Acción Requerida", "Por favor, cargue o cree una simulación primero.")
            return

        # Verificar si la malla existe (directorio VTK)
        vtk_path = self.file_handler.get_case_path() / "VTK"
        if not vtk_path.is_dir():
            QMessageBox.warning(self, "Malla no Encontrada", "No se ha generado una malla para el caso actual. Por favor, genere la malla primero.")
            return

        # Abrir diálogo para seleccionar el archivo extrudeMeshDict
        file_dialog = QFileDialog(self)
        #TODO: ver si queremos implementar este filtro de otra manera......
        file_dialog.setNameFilter("OpenFOAM Dictionary (extrudeMeshDict*)") #<--- le saco el filtro
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                source_path = Path(selected_files[0])
                destination_path = self.file_handler.get_case_path() / 'system' / 'extrudeMeshDict'

                try:
                    shutil.copy(source_path, destination_path)
                    QMessageBox.information(self, "Éxito", f"El archivo '{source_path.name}' se ha copiado a la carpeta 'system' como 'extrudeMeshDict'.")
                    # Ejecutar extrudeMesh en Docker
                    self._run_docker_script_in_thread("run_extrudeMesh.sh")

                except Exception as e:
                    QMessageBox.critical(self, "Error de Copia", f"No se pudo copiar el archivo: {e}")


    def _initialize_file_handler(self, case_name: str, template: str):
        """Inicializa el manejador de archivos para el caso."""
        self.file_handler = FileHandler(RUTA_LOCAL / case_name, template)

    def _setup_managers(self):
        """Configura los manejadores de la interfaz (navegador de archivos y editor)."""
        # Always re-create managers to ensure they are linked to the new file_handler
        self.file_browser_manager = FileBrowserManager(self.ui.fileBrowserDock, self.file_handler)
        self.file_browser_manager.file_clicked.connect(self.open_parameters_view)
        self.ui.fileBrowserDock.setWidget(self.file_browser_manager.get_widget())

        self.parameter_editor_manager = ParameterEditorManager(self.ui.parameterEditorScrollArea, self.file_handler, self._get_patch_names)

    def _setup_case_environment(self, mesh_file_path: Path):
        """Copia la geometría, inicializa Docker transforma la malla según el tipo de archivo 
           de entrada, y muestra la geometría."""

        self.docker_handler = DockerHandler(self.file_handler.get_case_path())

        if mesh_file_path.suffix == '.unv':
            # Es un .unv
            self._copy_geometry_file(mesh_file_path)
            self._run_docker_script_in_thread("run_transform_UNV.sh")
        else:
            #Es un blockMeshDict
            self._copy_geometry_file(mesh_file_path)
            self._run_docker_script_in_thread("run_transform_blockMeshDict.sh")

    def _check_mesh_and_visualize(self):
        """Verifica si la malla existe y la visualiza."""
        vtk_path = self.file_handler.get_case_path() / "VTK" / "case_0" / "boundary"
        if vtk_path.exists():
            self.show_geometry_visualizer(vtk_path)

        else:
            QMessageBox.warning(self, "Error de Malla/Docker", "No se pudo generar la malla. Revisa la configuración y el archivo de geometría. Recuerda ejecutar Docker.")
            return False

    def _copy_geometry_file(self, mesh_file_path: Path) -> bool:
        """
        Copia el archivo de malla al directorio del caso, colocándolo en la
        ubicación correcta según su tipo (UNV o blockMeshDict).
        """
        try:
            case_path = self.file_handler.get_case_path()

            if mesh_file_path.suffix == '.unv':
                destination_path = case_path / 'malla.unv'
                shutil.copy(mesh_file_path, destination_path)
            elif mesh_file_path.name == 'blockMeshDict':
                system_path = case_path / 'system'
                # Asegura que el directorio 'system' exista
                system_path.mkdir(exist_ok=True)
                destination_path = system_path / 'blockMeshDict'
                shutil.copy(mesh_file_path, destination_path)
            else:
                QMessageBox.critical(self, "Error de Archivo",
                                    "Tipo de archivo de malla no soportado.")
                return False

            return True
        except FileNotFoundError:
            QMessageBox.critical(self, "Error de Archivo",
                                f"No se pudo encontrar el archivo: {mesh_file_path}")
            return False
        except IOError as e:
            QMessageBox.critical(self, "Error de Archivo",
                                f"No se pudo copiar el archivo de malla: {e}")
            return False


    def execute_simulation(self):
        """Ejecuta la simulación si la configuración es válida."""
        if not self.docker_handler:
            QMessageBox.warning(self, "Error de Simulación", "No hay una simulación configurada. Por favor, cree un nuevo caso primero.")
            return
        
        if self.parameter_editor_manager:
            if not self.parameter_editor_manager.save_parameters():
                return
            else:
                self.file_handler.write_files()
                self.file_handler.save_all_parameters_to_json()

        #Acá está la logica de si usar OpenFOAM o SedFOAM segun el template!!!!!!!!!!!!!:
        if(self.file_handler.get_template == 'damBreak' or self.file_handler.get_template == 'waterChannel'):
            self._run_docker_script_in_thread("run_openfoam.sh")
        else:
            self._run_docker_script_in_thread("run_sedfoam.sh")

    def _run_docker_script_in_thread(self, script_name: str):
        """
        Runs a Docker script in a separate thread to avoid freezing the GUI.
        """
        self.ui.logPlainTextEdit.clear()
        self._set_ui_interactive(False)
        self.is_running_task = True
        
        self.thread = QThread()
        self.worker = DockerWorker(self.docker_handler, script_name)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.log_received.connect(self._append_log)
        self.worker.finished.connect(self._on_docker_script_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    @Slot(str)
    def _append_log(self, log_line: str):
        """Appends a line of text to the log viewer."""
        self.ui.logPlainTextEdit.appendPlainText(log_line)

    def _on_docker_script_finished(self, success: bool, script_name: str):
        """
        Handles the completion of a Docker script execution.
        """
        self.is_running_task = False
        self._set_ui_interactive(True) # Restore UI interaction

        if self.docker_handler and self.docker_handler.was_stopped_by_user:
            QMessageBox.information(self, "Simulación Detenida", f"La ejecución del script '{script_name}' fue detenida por el usuario.")
            self.docker_handler.was_stopped_by_user = False # Reset flag
        elif success:
            QMessageBox.information(self, "Ejecución de Docker", f"El script '{script_name}' se ejecutó correctamente.")
            if script_name in ["run_transform_UNV.sh", "run_transform_blockMeshDict.sh", "run_extrudeMesh.sh"]:
                patch_names = self._get_patch_names()
                if patch_names:
                    self.file_handler.initialize_parameters_from_schema(patch_names)
                self.file_handler.create_case_files()
                QTimer.singleShot(100, self._check_mesh_and_visualize)
            # No special action needed for "run_openfoam.sh" on success, message is sufficient
        else:
            QMessageBox.critical(self, "Error en Ejecución de Docker", f"Falló la ejecución del script '{script_name}'.")

    def _set_ui_interactive(self, enabled: bool):
        """
        Enables or disables UI elements to prevent user interaction during a task.
        If a task is starting (enabled=False), it also disables the stop action.
        """
        # Main actions are enabled when no task is running
        self.ui.actionNueva_Simulacion.setEnabled(enabled)
        self.ui.actionCargar_Simulacion.setEnabled(enabled)
        self.ui.actionEjecutar_Simulacion.setEnabled(enabled)
        self.ui.actionGuardar_Parametros.setEnabled(enabled)
        self.ui.actionCrear_Extrude.setEnabled(enabled)
        
        # The "Stop" action is the opposite: enabled only when a task is running
        self.ui.actionDetener_Simulacion.setEnabled(not enabled)
        
        # Docks are disabled during a task
        self.ui.parameterEditorDock.setEnabled(enabled)
        self.ui.fileBrowserDock.setEnabled(enabled)

    def stop_simulation(self):
        """
        Stops the currently running Docker simulation.
        """
        if self.is_running_task and self.docker_handler:
            self.docker_handler.stop_simulation()
            self._append_log(">>> Solicitud para detener la simulación enviada...")
        else:
            QMessageBox.warning(self, "Detener Simulación", "No hay ninguna simulación en ejecución para detener.")

    def save_all_parameters_action(self):
        """Guarda todos los parámetros editables en un archivo JSON."""

        if self.parameter_editor_manager:
            if not self.parameter_editor_manager.save_parameters():
                return
            else:
                self.file_handler.write_files()

        if self.file_handler:
            self.file_handler.save_all_parameters_to_json()
            QMessageBox.information(self, "Guardar Parámetros", "¡Parámetros guardados exitosamente!")
        else:
            QMessageBox.warning(self, "Guardar Parámetros", "No hay una simulación activa para guardar parámetros.")

    def open_parameters_view(self, file_path: Path):
        """Abre la vista de parámetros para un archivo específico."""
        if self.parameter_editor_manager:
            self.parameter_editor_manager.open_parameters_view(file_path)

            if self.visualizer:
                selected_patches = self.visualizer.get_selected_patches()
                for patch_name in selected_patches:
                    self.parameter_editor_manager.highlight_patch_group(patch_name, True)

    def _get_patch_names(self) -> list[str]:
        """Obtiene los nombres de los patches de VTK del directorio boundary."""
        if not self.file_handler:
            return []

        boundary_path = self.file_handler.get_case_path() / "constant" / "polyMesh" / "boundary"
        if not boundary_path.is_file():
            return []
        try:
            with open(boundary_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the content between the first '(' and last ')'
            start = content.find('(')
            end = content.rfind(')')
            if start == -1 or end == -1:
                return []
            
            content = content[start:end]

            # Find all words that are at the beginning of a line and are followed by a '{' on the next line.
            patch_names = re.findall(r'^\s*([a-zA-Z0-9_.-]+)\s*\n\s*\{', content, re.MULTILINE)
            return patch_names
        except Exception as e:
            print(f"Error parsing boundary file: {e}")
            return []


    def show_geometry_visualizer(self, geom_file_path: Path):
        while self.vtk_layout.count():
            item = self.vtk_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
        
        self.visualizer = GeometryView(geom_file_path)
        self.visualizer.patch_selection_changed.connect(self.on_patch_selection_changed)
        self.visualizer.deselect_all_patches_requested.connect(self.on_deselect_all_patches_requested)
        self.vtk_layout.addWidget(self.visualizer)
        """Crea o actualiza el visualizador de geometría."""

    def on_patch_selection_changed(self, patch_name: str, is_selected: bool):
        if self.parameter_editor_manager:
            self.parameter_editor_manager.highlight_patch_group(patch_name, is_selected)

    def on_deselect_all_patches_requested(self):
        if self.parameter_editor_manager:
            self.parameter_editor_manager.deselect_all_highlights()

    def _prompt_save_changes(self) -> bool:
        """ 
        Prompts the user to save changes if there are any. 
        Returns True if the action should continue, False if it should be aborted.
        """
        if self.parameter_editor_manager : #and self.parameter_editor_manager.current_file_path
            reply = QMessageBox.question(self,
                                         "Guardar Cambios",
                                         "¿Desea guardar los cambios en los parámetros actuales?",
                                         QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                                         QMessageBox.Cancel)

            if reply == QMessageBox.Save:
                if not self.parameter_editor_manager.save_parameters():
                    return False
                else:
                    self.file_handler.write_files()
                    self.file_handler.save_all_parameters_to_json() 
            elif reply == QMessageBox.Cancel:
                return False
            # If Discard, proceed without saving
        
        return True

    def setup_view_menu(self):
        """Configura el menú 'Ver' para mostrar/ocultar los docks."""
        self.ui.menuVer.addAction(self.ui.fileBrowserDock.toggleViewAction())
        self.ui.menuVer.addAction(self.ui.parameterEditorDock.toggleViewAction())
        self.ui.menuVer.addAction(self.ui.logDock.toggleViewAction())

    def closeEvent(self, event):
        """
        Sobrescribe el evento de cierre de la ventana para solicitar al usuario
        guardar los cambios antes de salir.
        """
        if self.is_running_task:
            reply = QMessageBox.question(self, "Tarea en Progreso",
                                         "Hay una simulación o tarea en progreso. ¿Está seguro de que desea salir? La tarea actual se cancelará.",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
        # Llama a la función de confirmación. Si devuelve False (el usuario canceló),
        # ignora el evento de cierre.
        if not self._prompt_save_changes():
            event.ignore()
        else:
            # Si el usuario eligió guardar o descartar, permite que la ventana se cierre.
            event.accept()

         
    def launch_paraview_action(self):
        """
        Prepara el caso y lanza ParaView instalado localmente.
        """
        if not self.docker_handler or not self.file_handler.get_case_path():
            QMessageBox.warning(self, "Error de Visualización", "No hay un caso activo para visualizar.")
            return

        # 1. Llamar al DockerHandler para preparar el caso
        success = self.docker_handler.prepare_case_for_paraview()
        if not success:
            QMessageBox.critical(self, "Error", "No se pudo preparar el caso para visualización.")
            return

        # 2. Abrir ParaView en la computadora local
        case_path_local = self.file_handler.get_case_path().as_posix()
        system = platform.system()
        
        try:
            if system == "Windows":
                # Usar os.startfile para una compatibilidad total
                os.startfile(case_path_local)
            elif system == "Darwin": # macOS
                command = ['open', case_path_local]
                subprocess.Popen(command)
            elif system == "Linux":
                command = ['paraview', case_path_local]
                subprocess.Popen(command)
            else:
                QMessageBox.warning(self, "Error", "Sistema operativo no soportado para el lanzamiento automático de ParaView.")
                return
                
        except FileNotFoundError:
            QMessageBox.critical(self, "Error de Programa", "No se encontró el programa para iniciar ParaView.")
        except Exception as e:
            QMessageBox.critical(self, "Error al Lanzar", f"Ocurrió un error inesperado: {e}")