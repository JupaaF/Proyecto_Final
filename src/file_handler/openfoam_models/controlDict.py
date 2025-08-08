from pathlib import Path
from .foam_file import FoamFile

class controlDict(FoamFile):
    """
    Representa y gestiona el archivo 'controlDict' de OpenFOAM.

    Esta clase genera el contenido del archivo controlDict, que es fundamental
    para definir cómo se ejecuta una simulación en OpenFOAM (solver, tiempo,
    intervalos de escritura, etc.).

    La clase centraliza la definición de parámetros editables, sus valores
    por defecto y metadatos para la GUI en un único método estático.
    """

    def __init__(self):
        """
        Inicializa el objeto controlDict.
        """
        super().__init__(name="controlDict", folder="system",class_type="dictionary")
        
        # Carga los parámetros y sus valores por defecto desde la fuente única.
        default_params = {key: data['default'] for key, data in self.get_editable_parameters().items()}
        
        # Atributos adicionales no expuestos en la GUI pero necesarios para el archivo.
        self.purgeWrite = 0
        self.writeFormat = "ascii"
        self.writePrecision = 6
        self.writeCompression = "off"
        self.timeFormat = "general"
        self.timePrecision = 6
        
        # Combina los defaults con los parámetros proporcionados por el usuario.
        self.update_parameters(default_params)

    @staticmethod
    def get_editable_parameters() -> dict:
        """
        Devuelve un diccionario con los parámetros que pueden ser editados por el usuario.

        Este método actúa como la "única fuente de verdad" para los parámetros
        configurables, sus etiquetas, descripciones, tipos y valores por defecto.
        Es utilizado para construir dinámicamente la interfaz de usuario.

        Returns:
            dict: Un diccionario que describe cada parámetro editable.
        """
        return {
            'application': {
                'label': 'Solver Application',
                'tooltip': 'El solver de OpenFOAM a utilizar (ej. interFoam).',
                'type': 'string',
                'default': 'interFoam',
                'group': 'Configuración General'
            },
            'startTime': {
                'label': 'Tiempo de Inicio (startTime)',
                'tooltip': 'El tiempo de inicio de la simulación (numérico).',
                'type': 'float',
                'default': 0,
                'group': 'Control de Tiempo'
            },
            'endTime': {
                'label': 'Tiempo Final (endTime)',
                'tooltip': 'El tiempo en el que la simulación se detendrá (numérico).',
                'type': 'float',
                'default': 10,
                'group': 'Control de Tiempo'
            },
            'deltaT': {
                'label': 'Paso de Tiempo (deltaT)',
                'tooltip': 'El intervalo de tiempo para cada paso de la simulación (numérico).',
                'type': 'float',
                'default': 0.01,
                'group': 'Control de Tiempo'
            },
            'writeInterval': {
                'label': 'Intervalo de Escritura (writeInterval)',
                'tooltip': 'La frecuencia con la que se guardan los resultados (numérico).',
                'type': 'float',
                'default': 0.5,
                'group': 'Control de Salida'
            }
        }

    def update_parameters(self, params: dict):
        """
        Actualiza los atributos de la instancia con los valores de un diccionario.

        Args:
            params (dict): Diccionario con los parámetros a actualizar.
                           Las claves deben coincidir con los atributos de la clase.
        """
        valid_keys = list(self.get_editable_parameters().keys())
        for key, value in params.items():
            if key in valid_keys:
                setattr(self, key, value)
            # Se podría añadir un warning si la clave no es válida.

    def _generate_content(self) -> str:
        """
        Genera el contenido completo del archivo controlDict como una cadena de texto.

        Returns:
            str: El contenido del archivo listo para ser escrito.
        """
        content = f"""
application     {self.application};

startFrom       startTime;
startTime       {self.startTime};

stopAt          endTime;
endTime         {self.endTime};

deltaT          {self.deltaT};

writeControl    runTime;
writeInterval   {self.writeInterval};

purgeWrite      {self.purgeWrite};
writeFormat     {self.writeFormat};
writePrecision  {self.writePrecision};
writeCompression {self.writeCompression};

timeFormat      {self.timeFormat};
timePrecision   {self.timePrecision};

runTimeModifiable true;
"""
        return self.get_header() + content

    def write_file(self, case_path: Path):
        """
        Escribe el contenido generado en la ruta del caso especificada.

        Args:
            case_path (Path): La ruta al directorio del caso de OpenFOAM.
        """
        output_path = case_path / self.folder / self.name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(self._generate_content())