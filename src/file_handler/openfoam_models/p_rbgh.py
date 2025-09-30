from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class p_rbgh(FoamFile):
    """
    Representa el archivo 'p_rbgh' de OpenFOAM.
    """
    def __init__(self, second_part=None):
        if second_part != None:
            name_aux = "p_rbgh" + "." + second_part
            object_name = "p_rbgh" + "_" + second_part
        else:
            name_aux = "p_rbgh"
            object_name = None
        super().__init__(name=name_aux, folder="0", class_type="volScalarField",object_name=object_name)
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Valores por defecto
        self.internalField = 0
        self.boundaryField = []
        self.unitDimensions = [1, -1, -2, 0, 0, 0, 0]
        self.customContent = None

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("p_rbgh_template.jinja2")
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
                'label': 'Campo Interno (p_rbgh)',
                'tooltip': 'Valor inicial de la presión modificada en el dominio.',
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
                        'default': 'fixedFluxPressure',
                        'options': [
                            {
                                'name': 'fixedFluxPressure',
                                'label': 'fixedFluxPressure',
                                'parameters' : [
                                    {
                                        'name': 'value',
                                        'type': 'float',
                                        'label': 'Valor (uniforme)',
                                        'tooltip': 'Valor de presión para esta condición de borde.',
                                        'default': 0
                                    },
                                    {
                                        'name': 'gradient',
                                        'type': 'float',
                                        'label': 'gradient',
                                        'tooltip': 'Valor de presión para esta condición de borde.',
                                        'default': 0
                                    }
                                ]
                            },
                            {
                                'name': 'zeroGradient',
                                'label': 'zeroGradient',
                                'parameters' : []
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
                                        'label': 'Valor (uniforme)',
                                        'tooltip': 'Valor de presión para esta condición de borde.',
                                        'default': 0
                                    }
                                ]
                            },
                            {
                                'name': 'symmetryPlane',
                                'label': 'symmetryPlane',
                                'parameters' : []
                            },
                            {
                                'name': 'totalPressure',
                                'label': 'totalPressure',
                                'parameters' : [
                                    {
                                        'name': 'p0', #cambie esto
                                        'type': 'float',
                                        'label': 'Valor de Presión Total',
                                        'tooltip': 'Valor de la presión total (p0) para esta condición.',
                                        'default': 0
                                    }
                                ]
                            },
                            {
                                'name': 'empty',
                                'label': 'empty',
                                'parameters' : []
                            },
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
