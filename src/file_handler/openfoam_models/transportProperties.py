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
        self.selected_solver = []
        self.customContent = None

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("transportProperties_template.jinja2")
        
        # Convierte la lista de parámetros en un diccionario para simplificar el manejo en el jinja
        # if self.selected_solver:
        params_dict = self.selected_solver[1].copy()
        params_dict['solver_selected'] = self.selected_solver[0]

        context = {
            'params': params_dict,
            'customContent':self.customContent
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
            'selected_solver': {
                'label': 'Caso/Solver a usar.',
                'tooltip': 'El archivo cambia según esto. Define las propiedades de cada fase (ej. agua, aire).', 
                'type': 'choice_with_options',
                'current': self.selected_solver,
                'group': 'Propiedades de Transporte',
                'options': [
                    {
                        'name': 'interFoam',
                        'label': 'interFoam',
                        'parameters':[
                            {
                                'name': 'sigma',
                                'label': 'Tensión Superficial (sigma)',
                                'tooltip': 'Coeficiente de tensión superficial entre fases.',
                                'type': 'float',
                                'default': 0.07,
                                'group': 'Propiedades Físicas',
                            },
                            {
                                'name': 'water_transportModel',
                                'label': 'water transportModel',
                                'tooltip': 'Modelo de transporte para el agua.' ,
                                'type': 'string',
                                'default': 'Newtonian'
                            },
                            {
                                'name': 'water_nu',
                                'label': 'water nu',
                                'tooltip': 'water nu',
                                'type': 'string',
                                'default': '1e-06'
                            },
                            {
                                'name': 'water_rho',
                                'label': 'water rho',
                                'tooltip': 'water rho',
                                'type': 'int',
                                'default': 1000
                            },
                            {
                                'name': 'air_transportModel',
                                'label': 'air transportModel',
                                'tooltip': 'Modelo de transporte para el aire.',
                                'type': 'string',
                                'default': 'Newtonian'
                            },
                            {
                                'name': 'air_nu',
                                'label': 'air nu',
                                'tooltip': 'air nu',
                                'type': 'string',
                                'default': '1.48e-05'
                            },
                            {
                                'name': 'air_rho',
                                'label': 'air rho',
                                'tooltip': 'air rho',
                                'type': 'int',
                                'default': 1
                            },
                        ]
                        
                    },
                    {
                        'name': '2DChannel',
                        'label': '2DChannel-SedFOAM',
                        'parameters':[
                            {
                                'name': 'da',
                                'label': 'Diámetro Fase A',
                                'tooltip': 'Diámetro de las partículas.' ,
                                'type': 'string',
                                'default': '1.e-7'
                            },                             #TODO: ver el tipo y si
                            {
                                'name': 'db',
                                'label': 'Diámetro Fase B',
                                'tooltip': 'Diámetro de las partículas.' ,
                                'type': 'string',
                                'default': '1.e-7'
                            }
                            ]
                    },
                    {
                        'name': '3DScourSqr',
                        'label': '3DScourSqr-SedFOAM',
                        'parameters':[
                            {
                                'name': 'da',
                                'label': 'Diámetro Fase A',
                                'tooltip': 'Diámetro de las partículas.' ,
                                'type': 'string',
                                'default': '0.26e-3'
                            },                             #TODO: ver el tipo y si
                            {
                                'name': 'db',
                                'label': 'Diámetro Fase B',
                                'tooltip': 'Diámetro de las partículas.' ,
                                'type': 'string',
                                'default': '10e-6'
                            }
                        ]
                    }
                ]
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



    