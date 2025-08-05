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

    