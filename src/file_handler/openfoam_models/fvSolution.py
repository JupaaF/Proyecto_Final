from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class fvSolution(FoamFile):

    def __init__(self):
        super().__init__(name="fvSolution", folder="system", class_type="dictionary")

        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

        # Valores por defecto
        self.alpha_water_tolerance = 1e-8
        self.alpha_water_relTol = 0
        self.p_rgh_tolerance = 1e-07
        self.p_rgh_relTol = 0.05
        self.U_tolerance = 1e-06
        self.U_relTol = 0
        self.nOuterCorrectors = 1
        self.nCorrectors = 3
        self.nNonOrthogonalCorrectors = 0

    def _get_string(self):
        template = self.jinja_env.get_template("fvSolution_template.jinja2")
        context = {
            'alpha_water_tolerance': self.alpha_water_tolerance,
            'alpha_water_relTol': self.alpha_water_relTol,
            'p_rgh_tolerance': self.p_rgh_tolerance,
            'p_rgh_relTol': self.p_rgh_relTol,
            'U_tolerance': self.U_tolerance,
            'U_relTol': self.U_relTol,
            'nOuterCorrectors': self.nOuterCorrectors,
            'nCorrectors': self.nCorrectors,
            'nNonOrthogonalCorrectors': self.nNonOrthogonalCorrectors
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
            'alpha_water_tolerance': {
                'label': 'alpha.water Tolerancia',
                'tooltip': 'Tolerancia para el solver alpha.water.',
                'type': 'float',
                'current': self.alpha_water_tolerance,
                'group': 'Solvers'
            },
            'alpha_water_relTol': {
                'label': 'alpha.water Rel. Tolerancia',
                'tooltip': 'Tolerancia relativa para el solver alpha.water.',
                'type': 'float',
                'current': self.alpha_water_relTol,
                'group': 'Solvers'
            },
            'p_rgh_tolerance': {
                'label': 'p_rgh Tolerancia',
                'tooltip': 'Tolerancia para el solver p_rgh.',
                'type': 'float',
                'current': self.p_rgh_tolerance,
                'group': 'Solvers'
            },
            'p_rgh_relTol': {
                'label': 'p_rgh Rel. Tolerancia',
                'tooltip': 'Tolerancia relativa para el solver p_rgh.',
                'type': 'float',
                'current': self.p_rgh_relTol,
                'group': 'Solvers'
            },
            'U_tolerance': {
                'label': 'U Tolerancia',
                'tooltip': 'Tolerancia para el solver U.',
                'type': 'float',
                'current': self.U_tolerance,
                'group': 'Solvers'
            },
            'U_relTol': {
                'label': 'U Rel. Tolerancia',
                'tooltip': 'Tolerancia relativa para el solver U.',
                'type': 'float',
                'current': self.U_relTol,
                'group': 'Solvers'
            },
            'nOuterCorrectors': {
                'label': 'PIMPLE nOuterCorrectors',
                'tooltip': 'Número de correctores externos en el algoritmo PIMPLE.',
                'type': 'integer',
                'current': self.nOuterCorrectors,
                'group': 'PIMPLE'
            },
            'nCorrectors': {
                'label': 'PIMPLE nCorrectors',
                'tooltip': 'Número de correctores internos en el algoritmo PIMPLE.',
                'type': 'integer',
                'current': self.nCorrectors,
                'group': 'PIMPLE'
            },
            'nNonOrthogonalCorrectors': {
                'label': 'PIMPLE nNonOrthogonalCorrectors',
                'tooltip': 'Número de correctores no ortogonales en el algoritmo PIMPLE.',
                'type': 'integer',
                'current': self.nNonOrthogonalCorrectors,
                'group': 'PIMPLE'
            }
        }