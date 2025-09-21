from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class s(FoamFile):
    """
    Representa el archivo 's' (presión modificada) de OpenFOAM.
    """
    def __init__(self, second_part=None):
        if second_part != None:
            name_aux = "s" + "." + second_part
            object_name = "s" + "_" + second_part
        else:
            name_aux = "s"
            object_name = None
        super().__init__(name="s", folder="0", class_type="volScalarField",object_name=object_name)
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Valores por defecto
        self.internalField = 0
        self.boundaryField = []
        self.unitDimensions = [0,0,0,0,0,0,0]
        self.customContent = None

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("s_template.jinja2")
        context = {
            'uDim':self.unitDimensions,
            'internalField': self.internalField,
            'boundaryField': self.boundaryField,
            'customContent': self.customContent
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

            if value is None:
                setattr(self, key, None)
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
                'label': 'Condiciones de Borde',
                'tooltip': 'Define las condiciones en los límites.',
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
                                'label': 'fixedValue',
                                'parameters' : [
                                    {
                                        'name': 'value',
                                        'type': 'float',
                                        'label': 'Valor (uniforme)',
                                        'tooltip': 'Valor para esta condición de borde.',
                                        'default': 0
                                    }
                                ]
                            },
                            {
                                'name': 'zeroGradient',
                                'label': 'zeroGradient',
                                'parameters' : [
                                    {
                                        'name': 'value',
                                        'type': 'float',
                                        'label': 'Valor de Neumann',
                                        'tooltip': 'El valor de s en la entrada.',
                                        'default': 0,
                                        'optional': True
                                    }
                                ]
                            },
                            {
                                'name': 'inletOutlet',
                                'label': 'inletOutlet',
                                'parameters' : [
                                    {
                                        'name': 'inletValue',
                                        'type': 'float',
                                        'label': 'inletValue',
                                        'tooltip': 'Valor de presión para esta condición de borde.',
                                        'default': 0
                                    },
                                    {
                                        'name': 'value',
                                        'type': 'float',
                                        'label': 'value',
                                        'tooltip': 'Valor de presión para esta condición de borde.',
                                        'default': 0
                                    }
                                ]
                            }
                        ]
                    }
                }
            },
            'unitDimensions': {
                'label': 'Dimension de unidades',
                'tooltip': 'Unidades de los parametros',
                'type': 'dimensions',
                'current': self.unitDimensions,
            },
            'customContent': {
                'label': 'Contenido de experto',
                'tooltip': 'Cosas que van directamente al archivo',
                'type': 'string',
                'default': "",
                'current': self.customContent,
                'optional': True
            }
        }
