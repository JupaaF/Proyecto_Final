from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class fvSchemes(FoamFile):

    def __init__(self):
        super().__init__(name="fvSchemes", folder="system", class_type="dictionary")

        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

        # Valores por defecto
        self.ddtSchemes = 'Euler'
        self.gradSchemes = 'Gauss linear'
        self.divSchemes = 'Gauss linearUpwind grad(U)'
        self.laplacianSchemes = 'Gauss linear corrected'
        self.interpolationSchemes = 'linear'
        self.snGradSchemes = 'corrected'

    def _get_string(self):
        template = self.jinja_env.get_template("fvSchemes_template.jinja2")
        context = {
            'ddtSchemes': self.ddtSchemes,
            'gradSchemes': self.gradSchemes,
            'divSchemes': self.divSchemes,
            'laplacianSchemes': self.laplacianSchemes,
            'interpolationSchemes': self.interpolationSchemes,
            'snGradSchemes': self.snGradSchemes
        }
        content = template.render(context)
        return self.get_header() + content

    def update_parameters(self, params: dict):
        for key, value in params.items():
            setattr(self, key, value)

    def write_file(self, case_path: Path):
        output_dir = case_path / self.folder
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / self.name
        with open(output_path, "w") as f:
            f.write(self._get_string())

    def get_editable_parameters(self):
        return {
            'ddtSchemes': {
                'label': 'ddtSchemes',
                'tooltip': 'Esquema de discretización temporal.',
                'type': 'string',
                'current': self.ddtSchemes,
                'group': 'Esquemas Temporales'
            },
            'gradSchemes': {
                'label': 'gradSchemes',
                'tooltip': 'Esquema de discretización para gradientes.',
                'type': 'string',
                'current': self.gradSchemes,
                'group': 'Esquemas de Gradiente'
            },
            'divSchemes': {
                'label': 'divSchemes',
                'tooltip': 'Esquema de discretización para divergencia.',
                'type': 'choice',
                'current': self.divSchemes,
                'group': 'Esquemas de Divergencia',
                'options': [
                    'Gauss linear',
                    'Gauss linearUpwind grad(U)',
                    'Gauss upwind',
                    'bounded Gauss upwind',
                    'bounded Gauss linearUpwind grad(U)'
                ]
            },
            'laplacianSchemes': {
                'label': 'laplacianSchemes',
                'tooltip': 'Esquema de discretización para laplacianos.',
                'type': 'string',
                'current': self.laplacianSchemes,
                'group': 'Esquemas de Laplaciano'
            },
            'interpolationSchemes': {
                'label': 'interpolationSchemes',
                'tooltip': 'Esquema de interpolación.',
                'type': 'string',
                'current': self.interpolationSchemes,
                'group': 'Esquemas de Interpolación'
            },
            'snGradSchemes': {
                'label': 'snGradSchemes',
                'tooltip': 'Esquema de discretización para gradientes de superficie normales.',
                'type': 'string',
                'current': self.snGradSchemes,
                'group': 'Esquemas de Gradiente de Superficie'
            }
        }