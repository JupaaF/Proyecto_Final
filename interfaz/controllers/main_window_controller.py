import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QTreeView
from PySide6.QtCore import QFile, QTextStream
from PySide6.QtUiTools import QUiLoader
from file_handler.file_handler import fileHandler
from PySide6.QtWidgets import QFileSystemModel 


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

            # TODO: Acá hiría la lógica de escribir el archivo 


        else:
            # El ítem es un directorio.
            # Puedes simplemente expandirlo o no hacer nada.
            print("Es un directorio, no se abre en el editor.")
