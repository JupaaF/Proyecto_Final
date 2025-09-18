from PySide6.QtWidgets import QHBoxLayout
from .base_widget import BaseParameterWidget
from ..helpers import NoScrollSpinBox

class IntWidget(BaseParameterWidget):
    """
    Widget para editar un parámetro de tipo 'int'.
    """
    def setup_ui(self):
        """
        Configura un QLineEdit con un validador de enteros.
        """
        current_value = self.param_props.get('current', '')
        if current_value is None:
            current_value = self.param_props.get('default',0)
        self.spinbox = NoScrollSpinBox()
        self.spinbox.setMaximum(2147483647)
        self.spinbox.setMinimum(-2147483648)
        self.spinbox.setValue(current_value)
        self.spinbox.setButtonSymbols(NoScrollSpinBox.NoButtons)
        

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.spinbox)
        self.setLayout(layout)

    def get_value(self):
        """
        Devuelve el valor entero del QLineEdit.
        Lanza un ValueError si el texto no es un entero válido.
        """
        try:
            return int(self.spinbox.value())
        except ValueError:
            raise
