from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                               QPushButton, QHBoxLayout, QMessageBox)

from .helpers import OptionalParametersDialog

class ParameterContainerWidget(QWidget):
    """
    Un widget contenedor que gestiona una lista de parámetros,
    incluyendo la lógica para añadir y quitar parámetros opcionales.
    """
    def __init__(self, parameters_schema: dict, widget_factory, parent=None):
        super().__init__(parent)
        self.parameters_schema = parameters_schema
        self.widget_factory = widget_factory

        self.parameter_widgets = {}
        self.optional_params_schema = {}
        self.active_optional_params = set()

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout = QFormLayout()

        required_params = {}

        # Separar parámetros requeridos de opcionales
        for name, props in self.parameters_schema.items():
            if props.get('optional'):
                self.optional_params_schema[name] = props
                # Los opcionales con valor 'current' se muestran de inicio
                if 'current' in props and props['current'] is not None:
                    required_params[name] = props
                    self.active_optional_params.add(name)
            else:
                required_params[name] = props

        # Crear y mostrar los widgets
        if not required_params and not self.optional_params_schema:
            self.form_layout.addRow(QLabel("No hay parámetros para mostrar."))
        else:
            for param_name, param_props in required_params.items():
                self._add_parameter_to_view(param_name, param_props)

        main_layout.addLayout(self.form_layout)

        # Añadir botón para parámetros opcionales si hay alguno
        if self.optional_params_schema:
            self.add_optional_param_button = QPushButton("Agregar Parámetro")
            self.add_optional_param_button.clicked.connect(self._open_optional_parameters_dialog)
            main_layout.addWidget(self.add_optional_param_button)
            self._update_add_button_state()

    def _add_parameter_to_view(self, param_name: str, param_props: dict):
        label = QLabel(param_props.get('label', param_name))
        label.setToolTip(param_props.get('tooltip', ''))

        if param_props.get('optional') and 'current' not in param_props:
            param_props['current'] = param_props.get('default')

        widget = self.widget_factory.create_widget(param_props)

        display_widget = widget
        if param_props.get('optional'):
            remove_button = QPushButton("X")
            remove_button.setFixedSize(24, 24)
            remove_button.setToolTip("Eliminar este parámetro opcional")

            # Usamos una lambda para capturar el nombre del parámetro
            remove_button.clicked.connect(
                lambda checked=False, name=param_name: self._remove_optional_parameter(name)
            )

            container = QWidget()
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.addWidget(widget)
            h_layout.addWidget(remove_button)
            display_widget = container

        self.form_layout.addRow(label, display_widget)
        self.parameter_widgets[param_name] = (widget, param_props)

    def _remove_optional_parameter(self, param_name: str):
        if param_name in self.parameter_widgets:
            # Encontrar y eliminar la fila del layout
            for i in range(self.form_layout.rowCount()):
                label_item = self.form_layout.itemAt(i, QFormLayout.LabelRole)
                if label_item and label_item.widget() and label_item.widget().text() == self.parameter_widgets[param_name][1].get('label', param_name):
                    # Eliminar el widget y la etiqueta
                    self.form_layout.removeRow(i)
                    break

            del self.parameter_widgets[param_name]
            self.active_optional_params.remove(param_name)
            self._update_add_button_state()

    def _open_optional_parameters_dialog(self):
        available_params = {
            name: props for name, props in self.optional_params_schema.items()
            if name not in self.active_optional_params
        }

        if not available_params:
            QMessageBox.information(self, "Sin Parámetros", "Todos los parámetros opcionales ya han sido añadidos.")
            return

        dialog = OptionalParametersDialog(available_params, self)
        if dialog.exec():
            selected_params = dialog.get_selected_parameters()
            for param_name in selected_params:
                if param_name not in self.active_optional_params:
                    param_props = self.optional_params_schema[param_name]
                    self._add_parameter_to_view(param_name, param_props)
                    self.active_optional_params.add(param_name)
            self._update_add_button_state()

    def _update_add_button_state(self):
        if hasattr(self, 'add_optional_param_button'):
            all_optionals_active = len(self.active_optional_params) == len(self.optional_params_schema)
            self.add_optional_param_button.setEnabled(not all_optionals_active)

    def get_values(self) -> dict:
        """
        Recopila los valores de todos los widgets de parámetros activos.
        """
        values = {}
        for param_name, (widget, props) in self.parameter_widgets.items():
            try:
                value = widget.get_value()
                if value is not None:
                    values[param_name] = value
            except ValueError:
                # Propagar el error para que el manager principal lo maneje
                raise ValueError(f"El valor para '{props.get('label', param_name)}' es inválido.")

        return values

    def get_all_widgets(self):
        return self.parameter_widgets
