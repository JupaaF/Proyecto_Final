from PySide6.QtWidgets import QLineEdit, QHBoxLayout
from .base_widget import BaseParameterWidget
from ..helpers import StrictDoubleValidator

class VectorWidget(BaseParameterWidget):
    """
    Widget para editar un parámetro de tipo 'vector' (x, y, z).
    """
    def setup_ui(self):
        """
        Configura tres QLineEdit para los componentes x, y, z.
        """
        current_value = self.param_props.get('current', {})
        safe_current_value = current_value if isinstance(current_value, dict) else {}

        self.x_edit = QLineEdit(str(safe_current_value.get('x', 0)))
        self.y_edit = QLineEdit(str(safe_current_value.get('y', 0)))
        self.z_edit = QLineEdit(str(safe_current_value.get('z', 0)))

        validator = StrictDoubleValidator()
        if 'min' in self.param_props:
            validator.setBottom(self.param_props['min'])
        if 'max' in self.param_props:
            validator.setTop(self.param_props['max'])

        self.x_edit.setValidator(validator)
        self.y_edit.setValidator(validator)
        self.z_edit.setValidator(validator)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.x_edit)
        layout.addWidget(self.y_edit)
        layout.addWidget(self.z_edit)
        self.setLayout(layout)

    def get_value(self):
        """
        Devuelve un diccionario con los valores x, y, z.
        Lanza un ValueError si alguno de los valores no es válido.
        """
        try:
            x = float(self.x_edit.text())
            y = float(self.y_edit.text())
            z = float(self.z_edit.text())
            return {'x': x, 'y': y, 'z': z}
        except ValueError:
            raise
