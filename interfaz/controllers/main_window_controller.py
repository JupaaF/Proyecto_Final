import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QDialog, QTreeView, QWidget, 
                             QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, 
                             QFormLayout, QGroupBox)
from PySide6.QtCore import QFile, QTextStream
from PySide6.QtUiTools import QUiLoader
from file_handler.file_handler import fileHandler
from PySide6.QtWidgets import QFileSystemModel
from interfaz.controllers.widget_geometría import GeometryView


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

        # 1. Asegúrate de que tu contenedor `vtkContainer` tenga un layout.
        #    Esto se hace una sola vez, idealmente en el __init__
        self.vtk_layout = QVBoxLayout(self.ui.vtkContainer)
        self.vtk_layout.setContentsMargins(0, 0, 0, 0) # Opcional: elimina los márgenes internos
        
        self.show_geometry_visualizer('C:/Users/piliv/OneDrive/Documentos/FACU/PFC/Proyecto_Final/Proyecto_Final-1/VTK')

    def open_new_simulation_wizard(self):
        """Abre el asistente para crear una nueva simulación."""
        wizard = SimulationWizardController(self)
        # Usamos exec() para abrir el wizard como un diálogo modal
        if wizard.exec() == QDialog.Accepted:
            data = wizard.get_data()
            # Aquí es donde se llama a file_handler para crear los archivos del caso
            self.file_handler = fileHandler(data["case_name"],data["template"])
            self.show_folder_tree()
            
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

    def show_folder_tree(self):
        """
        Muestra la estructura de directorios de una ruta dada en el fileBrowserDock.
        Args:
            root_path (str): La ruta del directorio raíz que se mostrará.
        """
        # 1. Crear un modelo de sistema de archivos.
        model = QFileSystemModel()

        root_path = self.file_handler.get_casePath()
        
        # 2. Establecer la carpeta raíz del modelo.
        model.setRootPath(str(root_path))

        # 3. Crear el widget que mostrará el árbol de directorios.
        tree_view = QTreeView()
        
        # 4. Asignar el modelo al widget de la vista.
        tree_view.setModel(model)
        
        # 5. Establecer la raíz visible para la vista. Esto asegura que se muestre
        #    la carpeta correcta en lugar de todo el sistema de archivos.
        tree_view.setRootIndex(model.index(str(root_path)))
        
        # Ocultar columnas irrelevantes para una mejor visualización.
        tree_view.hideColumn(1) 
        tree_view.hideColumn(2) 
        tree_view.hideColumn(3) 

        # 6. Asignar la vista del árbol (tree_view) a fileBrowserDock.
        self.ui.fileBrowserDock.setWidget(tree_view)

        # 7. Conectar la señal 'clicked' a un nuevo método en el controlador.
        tree_view.clicked.connect(self.handle_file_click)
            
    def handle_file_click(self, index):
        """
        Maneja el clic sobre un ítem del árbol de archivos.
        Args:
            index (QModelIndex): El índice del ítem presionado.
        """
        # Obtener el modelo de datos de la vista del árbol
        model = index.model()
        
        # Obtener la ruta completa del archivo/directorio
        file_path = model.filePath(index)

        # Verificar si el ítem es un directorio o un archivo
        is_dir = model.isDir(index)
        
        print(f"Has hecho clic en: {file_path}")
        print(f"¿Es un directorio?: {is_dir}")

        # Aquí puedes agregar la lógica que desees:
        if not is_dir:
            # El ítem es un archivo.
            # Por ejemplo, puedes abrirlo en un editor.
            print(f"Abriendo el archivo: {file_path}")
            # self.open_file_in_editor(file_path)


            ## Esto muestra los parametros que se muestran en la pantallita de abajo
            ## segun el archivo que tocaste, use toda la logica de arriba.
            self.open_parameters_view(file_path)

            # TODO: Acá iría la lógica de escribir el archivo 


        else:
            # El ítem es un directorio.
            # Puedes simplemente expandirlo o no hacer nada.
            print("Es un directorio, no se abre en el editor.")

    ##De aca para abajo es nuevo. 

    def open_parameters_view(self, file_path:str):

        ##Llamas a la funcion del file handler para que te pase los parametros
        ## (lo que hablamos ayer)
        dict_parameters = self.file_handler.get_editable_parameters(file_path)


        ##A partir de aca es logica de PyQt, por ahi quedate con que esto genera los campos y botones
        ## necesarios. Falta mucha logica, esto esta implementado muy por arriba.
        # 1. Crear un widget contenedor y un layout
        container = QWidget()
        layout = QVBoxLayout(container)

        # 2. Crear un QFormLayout para los parámetros
        form_layout = QFormLayout()

        # 3. Iterar sobre los parámetros y crear widgets
        for param_name, param_props in dict_parameters.items():
            label = QLabel(param_props['label'])
            label.setToolTip(param_props['tooltip'])
            
            widget = self._create_widget_for_parameter(param_props)
            
            form_layout.addRow(label, widget)

        # 4. Añadir el QFormLayout al layout principal
        layout.addLayout(form_layout)

        # 6. Limpiar el dock y establecer el nuevo widget
        # Si el dock ya tiene un widget, lo eliminamos para evitar duplicados.
        if self.ui.parameterEditorDock.widget():
            self.ui.parameterEditorDock.widget().deleteLater()
        
        self.ui.parameterEditorDock.setWidget(container)

    def _create_widget_for_parameter(self, props):
        """Crea el widget adecuado según el tipo de parámetro."""
        widget_type = props.get('type', 'string')

        if widget_type == 'vector':
            # Para un vector, usamos un QLineEdit simple por ahora.
            widget = QLineEdit(props.get('default', ''))
        elif widget_type == 'string':
            widget = QLineEdit(props.get('default', ''))
        elif widget_type == 'choice':
            # Para opciones, usamos un QComboBox.
            widget = QComboBox()
            options = props.get('validators', {}).get('options', [])
            for option in options:
                # Guardamos el 'name' como dato asociado a cada item.
                widget.addItem(option['label'], option['name'])
        elif widget_type == 'list_of_dicts':
            # Este es un caso complejo. Por ahora, mostraremos un texto.
            # Más adelante, esto podría ser un botón que abre otro diálogo/editor.
            widget = QLabel("Editor para 'list_of_dicts' aún no implementado.")
        else:
            # Un QLineEdit como fallback para tipos no reconocidos.
            widget = QLineEdit(props.get('default', ''))
        
        return widget

    def show_geometry_visualizer(self,geomFilePath):
        """
        Crea o actualiza el dock de visualización con el visualizador de geometría.
        """
        # Limpia el layout anterior si es necesario.
        # Esto elimina los widgets que existían antes.
        while self.vtk_layout.count():
            item = self.vtk_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 1. Crea una instancia del visualizador
        visualizer = GeometryView(geomFilePath)
        
        # 2. Asigna el visualizador al layout del contenedor
        self.vtk_layout.addWidget(visualizer)

