import sys
import shutil
from pathlib import Path

from PySide6.QtWidgets import (QApplication, QMainWindow, QDialog, QTreeView, QWidget, 
                             QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, 
                             QFormLayout, QGroupBox)
from PySide6.QtCore import QFile, QTextStream, QUrl
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileSystemModel


from scripts.initParam import RUTA_LOCAL, create_dir

from docker_handler.dockerHandler import DockerHandler
from file_handler.file_handler import FileHandler

from interface.controllers.widget_geometria import GeometryView
from .simulation_wizard_controller import SimulationWizardController

class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()

        create_dir()

        loader = QUiLoader()

        ui_path = Path(__file__).parent.parent / "ui" / "main_window_dock.ui"
        self.ui = loader.load(str(ui_path))
        self.setCentralWidget(self.ui)

        self.load_styles()

        self.ui.actionModo_Oscuro.triggered.connect(self.toggle_theme)
        self.ui.actionNueva_Simulacion.triggered.connect(self.open_new_simulation_wizard)
        self.ui.actionDocumentacion.triggered.connect(self.open_documentation)

        self.set_theme(dark_mode=False)

        self.setup_view_menu()

        # Layout para el visualizador VTK
        self.vtk_layout = QVBoxLayout(self.ui.vtkContainer)
        self.vtk_layout.setContentsMargins(0, 0, 0, 0)
        
        # Mantenido: La llamada al visualizador de geometría se conserva como estaba.
        self.show_geometry_visualizer('C:/Users/piliv/OneDrive/Documentos/FACU/PFC/Proyecto_Final/Proyecto_Final-1/VTK')

    def open_documentation(self):
        """Abre la documentación en el navegador web."""
        QDesktopServices.openUrl(QUrl("https://github.com/JupaaF/Proyecto_Final"))

    def open_new_simulation_wizard(self):
        """Abre el asistente para crear una nueva simulación."""
        wizard = SimulationWizardController(self)

        if wizard.exec() == QDialog.Accepted:
            data = wizard.get_data()

            self.file_handler = FileHandler(RUTA_LOCAL / data["case_name"], data["template"])
            self.show_folder_tree()

            self.copy_geometry_file(Path(data["mesh_file"]))          
            self.docker_handler = DockerHandler(self.file_handler.get_case_path())
            self.docker_handler.transformarMalla()

        else:
            print("Asistente cancelado por el usuario.")

    def copy_geometry_file(self, mesh_file_path: Path) -> None:
        """Copia el archivo de malla al directorio del caso."""
        # Corregido: El método ahora espera un objeto Path.
        case_path = self.file_handler.get_case_path()
        destination_path = case_path / 'malla.unv'
        shutil.copy(mesh_file_path, destination_path)
        print(f"Malla copiada a: {destination_path}")

    def load_styles(self):
        # Corregido: Rutas a QSS construidas de forma robusta.
        resources_path = Path(__file__).parent.parent / "resources"
        
        light_theme_file = QFile(str(resources_path / "light_theme.qss"))
        light_theme_file.open(QFile.ReadOnly | QFile.Text)
        self.light_theme = QTextStream(light_theme_file).readAll()
        light_theme_file.close()

        dark_theme_file = QFile(str(resources_path / "dark_theme.qss"))
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
        self.set_theme(self.ui.actionModo_Oscuro.isChecked())

    def setup_view_menu(self):
        self.ui.menuVer.addAction(self.ui.fileBrowserDock.toggleViewAction())
        self.ui.menuVer.addAction(self.ui.parameterEditorDock.toggleViewAction())
        self.ui.menuVer.addAction(self.ui.logDock.toggleViewAction())

    def show_folder_tree(self):
        model = QFileSystemModel()
        root_path = self.file_handler.get_case_path()
        model.setRootPath(str(root_path))

        tree_view = QTreeView()
        tree_view.setModel(model)
        tree_view.setRootIndex(model.index(str(root_path)))
        
        tree_view.hideColumn(1) 
        tree_view.hideColumn(2) 
        tree_view.hideColumn(3) 

        self.ui.fileBrowserDock.setWidget(tree_view)
        tree_view.clicked.connect(self.handle_file_click)
            
    def handle_file_click(self, index):
        model = index.model()
        # Corregido: Se convierte el string de la ruta a un objeto Path inmediatamente.
        file_path = Path(model.filePath(index))

        if not file_path.is_dir():
            print(f"Abriendo el archivo: {file_path}")
            self.open_parameters_view(file_path)
        else:
            print(f"Es un directorio, no se abre en el editor: {file_path}")

    def open_parameters_view(self, file_path: Path):
        """Muestra los parámetros editables para un archivo dado."""

        dict_parameters = self.file_handler.get_editable_parameters(file_path)

        container = QWidget()
        layout = QVBoxLayout(container)
        form_layout = QFormLayout()

        if not dict_parameters:
            # Si no hay parámetros, muestra un mensaje informativo.
            form_layout.addRow(QLabel("Este archivo no tiene parámetros editables."))
        else:
            for param_name, param_props in dict_parameters.items():
                label = QLabel(param_props.get('label', param_name))
                label.setToolTip(param_props.get('tooltip', ''))
                widget = self._create_widget_for_parameter(param_props)
                form_layout.addRow(label, widget)

        layout.addLayout(form_layout)

        if self.ui.parameterEditorDock.widget():
            self.ui.parameterEditorDock.widget().deleteLater()
        
        self.ui.parameterEditorDock.setWidget(container)

    def _create_widget_for_parameter(self, props):
        widget_type = props.get('type', 'string')
        if widget_type == 'vector':
            widget = QLineEdit(props.get('default', ''))
        elif widget_type == 'string':
            widget = QLineEdit(props.get('default', ''))
        elif widget_type == 'choice':
            widget = QComboBox()
            options = props.get('validators', {}).get('options', [])
            for option in options:
                widget.addItem(option['label'], option['name'])
        elif widget_type == 'list_of_dicts':
            widget = QLabel("Editor para 'list_of_dicts' aún no implementado.")
        else:
            widget = QLineEdit(props.get('default', ''))
        return widget

    # Mantenido: La firma del método se conserva como estaba.
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