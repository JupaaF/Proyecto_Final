# from PySide6.QtWidgets import QHBoxLayout
# from .base_widget import BaseParameterWidget
# from ..helpers import NoScrollDoubleSpinBox

# class FloatWidget(BaseParameterWidget):
#     """
#     Widget para editar un parámetro de tipo 'float'.
#     """
#     def setup_ui(self):
#         """
#         Configura un QLineEdit con un validador de dobles.
#         """
#         current_value = self.param_props.get('current', '')
#         if current_value is None:
#             current_value = self.param_props.get('default',0)
#         self.spinbox = NoScrollDoubleSpinBox()

#         self.spinbox.setValue(current_value)
#         self.spinbox.format_display_value()

#         layout = QHBoxLayout()
#         layout.setContentsMargins(0, 0, 0, 0)
#         layout.addWidget(self.spinbox)
#         self.setLayout(layout)

#     def get_value(self):
#         """
#         Devuelve el valor flotante del QDoubleSpinBox.
#         Lanza un ValueError si el texto no es un flotante válido.
#         """
#         try:
#             return float(self.spinbox.value())
#         except ValueError:
#             raise

from PySide6.QtWidgets import QHBoxLayout, QLineEdit
from .base_widget import BaseParameterWidget
from ..helpers import FloatValidator

class FloatWidget(BaseParameterWidget):
    """
    Widget para editar un parámetro de tipo 'float'.
    """
    def setup_ui(self):
        """
        Configura un QLineEdit con un validador de flotantes personalizado.
        """
        current_value = self.param_props.get('current', '')
        if current_value is None:
            current_value = self.param_props.get('default', 0)
        
        self.line_edit = QLineEdit()
        self.line_edit.setValidator(FloatValidator())
        self.line_edit.setText(str(current_value))

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        self.setLayout(layout)

    def get_value(self):
        """
        Devuelve el valor flotante del QLineEdit.
        Reemplaza la coma por un punto para la conversión.
        Lanza un ValueError si el texto no es un flotante válido.
        """
        text_value = self.line_edit.text().replace(',', '.', 1)
        try:
            if text_value.strip() in ('', '-', '+'):
                return self.param_props.get('default', 0.0)
            return float(text_value)
        except ValueError:
            # Esto no debería ocurrir si el validador funciona correctamente,
            # pero es una buena práctica manejarlo.
            raise ValueError(f"El valor '{self.line_edit.text()}' no es un flotante válido.")