import shutil
from pathlib import Path

from PySide6.QtWidgets import (QMainWindow, QDialog, QMessageBox, QVBoxLayout)
from PySide6.QtCore import QUrl
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QDesktopServices


from scripts.initParam import RUTA_LOCAL, create_dir

from docker_handler.dockerHandler import DockerHandler
from file_handler.file_handler import FileHandler

from interface.controllers.widget_geometria import GeometryView
from .simulation_wizard_controller import SimulationWizardController
from .theme_manager import ThemeManager
from .file_browser_manager import FileBrowserManager
from .parameter_editor_manager import ParameterEditorManager

class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()

        create_dir()
        self.setWindowTitle("Simulacion de OpenFOAM by Marti and Jupa")
        loader = QUiLoader()

        ui_path = Path(__file__).parent.parent / "ui" / "main_window_dock.ui"
        self.ui = loader.load(str(ui_path))
        self.setCentralWidget(self.ui)

        self.theme_manager = ThemeManager(self.ui)
        self.theme_manager.set_theme(dark_mode=False)

        self.ui.actionModo_Oscuro.triggered.connect(self.toggle_theme)
        self.ui.actionNueva_Simulacion.triggered.connect(self.open_new_simulation_wizard)
        self.ui.actionDocumentacion.triggered.connect(self.open_documentation)
        self.ui.actionEjecutar_Simulacion.triggered.connect(self.execute_simulation)

        self.setup_view_menu()

        # Layout para el visualizador VTK
        self.vtk_layout = QVBoxLayout(self.ui.vtkContainer)
        self.vtk_layout.setContentsMargins(0, 0, 0, 0)

        self.file_handler = None
        self.docker_handler = None
        self.file_browser_manager = None
        self.parameter_editor_manager = None

    def open_documentation(self):
        """Abre la documentación en el navegador web."""
        QDesktopServices.openUrl(QUrl("https://github.com/JupaaF/Proyecto_Final"))

    def open_new_simulation_wizard(self):
        """Abre el asistente para crear una nueva simulación."""
        wizard = SimulationWizardController(self)

        if wizard.exec() == QDialog.Accepted:
            data = wizard.get_data()
            self.setWindowTitle(f"Simulacion de OpenFOAM by Marti and Jupa - {data['case_name']}")

            self.file_handler = FileHandler(RUTA_LOCAL / data["case_name"], data["template"])
            
            if not self.file_browser_manager:
                self.file_browser_manager = FileBrowserManager(self.ui.fileBrowserDock, self.file_handler)
                self.file_browser_manager.file_clicked.connect(self.open_parameters_view)
                self.ui.fileBrowserDock.setWidget(self.file_browser_manager.get_widget())
            else:
                self.file_browser_manager.update_root_path()

            if not self.parameter_editor_manager:
                self.parameter_editor_manager = ParameterEditorManager(self.ui.parameterEditorDock, self.file_handler, self._get_vtk_patch_names)

            self.copy_geometry_file(Path(data["mesh_file"]))          
            self.docker_handler = DockerHandler(self.file_handler.get_case_path())
            self.docker_handler.transformar_malla()
            self.show_geometry_visualizer(self.file_handler.get_case_path()/ "VTK/case_0/boundary/")

        else:
            print("Asistente cancelado por el usuario.")

    def copy_geometry_file(self, mesh_file_path: Path) -> None:
        """Copia el archivo de malla al directorio del caso."""
        case_path = self.file_handler.get_case_path()
        destination_path = case_path / 'malla.unv'
        shutil.copy(mesh_file_path, destination_path)
        print(f"Malla copiada a: {destination_path}")

    def execute_simulation(self) -> bool:
        if not hasattr(self,"docker_handler") or self.docker_handler is None:
            QMessageBox.warning(self, "Error de validación", "El nombre del caso no puede estar vacío.")
            return False
        
        self.docker_handler.ejecutar_simulacion()
    
    def open_parameters_view(self, file_path: Path):
        if self.parameter_editor_manager:
            self.parameter_editor_manager.open_parameters_view(file_path)

    def _get_vtk_patch_names(self) -> list[str]:
        """Obtiene los nombres de los patches de VTK del directorio boundary."""
        patch_names = []
        if self.file_handler:
            vtk_boundary_path = self.file_handler.get_case_path() / "VTK" / "case_0" / "boundary"
            if vtk_boundary_path.is_dir():
                for item in vtk_boundary_path.iterdir():
                    patch_names.append(Path(item.name).stem)
        return patch_names

    def show_geometry_visualizer(self,geomFilePath):
        """
        Crea o actualiza el dock de visualización con el visualizador de geometría.
        """
        while self.vtk_layout.count():
            item = self.vtk_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        visualizer = GeometryView(geomFilePath)
        self.vtk_layout.addWidget(visualizer)

    def toggle_theme(self):
        self.theme_manager.set_theme(self.ui.actionModo_Oscuro.isChecked())

    def setup_view_menu(self):
        self.ui.menuVer.addAction(self.ui.fileBrowserDock.toggleViewAction())
        self.ui.menuVer.addAction(self.ui.parameterEditorDock.toggleViewAction())
        self.ui.menuVer.addAction(self.ui.logDock.toggleViewAction())