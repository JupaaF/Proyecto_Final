from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class ppProperties(FoamFile):
    """
    Representa el archivo 'ppProperties' de OpenFOAM.
    """
    def __init__(self):
        super().__init__(name="ppProperties", folder="constant", class_type="dictionary")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

        # Valores por defecto
        self.customContent = None
        self.ppModel = 'JohnsonJackson'
        self.alphaMax = 0.635
        self.alphaMinFriction = 0.57
        self.Fr = 0.05
        self.eta0 = 3
        self.eta1 = 5
        self.packingLimiter = 'no'
        
        
        

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("ppProperties_template.jinja2")

        context = {
            'ppModel': self.ppModel,
            'alphaMax': self.alphaMax,
            'alphaMinFriction': self.alphaMinFriction,
            'Fr': self.Fr,
            'eta0': self.eta0,
            'eta1': self.eta1,
            'packingLimiter': self.packingLimiter,
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
            'ppModel': {
                'label': 'ppModel',
                'tooltip': 'Modelo de la presión elástica.',
                'type': 'choice',
                'options': ['JohnsonJackson','Hsu','MerckelbachKranenburg','Chauchat'],
                'current': self.ppModel
            }, 
            'alphaMax': {
                'label': 'alphaMax',
                'tooltip': 'Fracción máxima de volumen sólido.',
                'type': 'float',
                'current': self.alphaMax
            }, 
            'alphaMinFriction': {
                'label': 'alphaMinFriction',
                'tooltip': 'Random loose packing frac.',
                'type': 'float',
                'current': self.alphaMinFriction
            }, 
            'Fr': {
                'label': 'Fr',
                'tooltip': 'Módulo elástico.',
                'type': 'float',
                'current': self.Fr
            }, 
            'eta0': {
                'label': 'eta0',
                'tooltip': 'Exponente empírico.',
                'type': 'float',
                'current': self.eta0
            },  
            'eta1': {
                'label': 'eta1',
                'tooltip': 'Exponente empírico.',
                'type': 'float',
                'current': self.eta1
            }, 
            'packingLimiter': {
                'label': 'packingLimiter',
                'tooltip': '',
                'type': 'choice',
                'options': ['yes','no'],
                'current': self.packingLimiter
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
       



    