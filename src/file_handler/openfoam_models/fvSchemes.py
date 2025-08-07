from .foam_file import FoamFile

class fvSchemes(FoamFile):

    def __init__(self):
        super().__init__("system", "dictionary", "fvSchemes")
        self.ddtSchemes = 'Euler'
        self.gradSchemes = 'Gauss linear'
        self.divSchemes = 'default none'
        self.laplacianSchemes = 'default Gauss linear corrected'
        self.interpolationSchemes = 'default linear'
        self.snGradSchemes = 'default corrected'

    def _get_string(self):
        content = f"""
ddtSchemes
{{
    default     {self.ddtSchemes};
}}

gradSchemes
{{
    default     {self.gradSchemes};
}}

divSchemes
{{
    {self.divSchemes};
}}

laplacianSchemes
{{
    default     {self.laplacianSchemes};
}}

interpolationSchemes
{{
    default     {self.interpolationSchemes}
}}

snGradSchemes
{{
    default         {self.snGradSchemes};
}}

"""
        return self.get_header() + content

    def modify_parameters(self, ddtSchemes, gradSchemes, divSchemes, laplacianSchemes, interpolationSchemes, snGradSchemes):
        self.ddtSchemes = ddtSchemes
        self.gradSchemes = gradSchemes
        self.divSchemes = divSchemes
        self.laplacianSchemes = laplacianSchemes
        self.interpolationSchemes = interpolationSchemes
        self.snGradSchemes = snGradSchemes

    def write_file(self, case_path):
        with open(case_path / self.folder / self.name, "w") as f:
            f.write(self._get_string())

    def get_editable_parameters(self):
        return {
            'ddtSchemes': {
                'label': 'ddtSchemes',
                'tooltip': 'Esquema de discretización temporal.',
                'type': 'string',
                'default': 'Euler',
                'group': 'Esquemas Temporales'
            },
            'gradSchemes': {
                'label': 'gradSchemes',
                'tooltip': 'Esquema de discretización para gradientes.',
                'type': 'string',
                'default': 'Gauss linear',
                'group': 'Esquemas de Gradiente'
            },
            'divSchemes': {
                'label': 'divSchemes',
                'tooltip': 'Esquema de discretización para divergencia.',
                'type': 'choice',
                'default': 'Gauss linearUpwind grad(U)',
                'group': 'Esquemas de Divergencia',
                'validators': {
                    'options': [
                        {'label': 'Gauss linear', 'name': 'Gauss linear'},
                        {'label': 'Gauss linearUpwind grad(U)', 'name': 'Gauss linearUpwind grad(U)'},
                        {'label': 'Gauss upwind', 'name': 'Gauss upwind'},
                        {'label': 'bounded Gauss upwind', 'name': 'bounded Gauss upwind'},
                        {'label': 'bounded Gauss linearUpwind grad(U)', 'name': 'bounded Gauss linearUpwind grad(U)'}
                    ]
                }
            },
            'laplacianSchemes': {
                'label': 'laplacianSchemes',
                'tooltip': 'Esquema de discretización para laplacianos.',
                'type': 'string',
                'default': 'default Gauss linear corrected',
                'group': 'Esquemas de Laplaciano'
            },
            'interpolationSchemes': {
                'label': 'interpolationSchemes',
                'tooltip': 'Esquema de interpolación.',
                'type': 'string',
                'default': 'default linear',
                'group': 'Esquemas de Interpolación'
            },
            'snGradSchemes': {
                'label': 'snGradSchemes',
                'tooltip': 'Esquema de discretización para gradientes de superficie normales.',
                'type': 'string',
                'default': 'default corrected',
                'group': 'Esquemas de Gradiente de Superficie'
            }
        }