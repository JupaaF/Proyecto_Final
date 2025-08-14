
from pathlib import Path

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QComboBox, QHBoxLayout, QGroupBox, QMessageBox)
from PySide6.QtGui import QIntValidator, QDoubleValidator, QFont

class ParameterEditorManager:
    def __init__(self, parent_widget: QWidget, file_handler, get_vtk_patch_names_func):
        self.parent_widget = parent_widget
        self.file_handler = file_handler
        self.get_vtk_patch_names = get_vtk_patch_names_func
        self.parameter_widgets = {}
        self.current_file_path = None

    def open_parameters_view(self, file_path: Path):
        # Auto-save the previous file's parameters before opening a new one
        if self.current_file_path and self.current_file_path != file_path:
            if not self.save_parameters():
                return # Abort opening new file if save fails

        self.current_file_path = file_path
        self.parameter_widgets = {}
        self.parent_widget.setWindowTitle(f"Editor de parámetros - {file_path.name}")

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
                self.parameter_widgets[param_name] = (widget, param_props)

        layout.addLayout(form_layout)

        # Clear existing widget in the dock
        if self.parent_widget.widget():
            self.parent_widget.widget().deleteLater()
        
        self.parent_widget.setWidget(container)

    def save_parameters(self) -> bool:
        if not self.current_file_path:
            return True

        new_params = {}
        for param_name, (widget, props) in self.parameter_widgets.items():
            widget_type = props.get('type', 'string')
            try:
                if widget_type == 'vector':
                    new_params[param_name] = self._get_vector_from_widget(widget)
                elif widget_type == 'list_of_dicts':
                    new_params[param_name] = self._get_list_of_dicts_from_widget(widget)
                elif widget_type == 'choice':
                    new_params[param_name] = widget.currentData()
                elif widget_type == 'integer':
                    new_params[param_name] = int(widget.text())
                elif widget_type == 'float':
                    new_params[param_name] = float(widget.text())
                else: # string
                    new_params[param_name] = widget.text()
            except ValueError:
                QMessageBox.warning(self.parent_widget, "Valor Inválido", f"Existen valores invalidos. Por favor revise los parametros")
                return False

        if new_params:
            self.file_handler.modify_parameters(self.current_file_path, new_params)
        
        return True

    def _get_vector_from_widget(self, vector_widget):
        layout = vector_widget.layout()
        x = layout.itemAt(0).widget().text()
        y = layout.itemAt(1).widget().text()
        z = layout.itemAt(2).widget().text()
        return {
            'x': float(x),
            'y': float(y),
            'z': float(z)
        }

    def _get_list_of_dicts_from_widget(self, container_widget):
        patches = []
        layout = container_widget.layout()
        for i in range(layout.count()):
            groupbox = layout.itemAt(i).widget()
            patch_name_label = groupbox.findChild(QLabel)
            if not patch_name_label: continue
            patch_name = patch_name_label.text()

            form_layout = groupbox.findChild(QFormLayout)
            if not form_layout: continue

            type_combo = form_layout.itemAt(0, QFormLayout.FieldRole).widget()
            value_widget = form_layout.itemAt(1, QFormLayout.FieldRole).widget()

            patch_data = {
                'patchName': patch_name,
                'type': type_combo.currentData()
            }

            if value_widget.isVisible():
                patch_data['value'] = self._get_vector_from_widget(value_widget)
            
            patches.append(patch_data)
        return patches

    def _create_vector_widget(self, current_value):
        vector_widget = QWidget()
        vector_layout = QHBoxLayout(vector_widget)
        vector_layout.setContentsMargins(0, 0, 0, 0)

        x_edit = QLineEdit(str(current_value.get('x', 0)))
        y_edit = QLineEdit(str(current_value.get('y', 0)))
        z_edit = QLineEdit(str(current_value.get('z', 0)))

        x_edit.setValidator(QDoubleValidator())
        y_edit.setValidator(QDoubleValidator())
        z_edit.setValidator(QDoubleValidator())

        vector_layout.addWidget(x_edit)
        vector_layout.addWidget(y_edit)
        vector_layout.addWidget(z_edit)

        return vector_widget

    def _create_widget_for_parameter(self, props):
        ## logica de manejo de widgets segun el parametro
        widget_type = props.get('type', 'string')
        current_value = props.get('current', '')

        if widget_type == 'vector':
            widget = self._create_vector_widget(current_value)
        elif widget_type == 'string':
            widget = QLineEdit(str(current_value))
        elif widget_type == 'float':
            widget = QLineEdit(str(current_value))
            widget.setValidator(QDoubleValidator())
        elif widget_type == 'integer':
            widget = QLineEdit(str(current_value))
            widget.setValidator(QIntValidator())
        elif widget_type == 'choice':
            widget = QComboBox()
            options = props.get('options', [])
            if isinstance(options, list):
                for option in options:
                    if isinstance(option, dict):
                        widget.addItem(option.get('label', option.get('name')), option.get('name'))
                    else:
                        widget.addItem(str(option), option)
            elif isinstance(options, dict):
                for name, details in options.items():
                    widget.addItem(details.get('label', name), name)
            
            if current_value:
                index = widget.findData(current_value)
                if index != -1:
                    widget.setCurrentIndex(index)

        elif widget_type == 'list_of_dicts':
            container_widget = QWidget()
            container_layout = QVBoxLayout(container_widget)
            container_layout.setContentsMargins(0, 0, 0, 0)

            patch_names = self.get_vtk_patch_names()
            current_patches = {p.get('patchName'): p for p in current_value}

            def add_patch_row(patch_name=None):
                patch_data = current_patches.get(patch_name, {})
                
                patch_groupbox = QGroupBox()
                group_layout = QVBoxLayout(patch_groupbox)

                patch_name_label = QLabel(patch_name)
                font = QFont()
                font.setBold(True)
                patch_name_label.setFont(font)
                group_layout.addWidget(patch_name_label)

                patch_form_layout = QFormLayout()
                group_layout.addLayout(patch_form_layout)

                type_combo = QComboBox()
                type_options = props.get('schema', {}).get('type', {}).get('options', [])
                type_combo.addItem("-- Seleccionar Tipo --")
                for option in type_options:
                    type_combo.addItem(option.get('label'), option.get('name'))
                
                patch_form_layout.addRow("Tipo:", type_combo)

                value_label = QLabel("Valor:")
                value_input_widget = self._create_vector_widget(patch_data.get('value', {}))
                patch_form_layout.addRow(value_label, value_input_widget)
                value_label.hide()
                value_input_widget.hide()

                def update_value_input_visibility(index):
                    selected_type_name = type_combo.itemData(index)
                    requires_value = False
                    for option in type_options:
                        if option.get('name') == selected_type_name:
                            requires_value = option.get('requires_value', False)
                            break
                    value_label.setVisible(requires_value)
                    value_input_widget.setVisible(requires_value)
                
                type_combo.currentIndexChanged.connect(update_value_input_visibility)

                # Set current values
                if patch_data:
                    current_type = patch_data.get('type')
                    if current_type:
                        index = type_combo.findData(current_type)
                        if index != -1:
                            type_combo.setCurrentIndex(index)

                container_layout.addWidget(patch_groupbox)

            for patch_name in patch_names:
                add_patch_row(patch_name=patch_name)

            widget = container_widget
        else:
            widget = QLineEdit(str(current_value))
        return widget

