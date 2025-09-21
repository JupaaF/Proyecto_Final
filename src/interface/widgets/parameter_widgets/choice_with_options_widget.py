from PySide6.QtWidgets import QVBoxLayout, QWidget
from .base_widget import BaseParameterWidget
from ..helpers import NoScrollComboBox
from ..parameter_container_widget import ParameterContainerWidget

class ChoiceWithOptionsWidget(BaseParameterWidget):
    """
    Widget para un parámetro 'choice_with_options', que muestra sub-parámetros
    dinámicamente según la opción seleccionada en un QComboBox.
    """
    def __init__(self, param_props: dict, widget_factory):
        self.widget_factory = widget_factory
        self.sub_param_container = None
        super().__init__(param_props)

    def setup_ui(self):
        """
        Configura el QComboBox principal y el layout para los sub-widgets.
        """
        self.current_value = self.param_props.get('current', [])
        self.options = self.param_props.get('options', [])

        container_layout = QVBoxLayout(self)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self.main_combo = NoScrollComboBox()
        for option in self.options:
            if isinstance(option, dict):
                self.main_combo.addItem(option.get('label', option.get('name')), option.get('name'))
        container_layout.addWidget(self.main_combo)

        # Contenedor para el ParameterContainerWidget
        self.sub_widgets_container = QWidget()
        self.sub_widgets_layout = QVBoxLayout(self.sub_widgets_container)
        self.sub_widgets_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.sub_widgets_container)

        self.main_combo.currentIndexChanged.connect(self.show_parameters)

        # Seleccionar valor inicial
        if self.current_value:
            initial_selection = self.current_value[0]
            idx = self.main_combo.findData(initial_selection)
            if idx != -1:
                self.main_combo.setCurrentIndex(idx)

        # Llama a show_parameters para el estado inicial
        self.show_parameters(self.main_combo.currentIndex())

    def show_parameters(self, index):
        """
        Muestra los sub-parámetros correspondientes a la opción seleccionada
        utilizando un ParameterContainerWidget.
        """
        # Limpiar container anterior
        if self.sub_param_container:
            self.sub_param_container.deleteLater()
            self.sub_param_container = None

        selected_option_name = self.main_combo.itemData(index)
        parameters_schema_list = next(
            (opt.get('parameters', []) for opt in self.options if opt.get('name') == selected_option_name),
            []
        )

        # Obtener valores actuales para esta opción
        current_sub_values = {}
        if self.current_value and self.current_value[0] == selected_option_name:
            current_sub_values = self.current_value[1]

        # Preparar el schema para el container, inyectando los valores actuales
        parameters_schema_dict = {}
        for param_props in parameters_schema_list:
            
            param_name = param_props['name']
            new_props = param_props.copy()
            if param_name in current_sub_values:
                new_props['current'] = current_sub_values[param_name]
            elif param_props.get('optional') is None:
                new_props['current'] = param_props.get('default')
            parameters_schema_dict[param_name] = new_props

        # Crear y añadir el nuevo container
        self.sub_param_container = ParameterContainerWidget(parameters_schema_dict, self.widget_factory)
        self.sub_widgets_layout.addWidget(self.sub_param_container)

    def get_value(self):
        """
        Devuelve la opción principal seleccionada y los valores de sus sub-parámetros.
        """
        main_option = self.main_combo.currentData()

        sub_params = {}
        if self.sub_param_container:
            sub_params = self.sub_param_container.get_values()

        return [main_option, sub_params]
