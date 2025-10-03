from pathlib import Path

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QMessageBox, QScrollArea, QApplication)
from PySide6.QtGui import QPalette

from ..widgets.widget_factory import WidgetFactory
from ..widgets.parameter_widgets.patches_widget import PatchesWidget
from ..widgets.parameter_container_widget import ParameterContainerWidget

class ParameterEditorManager:
    """
    Gestiona la creación y actualización de la interfaz de usuario para la edición de parámetros.
    Delega la mayor parte de la lógica a un ParameterContainerWidget.
    """
    def __init__(self, scroll_area: QScrollArea, file_handler, get_vtk_patch_names_func):
        """
        Inicializa el gestor del editor de parámetros.
        """
        self.scroll_area = scroll_area
        self.file_handler = file_handler

        self.current_file_path = None
        self.main_container = None
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
        self.main_container = None
        self.patches_widget_instance = None

        if self.scroll_area.parentWidget() and self.scroll_area.parentWidget().parentWidget():
            dock_widget = self.scroll_area.parentWidget().parentWidget()
            dock_widget.setWindowTitle(f"Editor de parámetros - {file_path.name}")

        # Obtener todos los parámetros del archivo
        all_params_schema = self.file_handler.get_editable_parameters(file_path)
        
        # Crear el contenedor principal que manejará todos los parámetros
        self.main_container = ParameterContainerWidget(all_params_schema, self.widget_factory)

        # Buscar si se creó un PatchesWidget para delegar el resaltado
        widgets_map = self.main_container.get_all_widgets()
        for widget, props in widgets_map.values():
            if isinstance(widget, PatchesWidget):
                self.patches_widget_instance = widget
                break

        # Limpiar el widget anterior del scroll area y establecer el nuevo
        if self.scroll_area.widget():
            self.scroll_area.widget().deleteLater()
        
        self.scroll_area.setWidget(self.main_container)
        self.scroll_area.setMinimumWidth(self.main_container.sizeHint().width() + 40)

    def close(self):
        """
        Cierra el editor de parámetros actual, limpiando la UI y el estado.
        """
        # Limpiar el widget del scroll area
        if self.scroll_area.widget():
            self.scroll_area.widget().deleteLater()
            self.scroll_area.setWidget(None) # Asegurarse de que no haya widget colgando

        # Resetear el título del dock
        if self.scroll_area.parentWidget() and self.scroll_area.parentWidget().parentWidget():
            dock_widget = self.scroll_area.parentWidget().parentWidget()
            dock_widget.setWindowTitle("Editor de parámetros")

        # Limpiar el estado interno
        self.current_file_path = None
        self.main_container = None
        self.patches_widget_instance = None


    def save_parameters(self) -> bool:
        """
        Recopila los valores de los widgets de la UI, los valida y los guarda.
        """
        if not self.current_file_path or not self.main_container:
            return True

        try:
            # Obtener todos los valores del contenedor principal
            new_params = self.main_container.get_values()
            
            # El file_handler espera que los opcionales no presentes se pasen como None
            # para eliminarlos del archivo. El container no devuelve los no activos.
            # Por lo tanto, debemos añadirlos explícitamente.
            all_param_names_in_schema = self.main_container.parameters_schema.keys()
            for param_name in all_param_names_in_schema:
                param_props = self.main_container.parameters_schema[param_name]
                if param_props.get('optional') and param_name not in new_params:
                    new_params[param_name] = None

            if new_params:
                self.file_handler.modify_parameters(self.current_file_path, new_params)
            
            return True

        except ValueError as e:
            QMessageBox.warning(self.scroll_area, "Valor Inválido", str(e))
            return False

    def highlight_patch_group(self, patch_name: str, is_selected: bool):
        """
        Delega el resaltado de un patch al widget de patches, si existe.
        """
        if self.patches_widget_instance:
            self.patches_widget_instance.highlight_patch_group(patch_name, is_selected)

    def deselect_all_highlights(self):
        """
        Delega la deselección de todos los patches al widget de patches, si existe.
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