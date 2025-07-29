from foamFile import foamFile

class transportProperties(foamFile):

    def __init__(self, phasesList, phasesContent, sigma): #Posiblemente saque los valores
        super().__init__("constant", "dictionary", "transportProperties")
        self.phasesList = phasesList
        self.phasesContent = phasesContent
        self.sigma = sigma

    def __getString__(self):
        phases_str = " ".join(self.phasesList)
        content = f"""              
            phases      ({phases_str});
            """
        for i in range(len(self.phasesList)):
            content += f""" 
            {self.phasesList[i]}
            {{
                {self.phasesContent[i]}
            }}
            """
        
        content += f"""
            sigma       {self.sigma};
        """
        
        return self.get_header() + content
   

    def write_file(self,archivo): 
        archivo.write(self.__getString__())

    