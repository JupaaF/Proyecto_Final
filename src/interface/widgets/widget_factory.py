from .parameter_widgets.string_widget import StringWidget
from .parameter_widgets.int_widget import IntWidget
from .parameter_widgets.float_widget import FloatWidget
from .parameter_widgets.vector_widget import VectorWidget
from .parameter_widgets.dimensions_widget import DimensionsWidget
from .parameter_widgets.choice_widget import ChoiceWidget
from .parameter_widgets.choice_with_options_widget import ChoiceWithOptionsWidget
from .parameter_widgets.patches_widget import PatchesWidget

class WidgetFactory:
    """
    Fábrica para crear los widgets de parámetros apropiados según el tipo de parámetro.
    """
    def __init__(self, get_vtk_patch_names_func=None, highlight_colors=None):
        """
        Inicializa la fábrica de widgets.

        Args:
            get_vtk_patch_names_func (callable, optional): Función para obtener los nombres de los patches.
                                                           Requerido para PatchesWidget.
            highlight_colors (list, optional): Lista de colores para resaltar patches.
                                               Requerido para PatchesWidget.
        """
        self.get_vtk_patch_names_func = get_vtk_patch_names_func
        self.highlight_colors = highlight_colors if highlight_colors is not None else []

        self.widget_map = {
            'string': StringWidget,
            'int': IntWidget,
            'float': FloatWidget,
            'vector': VectorWidget,
            'dimensions': DimensionsWidget,
            'choice': ChoiceWidget,
            'choice_with_options': ChoiceWithOptionsWidget,
            'patches': PatchesWidget,
        }

    def create_widget(self, param_props: dict):
        """
        Crea y devuelve un widget de parámetro basado en sus propiedades.

        Args:
            param_props (dict): El diccionario de propiedades del parámetro.

        Returns:
            BaseParameterWidget: Una instancia del widget apropiado.
        """
        widget_type = param_props.get('type', 'string')
        widget_class = self.widget_map.get(widget_type, StringWidget)

        # Manejo de dependencias para widgets complejos
        if widget_class is ChoiceWithOptionsWidget:
            return ChoiceWithOptionsWidget(param_props, widget_factory=self)

        if widget_class is PatchesWidget:
            if not self.get_vtk_patch_names_func:
                raise ValueError("La función 'get_vtk_patch_names_func' es necesaria para PatchesWidget.")
            return PatchesWidget(param_props,
                                 widget_factory=self,
                                 get_vtk_patch_names_func=self.get_vtk_patch_names_func,
                                 highlight_colors=self.highlight_colors)

        # Creación de widgets simples
        return widget_class(param_props)
