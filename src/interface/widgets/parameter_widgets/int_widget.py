from PySide6.QtWidgets import QLineEdit, QHBoxLayout
from .base_widget import BaseParameterWidget
from ..helpers import StrictIntValidator

class IntWidget(BaseParameterWidget):
    """
    Widget para editar un parámetro de tipo 'int'.
    """
    def setup_ui(self):
        """
        Configura un QLineEdit con un validador de enteros.
        """
        current_value = self.param_props.get('current', '')
        self.line_edit = QLineEdit(str(current_value))

        validator = StrictIntValidator()
        if 'min' in self.param_props:
            validator.setBottom(self.param_props['min'])
        if 'max' in self.param_props:
            validator.setTop(self.param_props['max'])
        self.line_edit.setValidator(validator)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        self.setLayout(layout)

    def get_value(self):
        """
        Devuelve el valor entero del QLineEdit.
        Lanza un ValueError si el texto no es un entero válido.
        """
        try:
            return int(self.line_edit.text())
        except ValueError:
            raise
