from PySide6.QtWidgets import QGridLayout, QLabel
from .base_widget import BaseParameterWidget
from ..helpers import NoScrollSpinBox

class DimensionsWidget(BaseParameterWidget):
    """
    Widget para editar un parámetro de tipo 'dimensions' (kg, m, s, K, mol, A, cd).
    """
    def setup_ui(self):
        """
        Configura siete QSpinBox para las componentes de las dimensiones en una grilla compacta.
        """
        self.dimension_names = ["kg", "m", "s", "K", "mol", "A", "cd"]
        self.spinboxes = {}

        main_layout = QGridLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setHorizontalSpacing(4)
        main_layout.setVerticalSpacing(2)

        current_values = self.param_props.get('current', [0] * 7)
        if not isinstance(current_values, list) or len(current_values) != 7:
            current_values = self.param_props.get('default', [0] * 7)
        if not isinstance(current_values, list) or len(current_values) != 7:
            current_values = [0] * 7

        for i, name in enumerate(self.dimension_names):
            label = QLabel(name)
            spinbox = NoScrollSpinBox()
            spinbox.setValue(current_values[i])
            
            self.spinboxes[name] = spinbox
            
            main_layout.addWidget(label, 0, i)
            main_layout.addWidget(spinbox, 1, i)

        self.setLayout(main_layout)

    def get_value(self):
        """
        Devuelve una lista con los valores de las dimensiones.
        """
        try:
            values = [self.spinboxes[name].value() for name in self.dimension_names]
            return values
        except ValueError:
            raise