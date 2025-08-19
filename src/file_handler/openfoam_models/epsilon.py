from pathlib import Path
from .foam_file import FoamFile
# Para que este script funcione, se debe instalar Jinja2:
# pip install Jinja2
from jinja2 import Environment, FileSystemLoader

class epsilon(FoamFile):
    """
    Representa el archivo 'U' (velocidad) de OpenFOAM, utilizando el motor
    de plantillas Jinja2 para generar su contenido.

    Este enfoque externaliza completamente la estructura del archivo a una
    plantilla, permitiendo que el código Python se centre únicamente en la
    preparación de los datos.
    """
    def __init__(self):
        super().__init__(name="epsilon", folder="0", class_type="volScalarField")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        # Inicializa los parámetros con valores por defecto
        self.internalField = 0
        self.boundaryField = []

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo 'U' renderizando la plantilla Jinja2
        con los datos de la instancia.
        """
        template = self.jinja_env.get_template("epsilon_template.jinja2")
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
                'label': 'Campo Interno (epsilon)',
                'tooltip': 'Define el valor inicial de la tasa de disipación de turbulencia (epsilon) en todo el dominio.',
                'type': 'float',
                'current': self.internalField,
                'group': 'Campo Interno',
            },
            'boundaryField': {
                'label': 'Condiciones de Borde',
                'tooltip': 'Define las condiciones de epsilon en los límites del dominio.',
                'type': 'patches',
                'current': self.boundaryField,
                'group': 'Condiciones de Borde',
                'schema': {
                    'patchName': 'string',
                    'type': {
                        'type': 'choice',
                        'default': 'epsilonWallFunction',
                        'options': [
                            {
                                'name': 'epsilonWallFunction',
                                'label': 'Función de Pared (epsilonWallFunction)',
                                'parameters': [
                                    {
                                        'name': 'value',
                                        'type': 'float',
                                        'label': 'Valor',
                                        'tooltip': 'Valor para la función de pared de epsilon.',
                                        'default': 0
                                    }
                                ]
                            },
                            {
                                'name': 'inletOutlet',
                                'label': 'Entrada/Salida',
                                'parameters' : [
                                    {
                                        'name': 'inletValue',
                                        'type': 'float',
                                        'label': 'Valor de Entrada',
                                        'tooltip': 'Valor de epsilon en la entrada.',
                                        'default': 0
                                    },
                                    {
                                        'name': 'value',
                                        'type': 'float',
                                        'label': 'Valor (uniforme)',
                                        'tooltip': 'Valor uniforme para la condición de borde.',
                                        'default': 0
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
    

