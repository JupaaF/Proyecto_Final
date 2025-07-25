
# interfaz/controllers/simulation_wizard_controller.py
import os
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtWidgets import QLineEdit, QDoubleSpinBox, QListWidget

class SimulationWizardController:
    """Controlador para la ventana del asistente de simulación."""
    def __init__(self, parent=None):
        loader = QUiLoader()
        
        # La ruta se construye relativa a la ubicación de ESTE archivo
        ui_file_path = os.path.join(os.path.dirname(__file__), "..","ui", "wizard_simulacion.ui")
        ui_file = QFile(ui_file_path)
        ui_file.open(QIODevice.ReadOnly)
        
        # self.widget es la instancia real de QWizard cargada desde el .ui
        self.widget = loader.load(ui_file, parent)
        ui_file.close()

    def exec(self):
        """Muestra el wizard como un diálogo modal y devuelve si se aceptó o canceló."""
        return self.widget.exec()

    def get_data(self):
        """
        Recoge los datos de los campos del wizard y los devuelve en un diccionario.
        Se debe llamar a esta función DESPUÉS de que exec() devuelva un resultado exitoso.
        """
        # Usamos findChild para obtener los widgets por su 'objectName' de Qt Designer
        nombre = self.widget.findChild(QLineEdit, "rutaText").text()
        template = self.widget.findChild(QListWidget, "templateElegido").currentItem().text()
        end_time = self.widget.findChild(QDoubleSpinBox, "endTimeBox").value()
        delta_t = self.widget.findChild(QDoubleSpinBox, "deltaTimeBox").value()
        write_interval = self.widget.findChild(QDoubleSpinBox, "writeIntervalBox").value()
        
        return {
            "nombre_simulacion": nombre,
            "template": template,
            "endTime": end_time,
            "deltaT": delta_t,
            "writeInterval": write_interval
        }
