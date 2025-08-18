from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class fvSolution(FoamFile):

    def __init__(self):
        super().__init__(name="fvSolution", folder="system", class_type="dictionary")

        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        self.selected_solver = []
        # Valores por defecto
        # self.selected_solver = 'damBreak'
        # self.alpha_water_tolerance = 1e-8
        # self.alpha_water_relTol = 0
        # self.p_rgh_tolerance = 1e-07
        # self.p_rgh_relTol = 0.05
        # self.U_tolerance = 1e-06
        # self.U_relTol = 0
        # self.nOuterCorrectors = 1
        # self.nCorrectors = 3
        # self.nNonOrthogonalCorrectors = 0

    def _get_string(self):
        template = self.jinja_env.get_template("fvSolution_template.jinja2")

        # Convierte la lista de parámetros en un diccionario para simplificar el manejo en el jinja
        params_dict = {item['param_name']: item['value'] for item in self.selected_solver}

        context = {
            'params': params_dict
        }

        content = template.render(context)
        return self.get_header() + content

    def update_parameters(self, params: dict):
        for key, value in params.items():
            setattr(self, key, value)

    def write_file(self, case_path: Path):
        print(self.selected_solver)
        output_dir = case_path / self.folder
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / self.name
        with open(output_path, "w") as f:
            f.write(self._get_string())


    def get_editable_parameters(self):
        return {
            'selected_solver': {
                'label': 'Condiciones de Borde',
                'tooltip': 'Define las condiciones de velocidad en los límites del dominio.', #cambiar
                'type': 'choice_with_options',
                'current': self.selected_solver,
                'group': 'Condiciones de Borde',
                'options': [
                    {
                        'name': 'damBreak',
                        'label': 'damBreak-interFoam',
                        'parameters':[
                            {
                                'name': 'alpha_water_tolerance',
                                'label': 'alpha.water Tolerancia',
                                'tooltip': 'Tolerancia para el solver alpha.water.',
                                'type': 'float',
                                'default': 1e-8,
                            },
                            {
                                'name': 'alpha_water_relTol',
                                'label': 'alpha.water Rel. Tolerancia',
                                'tooltip': 'Tolerancia relativa para el solver alpha.water.',
                                'type': 'float',
                                'default': 0
                            },
                            {
                                'name': 'p_rgh_tolerance',
                                'label': 'p_rgh Tolerancia',
                                'tooltip': 'Tolerancia para el solver p_rgh.',
                                'type': 'float',
                                'default': 1e-07
                            },
                            {
                                'name': 'p_rgh_relTol',
                                'label': 'p_rgh Rel. Tolerancia',
                                'tooltip': 'Tolerancia relativa para el solver p_rgh.',
                                'type': 'float',
                                'default': 0.05
                            },
                            {
                                'name': 'U_tolerance',
                                'label': 'U Tolerancia',
                                'tooltip': 'Tolerancia para el solver U.',
                                'type': 'float',
                                'default': 1e-06
                            },
                            {
                                'name': 'U_relTol',
                                'label': 'U Rel. Tolerancia',
                                'tooltip': 'Tolerancia relativa para el solver U.',
                                'type': 'float',
                                'default': 0
                            },
                            {
                                'name': 'nOuterCorrectors',
                                'label': 'PIMPLE nOuterCorrectors',
                                'tooltip': 'Número de correctores externos en el algoritmo PIMPLE.',
                                'type': 'integer',
                                'default': 1
                            },
                            {
                                'name': 'nCorrectors',
                                'label': 'PIMPLE nCorrectors',
                                'tooltip': 'Número de correctores internos en el algoritmo PIMPLE.',
                                'type': 'integer',
                                'default': 3
                            },
                            {
                                'name': 'nNonOrthogonalCorrectors',
                                'label': 'PIMPLE nNonOrthogonalCorrectors',
                                'tooltip': 'Número de correctores no ortogonales en el algoritmo PIMPLE.',
                                'type': 'integer',
                                'default': 0
                            }
                        ]
                    },
                    {
                        'name': 'otro_solver',
                        'label': 'otro_solver_o_caso',
                        'parameters' : []
                    }
                ]
                }
            }
        
    