from PySide6.QtWidgets import QWizard
from PySide6.QtUiTools import QUiLoader
from pathlib import Path
from .parameter_editor_manager import ParameterEditorManager

class ParallelWizardController(QWizard):
    """
    A wizard to configure settings for a parallel simulation run using
    the ParameterEditorManager to edit decomposeParDict.
    """
    def __init__(self, file_handler, parent=None):
        super().__init__(parent)
        self.file_handler = file_handler

        # Load the UI for the wizard page
        loader = QUiLoader()
        ui_path = Path(__file__).parent.parent / "ui" / "wizard_page_parallel.ui"
        self.page = loader.load(str(ui_path))
        self.addPage(self.page)

        # Setup the parameter editor
        self.parameter_editor_manager = ParameterEditorManager(
            self.page.parameterEditorScrollArea,
            self.file_handler,
            lambda: []  # Patches are not needed for decomposeParDict
        )

        # Open the decomposeParDict file for editing
        decompose_par_dict_path = self.file_handler.get_case_path() / "system" / "decomposeParDict"
        if decompose_par_dict_path.exists():
            self.parameter_editor_manager.open_parameters_view(decompose_par_dict_path)

        # Configure the wizard
        self.setWindowTitle("Asistente de Ejecución en Paralelo")
        self.setWizardStyle(QWizard.ModernStyle)

    def save_parameters(self) -> bool:
        """Saves the parameters from the editor via the ParameterEditorManager."""
        return self.parameter_editor_manager.save_parameters()

    def get_data(self) -> dict:
        """
        Retrieves the number of processors from the parameter editor's widgets.
        This is needed by the main window to pass to the Docker execution command.
        """
        num_processors = 1  # Default to a safe value
        try:
            # The parameter name in DecomposeParDict is 'numberOfSubdomains'
            widget, _ = self.parameter_editor_manager.parameter_widgets.get('numberOfSubdomains', (None, None))
            if widget:
                num_processors = int(widget.text())
        except (ValueError, AttributeError) as e:
            print(f"Could not retrieve 'numberOfSubdomains' from the wizard's editor: {e}. Defaulting to {num_processors}.")

        return {'num_processors': num_processors}
