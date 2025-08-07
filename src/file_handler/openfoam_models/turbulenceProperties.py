from foam_file import FoamFile

class turbulenceProperties(FoamFile):

    def __init__(self):
        super().__init__("constant", "dictionary", "turbulenceProperties")
        self.simulation_type = "RAS"
        

    def _get_string(self):
        
        content = f"""
simulationType       {self.simulation_type};

RAS
{{
    RASModel        kEpsilon;

    turbulence      on;

    printCoeffs     on;
}}

        """
        
        return self.get_header() + content
   
    def modify_parameters(self, data:dict):

        if data.get('simulation_type'):
            self.simulation_type = data['simulation_type']


    def write_file(self,case_path): 
        with open(case_path / self.folder / self.name, "w") as f:
            f.write(self._get_string())

    def get_editable_parameters(self):
        return {
            'simulation_type': {
                'label': 'Tipo de simulacion',
                'tooltip': 'El solver de OpenFOAM a utilizar (ej. interFoam, simpleFoam).',
                'type': 'string',
                'default': self.simulation_type,
                'group': 'Configuración General'

            }
        }
