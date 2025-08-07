from foamFile import foamFile

class fvSchemes(foamFile):

    def __init__(self): 
        super().__init__("system", "dictionary", "fvSchemes")
        

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
    
    def write_file(self,archivo, divSchemes, laplacianSchemes, interpolationSchemes, snGradSchemes, ddtSchemes = 'Euler', gradSchemes = 'Gauss Linear'):
        self.divSchemes = divSchemes
        self.laplacianSchemes = laplacianSchemes
        self.interpolationSchemes = interpolationSchemes
        self.snGradSchemes = snGradSchemes
        self.ddtSchemes = ddtSchemes
        self.gradSchemes = gradSchemes
        archivo.write(self.__getString__())

    