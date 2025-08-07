from foamFile import foamFile

class turbulenceProperties(foamFile):

    def __init__(self):
        super().__init__("constant", "dictionary", "turbulenceProperties")
        

    def __getString__(self):
        
        content = f"""
simulationType       {self.simulationType};
        """
        
        return self.get_header() + content
   

    def write_file(self,archivo,simulationType): 
        self.simulationType = simulationType
        archivo.write(self.__getString__())

    