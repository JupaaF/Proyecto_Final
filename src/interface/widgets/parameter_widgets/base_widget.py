from PySide6.QtWidgets import QWidget

class BaseParameterWidget(QWidget):
    """
    Clase base para todos los widgets de parámetros.
    Define la interfaz común que deben seguir los widgets específicos.
    """
    def __init__(self, param_props: dict):
        """
        Inicializa el widget base.

        Args:
            param_props (dict): Un diccionario con las propiedades del parámetro,
                                como 'type', 'current', 'default', 'label', etc.
        """
        super().__init__()
        self.param_props = param_props
        self.setup_ui()

    def setup_ui(self):
        """
        Configura la interfaz de usuario del widget.
        Este método debe ser implementado por las subclases.
        """
        raise NotImplementedError("El método 'setup_ui' debe ser implementado por la subclase.")

    def get_value(self):
        """
        Devuelve el valor actual del widget.
        Este método debe ser implementado por las subclases.
        """
        raise NotImplementedError("El método 'get_value' debe ser implementado por la subclase.")
