from PySide6.QtWidgets import (QComboBox, QDialog, QVBoxLayout, QCheckBox,
                               QDialogButtonBox, QDoubleSpinBox,QSpinBox,QPlainTextEdit)
from PySide6.QtGui import QIntValidator, QDoubleValidator

from PySide6.QtGui import QIntValidator, QDoubleValidator, QValidator


class FloatValidator(QValidator):
    """
    Un validador para números de punto flotante que acepta notación científica
    y comas o puntos como separadores decimales.
    """
    def validate(self, input_str: str, pos: int):
        # Si el campo está vacío, es un estado intermedio (válido para borrar).
        if not input_str:
            return (QValidator.State.Intermediate, input_str, pos)

        # Reemplazar coma por punto para la validación interna.
        test_str = input_str.replace(',', '.', 1)

        # Permitir un único signo al principio.
        if test_str in ['-', '+']:
            return (QValidator.State.Intermediate, input_str, pos)
        
        # Validar el formato general del número.
        try:
            float(test_str)
            return (QValidator.State.Acceptable, input_str, pos)
        except ValueError:
            # Si la conversión falla, puede ser un estado intermedio válido.
            # Por ejemplo, para notación científica: "1e", "1e-", "1.2e+"
            if 'e' in test_str.lower():
                parts = test_str.lower().split('e')
                if len(parts) == 2:
                    mantissa, exponent = parts
                    
                    # La mantisa debe ser un número válido por sí sola (o vacía si se empieza con 'e').
                    if mantissa in ['', '-', '+']:
                        return (QValidator.State.Intermediate, input_str, pos)
                    try:
                        float(mantissa)
                    except ValueError:
                        # permitir un punto al final de la mantisa
                        if mantissa.endswith('.'):
                            try:
                                float(mantissa[:-1])
                                return (QValidator.State.Intermediate, input_str, pos)
                            except ValueError:
                                return (QValidator.State.Invalid, input_str, pos)
                        return (QValidator.State.Invalid, input_str, pos)

                    # El exponente puede estar vacío o ser solo un signo.
                    if exponent in ['', '-', '+']:
                        return (QValidator.State.Intermediate, input_str, pos)
            
            # permitir un punto al final del número
            if test_str.endswith('.'):
                try:
                    float(test_str[:-1])
                    return (QValidator.State.Intermediate, input_str, pos)
                except ValueError:
                    pass

            # Si no coincide con ninguna forma válida o intermedia, es inválido.
            return (QValidator.State.Invalid, input_str, pos)

