from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class granularRheologyProperties(FoamFile):
    """
    Representa el archivo 'granularRheologyProperties' de OpenFOAM.
    """
    def __init__(self):
        super().__init__(name="granularRheologyProperties", folder="constant", class_type="dictionary")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Valores por defecto
        self.FrictionModel = "MuIv"
        self.granularRheology = 'off'
        self.granularDilatancy = 'off'
        self.granularCohesion = 'off'
        self.alphaMaxG = 0.625
        self.mus = 0.4
        self.mu2 = 0.9
        self.I0 = 0.6
        self.Bphi = 0.66
        self.n = 2.5
        self.Dsmall = 0.0001
        self.relaxPa = 0.0005
        self.PPressureModel =  'MuI'
        self.FluidViscosityModel = 'BoyerEtAl'
        self.customContent = "zbed         zbed [ 0 1 0 0 0 0 0 ] 0.0;"

    def _get_string(self) -> str:
        """
        Genera el contenido del archivo renderizando la plantilla Jinja2.
        """
        template = self.jinja_env.get_template("granularRheologyProperties_template.jinja2")

        context = {
            'FrictionModel': self.FrictionModel,
            'granularRheology': self.granularRheology,
            'granularDilatancy': self.granularDilatancy,
            'granularCohesion': self.granularCohesion,
            'alphaMaxG': self.alphaMaxG,
            'mus': self.mus,
            'mu2': self.mu2,
            'I0': self.I0,
            'Bphi': self.Bphi,
            'n': self.n,
            'Dsmall': self.Dsmall,
            'PPressureModel': self.PPressureModel,
            'FluidViscosityModel': self.FluidViscosityModel,
            'relaxPa': self.relaxPa,
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
            'FrictionModel': {
                'label': 'FrictionModel',
                'tooltip': 'Modelo matemático para la fricción granular.',
                'type': 'choice',
                'options': ['MuI','MuIv','Coulomb','none'], 
                'current': self.FrictionModel,
                'required': True
            },
            'granularRheology': {
                'label': 'granularRheology',
                'tooltip': 'Utilizar la reología de flujo granular denso o no.',
                'type': 'choice',
                'options': ['on','off'], 
                'current': self.granularRheology,
                'required': True
            },
            'granularDilatancy': {
                'label': 'granularDilatancy',
                'tooltip': '',
                'type': 'choice',
                'options': ['on','off'], 
                'current': self.granularDilatancy,
                'required': True
            },
            'granularCohesion': {
                'label': 'granularCohesion',
                'tooltip': '',
                'type': 'choice',
                'options': ['on','off'], 
                'current': self.granularCohesion,
                'required': True
            },
            'alphaMaxG': {
                'label': 'alphaMaxG',
                'tooltip': 'Fracción máxima de volumen sólido.',
                'type': 'float',
                'current': self.alphaMaxG,
                'required': True
            },
            'mus': {
                'label': 'mus',
                'tooltip': 'Coeficiente de fricción estática',
                'type': 'float',
                'current': self.mus,
                'required': True
            },
            'mu2': {
                'label': 'mu2',
                'tooltip': 'Coeficiente de fricción dinámica',
                'type': 'float',
                'current': self.mu2,
                'required': True
            },
            'I0': {
                'label': 'I0',
                'tooltip': 'Coeficiente empírico mu(I)',
                'type': 'float',
                'current': self.I0,
                'required': True
            },
            'Bphi': {
                'label': 'Bphi',
                'tooltip': 'Coeficiente empírico phi(I)',
                'type': 'float',
                'current': self.Bphi,
                'required': True
            },
            'n': {
                'label': 'n',
                'tooltip': 'Exponente viscosidad efectiva.',
                'type': 'float',
                'current': self.n,
                'required': True
            },
            'Dsmall': {
                'label': 'Dsmall',
                'tooltip': 'Parámetro de regularización',
                'type': 'float',
                'current': self.Dsmall,
                'required': True
            },
            'relaxPa': {
                'label': 'relaxPa',
                'tooltip': 'Factor de relajación para Pa',
                'type': 'float',
                'current': self.relaxPa,
                'required': True
            },
            'PPressureModel': {
                'label': 'PPressureModel',
                'tooltip': 'Modelo de presión.',
                'type': 'choice',
                'options': ['MuI','MuIv','none'], 
                'current': self.PPressureModel,
                'required': True
            },
            'FluidViscosityModel': {
                'label': 'FluidViscosityModel',
                'tooltip': 'Modo de viscosidad del fluido.',
                'type': 'choice',
                'options': ['BoyerEtAl','Einstein','KriegerDougherty','none'], 
                'current': self.FluidViscosityModel,
                'required': True
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
       
