from .foam_file import FoamFile

class U(FoamFile): #en una primera instancia dejamos las dimensiones fijas

    def __init__(self): 
        super().__init__("0.orig", "volVectorField", "U")

    def _get_string(self):
        content = f"""              
dimensions      [0 1 -1 0 0 0 0];

internalField   {self.internal_field_value};

boundaryField
{{
"""
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
   
    def modify_parameters(self, patch_list,patch_content,internal_field_value):
        self.internal_field_value = internal_field_value
        self.patch_list = patch_list
        self.patch_content = patch_content 

    def write_file(self,case_path): 
        with open(case_path / self.folder / self.name, "w") as f:
            f.write(self._get_string())

    def get_editable_parameters(self):
        return {
            'internalField': {
                'label': 'Campo Interno (Velocidad)',
                'tooltip': 'Valor inicial de la velocidad en el interior del dominio. Formato: (Ux Uy Uz)',
                'type': 'vector',
                'default': '(0 0 0)',
                'group': 'Valores Iniciales'
            },
            'boundaryField': {
                'label': 'Condiciones de Borde',
                'tooltip': 'Define las condiciones de velocidad en los límites del dominio.',
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
                        'default': 'fixedValue',
                        'validators': {
                            # Cada opción es un diccionario que describe la condición
                            # y si necesita un valor adicional.
                            'options': [
                                {
                                    'name': 'fixedValue',
                                    'label': 'Valor Fijo (fixedValue)',
                                    'requires_value': True,
                                    'value_schema': {'type': 'vector', 'label': 'Valor de Velocidad'}
                                },
                                {
                                    'name': 'noSlip',
                                    'label': 'Sin Deslizamiento (noSlip)',
                                    'requires_value': False
                                },
                                {
                                    'name': 'zeroGradient',
                                    'label': 'Gradiente Cero (zeroGradient)',
                                    'requires_value': False
                                },
                                {
                                    'name': 'inletOutlet',
                                    'label': 'Entrada/Salida (inletOutlet)',
                                    'requires_value': True,
                                    'value_schema': {'type': 'vector', 'label': 'Valor en la Entrada'}
                                },
                                {
                                    'name': 'pressureInletOutletVelocity',
                                    'label': 'Salida/Entrada por Presión (pressureInletOutletVelocity)',
                                    'requires_value': False
                                },
                                {
                                    'name': 'slip',
                                    'label': 'Deslizamiento (slip)',
                                    'requires_value': False
                                }
                            ]
                        }
                    }
                }
            }
        }

    