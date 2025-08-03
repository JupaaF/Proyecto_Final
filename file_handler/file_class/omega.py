from foamFile import foamFile

class omega(foamFile): #en una primera instancia dejamos las dimensiones fijas

    def __init__(self): #Posiblemente saque los valores
        super().__init__("0", "volScalarField", "omega")
        

    def __getString__(self):
        content = f"""              
            dimensions      [0 0 -1 0 0 0 0];

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
   

    def write_file(self,archivo, patchList, patchContent, internalField_value = "uniform (0 0 0)"): 
        self.internalField_value = internalField_value
        self.patchList = patchList
        self.patchContent = patchContent
        archivo.write(self.__getString__())

    