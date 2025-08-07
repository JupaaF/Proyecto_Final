from .foam_file import FoamFile

class p_rgh(FoamFile):

    def __init__(self):
        super().__init__("0", "volScalarField", "p_rgh")
        self.patch_list = None
        self.patch_content = None
        self.internal_field = "uniform 0"

    def _get_string(self):
        content = f"""
dimensions      [1 -1 -2 0 0 0 0];

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
                'tooltip': 'Valor inicial de la presión en el dominio.',
                'type': 'string',
                'default': 'uniform 0',
                'group': 'General'
            },
            'boundaryField': {
                'label': 'Condiciones de Borde para Presión',
                'tooltip': 'Define las condiciones de presión en los límites.',
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
                        'default': 'fixedFluxPressure',
                        'validators': {
                            'options': [
                                {
                                    'name': 'fixedFluxPressure',
                                    'label': 'Presión con Flujo Fijo (fixedFluxPressure)',
                                    'requires_value': False
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