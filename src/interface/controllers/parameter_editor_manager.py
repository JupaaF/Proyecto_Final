
from pathlib import Path

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QComboBox, QHBoxLayout)

class ParameterEditorManager:
    def __init__(self, parent_widget: QWidget, file_handler, get_vtk_patch_names_func):
        self.parent_widget = parent_widget
        self.file_handler = file_handler
        self.get_vtk_patch_names = get_vtk_patch_names_func

    def open_parameters_view(self, file_path: Path):
        container = QWidget()
        layout = QVBoxLayout(container)
        form_layout = QFormLayout()

        dict_parameters = self.file_handler.get_editable_parameters(file_path)

        if not dict_parameters:
            form_layout.addRow(QLabel("Este archivo no tiene parámetros editables."))
        else:
            for param_name, param_props in dict_parameters.items():
                label = QLabel(param_props.get('label', param_name))
                label.setToolTip(param_props.get('tooltip', ''))
                widget = self._create_widget_for_parameter(param_props)
                form_layout.addRow(label, widget)

        layout.addLayout(form_layout)

        # Clear existing widget in the dock
        if self.parent_widget.widget():
            self.parent_widget.widget().deleteLater()
        
        self.parent_widget.setWidget(container)

    def _create_widget_for_parameter(self, props):
        widget_type = props.get('type', 'string')
        if widget_type == 'vector':
            widget = QLineEdit(props.get('default', ''))
        elif widget_type == 'string':
            widget = QLineEdit(props.get('default', ''))
        elif widget_type == 'choice':
            widget = QComboBox()
            options = props.get('validators', {}).get('options', [])
            for option in options:
                widget.addItem(option['label'], option['name'])
        elif widget_type == 'list_of_dicts':
            container_widget = QWidget()
            container_layout = QVBoxLayout(container_widget)
            container_layout.setContentsMargins(0, 0, 0, 0)

            def add_patch_row(patch_name=None):
                patch_row_widget = QWidget()
                patch_row_layout = QHBoxLayout(patch_row_widget)
                patch_row_layout.setContentsMargins(0, 0, 0, 0)

                patch_name_label = QLabel(patch_name)
                patch_row_layout.addWidget(patch_name_label)

                type_combo = QComboBox()
                type_options = props.get('schema', {}).get('type', {}).get('validators', {}).get('options', [])
                type_combo.addItem("-- Seleccionar Tipo --")
                for option in type_options:
                    type_combo.addItem(option['label'], option['name'])
                patch_row_layout.addWidget(type_combo)

                value_input = QLineEdit()
                value_input.setPlaceholderText("Valor (ej. (0 0 0))")
                value_input.hide()
                patch_row_layout.addWidget(value_input)

                def update_value_input_visibility(index):
                    selected_type_name = type_combo.itemData(index)
                    requires_value = False
                    for option in type_options:
                        if option['name'] == selected_type_name and option.get('requires_value', False):
                            requires_value = True
                            break
                    value_input.setVisible(requires_value)
                type_combo.currentIndexChanged.connect(update_value_input_visibility)

                container_layout.addWidget(patch_row_widget)

            for patch_name in self.get_vtk_patch_names():
                add_patch_row(patch_name=patch_name)

            widget = container_widget
        else:
            widget = QLineEdit(props.get('default', ''))
        return widget
