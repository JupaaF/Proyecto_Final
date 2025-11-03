import sys
from PySide6.QtWidgets import QWizard, QApplication, QFileDialog, QMessageBox, QInputDialog, QListWidgetItem
from PySide6.QtUiTools import QUiLoader
from pathlib import Path
import json
from PySide6.QtCore import QCoreApplication, Qt

from src.file_handler.file_handler import FILE_CLASS_MAP
from src.config import RUTA_LOCAL

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
        self.populate_available_list()

        # Conectar los radio buttons a un método para actualizar la UI
        self.page1.templateRadioButton.toggled.connect(self.update_creation_mode)
        self.page1.customFilesRadioButton.toggled.connect(self.update_creation_mode)

        # Conectar botones de añadir/quitar archivos
        self.page1.addButton.clicked.connect(self.add_file_to_selection)
        self.page1.removeButton.clicked.connect(self.remove_file_from_selection)

        # Conectar el botón de examinar malla en la segunda página
        self.page2.browseMeshButton.clicked.connect(self.browse_mesh_file)
        
        # Configurar el wizard
        self.setWindowTitle("Asistente de Nueva Simulación")
        self.setWizardStyle(QWizard.ModernStyle)

        # Estado inicial de la UI
        self.essential_files = ['controlDict', 'fvSchemes', 'fvSolution']
        self.update_creation_mode()

    def populate_available_list(self):
        """
        Carga la lista de archivos base disponibles desde FILE_CLASS_MAP.
        """
        self.page1.availableFilesListWidget.clear()
        for file_name in sorted(FILE_CLASS_MAP.keys()):
            self.page1.availableFilesListWidget.addItem(file_name)

    def update_creation_mode(self):
        """
        Muestra u oculta los widgets de selección de plantillas o archivos
        personalizados según el radio button seleccionado.
        """
        if self.page1.templateRadioButton.isChecked():
            self.page1.creationModeStackedWidget.setCurrentIndex(0)
        else:
            self.page1.creationModeStackedWidget.setCurrentIndex(1)
            # Pre-populate essential files if the list is empty
            if self.page1.selectedFilesListWidget.count() == 0:
                for file_name in self.essential_files:
                    item = QListWidgetItem(file_name)
                    item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
                    item.setForeground(Qt.gray)
                    self.page1.selectedFilesListWidget.addItem(item)

    def add_file_to_selection(self):
        """
        Añade un archivo de la lista de disponibles a la de seleccionados.
        Si el archivo pertenece a la carpeta '0', pide un sufijo al usuario.
        """
        selected_item = self.page1.availableFilesListWidget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Error", "Seleccione un archivo para añadir.")
            return

        base_name = selected_item.text()
        
        # Determinar si el archivo puede tener sufijo
        foam_class = FILE_CLASS_MAP.get(base_name)
        if not foam_class:
            QMessageBox.critical(self, "Error Interno", f"No se encontró la clase para '{base_name}'.")
            return
        
        instance = foam_class()
        can_have_suffix = (instance.folder == "0")
        
        full_name = base_name
        if can_have_suffix:
            suffix, ok = QInputDialog.getText(self, "Añadir Sufijo", f"Ingrese un sufijo para '{base_name}' (opcional):")
            if not ok:
                return # El usuario canceló
            if suffix:
                full_name = f"{base_name}.{suffix}"
        
        # Validación de duplicados
        existing_items = [self.page1.selectedFilesListWidget.item(i).text() for i in range(self.page1.selectedFilesListWidget.count())]
        if full_name in existing_items:
            QMessageBox.warning(self, "Error", f"El archivo '{full_name}' ya ha sido añadido.")
            return
        
        self.page1.selectedFilesListWidget.addItem(full_name)

    def remove_file_from_selection(self):
        """
        Quita un archivo de la lista de seleccionados, a menos que sea esencial.
        """
        selected_item = self.page1.selectedFilesListWidget.currentItem()
        if not selected_item:
            return

        if selected_item.text() in self.essential_files:
            QMessageBox.warning(self, "Archivo Requerido", f"El archivo '{selected_item.text()}' es esencial y no se puede quitar.")
            return
        
        self.page1.selectedFilesListWidget.takeItem(self.page1.selectedFilesListWidget.row(selected_item))

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
            
            # Validación específica del modo de creación
            if self.page1.customFilesRadioButton.isChecked():
                if self.page1.selectedFilesListWidget.count() == 0:
                    QMessageBox.warning(self, "Error", "Debe seleccionar al menos un archivo.")
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
            
    def get_data(self):
        """Devuelve los datos de configuración de todas las páginas del asistente."""
        data = {
            "case_name": self.page1.caseNameLineEdit.text(),
            "mesh_file": self.page2.meshPathLineEdit.text(),
        }
        if self.page1.templateRadioButton.isChecked():
            data["template"] = self.page1.templateComboBox.currentData()
        else:
            selected_files = [self.page1.selectedFilesListWidget.item(i).text() for i in range(self.page1.selectedFilesListWidget.count())]
            data["file_names"] = selected_files
        return data