from foamFile import foamFile

class turbulenceProperties(foamFile):

    def __init__(self, simulationType): #Posiblemente saque los valores
        super().__init__("constant", "dictionary", "turbulenceProperties")
        self.simulationType = simulationType

    def __getString__(self):
        
        content = f"""
simulationType       {self.simulationType};
        """
        
        return self.get_header() + content
   

    def write_file(self,archivo): 
        archivo.write(self.__getString__())

    