class OptionalParametersDialog(QDialog):
    """
    Un diálogo que permite al usuario seleccionar parámetros opcionales para añadir.
    """
    def __init__(self, available_params, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Parámetros Opcionales")

        layout = QVBoxLayout(self)
        self.checkboxes = {}

        # Crea un checkbox por cada parámetro opcional disponible.
        for param_name, param_props in available_params.items():
            label = param_props.get('label', param_name)
            checkbox = QCheckBox(label)
            checkbox.setToolTip(param_props.get('tooltip', ''))
            self.checkboxes[param_name] = checkbox
            layout.addWidget(checkbox)

        # Botones de Aceptar/Cancelar.
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_parameters(self):
        """
        Devuelve una lista con los nombres de los parámetros seleccionados.
        """
        return [name for name, checkbox in self.checkboxes.items() if checkbox.isChecked()]


class StrictIntValidator(QIntValidator):
    """
    Un validador de enteros que considera los valores fuera de rango como
    inválidos inmediatamente, en lugar de intermedios.
    """
    def validate(self, input_str: str, pos: int):
        # Primero, obtenemos el estado del validador base.
        state, ret_input, ret_pos = super().validate(input_str, pos)

        # Si el estado es intermedio, podría ser un número fuera de rango.
        # Excluimos strings vacíos o solo con signo,
        # que son intermedios válidos.
        if state == self.State.Intermediate and input_str and input_str not in ('-', '+'):
            try:
                val = int(input_str)
                # Si el número está fuera de los límites,
                # lo marcamos como inválido.
                if val < self.bottom() or val > self.top():
                    return (self.State.Invalid, ret_input, ret_pos)
            except ValueError:
                # Si no se puede convertir a entero (p.ej. "1-2"), dejamos
                # que el validador base decida.
                pass

        return state, ret_input, ret_pos


class StrictDoubleValidator(QDoubleValidator):
    """
    Un validador de dobles que considera los valores fuera de rango como inválidos
    inmediatamente, en lugar de intermedios.
    """
    def validate(self, input_str: str, pos: int):
        # Primero, obtenemos el estado del validador base.
        state, ret_input, ret_pos = super().validate(input_str, pos)
        if input_str:
            test_str = input_str.replace(',', '.', 1)

        # Si el estado es intermedio, podría ser un número fuera de rango.
        if state == self.State.Intermediate and input_str and input_str not in ('-', '+', '.', ','):
            # Reemplazamos la coma decimal para que float() funcione universalmente.
            try:
                val = float(test_str)
                # Si el número está fuera de los límites, lo marcamos como inválido.
                if val < self.bottom() or val > self.top():
                    return (self.State.Invalid, ret_input, ret_pos)
            except ValueError:
                # No se puede convertir (p.ej. "1.2e-"), dejamos que el validador
                # base decida.
                pass

        return state, ret_input, ret_pos


def format_significant_decimals(value, max_decimals=10):
    """
    Formatea un número float mostrando solo los decimales significativos
    hasta un máximo especificado.
    """
    if value == int(value):
        return f"{int(value)}"  # Si es entero, sin decimales
    
    # Convertir a string y encontrar decimales significativos
    str_value = f"{value:.{max_decimals}f}"
    
    # Eliminar ceros a la derecha
    if '.' in str_value:
        str_value = str_value.rstrip('0')
        if str_value[-1] == '.':
            str_value = str_value[:-1]
    
    return str_value

class NoScrollDoubleSpinBox(QDoubleSpinBox):

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setDecimals(12)
        self.setRange(-1.7e308, 1.7e308)
        self.setButtonSymbols(NoScrollDoubleSpinBox.NoButtons)
        self.lineEdit().textEdited.connect(self.on_text_edited)
        
    def format_significant_decimals(self,value, max_decimals=15):
        """
        Formatea un número float mostrando solo los decimales significativos
        hasta un máximo especificado.
        """
        if value == int(value):
            return f"{int(value)}"  # Si es entero, sin decimales
        
        # Convertir a string y encontrar decimales significativos
        str_value = f"{value:.{max_decimals}f}"
        
        # Eliminar ceros a la derecha
        if '.' in str_value:
            str_value = str_value.rstrip('0')
            if str_value[-1] == '.':
                str_value = str_value[:-1]
        
        return str_value

    def on_text_edited(self, text):
        # Permite edición libre sin formateo
        pass
    
    def format_display_value(self):
        """Método que hace lo mismo que focusOutEvent pero se puede llamar directamente"""
        current_value = self.value()
        formatted_text = self.format_significant_decimals(current_value)
        self.lineEdit().setText(formatted_text)

    def focusOutEvent(self, event):
        # Al perder foco, formatea mostrando solo decimales significativos
        super().focusOutEvent(event)
        self.format_display_value()
    
    def stepBy(self, steps):
        # Asegurar que el stepping mantenga el formateo
        super().stepBy(steps)
        self.format_display_value()

    def wheelEvent(self, event):
        event.ignore()

class NoScrollSpinBox(QSpinBox):

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setMaximum(2147483647)
        self.setMinimum(-2147483648)
        self.setButtonSymbols(NoScrollSpinBox.NoButtons)
        
    def wheelEvent(self, event):
        event.ignore()

class NoScrollComboBox(QComboBox):
    """
    Una subclase de QComboBox que ignora los eventos de la rueda del ratón para
    evitar cambios accidentales al hacer scroll.
    """
    def wheelEvent(self, event):
        # Ignora el evento de la rueda del ratón para prevenir el cambio de ítem.
        event.ignore()
