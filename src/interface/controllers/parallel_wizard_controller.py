from PySide6.QtWidgets import QWizard
from PySide6.QtUiTools import QUiLoader
from pathlib import Path
from .parameter_editor_manager import ParameterEditorManager

class ParallelWizardController(QWizard):
    """
    A simple wizard to configure settings for a parallel simulation run.
    """
    def __init__(self, file_handler, parent=None):
        super().__init__(parent)

        # Load the UI for the wizard page
        loader = QUiLoader()
        ui_path = Path(__file__).parent.parent / "ui" / "wizard_page_parallel.ui"
        self.page = loader.load(str(ui_path))
        self.addPage(self.page)

        self.parameter_editor_manager = ParameterEditorManager(self.page.parameterEditorScrollArea, self.file_handler)

        # Configure the wizard
        self.setWindowTitle("Asistente de Ejecución en Paralelo")
        self.setWizardStyle(QWizard.ModernStyle)

    def get_data(self) -> int:
        """
        Returns the number of processors selected by the user in the wizard.
        """
        data = {
            'num_processors': self.page.numProcessorsSpinBox.value(),
            'method': self.page.method_comboBox.currentData(),
            'n_x': self.page.nxSpinBox.value(),
            'n_y': self.page.nySpinBox.value(),
            'n_z': self.page.nzSpinBox.value()
        }
        return data
