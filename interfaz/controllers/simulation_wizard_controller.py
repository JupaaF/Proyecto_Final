import sys
from PySide6.QtWidgets import QWizard, QApplication
from PySide6.QtUiTools import QUiLoader

class SimulationWizardController(QWizard):
    # Definimos un ID para nuestra página para poder referenciarla sin ambigüedad
    Page_Intro = 0

    def __init__(self, parent=None):
        super().__init__(parent)

        # Cargar la PÁGINA desde el archivo .ui
        loader = QUiLoader()
        self.intro_page = loader.load("interfaz/ui/wizard_simulacion.ui")

        # Añadir la página cargada al wizard, usando el ID que definimos
        self.addPage(self.intro_page)

        # Poblar el ComboBox de plantillas
        self.populate_templates()

        # Configurar el wizard
        self.setWindowTitle("Asistente de Nueva Simulación")
        self.setWizardStyle(QWizard.ModernStyle)

    def populate_templates(self):
        # TODO: Cargar estas plantillas desde una configuración o un directorio
        templates = [
            "DamBreak",
        ]
        self.intro_page.templateComboBox.addItems(templates)

    def get_data(self):
        """Devuelve los datos de configuración introducidos por el usuario."""
        return {
            "case_name": self.intro_page.caseNameLineEdit.text(),
            "template": self.intro_page.templateComboBox.currentText()
        }

