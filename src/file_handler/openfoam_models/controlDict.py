from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class controlDict(FoamFile):

    def __init__(self):
        super().__init__(name="controlDict", folder="system", class_type="dictionary")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

        # Valores por defecto
        self.application = "interFoam"
        self.startTime = 0
        self.endTime = 1
        self.deltaT = 0.001
        self.writeInterval = 0.1
        self.startFrom = 'startTime'
        self.stopAt = 'endTime'
        self.writeControl = 'adjustable'
        self.purgeWrite = 0
        self.writeFormat = 'ascii'
        self.adjustTimeStep = 'yes'
        self.maxCo = 1
        self.maxAlphaCo = 1
        self.maxDeltaT = 1
        self.writeCompression = 'off'
        self.runTimeModifiable = 'yes'
        
    def _get_string(self):
        template = self.jinja_env.get_template("controlDict_template.jinja2")
        context = {
            'application': self.application,
            'startFrom': self.startFrom,
            'startTime': self.startTime,
            'stopAt': self.stopAt,
            'endTime': self.endTime,
            'deltaT': self.deltaT,
            'writeInterval': self.writeInterval,
            'writeControl': self.writeControl,
            'purgeWrite': self.purgeWrite,
            'writeFormat': self.writeFormat,
            'adjustTimeStep': self.adjustTimeStep,
            'maxCo': self.maxCo,
            'maxAlphaCo': self.maxAlphaCo,
            'maxDeltaT': self.maxDeltaT,
            'writeCompression': self.writeCompression,
            'runTimeModifiable': self.runTimeModifiable
        }
        content = template.render(context)
        return self.get_header() + content
    
    def update_parameters(self, params: dict):
        """
        Actualiza los parámetros desde un diccionario.
        """

        param_props = self.get_editable_parameters()

        for key, value in params.items():

            if not hasattr(self,key):
                continue

            props = param_props[key]
            type_data = props['type']

            try:
                self._validate(value,type_data,props)
            except ValueError:
                raise

            setattr(self, key, value)

    def write_file(self, case_path: Path): 
        output_dir = case_path / self.folder
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / self.name
        with open(output_path, "w") as f:
            f.write(self._get_string())

    def get_editable_parameters(self):
        return {
            # --- Configuración General (Obligatorios) ---
            'application': {
                'label': 'Solver (application)',
                'tooltip': 'Solver para flujo multifase (interFoam).',
                'type': 'string',
                'current': self.application,  # Fijo para damBreak
                'required': True,
                'editable': False,  # No se debe cambiar en este caso
                'group': 'Configuración General'
            },
            'startFrom': {
                'label': 'Comenzar desde (startFrom)',
                'tooltip': 'Punto inicial. Para damBreak: "startTime" (0) o "latestTime".',
                'type': 'choice',
                'current': self.startFrom,
                'group': 'Control de Tiempo',
                'options': ['startTime', 'latestTime'],  # firstTime no es común aquí
                'required': True
            },
            'startTime': {
                'label': 'Tiempo de Inicio (startTime)',
                'tooltip': 'Tiempo inicial (típicamente 0 para damBreak).',
                'type': 'float',
                'current': self.startTime,
                'required': True,
                'group': 'Control de Tiempo'
            },

            # --- Control de Tiempo (Obligatorios) ---
            'stopAt': {
                'label': 'Detener en (stopAt)',
                'tooltip': 'Para damBreak: "endTime" (ej: 1-5 segundos).',
                'type': 'choice',
                'options': ['endTime'],  # writeNow/noWriteNow raramente usados aquí
                'current': self.stopAt,
                'required': True,
                'group': 'Control de Tiempo'
            },
            'endTime': {
                'label': 'Tiempo Final (endTime)',
                'tooltip': 'Duración de la simulación (típico: 1-5 segundos).',
                'type': 'float',
                'current': self.endTime,
                'required': True,
                'group': 'Control de Tiempo'
            },
            'deltaT': {
                'label': 'Paso de Tiempo (deltaT)',
                'tooltip': 'Intervalo de tiempo (típico: 0.001 para precisión en interFoam).',
                'type': 'float',
                'current': self.deltaT,
                'required': True,
                'group': 'Control de Tiempo'
            },

            # --- Escritura de Datos (Ajustes típicos para damBreak) ---
            'writeControl': {
                'label': 'Control de Escritura (writeControl)',
                'tooltip': 'Para damBreak: "adjustableRunTime" (ajusta pasos para writeInterval).',
                'type': 'choice',
                'options': ['adjustable'],  # Más relevante que timeStep/runTime
                'current': self.writeControl,
                'required': True,
                'group': 'Escritura de datos'
            },
            'writeInterval': {
                'label': 'Intervalo de Escritura (writeInterval)',
                'tooltip': 'Guardar cada X segundos (ej: 0.05 para alta frecuencia).',
                'type': 'float',
                'current': self.writeInterval,
                'required': True,
                'group': 'Escritura de datos'
            },
            'purgeWrite': {
                'label': 'Purge Write',
                'tooltip': 'Máximo de archivos de tiempo guardados (0 = todos).',
                'type': 'int',
                'current': self.purgeWrite,
                'required': False,
                'group': 'Escritura de datos'
            },
            'writeFormat': {
                'label': 'Formato de Escritura',
                'tooltip': '"binary" para ahorrar espacio, "ascii" para depuración.',
                'type': 'choice',
                'options': ['ascii', 'binary'],
                'current': self.writeFormat,
                'required': False,
                'group': 'Escritura de datos'
            },

            # --- Parámetros Críticos para interFoam/damBreak ---
            'adjustTimeStep': {
                'label': 'Ajustar Paso de Tiempo',
                'tooltip': 'Activar para ajuste automático basado en números de Courant.',
                'type': 'choice',
                'options': ['yes', 'no'],
                'current': self.adjustTimeStep,  # Esencial para estabilidad en interFoam
                'required': True,
                'group': 'Control de Tiempo'
            },
            'maxCo': {
                'label': 'Número de Courant Máximo',
                'tooltip': 'Límite para ajuste de deltaT (típico: 0.5-1 para interFoam).',
                'type': 'float',
                'current': self.maxCo,
                'required': True if self.adjustTimeStep else False,
                'group': 'Control de Tiempo'
            },
            'maxAlphaCo': {
                'label': 'Número de Courant (Alpha) Máximo',
                'tooltip': 'Límite para ajuste en interfases (típico: 1 para interFoam).',
                'type': 'float',
                'current': self.maxAlphaCo,
                'required': True if self.adjustTimeStep else False,
                'group': 'Control de Tiempo'
            },
            'maxDeltaT': {
                'label': 'Paso de Tiempo Máximo',
                'tooltip': 'Límite superior para deltaT (ej: 1 para evitar pasos muy grandes).',
                'type': 'float',
                'current': self.maxDeltaT,
                'required': True if self.adjustTimeStep else False,
                'group': 'Control de Tiempo'
            },

            # --- Opcionales Recomendados ---
            'writeCompression': {
                'label': 'Compresión de Archivos',
                'tooltip': '"on" para reducir tamaño de archivos (recomendado en producción).',
                'type': 'choice',
                'options': ['on', 'off'],
                'current': self.writeCompression,
                'required': False,
                'group': 'Escritura de datos'
            },
            'runTimeModifiable': {
                'label': 'Modificable en Ejecución',
                'tooltip': '"yes" para permitir cambios durante la simulación (útil para pruebas).',
                'type': 'choice',
                'options': ['yes','no'],
                'current': self.runTimeModifiable,
                'required': False,
                'group': 'Avanzado'
            }
        }
