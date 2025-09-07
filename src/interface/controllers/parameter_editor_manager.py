from pathlib import Path

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel,
                               QHBoxLayout, QMessageBox, QScrollArea,
                               QPushButton, QDialog, QCheckBox,
                               QDialogButtonBox, QApplication)
from PySide6.QtGui import QPalette

from ..widgets.widget_factory import WidgetFactory
from ..widgets.parameter_widgets.patches_widget import PatchesWidget


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


class ParameterEditorManager:
    """
    Gestiona la creación y actualización de la interfaz de usuario para la edición de parámetros.

    Esta clase se encarga de generar dinámicamente widgets de PySide6 basados en un
    diccionario de parámetros, utilizando una fábrica de widgets.
    Permite al usuario modificar estos parámetros y guardarlos.
    """
    def __init__(self, scroll_area: QScrollArea, file_handler, get_vtk_patch_names_func):
        """
        Inicializa el gestor del editor de parámetros.

        Args:
            scroll_area (QScrollArea): El QScrollArea donde se mostrarán los widgets de parámetros.
            file_handler: Una instancia de una clase controladora de archivos.
            get_vtk_patch_names_func: Función para obtener los nombres de los patches de VTK.
        """
        self.scroll_area = scroll_area
        self.file_handler = file_handler

        self.parameter_widgets = {}
        self.optional_params_schema = {}
        self.active_optional_params = set()
        self.current_file_path = None
        self.patches_widget_instance = None

        self._setup_highlight_colors()
        self.widget_factory = WidgetFactory(
            get_vtk_patch_names_func=get_vtk_patch_names_func,
            highlight_colors=self.highlight_colors
        )

    def open_parameters_view(self, file_path: Path):
        """
        Crea y muestra la vista del editor de parámetros para un archivo específico.
        """
        if self.current_file_path and not self.save_parameters():
            return

        self.current_file_path = file_path
        self.parameter_widgets.clear()
        self.patches_widget_instance = None

        if self.scroll_area.parentWidget() and self.scroll_area.parentWidget().parentWidget():
            dock_widget = self.scroll_area.parentWidget().parentWidget()
            dock_widget.setWindowTitle(f"Editor de parámetros - {file_path.name}")

        container = QWidget()
        layout = QVBoxLayout(container)
        form_layout = QFormLayout()

        all_params = self.file_handler.get_editable_parameters(file_path)
        
        self.optional_params_schema.clear()
        self.active_optional_params.clear()

        required_params = {}
        if all_params:
            for name, props in all_params.items():
                if props.get('optional'):
                    self.optional_params_schema[name] = props
                    if props.get('current') is not None:
                        required_params[name] = props
                        self.active_optional_params.add(name)
                else:
                    required_params[name] = props

        if not required_params:
            form_layout.addRow(QLabel("Este archivo no tiene parámetros editables."))
        else:
            for param_name, param_props in required_params.items():
                self._add_parameter_to_view(param_name, param_props, form_layout)

        layout.addLayout(form_layout)

        if self.optional_params_schema:
            self.add_optional_param_button = QPushButton("Agregar Parámetro Opcional")
            if len(self.active_optional_params) == len(self.optional_params_schema):
                self.add_optional_param_button.setEnabled(False)
            self.add_optional_param_button.clicked.connect(self._open_optional_parameters_dialog)
            layout.addWidget(self.add_optional_param_button)

        self.scroll_area.setMinimumWidth(form_layout.sizeHint().width() + 40)

        if self.scroll_area.widget():
            self.scroll_area.widget().deleteLater()
        
        self.scroll_area.setWidget(container)

    def save_parameters(self) -> bool:
        """
        Recopila los valores de los widgets de la UI, los valida y los guarda.
        """
        if not self.current_file_path:
            return True

        new_params = {}
        for param_name, (widget, props) in self.parameter_widgets.items():
            try:
                value = widget.get_value()
                if value is not None:
                    new_params[param_name] = value
            except ValueError:
                QMessageBox.warning(self.scroll_area, "Valor Inválido",
                                    f"El valor para '{props.get('label', param_name)}' es inválido.")
                return False

        for param_name in self.optional_params_schema:
            if param_name not in self.active_optional_params:
                new_params[param_name] = None

        if new_params:
            self.file_handler.modify_parameters(self.current_file_path, new_params)
        
        return True

    def _add_parameter_to_view(self, param_name: str, param_props: dict, layout: QFormLayout):
        """
        Crea y añade un widget para un parámetro al layout especificado.
        """
        label = QLabel(param_props.get('label', param_name))
        label.setToolTip(param_props.get('tooltip', ''))
        
        if param_props.get('optional') and 'current' not in param_props:
            param_props['current'] = param_props.get('default')

        widget = self.widget_factory.create_widget(param_props)
        
        if isinstance(widget, PatchesWidget):
            self.patches_widget_instance = widget

        if param_props.get('optional'):
            remove_button = QPushButton("X")
            remove_button.setFixedSize(24, 24)
            remove_button.setToolTip("Eliminar este parámetro opcional")
            
            remove_button.clicked.connect(
                lambda: self._remove_optional_parameter(param_name, layout)
            )

            container = QWidget()
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.addWidget(widget)
            h_layout.addWidget(remove_button)
            
            layout.addRow(label, container)
        else:
            layout.addRow(label, widget)
            
        self.parameter_widgets[param_name] = (widget, param_props)

    def _remove_optional_parameter(self, param_name: str, layout: QFormLayout):
        """
        Elimina un parámetro opcional de la vista y de los widgets activos.
        """
        if param_name in self.parameter_widgets:
            for i in range(layout.rowCount()):
                label_item = layout.itemAt(i, QFormLayout.LabelRole)
                if label_item and label_item.widget() and label_item.widget().text() == self.parameter_widgets[param_name][1].get('label', param_name):
                    layout.removeRow(i)
                    break
            
            del self.parameter_widgets[param_name]
            self.active_optional_params.remove(param_name)
            
            if hasattr(self, 'add_optional_param_button'):
                self.add_optional_param_button.setEnabled(True)

    def _open_optional_parameters_dialog(self):
        """
        Abre un diálogo para que el usuario seleccione qué parámetros opcionales añadir.
        """
        available_params = {
            name: props for name, props in self.optional_params_schema.items()
            if name not in self.active_optional_params
        }

        if not available_params:
            QMessageBox.information(self.scroll_area, "Sin Parámetros",
                                    "Todos los parámetros opcionales ya han sido añadidos.")
            return

        dialog = OptionalParametersDialog(available_params, self.scroll_area)
        if dialog.exec() == QDialog.Accepted:
            selected_params = dialog.get_selected_parameters()
            
            form_layout = self.scroll_area.widget().findChild(QFormLayout)
            if form_layout:
                for param_name in selected_params:
                    if param_name not in self.active_optional_params:
                        param_props = self.optional_params_schema[param_name]
                        self._add_parameter_to_view(param_name, param_props, form_layout)
                        self.active_optional_params.add(param_name)

            if len(self.active_optional_params) == len(self.optional_params_schema):
                self.add_optional_param_button.setEnabled(False)

    def highlight_patch_group(self, patch_name: str, is_selected: bool):
        """
        Delega el resaltado de un patch al widget de patches.
        """
        if self.patches_widget_instance:
            self.patches_widget_instance.highlight_patch_group(patch_name, is_selected)

    def deselect_all_highlights(self):
        """
        Delega la deselección de todos los patches al widget de patches.
        """
        if self.patches_widget_instance:
            self.patches_widget_instance.deselect_all_highlights()

    def _setup_highlight_colors(self):
        """
        Configura los colores de resaltado basados en el tema de la aplicación (claro/oscuro).
        """
        app = QApplication.instance()
        if not app:
            self.highlight_colors = []
            return

        palette = app.palette()
        bg_color = palette.color(QPalette.Window)
        
        luminance = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue())

        if luminance < 128:  # Dark theme
            self.highlight_colors = [
                "#5B5B9A", "#9A5B9A", "#B98A5B", "#A8A85B",
                "#5B9AA8", "#A85B5B", "#5BA85B"
            ]
        else:  # Light theme
            self.highlight_colors = [
                "#E6E6FA", "#D8BFD8", "#FFDAB9", "#F0E68C",
                "#ADD8E6", "#F08080", "#98FB98"
            ]