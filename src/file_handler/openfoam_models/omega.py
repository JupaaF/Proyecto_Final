from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class omega(FoamFile):
    """
    Representa el archivo 'omega' (tasa de disipación específica) de OpenFOAM.
    """
    def __init__(self, second_part=None):
        if second_part != None:
            name_aux = "omega" + "." + second_part
        else:
            name_aux = "omega"
            
        super().__init__(name=name_aux, folder="0", class_type="volScalarField",object_name="omega")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Valores por defecto
        self.internalField = 10
        self.boundaryField = []
        self.unitDimensions = [0, 0, -1, 0, 0, 0, 0]
        self.customContent = None

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("omega_template.jinja2")
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
                'label': 'Campo Interno',
                'tooltip': 'Valor inicial en el dominio.',
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
                        'default': 'fixedValue',
                        'options': [
                            {
                                'name': 'fixedValue',
                                'label': 'fixedValue',
                                'parameters' : [
                                    {
                                        'name': 'value',
                                        'type': 'float',
                                        'label': 'Valor (uniforme)',
                                        'tooltip': 'value',
                                        'default': 0
                                    }
                                ]
                            },{
                                'name': 'zeroGradient',
                                'label': 'zeroGradient',
                                'parameters' : []
                            },
                            {
                                'name': 'omegaWallFunction',
                                'label': 'omegaWallFunction',
                                'parameters' : [
                                    
                                    {
                                        'name': 'value', 
                                        'type': 'float',
                                        'label': 'value',
                                        'tooltip': 'value',
                                        'default': 594.884
                                    },
                                    {
                                        'name': 'kn', 
                                        'type': 'float',
                                        'label': 'kn',
                                        'tooltip': 'kn',
                                        'default': 0.0002,
                                        'optional': True
                                    },
                                    {
                                        'name': 'blending', 
                                        'type': 'string',
                                        'label': 'blending',
                                        'tooltip': 'blending',
                                        'default': 'tanh',
                                        'optional':True
                                    }
                                ]
                            },
                            {
                                'name': 'inletOutlet',
                                'label': 'inletOutlet',
                                'parameters' : [
                                    {
                                        'name': 'inletValue', #cambie esto
                                        'type': 'float',
                                        'label': 'inletValue',
                                        'tooltip': 'inletValue',
                                        'default': 0
                                    },
                                    {
                                        'name': 'value', #cambie esto
                                        'type': 'float',
                                        'label': 'value',
                                        'tooltip': 'value',
                                        'default': 0
                                    }
                                ]
                            },
                            {
                                'name': 'wilcoxOmegaWallFunction',
                                'label': 'wilcoxOmegaWallFunction',
                                'parameters' : [
                                    {
                                        'name': 'value', 
                                        'type': 'float',
                                        'label': 'value',
                                        'tooltip': 'value',
                                        'default': 594.884
                                    },
                                    {
                                        'name': 'kn', 
                                        'type': 'float',
                                        'label': 'kn',
                                        'tooltip': 'kn',
                                        'default': 0.0002
                                    }
                                ]
                            },
                            {
                                'name': 'cyclic',
                                'label': 'cyclic',
                                'parameters' : []
                            },
                            {
                                'name': 'symmetryPlane',
                                'label': 'symmetryPlane',
                                'parameters' : []
                            },
                            {
                                'name': 'groovyBC',
                                'label': 'groovyBC',
                                'parameters' : []
                            },
                            {
                                'name': 'empty',
                                'label': 'empty',
                                'parameters' : []
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
