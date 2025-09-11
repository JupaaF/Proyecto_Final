# from PySide6.QtWidgets import QLineEdit, QHBoxLayout
# from .base_widget import BaseParameterWidget
# from ..helpers import StrictDoubleValidator

# class FloatWidget(BaseParameterWidget):
#     """
#     Widget para editar un parámetro de tipo 'float'.
#     """
#     def setup_ui(self):
#         """
#         Configura un QLineEdit con un validador de dobles.
#         """
#         current_value = self.param_props.get('current', '')
#         self.line_edit = QLineEdit(str(current_value))

#         validator = StrictDoubleValidator()
#         if 'min' in self.param_props:
#             validator.setBottom(self.param_props['min'])
#         if 'max' in self.param_props:
#             validator.setTop(self.param_props['max'])
#         self.line_edit.setValidator(validator)

#         layout = QHBoxLayout()
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.addWidget(self.line_edit)
#         self.setLayout(layout)

#     def get_value(self):
#         """
#         Devuelve el valor flotante del QLineEdit.
#         Lanza un ValueError si el texto no es un flotante válido.
#         """
#         try:
#             return float(self.line_edit.text())
#         except ValueError:
#             raise

from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QDoubleSpinBox
from .base_widget import BaseParameterWidget
from ..helpers import StrictDoubleValidator

class FloatWidget(BaseParameterWidget):
    """
    Widget para editar un parámetro de tipo 'float'.
    """
    def setup_ui(self):
        """
        Configura un QLineEdit con un validador de dobles.
        """
        current_value = self.param_props.get('current', '')
        self.line_edit = QDoubleSpinBox()
        self.line_edit.setDecimals(5)
        self.line_edit.setValue(current_value)
        self.line_edit.setButtonSymbols(QDoubleSpinBox.NoButtons)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        self.setLayout(layout)

    def get_value(self):
        """
        Devuelve el valor flotante del QDoubleSpinBox.
        Lanza un ValueError si el texto no es un flotante válido.
        """
        try:
            return float(self.line_edit.value())
        except ValueError:
            raise