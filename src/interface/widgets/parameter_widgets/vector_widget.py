from PySide6.QtWidgets import QHBoxLayout
from .base_widget import BaseParameterWidget
from ..helpers import NoScrollDoubleSpinBox

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

        if safe_current_value.get('x') is None:
            safe_current_value['x'] = self.param_props.get('default').get('x',0)
        if safe_current_value.get('y') is None:
            safe_current_value['y'] = self.param_props.get('default').get('y',0)
        if safe_current_value.get('z') is None:
            safe_current_value['z'] = self.param_props.get('default').get('z',0)

        self.x_spinbox = NoScrollDoubleSpinBox()
        self.y_spinbox = NoScrollDoubleSpinBox()
        self.z_spinbox = NoScrollDoubleSpinBox()

        self.x_spinbox.setValue(safe_current_value.get('x',0))
        self.y_spinbox.setValue(safe_current_value.get('y',0))
        self.z_spinbox.setValue(safe_current_value.get('z',0))

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.x_spinbox)
        layout.addWidget(self.y_spinbox)
        layout.addWidget(self.z_spinbox)
        self.setLayout(layout)

    def get_value(self):
        """
        Devuelve un diccionario con los valores x, y, z.
        Lanza un ValueError si alguno de los valores no es válido.
        """
        try:
            x = float(self.x_spinbox.value())
            y = float(self.y_spinbox.value())
            z = float(self.z_spinbox.value())
            return {'x': x, 'y': y, 'z': z}
        except ValueError:
            raise
