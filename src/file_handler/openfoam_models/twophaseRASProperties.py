from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class twophaseRASProperties(FoamFile):
    """
    Representa el archivo 'twophaseRASProperties' de OpenFOAM.
    """
    def __init__(self):
        super().__init__(name="twophaseRASProperties", folder="constant", class_type="dictionary")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Valores por defecto
        self.customContent = None
        self.SUS = 1
        self.KE1 = 0
        self.KE3 = 0
        self.B = 0.25
        self.Tpsmall = 1e-6

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("twophaseRASProperties_template.jinja2")

        context = {
            'SUS': self.SUS,
            'KE1': self.KE1,
            'KE3': self.KE3,
            'B': self.B,
            'Tpsmall': self.Tpsmall,
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
            'SUS': {
                'label': 'SUS',
                'tooltip': '',
                'type': 'float',
                'current': self.SUS
            },  
            'KE1': {
                'label': 'KE1',
                'tooltip': 'coef. for density stratif (Uf-Us)',
                'type': 'float',
                'current': self.KE1
            },  
            'KE3': {
                'label': 'KE3',
                'tooltip': 'coef. for turbulence generation',
                'type': 'float',
                'current': self.KE3
            },  
            'B': {
                'label': 'B',
                'tooltip': 'empirical parameter for turb drag',
                'type': 'float',
                'current': self.B
            },  
            'Tpsmall': {
                'label': 'Tpsmall',
                'tooltip': 'min. Tp value for turb. drag	',
                'type': 'float',
                'current': self.Tpsmall
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
       



    