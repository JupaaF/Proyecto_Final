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
        self.adjustTimeStep = 'true'
        self.maxCo = 1
        self.maxAlphaCo = 1
        self.maxDeltaT = 1
        self.writeCompression = 'false'
        self.runTimeModifiable = 'on'
        self.writePrecision = 6
        self.functions = 'damBreakOpenFoam'

        # Valores para parámetros opcionales
        self.timeFormat = None
        self.timePrecision = None
        
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
            'runTimeModifiable': self.runTimeModifiable,
            'timeFormat': self.timeFormat,
            'timePrecision': self.timePrecision,
            'functions': self.functions
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
            
            # Si el valor es None, es un parámetro opcional que se está desactivando.
            # Lo seteamos directamente sin validar.
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
                'type': 'choice',
                'current': self.application, 
                'group': 'Configuración General',
                'options': ['interFoam', 'sedFoam']
            },
            'startFrom': {
                'label': 'Comenzar desde (startFrom)',
                'tooltip': 'Punto inicial. Para damBreak: "startTime" (0) o "latestTime".',
                'type': 'choice',
                'current': self.startFrom,
                'group': 'Control de Tiempo',
                'options': ['startTime', 'latestTime'],  # firstTime no es común aquí
            },
            'startTime': {
                'label': 'Tiempo de Inicio (startTime)',
                'tooltip': 'Tiempo inicial (típicamente 0 para damBreak).',
                'type': 'float',
                'current': self.startTime,
                'group': 'Control de Tiempo'
            },

            # --- Control de Tiempo (Obligatorios) ---
            'stopAt': {
                'label': 'Detener en (stopAt)',
                'tooltip': 'Para damBreak: "endTime" (ej: 1-5 segundos).',
                'type': 'choice',
                'options': ['endTime'],  # writeNow/noWriteNow raramente usados aquí
                'current': self.stopAt,
                'group': 'Control de Tiempo'
            },
            'endTime': {
                'label': 'Tiempo Final (endTime)',
                'tooltip': 'Duración de la simulación.',
                'type': 'float',
                'current': self.endTime,
                'group': 'Control de Tiempo'
            },
            'deltaT': {
                'label': 'Paso de Tiempo (deltaT)',
                'tooltip': 'Intervalo de tiempo (típico: 0.001 para precisión en interFoam).',
                'type': 'float',
                'current': self.deltaT,
                'group': 'Control de Tiempo'
            },

            # --- Escritura de Datos (Ajustes típicos para damBreak) ---
            'writeControl': {
                'label': 'Control de Escritura (writeControl)',
                'tooltip': 'Para damBreak: "adjustableRunTime" (ajusta pasos para writeInterval).',
                'type': 'choice',
                'options': ['adjustable'],  # Más relevante que timeStep/runTime
                'current': self.writeControl,
                'group': 'Escritura de datos'
            },
            'writeInterval': {
                'label': 'Intervalo de Escritura (writeInterval)',
                'tooltip': 'Guardar cada X segundos (ej: 0.05 para alta frecuencia).',
                'type': 'float',
                'current': self.writeInterval,
                'group': 'Escritura de datos'
            },
            'purgeWrite': {
                'label': 'Purge Write',
                'tooltip': 'Máximo de archivos de tiempo guardados (0 = todos).',
                'type': 'int',
                'current': self.purgeWrite,
                'group': 'Escritura de datos'
            },
            'writeFormat': {
                'label': 'Formato de Escritura',
                'tooltip': '"binary" para ahorrar espacio, "ascii" para depuración.',
                'type': 'choice',
                'options': ['ascii', 'binary'],
                'current': self.writeFormat,
                'group': 'Escritura de datos'
            },
            'writePrecision': {
                'label': 'Precision de Escritura',
                'tooltip': 'Decimales de precision',
                'type': 'int',
                'current': self.writePrecision,
                'group': 'Escritura de datos'
            },
            'writeCompression': {
                'label': 'Compresión de Archivos',
                'tooltip': '"on" para reducir tamaño de archivos (recomendado en producción).',
                'type': 'choice',
                'options': ['true','false'],
                'current': self.writeCompression,
                'group': 'Escritura de datos'
            },
            'timeFormat': {
                'label': 'Formato de Tiempo',
                'tooltip': 'Formato para los nombres de los directorios de tiempo.',
                'type': 'choice',
                'options': ['general', 'fixed', 'scientific'],
                'default': 'general',
                'optional': True,
                'group': 'Avanzado',
                'current': self.timeFormat
            },
            'timePrecision': {
                'label': 'Precisión del Tiempo',
                'tooltip': 'Número de dígitos en los nombres de los directorios de tiempo.',
                'type': 'int',
                'default': 6,
                'min': 1,
                'max': 12,
                'optional': True,
                'group': 'Avanzado',
                'current': self.timePrecision
            },
            'runTimeModifiable': {
                'label': 'runTimeModifiable',
                'tooltip': '"on" para permitir cambios durante la simulación (útil para pruebas).',
                'type': 'choice',
                'options': ['on','off'],
                'current': self.runTimeModifiable,
                'group': 'Avanzado'
            },

            # --- Parámetros Críticos para interFoam/damBreak ---
            'adjustTimeStep': {
                'label': 'adjustTimeStep',
                'tooltip': 'Activar para ajuste automático basado en números de Courant.',
                'type': 'choice',
                'options': ['true', 'false'],
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
            'functions': {
                'label': 'Funciones para cosas', #TODO: renombrar xd
                'tooltip': 'Funciones para cosas',
                'type': 'choice',
                'options': ['damBreakOpenFoam','waterChannelOpenFoam','2DChannelSedFoam', '3DScourSqrSedFoam'],  
                'current': self.functions,
            }
        }
