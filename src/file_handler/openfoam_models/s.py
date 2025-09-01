from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class s(FoamFile):
    """
    Representa el archivo 's' (presión modificada) de OpenFOAM.
    """
    def __init__(self):
        super().__init__(name="s", folder="0", class_type="volScalarField")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Valores por defecto
        self.internalField = 0
        self.boundaryField = []

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("s_template.jinja2")
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
        if not isinstance(params,dict):
            raise ValueError("Me tenes que dar un diccionario")
        
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
                'label': 'Campo Interno (s)',
                'tooltip': 'Valor inicial de la s modificada en el dominio.',
                'type': 'float',
                'current': self.internalField,
                'group': 'General'
            },
            'boundaryField': {
                'label': 'Condiciones de Borde para Presión',
                'tooltip': 'Define las condiciones de presión modificada en los límites.',
                'type': 'patches',
                'current': self.boundaryField,
                'group': 'Condiciones de Borde',
                'schema': {
                    'patchName': 'string',
                    'type': {
                        'type': 'choice',
                        'default': 'zeroGradient',
                        'options': [
                            {
                                'name': 'fixedValue',
                                'label': 'Valor Fijo',
                                'parameters' : [
                                    {
                                        'name': 'value',
                                        'type': 'float',
                                        'label': 'Valor (uniforme)',
                                        'tooltip': 'Valor de presión para esta condición de borde.',
                                        'default': 0
                                    }
                                ]
                            },
                            {
                                'name': 'zeroGradient',
                                'label': 'Gradiente zero',
                                'parameters' : []
                            },
                            {
                                'name': 'inletOutlet',
                                'label': 'Entrada/Salida',
                                'parameters' : [
                                    {
                                        'name': 'inletValue',
                                        'type': 'float',
                                        'label': 'Valor de entrada',
                                        'tooltip': 'Valor de presión para esta condición de borde.',
                                        'default': 0
                                    },
                                    {
                                        'name': 'value',
                                        'type': 'float',
                                        'label': 'Valor fijo',
                                        'tooltip': 'Valor de presión para esta condición de borde.',
                                        'default': 0
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
