from PySide6.QtWidgets import QHBoxLayout
from .base_widget import BaseParameterWidget
from ..helpers import NoScrollComboBox

class ChoiceWidget(BaseParameterWidget):
    """
    Widget para editar un parámetro de tipo 'choice' usando un QComboBox.
    """
    def setup_ui(self):
        """
        Configura un QComboBox con las opciones dadas.
        """
        current_value = self.param_props.get('current', '')
        options = self.param_props.get('options', [])

        self.combo_box = NoScrollComboBox()

        if isinstance(options, list):
            for option in options:
                if isinstance(option, dict):
                    self.combo_box.addItem(option.get('label', option.get('name')), option.get('name'))
                else:  # Lista de strings simples
                    self.combo_box.addItem(str(option), option)
        elif isinstance(options, dict):
            for name, details in options.items():
                self.combo_box.addItem(details.get('label', name), name)

        if current_value:
            index = self.combo_box.findData(current_value)
            if index != -1:
                self.combo_box.setCurrentIndex(index)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_box)
        self.setLayout(layout)

    def get_value(self):
        """
        Devuelve el dato asociado a la opción seleccionada en el QComboBox.
        """
        return self.combo_box.currentData()
