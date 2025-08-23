from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class omega(FoamFile):
    """
    Representa el archivo 'omega' (tasa de disipación específica) de OpenFOAM.
    """
    def __init__(self):
        super().__init__(name="omega", folder="0", class_type="volScalarField")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Valores por defecto
        self.internalField = 10
        self.boundaryField = []

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("omega_template.jinja2")
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

        param_props = self.get_editable_parameters()

        for key, value in params.items():

            if not hasattr(self,key):
                continue

            props = param_props[key]
            type_data = props['type']

            try:
                self._validate(value,type_data,props)
            except ValueError:
                raise

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
                'label': 'Campo Interno (omega)',
                'tooltip': 'Valor inicial de omega en el dominio.',
                'type': 'float',
                'current': self.internalField,
                'group': 'General'
            },
            'boundaryField': {
                'label': 'Condiciones de Borde para Omega',
                'tooltip': 'Define las condiciones de omega en los límites.',
                'type': 'list_of_dicts',
                'current': self.boundaryField,
                'group': 'Condiciones de Borde',
                'schema': {
                    'patchName': 'string',
                    'type': {
                        'type': 'choice',
                        'default': 'omegaWallFunction',
                        'options': [
                            {
                                'name': 'omegaWallFunction',
                                'label': 'Función de Pared (omegaWallFunction)',
                                'requires_value': True,
                                'value_schema': {'type': 'float', 'label': 'Valor'}
                            },
                            {
                                'name': 'zeroGradient',
                                'label': 'Gradiente Cero (zeroGradient)',
                                'requires_value': False
                            },
                            {
                                'name': 'fixedValue',
                                'label': 'Valor Fijo (fixedValue)',
                                'requires_value': True,
                                'value_schema': {'type': 'float', 'label': 'Valor'}
                            }
                        ]
                    }
                }
            }
        }
