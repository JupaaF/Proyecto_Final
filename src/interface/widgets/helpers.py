from PySide6.QtWidgets import QComboBox
from PySide6.QtGui import QIntValidator, QDoubleValidator


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


class NoScrollComboBox(QComboBox):
    """
    Una subclase de QComboBox que ignora los eventos de la rueda del ratón para
    evitar cambios accidentales al hacer scroll.
    """
    def wheelEvent(self, event):
        # Ignora el evento de la rueda del ratón para prevenir el cambio de ítem.
        event.ignore()
