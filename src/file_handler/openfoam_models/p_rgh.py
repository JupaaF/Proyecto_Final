from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class p_rgh(FoamFile):
    """
    Representa el archivo 'p_rgh' (presión modificada) de OpenFOAM.
    """
    def __init__(self):
        super().__init__(name="p_rgh", folder="0", class_type="volScalarField")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Valores por defecto
        self.internalField = 0
        self.boundaryField = []

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("p_rgh_template.jinja2")
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
                'label': 'Campo Interno (p_rgh)',
                'tooltip': 'Valor inicial de la presión modificada en el dominio.',
                'type': 'float',
                'current': self.internalField,
                'group': 'General'
            },
            'boundaryField': {
                'label': 'Condiciones de Borde para Presión',
                'tooltip': 'Define las condiciones de presión modificada en los límites.',
                'type': 'list_of_dicts',
                'current': self.boundaryField,
                'group': 'Condiciones de Borde',
                'schema': {
                    'patchName': 'string',
                    'type': {
                        'type': 'choice',
                        'default': 'fixedFluxPressure',
                        'options': [
                            {
                                'name': 'fixedFluxPressure',
                                'label': 'Presión con Flujo Fijo (fixedFluxPressure)',
                                'requires_value': False
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
