import sys
from PySide6.QtWidgets import QWizard, QApplication, QFileDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
from pathlib import Path
import json
from PySide6.QtCore import QCoreApplication


from config import RUTA_LOCAL

##Esta es la que mas cambio por ahi.
##Lo mas importante esta en el ultimo metodo get_data(). Vamos para alla
class SimulationWizardController(QWizard):
    # Definimos IDs para las páginas

    def __init__(self, parent=None):
        super().__init__(parent)

        # Cargar las PÁGINAS desde los archivos .ui
        loader = QUiLoader()
        ui_path = Path(__file__).parent.parent / "ui"
        self.page1 = loader.load(str(ui_path / "wizard_page_1_initial_setup.ui"))
        self.page2 = loader.load(str(ui_path / "wizard_page_2_mesh_and_params.ui"))

        # Añadir las páginas al wizard
        self.addPage(self.page1)
        self.addPage(self.page2)

        # Poblar el ComboBox de plantillas en la primera página
        self.populate_templates()

        # Conectar el botón de examinar malla en la segunda página
        self.page2.browseMeshButton.clicked.connect(self.browse_mesh_file)
        

        # Configurar el wizard
        self.setWindowTitle("Asistente de Nueva Simulación")
        self.setWizardStyle(QWizard.ModernStyle)

    def validateCurrentPage(self):
        """
        Valida la página actual antes de pasar a la siguiente.
        Se asegura de que el nombre del caso no esté vacío y, si existe, pide confirmación para sobrescribir.
        """
        # Si estamos en la primera página, validamos el nombre del caso
        if self.currentPage() is self.page1:
            case_name = self.page1.caseNameLineEdit.text()

            # Validar que el nombre del caso no esté vacío
            if not case_name:
                QMessageBox.warning(self, "Error de validación", "El nombre del caso no puede estar vacío.")
                return False

            # Validar que el nombre del caso no contenga caracteres inválidos
            invalid_chars = '<>:"/|?*'
            if any(char in case_name for char in invalid_chars):
                QMessageBox.warning(
                    self,
                    "Error de validación",
                    f"El nombre del caso contiene caracteres inválidos. Por favor, evita: {invalid_chars}",
                )
                return False

            # Validar que la ruta no exista, y si existe, preguntar si se quiere sobrescribir
            path_route = Path(RUTA_LOCAL / case_name)
            if path_route.exists():
                reply = QMessageBox.question(
                    self,
                    "Confirmar Sobrescritura",
                    f"La carpeta del caso '{case_name}' ya existe en la ruta:\n{path_route}\n\n¿Desea sobrescribirla? Se perderán los datos anteriores.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return False
        
        if self.currentPage() is self.page2:
            mesh_file = self.page2.meshPathLineEdit.text()
            if not mesh_file:
                QMessageBox.warning(self, "Error de validación", "Una malla es necesaria para la simulación.")
                return False
        # Si la validación es exitosa, permite continuar
        return super().validateCurrentPage()

    def populate_templates(self):
        """
        Carga las plantillas de simulación desde el archivo templates.json y las añade al ComboBox.
        Si el archivo no existe o hay un error, usa una plantilla por defecto.
        """
        try:
            # Construir la ruta al archivo JSON
            # Usamos __file__ para obtener la ruta del script actual
            # Luego navegamos hasta el directorio 'src' y abrimos 'templates.json'
            # Esta es una forma más robusta que usar rutas relativas simples
            base_path = Path(__file__).parent.parent.parent / "file_handler"
            json_path = base_path / "templates.json"
            
            with open(json_path, 'r') as f:
                templates = json.load(f)

            # Limpiar el ComboBox antes de añadir nuevos ítems
            self.page1.templateComboBox.clear()

            # Añadir cada plantilla al ComboBox
            for template in templates:
                # Mostramos el nombre amigable en la lista
                self.page1.templateComboBox.addItem(template["name"], userData=template["id"])

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            # Si hay un error, mostramos una advertencia y usamos una plantilla por defecto
            print(f"Error cargando plantillas: {e}. Usando plantilla por defecto.")
            
            # Limpiar por si se añadieron ítems parciales
            self.page1.templateComboBox.clear()

            # Añadir una plantilla de respaldo para que la aplicación siga funcionando
            self.page1.templateComboBox.addItem("Dam Break (por defecto)", userData="damBreak")



    def browse_mesh_file(self):
        """Abre un diálogo para seleccionar un archivo de malla .unv."""
        # Abre un diálogo de archivo y filtra por archivos .unv
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Seleccionar Malla", 
            ""
            # , # Directorio inicial
            # "UNV Files (*.unv)"      ------> le saqué el filtro .unv
        )
        if file_path:
            # Si el usuario selecciona un archivo, actualiza el QLineEdit
            self.page2.meshPathLineEdit.setText(file_path)
            


##Aca se define el diccionario donde se le pasa toda la info desde el wizard a la mainWindow
## La primera pagina es lo suficientemente descriptiva. En la segunda pagina el mesh_file se refiere
## a la ruta de la malla que por el momento solo va a ser .unv, y el resto son parametros del controlDict.
## Puse los que estaban en la clase controlDict.
    def get_data(self):
        """Devuelve los datos de configuración de todas las páginas del asistente."""
        return {
            # Página 1
            "case_name": self.page1.caseNameLineEdit.text(),
            "template": self.page1.templateComboBox.currentData(),
            
            # Página 2
            "mesh_file": self.page2.meshPathLineEdit.text(),
            
        }