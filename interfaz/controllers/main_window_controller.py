
# interfaz/controllers/main_window_controller.py
import os
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from initParam import create_dir

# Importamos el controlador del wizard para poder crearlo
from .simulation_wizard_controller import SimulationWizardController

class MainWindowController:
    """Controlador para la ventana principal de la aplicación."""
    def __init__(self):
        loader = QUiLoader()
        ui_file_path = os.path.join(os.path.dirname(__file__), "..","ui", "cositas.ui")
        ui_file = QFile(ui_file_path)
        ui_file.open(QIODevice.ReadOnly)
        
        create_dir()

        # self.widget es la QMainWindow real. La clase en sí no es una ventana.
        self.widget = loader.load(ui_file)
        ui_file.close()

        # Conecta las señales a los métodos de ESTA clase
        self._connect_signals()

    def _connect_signals(self):
        """Conecta todos los widgets a sus funciones correspondientes."""
        self.widget.nuevaSimulacionButton.clicked.connect(self.open_simulation_wizard)
        self.widget.documentacionButton.clicked.connect(self.open_documentation)

    def open_simulation_wizard(self):
        """Crea y ejecuta el controlador del asistente de simulación."""
        # Creamos una instancia del controlador del wizard, pasando la ventana principal como padre
        wizard_controller = SimulationWizardController(parent=self.widget)
        
        # El wizard se ejecuta de forma modal. El código se detiene aquí hasta que se cierra.
        result = wizard_controller.exec()

        # Si el usuario hizo clic en "Finalizar" (o Aceptar), recogemos los datos
        if result:
            datos = wizard_controller.get_data()
            print("Asistente finalizado. Datos recogidos:", datos)
            # Aquí llamarías a la lógica de negocio, por ejemplo:
            # from logic.simulation_handler import crear_caso_dambreak
            # crear_caso_dambreak(datos)

    def open_documentation(self):
        print("Botón de documentación presionado.")
        # Aquí iría la lógica para abrir un diálogo de ayuda o una URL

    def show(self):
        """Muestra el widget que esta clase controla."""
        self.widget.show()
