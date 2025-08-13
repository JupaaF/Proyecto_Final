from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class controlDict(FoamFile):

    def __init__(self):
        super().__init__(name="controlDict", folder="system", class_type="dictionary")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

        # Valores por defecto
        self.solver = "interFoam"
        self.startTime = 0
        self.endTime = 1
        self.deltaT = 0.01
        self.writeInterval = 0.1
        
    def _get_string(self):
        template = self.jinja_env.get_template("controlDict_template.jinja2")
        context = {
            'solver': self.solver,
            'startTime': self.startTime,
            'endTime': self.endTime,
            'deltaT': self.deltaT,
            'writeInterval': self.writeInterval
        }
        content = template.render(context)
        return self.get_header() + content
    
    def update_parameters(self, params: dict):
        for key, value in params.items():
            setattr(self, key, value)

    def write_file(self, case_path: Path): 
        output_dir = case_path / self.folder
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / self.name
        with open(output_path, "w") as f:
            f.write(self._get_string())

    def get_editable_parameters(self):
        return {
            'solver': {
                'label': 'Solver',
                'tooltip': 'El solver de OpenFOAM a utilizar (ej. interFoam, simpleFoam).',
                'type': 'string',
                'current': self.solver,
                'group': 'Configuración General'
            },
            'startTime': {
                'label': 'Tiempo de Inicio (startTime)',
                'tooltip': 'El tiempo de inicio de la simulación.',
                'type': 'float',
                'current': self.startTime,
                'group': 'Control de Tiempo'
            },
            'endTime': {
                'label': 'Tiempo Final (endTime)',
                'tooltip': 'El tiempo en el que la simulación se detendrá.',
                'type': 'float',
                'current': self.endTime,
                'group': 'Control de Tiempo'
            },
            'deltaT': {
                'label': 'Paso de Tiempo (deltaT)',
                'tooltip': 'El intervalo de tiempo entre cada paso de la simulación.',
                'type': 'float',
                'current': self.deltaT,
                'group': 'Control de Tiempo'
            },
            'writeInterval': {
                'label': 'Intervalo de Escritura (writeInterval)',
                'tooltip': 'La frecuencia con la que se guardan los resultados.',
                'type': 'float',
                'current': self.writeInterval,
                'group': 'Control de Tiempo'
            }
        }

    

    