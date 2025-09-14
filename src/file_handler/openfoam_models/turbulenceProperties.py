from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class turbulenceProperties(FoamFile):
    """
    Representa el archivo 'turbulenceProperties' de OpenFOAM.
    """
    def __init__(self, second_part=None):
        if second_part != None:
            name_aux = "turbulenceProperties" + "." + second_part
        else:
            name_aux = "turbulenceProperties"

        super().__init__(name=name_aux, folder="constant", class_type="dictionary")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Valores por defecto
        self.simulation_type = 'laminar'

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("turbulenceProperties_template.jinja2")
        context = {
            'simulation_type': self.simulation_type
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
            'simulation_type': {
                'label': 'Tipo de simulación',
                'tooltip': 'Define el tipo de simulación de turbulencia (ej. laminar (sin turbulencia), RAS, LES).',
                'type': 'choice',
                'current': self.simulation_type,
                'group': 'Configuración General',
                # 'options': [  #TODO: completar con los demas tipos que hayan
                #     {'name': 'laminar', 'label': 'laminar'},
                #     {'name': 'RAS', 'label': 'RAS'},
                #     {'name': 'LES', 'label': 'LES'}
                # ]
                'options': ['laminar','RASWaterChannel','LES','RASSedFoam']
            }
        }