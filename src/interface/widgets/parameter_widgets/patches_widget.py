from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                               QGroupBox)
from PySide6.QtGui import QFont
from .base_widget import BaseParameterWidget
from ..helpers import NoScrollComboBox
from ..parameter_container_widget import ParameterContainerWidget

class PatchesWidget(BaseParameterWidget):
    """
    Widget para editar las condiciones de borde de los 'patches'.
    """
    def __init__(self, param_props: dict, widget_factory, get_vtk_patch_names_func, highlight_colors: list):
        self.widget_factory = widget_factory
        self.get_vtk_patch_names = get_vtk_patch_names_func
        self.highlight_colors = highlight_colors

        self.patch_groupboxes = {}
        self.patch_widgets_map = {}
        self.highlighted_patches = {}

        super().__init__(param_props)

    def setup_ui(self):
        """
        Crea un GroupBox para cada patch con sus parámetros editables.
        """
        container_layout = QVBoxLayout(self)
        container_layout.setContentsMargins(0, 0, 0, 0)

        patch_names = self.get_vtk_patch_names()
        current_patches_map = {p.get('patchName'): p for p in self.param_props.get('current', [])}
        self.schema = self.param_props.get('schema', {})
        self.type_options = self.schema.get('type', {}).get('options', [])

        for patch_name in patch_names:
            patch_data = current_patches_map.get(patch_name, {})

            patch_groupbox = QGroupBox()
            self.patch_groupboxes[patch_name] = patch_groupbox
            group_layout = QVBoxLayout(patch_groupbox)

            patch_name_label = QLabel(patch_name)
            font = QFont()
            font.setBold(True)
            patch_name_label.setFont(font)
            group_layout.addWidget(patch_name_label)

            # Layout que contendrá el ComboBox y el ParameterContainer
            patch_content_layout = QVBoxLayout()
            group_layout.addLayout(patch_content_layout)

            type_combo = NoScrollComboBox()
            for option in self.type_options:
                type_combo.addItem(option.get('label'), option.get('name'))

            # Usar un FormLayout para el ComboBox para mantener la alineación
            combo_form_layout = QFormLayout()
            combo_form_layout.addRow("Tipo:", type_combo)
            patch_content_layout.addLayout(combo_form_layout)

            self.patch_widgets_map[patch_name] = {'type_combo': type_combo, 'container': None}

            update_func = self._make_update_params_func(patch_name, patch_content_layout, type_combo, patch_data)
            type_combo.currentIndexChanged.connect(update_func)

            initial_type = patch_data.get('type', self.schema.get('type', {}).get('default'))
            if initial_type:
                index = type_combo.findData(initial_type)
                if index != -1:
                    type_combo.setCurrentIndex(index)

            update_func(type_combo.currentIndex())

            container_layout.addWidget(patch_groupbox)

    def _make_update_params_func(self, patch_name, layout, combo, data):
        def update_value_input_visibility(index):
            # Limpiar container anterior
            if self.patch_widgets_map[patch_name].get('container'):
                self.patch_widgets_map[patch_name]['container'].deleteLater()
                self.patch_widgets_map[patch_name]['container'] = None

            selected_type_name = combo.itemData(index)
            parameters_schema_list = next(
                (opt.get('parameters', []) for opt in self.type_options if opt.get('name') == selected_type_name),
                []
            )

            # Preparar schema para el container, inyectando valores actuales
            parameters_schema_dict = {}
            for param_props in parameters_schema_list:
                param_name_key = param_props.get('name')
                # Usar valor actual del patch o el default del schema
                value = data.get(param_name_key, param_props.get('default'))

                new_props = param_props.copy()
                new_props['current'] = value
                parameters_schema_dict[param_name_key] = new_props

            container = ParameterContainerWidget(parameters_schema_dict, self.widget_factory)
            self.patch_widgets_map[patch_name]['container'] = container
            layout.addWidget(container)

        return update_value_input_visibility

    def get_value(self):
        """
        Recopila y devuelve la configuración de todos los patches.
        """
        patches = []
        for patch_name, widgets in self.patch_widgets_map.items():
            selected_type_name = widgets['type_combo'].currentData()
            patch_data = {'patchName': patch_name, 'type': selected_type_name}

            container = widgets.get('container')
            if container:
                sub_params = container.get_values()
                patch_data.update(sub_params)

            patches.append(patch_data)
        return patches

    def highlight_patch_group(self, patch_name: str, is_selected: bool):
        """
        Resalta o des-resalta el GroupBox de un patch específico.
        """
        groupbox = self.patch_groupboxes.get(patch_name)
        if not groupbox:
            return

        if is_selected:
            used_colors = {p['color'] for p in self.highlighted_patches.values()}
            available_colors = [c for c in self.highlight_colors if c not in used_colors]

            color = available_colors[0] if available_colors else self.highlight_colors[0]

            self.highlighted_patches[patch_name] = {
                'color': color,
                'original_style': groupbox.styleSheet()
            }
            groupbox.setStyleSheet(f"QGroupBox {{ background-color: {color}; border: 1px solid #A9A9A9; margin-top: 10px;}} QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }}")
        else:
            if patch_name in self.highlighted_patches:
                original_style = self.highlighted_patches[patch_name]['original_style']
                groupbox.setStyleSheet(original_style)
                del self.highlighted_patches[patch_name]

    def deselect_all_highlights(self):
        """
        Quita el resaltado de todos los patches.
        """
        for patch_name, data in self.highlighted_patches.items():
            groupbox = self.patch_groupboxes.get(patch_name)
            if groupbox:
                groupbox.setStyleSheet(data['original_style'])
        self.highlighted_patches.clear()
