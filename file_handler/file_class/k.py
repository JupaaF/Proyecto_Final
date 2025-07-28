from foamFile import foamFile

class k(foamFile): #en una primera instancia dejamos las dimensiones fijas

    def __init__(self, patchList, patchContent, internalField_value = "uniform (0 0 0)"): #Posiblemente saque los valores
        super().__init__("0", "volScalarField", "k")
        self.internalField_value = internalField_value
        self.patchList = patchList
        self.patchContent = patchContent

    def __getString__(self):
        content = f"""              
            dimensions      [0 2 -2 0 0 0 0];

            internalField   {self.internalField_value};

            boundaryField
            {{
            """
        for i in range(len(self.patchList)):
            content += f""" 
                {self.patchList[i]}
                {{
                    {self.patchContent[i]}
                }}
            """
        
        content += f"""
            }}
        """
        
        return self.get_header() + content
   

    def write_file(self,archivo): 
        archivo.write(self.__getString__())

    