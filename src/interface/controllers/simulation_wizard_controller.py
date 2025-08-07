import sys
from PySide6.QtWidgets import QWizard, QApplication, QFileDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
from pathlib import Path


RUTA_LOCAL = Path.home() / "CasosOpenFOAM" #TODO: hacer el import de esto desde initParam.py

##Esta es la que mas cambio por ahi.
##Lo mas importante esta en el ultimo metodo get_data(). Vamos para alla
class SimulationWizardController(QWizard):
    # Definimos IDs para las páginas
    Page_Intro = 0
    Page_Mesh_And_Params = 1

    def __init__(self, parent=None):
        super().__init__(parent)

        # Cargar las PÁGINAS desde los archivos .ui
        loader = QUiLoader()
        self.page1 = loader.load("src/interface/ui/wizard_page_1_initial_setup.ui")
        self.page2 = loader.load("src/interface/ui/wizard_page_2_mesh_and_params.ui")

        # Añadir las páginas al wizard
        self.addPage(self.page1)
        self.addPage(self.page2)

        # Poblar el ComboBox de plantillas en la primera página
        self.populate_templates()

        self.page1.caseNameLineEdit.textEdited.connect(self.check_file_path)

        # Conectar el botón de examinar malla en la segunda página
        self.page2.browseMeshButton.clicked.connect(self.browse_mesh_file)
        

        # Configurar el wizard
        self.setWindowTitle("Asistente de Nueva Simulación")
        self.setWizardStyle(QWizard.ModernStyle)
    
    def check_file_path(self):
        path_route = Path(RUTA_LOCAL / self.page1.caseNameLineEdit.text())
        if path_route.exists():
            QMessageBox.warning(self, "Error de validación", "El archivo ya existe. Por favor, elige un nombre diferente.")
        else:
            pass

    def populate_templates(self):
        # TODO: Cargar estas plantillas desde una configuración o un directorio
        templates = [
            "DamBreak",
        ]
        self.page1.templateComboBox.addItems(templates)

    def browse_mesh_file(self):
        """Abre un diálogo para seleccionar un archivo de malla .unv."""
        # Abre un diálogo de archivo y filtra por archivos .unv
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Seleccionar Malla", 
            "", # Directorio inicial
            "UNV Files (*.unv)"
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
            "template": self.page1.templateComboBox.currentText(),
            
            # Página 2
            "mesh_file": self.page2.meshPathLineEdit.text(),
            "solver": self.page2.solverLineEdit.text(),
            "start_time": self.page2.startTimeLineEdit.text(),
            "end_time": self.page2.endTimeLineEdit.text(),
            "delta_t": self.page2.deltaTLineEdit.text(),
            "write_interval": self.page2.writeIntervalLineEdit.text(),
        }