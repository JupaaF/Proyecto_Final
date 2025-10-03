
from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class kineticTheoryProperties(FoamFile):
    """
    Representa el archivo 'kineticTheoryProperties' de OpenFOAM.
    """
    def __init__(self):
        super().__init__(name="kineticTheoryProperties", folder="constant", class_type="dictionary")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Valores por defecto
        self.customContent = None
        self.kineticTheory = 'off'
        self.granularPressureModel = 'Lun'
        self.radialModel = 'CarnahanStarling'
        self.viscosityModel = 'Syamlal'
        self.conductivityModel = 'Syamlal'
        self.e = 0.9
        self.alphaMax = 0.6
        self.MaxTheta = 0.001
        self.phi = 32

        

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("kineticTheoryProperties_template.jinja2")

        context = {
            'customContent': self.customContent,
            'kineticTheory': self.kineticTheory,
            'granularPressureModel': self.granularPressureModel,
            'radialModel': self.radialModel,
            'viscosityModel': self.viscosityModel,
            'conductivityModel': self.conductivityModel,
            'e': self.e,
            'alphaMax': self.alphaMax,
            'MaxTheta': self.MaxTheta,
            'phi': self.phi
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
            'kineticTheory': {
                'label': 'kineticTheory',
                'tooltip': 'Utilizar la teoría cinética o no.',
                'type': 'choice',
                'options': ['on','off'], 
                'current': self.kineticTheory,
            },
            'granularPressureModel': {
                'label': 'granularPressureModel',
                'tooltip': 'Modelo de presión granular.',
                'type': 'choice',
                'options': ['Lun','SyamlalRogersOBrien','Torquato'], 
                'current': self.granularPressureModel
            },
            'radialModel': {
                'label': 'radialModel',
                'tooltip': 'Modelo de distribución radial de la partícula.',
                'type': 'choice',
                'options': ['CamahanStarIing','ChialvoSundaresan','Gidaspow','LunSavage','SinclairJackson','Torquato'], 
                'current': self.radialModel
            },
            'viscosityModel': {
                'label': 'viscosityModel',
                'tooltip': 'Modelo para la viscosidad de corte y la viscosidad volumétrica.',
                'type': 'choice',
                'options': ['GarzoDufty','GarzoDuftyMod','Gidaspow','HrenyaSincIair','Syamlal','none'], 
                'current': self.viscosityModel
            },
            'conductivityModel': {
                'label': 'conductivityModel',
                'tooltip': 'Modelo para la conductividad de la temperatura granular.',
                'type': 'choice',
                'options': ['GarzoDufty','GarzoDuftyMod','Gidaspow','HrenyaSincIair','Syamlal'], 
                'current': self.conductivityModel
            },
            'e': {
                'label': 'e',
                'tooltip': 'Coeficiente de restitución.',
                'type': 'float',
                'current': self.e
            },
            'alphaMax': {
                'label': 'alphaMax',
                'tooltip': 'Fracción máxima de volumen sólido.',
                'type': 'float',
                'current': self.alphaMax
            },
            'MaxTheta': {
                'label': 'MaxTheta',
                'tooltip': 'Temperatura granular máxima.',
                'type': 'float', 
                'current': self.MaxTheta
            },
            'phi': {
                'label': 'phi',
                'tooltip': 'Ángulo de fricción.',
                'type': 'float', 
                'current': self.phi
            },
            'customContent': {
                'label': 'Contenido de experto',
                'tooltip': 'Cosas que van directamente al archivo.',
                'type': 'string',
                'default': "",
                'current': self.customContent,
                'optional': True
            }
        }
