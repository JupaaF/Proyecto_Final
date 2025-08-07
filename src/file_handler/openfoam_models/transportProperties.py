from foam_file import FoamFile

class transportProperties(FoamFile):

    def __init__(self): 
        super().__init__("constant", "dictionary", "transportProperties")
        self.phases_list = []
        self.phases_content = []
        self.sigma = 0.07
        

    def __getString__(self):
        phases_str = " ".join(self.phases_list)
        content = f"""              
            phases      ({phases_str});
            """
        for i in range(len(self.phases_list)):
            content += f""" 
            {self.phases_list[i]}
            {{
                {self.phases_content[i]}
            }}
            """
        
        content += f"""
            sigma       {self.sigma};
        """
        
        return self.get_header() + content

    def modify_parameters(self,data:dict):
        if data.get('phases_list'):
            self.phases_list = data['phases_list']
        if data.get('phases_content'):
            self.phases_content = data['phases_content']
        if data.get('sigma'):
            self.sigma = data['sigma']

    def write_file(self,case_path): 
        with open(case_path / self.folder / self.name, "w") as f:
            f.write(self._get_string())


    