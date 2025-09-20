from PySide6.QtWidgets import QWizard, QWizardPage, QVBoxLayout, QMessageBox
from pathlib import Path

# Import local classes
from file_handler.openfoam_models.decomposeParDict import decomposeParDict
from ..widgets.parameter_container_widget import ParameterContainerWidget
from ..widgets.widget_factory import WidgetFactory

class ParallelWizardController(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 1. Instantiate the data model
        self.decompose_par_dict = decomposeParDict()

        # 2. Create the wizard page and layout
        self.main_page = QWizardPage(self)
        self.main_page.setTitle("Configuración de Paralelización")
        self.main_page.setSubTitle("Define el número de subdominios y el método de descomposición.")
        
        layout = QVBoxLayout(self.main_page)

        # 3. Create the widget factory and parameter container
        widget_factory = WidgetFactory()
        params_schema = self.decompose_par_dict.get_editable_parameters()
        self.container_widget = ParameterContainerWidget(params_schema, widget_factory)
        
        layout.addWidget(self.container_widget)
        
        self.addPage(self.main_page)

        # 4. Configure the wizard
        self.setWindowTitle("Asistente de Configuración Paralela")

    def get_data(self):
        """
        Retrieves the configured data from the UI, updates the model,
        and returns the model instance.
        """
        try:
            # Get values from the dynamic form
            updated_values = self.container_widget.get_values()
            
            # Update the data model instance
            self.decompose_par_dict.update_parameters(updated_values)
            
            return self.decompose_par_dict
        except ValueError as e:
            QMessageBox.warning(self, "Error de Validación", str(e))
            return None

    def accept(self):
        """
        Called when the user clicks 'Finish'.
        We validate the data before closing.
        """
        if self.get_data() is not None:
            super().accept()
        # If get_data() returns None, it means validation failed and a message was shown.
        # We don't call super().accept(), so the wizard stays open.
