from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from .base_widget import BaseParameterWidget
from ..helpers import NoScrollComboBox

class ChoiceWithOptionsWidget(BaseParameterWidget):
    """
    Widget para un parámetro 'choice_with_options', que muestra sub-parámetros
    dinámicamente según la opción seleccionada en un QComboBox.
    """
    def __init__(self, param_props: dict, widget_factory):
        self.widget_factory = widget_factory
        self.sub_widgets = {}
        # Inicialización de BaseParameterWidget se llama al final
        # después de que las dependencias estén listas.
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

        self.sub_widgets_container = QWidget()
        self.sub_widgets_layout = QVBoxLayout(self.sub_widgets_container)
        self.sub_widgets_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.sub_widgets_container)

        self.main_combo.currentIndexChanged.connect(self.show_parameters)

        if self.current_value:
            initial_selection = self.current_value[0]
            idx = self.main_combo.findData(initial_selection)
            if idx != -1:
                self.main_combo.setCurrentIndex(idx)

        self.show_parameters(self.main_combo.currentIndex())

    def show_parameters(self, index):
        """
        Muestra los sub-parámetros correspondientes a la opción seleccionada.
        """
        # Limpiar widgets anteriores
        while self.sub_widgets_layout.count() > 0:
            child = self.sub_widgets_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.sub_widgets.clear()

        selected_option_name = self.main_combo.itemData(index)
        parameters_schema = next(
            (opt.get('parameters', []) for opt in self.options if opt.get('name') == selected_option_name),
            []
        )

        is_current_selection = len(self.current_value) > 0 and self.current_value[0] == selected_option_name

        for param_props in parameters_schema:
            param_name = param_props.get('name')

            current_sub_value = None
            if is_current_selection:
                current_sub_value = self.current_value[1].get(param_name)

            value_for_widget = current_sub_value if current_sub_value is not None else param_props.get('default')

            sub_props = param_props.copy()
            sub_props['current'] = value_for_widget

            param_widget = self.widget_factory.create_widget(sub_props)

            if param_widget:
                row_widget = QWidget()
                hlayout = QHBoxLayout(row_widget)
                hlayout.setContentsMargins(0,0,0,0)
                hlayout.addWidget(QLabel(sub_props.get('label', param_name)))
                hlayout.addWidget(param_widget)
                self.sub_widgets_layout.addWidget(row_widget)
                self.sub_widgets[param_name] = param_widget

    def get_value(self):
        """
        Devuelve la opción principal seleccionada y los valores de sus sub-parámetros.
        """
        main_option = self.main_combo.currentData()
        sub_params = {}
        for name, widget in self.sub_widgets.items():
            sub_params[name] = widget.get_value()

        return [main_option, sub_params]
