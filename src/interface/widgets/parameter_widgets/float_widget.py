from PySide6.QtWidgets import QHBoxLayout
from .base_widget import BaseParameterWidget
from ..helpers import NoScrollDoubleSpinBox

class FloatWidget(BaseParameterWidget):
    """
    Widget para editar un parámetro de tipo 'float'.
    """
    def setup_ui(self):
        """
        Configura un QLineEdit con un validador de dobles.
        """
        current_value = self.param_props.get('current', '')
        if current_value is None:
            current_value = self.param_props.get('default',0)
        self.spinbox = NoScrollDoubleSpinBox()

        self.spinbox.setValue(current_value)
        self.spinbox.format_display_value()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.spinbox)
        self.setLayout(layout)

    def get_value(self):
        """
        Devuelve el valor flotante del QDoubleSpinBox.
        Lanza un ValueError si el texto no es un flotante válido.
        """
        try:
            return float(self.spinbox.value())
        except ValueError:
            raise