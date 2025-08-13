from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class g(FoamFile):
    """
    Representa el archivo 'g' (gravedad) de OpenFOAM.
    """
    def __init__(self):
        super().__init__(name="g", folder="constant", class_type="uniformDimensionedVectorField")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Valor por defecto para la gravedad
        self.value = {'x': 0, 'y': -9.81, 'z': 0}

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("g_template.jinja2")
        context = {
            'value': self.value
        }
        content = template.render(context)
        return self.get_header() + content

    def update_parameters(self, params: dict):
        """
        Actualiza los parámetros desde un diccionario.
        """
        for key, value in params.items():
            setattr(self, key, value)

    def write_file(self, case_path: Path):
        """
        Escribe el contenido generado en la ruta del caso especificada.
        """
        output_dir = case_path / self.folder
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / self.name
        with open(output_path, "w") as f:
            f.write(self._get_string())

    def get_editable_parameters(self):
        """
        Devuelve un diccionario con los parámetros editables y sus valores actuales.
        """
        return {
            'value': {
                'label': 'Vector de Gravedad',
                'tooltip': 'Define el vector de la aceleración de la gravedad.',
                'type': 'vector',
                'current': self.value,
                'group': 'Constantes Físicas',
            }
        }


    