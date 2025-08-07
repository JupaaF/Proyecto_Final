from foam_file import FoamFile

class p_rgh(FoamFile): #en una primera instancia dejamos las dimensiones fijas

    def __init__(self): 
        super().__init__("0.orig", "volScalarField", "p_rgh")
        

    def __getString__(self):
        content = f"""              
            dimensions      [1 -1 -2 0 0 0 0];

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
   

    def write_file(self,archivo,patchList, patchContent, internalField_value = "uniform 0"): 
        self.internalField_value = internalField_value
        self.patchList = patchList
        self.patchContent = patchContent
        archivo.write(self.__getString__())

    