from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class Theta(FoamFile):
    """
    Representa el archivo 'Theta' de OpenFOAM, utilizando el motor
    de plantillas Jinja2 para generar su contenido.
    """
    def __init__(self, second_part=None):
        if second_part != None:
            name_aux = "Theta" + "." + second_part
        else:
            name_aux = "Theta"
        super().__init__(name=name_aux, folder="0", class_type="volScalarField")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Inicializa los parámetros con valores por defecto
        self.internalField = []
        self.boundaryField = []
        self.unitDimensions = [0, 2, -2, 0, 0, 0, 0]
        self.customContent = None

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """

        internalField = self.internalField[1].copy()
        internalField['option_selected'] = self.internalField[0]

        template = self.jinja_env.get_template("Theta_template.jinja2")
        context = {
            'uDim': self.unitDimensions,
            'internalField': internalField,
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
                'label': 'InternalField (Theta)',
                'tooltip': 'Define el valor inicial de Theta en todo el dominio (0 a 1).',
                'type': 'choice_with_options',
                'current': self.internalField,
                'options': [
                            {
                                'name': 'uniform',
                                'label': 'uniform',
                                'parameters' : [
                                    {
                                        'name': 'value',
                                        'type': 'float',
                                        'label': 'value',
                                        'tooltip': 'value',
                                        'default': 0
                                    },
                                ]
                            },
                            {
                                'name': 'customPatch',
                                'label': 'Contenido Personalizado',
                                'parameters' : [
                                    {
                                        'name': 'customPatchContent',
                                        'type': 'string',
                                        'label': 'customPatchContent',
                                        'tooltip': 'customPatchContent',
                                        'default': "",
                                    }
                                ] 
                            }
                        ],
                'group': 'Campo Interno',
            },
            'boundaryField': {
                'label': 'Condiciones de Borde',
                'tooltip': 'Define las condiciones de alpha.water en los límites del dominio.',
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
                                'name': 'zeroGradient',
                                'label': 'zeroGradient',
                                'parameters': []
                            },
                            {
                                'name': 'cyclic',
                                'label': 'cyclic',
                                'parameters' : []
                            },
                            {
                                'name': 'groovyBC',
                                'label': 'groovyBC',
                                'parameters' : []
                            },
                            {
                                'name': 'fixedValue',
                                'label': 'fixedValue',
                                'parameters' : [
                                    {
                                        'name': 'value',
                                        'type': 'float',
                                        'label': 'value',
                                        'tooltip': 'value',
                                        'default': 0
                                    },
                                ]
                            },
                            {
                                'name': 'empty',
                                'label': 'empty',
                                'parameters' : []
                            },
                            {
                                'name': 'symmetryPlane',
                                'label': 'symmetryPlane',
                                'parameters' : []
                            },
                            {
                                'name': 'customPatch',
                                'label': 'customPatch',
                                'parameters' : [
                                    {
                                        'name': 'customPatchContent',
                                        'type': 'string',
                                        'label': 'customPatchContent',
                                        'tooltip': 'customPatchContent',
                                        'default': "",
                                    }
                                ] 
                            }
                            # {
                            #     'name': 'inletOutlet',
                            #     'label': 'inletOutlet',
                            #     'parameters' : [
                            #         {
                            #             'name': 'inletValue',
                            #             'type': 'float',
                            #             'label': 'Valor de Entrada',
                            #             'tooltip': 'El valor de alpha.water en la entrada.',
                            #             'default': 0
                            #         },
                            #         {
                            #             'name': 'value',
                            #             'type': 'float',
                            #             'label': 'Valor Uniforme',
                            #             'tooltip': 'El valor uniforme de alpha.water para esta condición.',
                            #             'default': 0
                            #         }
                            #     ]
                            # },
                            
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


    