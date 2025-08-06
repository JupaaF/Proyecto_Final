from .foamFile import foamFile

class controlDict(foamFile):

    def __init__(self):
        super().__init__("system", "dictionary", "controlDict")
        

    def __getString__(self):
        content = f"""
application     {self.solver};

startFrom       startTime;
startTime       {self.start_time};

stopAt          endTime;
endTime         {self.end_time};

deltaT          {self.delta_t};

writeControl    runTime;
writeInterval   {self.write_interval};

purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
writeCompression off;

timeFormat      general;
timePrecision   6;
"""
        return self.get_header_location() + content
    
    def writeFile(self,archivo,solver = "interFoam", start_time = 0, end_time = 1, delta_t = 0.01, write_interval = 0.1): #Posiblemente saque los valores
        self.solver = solver
        self.start_time = start_time
        self.end_time = end_time
        self.delta_t = delta_t
        self.write_interval = write_interval
        archivo.write(self.__getString__())

    def get_editable_parameters(self):
        return {
            'solver': {
                'label': 'Solver',
                'tooltip': 'El solver de OpenFOAM a utilizar (ej. interFoam, simpleFoam).',
                'type': 'string',
                'default': 'interFoam',
                'group': 'Configuración General'
            },
            'startTime': {
                'label': 'Tiempo de Inicio (startTime)',
                'tooltip': 'El tiempo de inicio de la simulación.',
                'type': 'string',
                'default': '0',
                'group': 'Control de Tiempo'
            },
            'endTime': {
                'label': 'Tiempo Final (endTime)',
                'tooltip': 'El tiempo en el que la simulación se detendrá.',
                'type': 'string',
                'default': '1',
                'group': 'Control de Tiempo'
            },
            'deltaT': {
                'label': 'Paso de Tiempo (deltaT)',
                'tooltip': 'El intervalo de tiempo entre cada paso de la simulación.',
                'type': 'string',
                'default': '0.01',
                'group': 'Control de Tiempo'
            },
            'writeInterval': {
                'label': 'Intervalo de Escritura (writeInterval)',
                'tooltip': 'La frecuencia con la que se guardan los resultados.',
                'type': 'string',
                'default': '0.1',
                'group': 'Control de Tiempo'
            }
        }

    

    