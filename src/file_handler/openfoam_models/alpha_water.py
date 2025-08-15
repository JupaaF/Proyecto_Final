from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class alpha_water(FoamFile):
    """
    Representa el archivo 'alpha.water' de OpenFOAM, utilizando el motor
    de plantillas Jinja2 para generar su contenido.
    """
    def __init__(self):
        super().__init__(name="alpha.water", folder="0", class_type="volScalarField")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Inicializa los parámetros con valores por defecto
        self.internalField = 0
        self.boundaryField = []

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("alpha_water_template.jinja2")
        context = {
            'internalField': self.internalField,
            'boundaryField': self.boundaryField
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
            'internalField': {
                'label': 'Campo Interno (alpha.water)',
                'tooltip': 'Define el valor inicial de alpha.water en todo el dominio (0 a 1).',
                'type': 'float',
                'current': self.internalField,
                'group': 'Campo Interno',
            },
            'boundaryField': {
                'label': 'Condiciones de Borde',
                'tooltip': 'Define las condiciones de alpha.water en los límites del dominio.',
                'type': 'list_of_dicts',
                'current': self.boundaryField,
                'group': 'Condiciones de Borde',
                'schema': {
                    'patchName': 'string',
                    'type': {
                        'type': 'choice',
                        'default': 'zeroGradient',
                        'options': [
                            {
                                'name': 'zeroGradient',
                                'label': 'Gradiente Cero',
                                'parameters': []
                            },
                            {
                                'name': 'inletOutlet',
                                'label': 'Valor Fijo',
                                'parameters' : [
                                    {
                                        'name': 'inletValue',
                                        'type': 'float',
                                        'label': 'inletValue',
                                        'default': 0
                                    },
                                    {
                                        'name': 'value',
                                        'type': 'float',
                                        'label': 'value',
                                        'default': 0
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }


    