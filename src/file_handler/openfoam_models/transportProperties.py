from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class transportProperties(FoamFile):
    """
    Representa el archivo 'transportProperties' de OpenFOAM.
    """
    def __init__(self):
        super().__init__(name="transportProperties", folder="constant", class_type="dictionary")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Valores por defecto
        self.sigma = 0.07
        self.phases = [
            {'name': 'water', 'content': 'transportModel  Newtonian;\nviscosity       uniform 1e-06;\ndensity         uniform 1000;'},
            {'name': 'air', 'content': 'transportModel  Newtonian;\nviscosity       uniform 1.8e-05;\ndensity         uniform 1;'}
        ]

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("transportProperties_template.jinja2")
        context = {
            'sigma': self.sigma,
            'phases': self.phases
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
            'sigma': {
                'label': 'Tensión Superficial (sigma)',
                'tooltip': 'Coeficiente de tensión superficial entre fases.',
                'type': 'float',
                'current': self.sigma,
                'group': 'Propiedades Físicas',
            },
            'phases': {
                'label': 'Fases',
                'tooltip': 'Define las propiedades de cada fase (ej. agua, aire).',
                'type': 'list_of_dicts',
                'current': self.phases,
                'group': 'Propiedades de Fase',
                'schema': {
                    'name': {'label': 'Nombre de la Fase', 'type': 'string', 'default': 'nuevaFase'},
                    'content': {'label': 'Contenido de la Fase', 'type': 'string', 'multiline': True, 'default': 'transportModel  Newtonian;\nviscosity       uniform 1e-06;\ndensity         uniform 1000;'}
                }
            }
        }



    