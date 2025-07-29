from foamFile import foamFile

class fvSchemes(foamFile):

    def __init__(self, divSchemes, laplacianSchemes, interpolationSchemes, snGradSchemes, ddtSchemes = 'Euler', gradSchemes = 'Gauss Linear'): #Posiblemente saque los valores
        super().__init__("system", "dictionary", "fvSchemes")
        self.divSchemes = divSchemes
        self.laplacianSchemes = laplacianSchemes
        self.interpolationSchemes = interpolationSchemes
        self.snGradSchemes = snGradSchemes
        self.ddtSchemes = ddtSchemes
        self.gradSchemes = gradSchemes

    def __getString__(self):
        content = f"""
ddtSchemes
{{
    default     {self.ddtSchemes};
}}

gradSchemes
{{
    default     {self.gradSchemes};
}}

divSchemes
{{
    {self.divSchemes};
}}

laplacianSchemes
{{
    default     {self.laplacianSchemes};
}}

interpolationSchemes
{{
    default     {self.interpolationSchemes}
}}

snGradSchemes
{{
    default         {self.snGradSchemes};
}}

"""    
        
        return self.get_header() + content
    
    def write_file(self,archivo):
        archivo.write(self.__getString__())

    