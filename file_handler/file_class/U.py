from .foamFile import foamFile

class U(foamFile): #en una primera instancia dejamos las dimensiones fijas

    def __init__(self): 
        super().__init__("0", "volVectorField", "U")

    def __getString__(self):
        content = f"""              
            dimensions      [0 1 -1 0 0 0 0];

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
   

    def write_file(self,filePath ,patchList, patchContent, internalField_value): 
        self.internalField_value = internalField_value
        self.patchList = patchList
        self.patchContent = patchContent

        with open(filePath, "w") as archivo:
            archivo.write(self.__getString__())

    