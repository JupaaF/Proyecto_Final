from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class setFieldsDict(FoamFile):
    """
    Representa el archivo 'setFieldsDict' de OpenFOAM.
    """
    def __init__(self):
        super().__init__(name="setFieldsDict", folder="system", class_type="dictionary")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Valores por defecto para la caja
        self.box_min = {'x': 0, 'y': 0, 'z': -1}
        self.box_max = {'x': 0.1461, 'y': 0.292, 'z': 1}
        self.filePhase = 'alpha.water'
        self.customContent = None

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("setFieldsDict_template.jinja2")
        context = {
            'filePhase': self.filePhase,
            'box_min': self.box_min,
            'box_max': self.box_max,
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
            'box_min': {
                'label': 'Caja Mínima (x y z)',
                'tooltip': 'Coordenadas mínimas de la caja para setFields.',
                'type': 'vector',
                'current': self.box_min,
                'group': 'Región de Inicialización',
            },
            'box_max': {
                'label': 'Caja Máxima (x y z)',
                'tooltip': 'Coordenadas máximas de la caja para setFields.',
                'type': 'vector',
                'current': self.box_max,
                'group': 'Región de Inicialización',
            },
            'filePhase':{
                'label': 'Archivo y phase a agregar',
                'tooltip': 'Algo',#TODO
                'type': 'string',
                'current': self.filePhase,
                'group': 'Región de Inicialización',
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