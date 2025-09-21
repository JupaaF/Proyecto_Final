from PySide6.QtWidgets import QHBoxLayout,QTextEdit
from .base_widget import BaseParameterWidget

class StringWidget(BaseParameterWidget):
    """
    Widget para editar un parámetro de tipo 'string'.
    """
    def setup_ui(self):
        """
        Configura un QLineEdit para la edición del texto.
        """
        current_value = self.param_props.get('current', '')
        if current_value is None:
            current_value = self.param_props.get('default','')
        self.line_edit = QTextEdit(str(current_value))

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        self.setLayout(layout)

    def get_value(self):
        """
        Devuelve el texto actual del QLineEdit.
        """
        return self.line_edit.toPlainText()
