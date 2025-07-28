from foamFile import foamFile

class controlDict(foamFile):

    def __init__(self, solver = "interFoam", start_time = 0, end_time = 1, delta_t = 0.01, write_interval = 0.1): #Posiblemente saque los valores
        super().__init__("system", "dictionary", "controlDict")
        self.solver = solver
        self.start_time = start_time
        self.end_time = end_time
        self.delta_t = delta_t
        self.write_interval = write_interval

    def modificarParam(self, solver = "interFoam", start_time = 0, end_time = 1, delta_t = 0.01, write_interval = 0.1):
        self.solver = solver
        self.start_time = start_time
        self.end_time = end_time
        self.delta_t = delta_t
        self.write_interval = write_interval

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
    
    def modificarArchivo(self,archivo):
        archivo.write(self.__getString__())

    