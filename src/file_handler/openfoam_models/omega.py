from .foam_file import FoamFile

class omega(FoamFile):

    def __init__(self):
        super().__init__("0", "volScalarField", "omega")
        self.patch_list = None
        self.patch_content = None
        self.internal_field = "uniform 10"

    def _get_string(self):
        content = f"""
dimensions      [0 0 -1 0 0 0 0];

internalField   {self.internal_field};

boundaryField
{{
"""
        if self.patch_list and self.patch_content:
            for i in range(len(self.patch_list)):
                content += f"""
    {self.patch_list[i]}
    {{
        {self.patch_content[i]}
    }}
"""
        
        content += f"""
}}
"""
        
        return self.get_header() + content

    def modify_parameters(self, data:dict):
        if data.get('patch_list'):
            self.patch_list = data['patch_list']
        if data.get('patch_content'):
            self.patch_content = data['patch_content']
        if data.get('internalField'):
            self.internal_field = data['internalField']

    def write_file(self,case_path):
        with open(case_path / self.folder / self.name, "w") as f:
            f.write(self._get_string())

    def get_editable_parameters(self):
        return {
            'internalField': {
                'label': 'Campo Interno (internalField)',
                'tooltip': 'Valor inicial de omega en el dominio.',
                'type': 'string',
                'default': 'uniform 10',
                'group': 'General'
            },
            'boundaryField': {
                'label': 'Condiciones de Borde para Omega',
                'tooltip': 'Define las condiciones de omega en los límites.',
                'type': 'list_of_dicts',
                'group': 'Condiciones de Borde',
                'schema': {
                    'patchName': {
                        'label': 'Nombre del Patch',
                        'type': 'string',
                        'default': 'nuevoPatch'
                    },
                    'type': {
                        'label': 'Tipo de Condición',
                        'type': 'choice',
                        'default': 'omegaWallFunction',
                        'validators': {
                            'options': [
                                {
                                    'name': 'omegaWallFunction',
                                    'label': 'Función de Pared (omegaWallFunction)',
                                    'requires_value': True,
                                    'value_schema': {'type': 'string', 'label': 'Valor', 'default': 'uniform 10e-6'}
                                },
                                {
                                    'name': 'zeroGradient',
                                    'label': 'Gradiente Cero (zeroGradient)',
                                    'requires_value': False
                                },
                                {
                                    'name': 'fixedValue',
                                    'label': 'Valor Fijo (fixedValue)',
                                    'requires_value': True,
                                    'value_schema': {'type': 'scalar', 'label': 'Valor'}
                                }
                            ]
                        }
                    }
                }
            }
        }