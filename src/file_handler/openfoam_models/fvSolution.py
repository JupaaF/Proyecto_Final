from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class fvSolution(FoamFile):

    def __init__(self):
        super().__init__(name="fvSolution", folder="system", class_type="dictionary")

        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        self.selected_solver = []
        self.customContent = None

    def _get_string(self):
        template = self.jinja_env.get_template("fvSolution_template.jinja2")
        params_dict = {}
        # Convierte la lista de parámetros en un diccionario para simplificar el manejo en el jinja
        if self.selected_solver:
            params_dict = self.selected_solver[1].copy()
            params_dict['solver_selected'] = self.selected_solver[0]

        context = {
            'params': params_dict,
            'customContent': self.customContent
        }

        content = template.render(context)
        return self.get_header() + content
    
    def update_parameters(self, params: dict):
        """
        Actualiza los parámetros desde un diccionario.
        """
        if not isinstance(params,dict):
            raise ValueError("Me tenes que dar un diccionario")
        
        param_props = self.get_editable_parameters()

        for key, value in params.items():

            if not hasattr(self,key):
                continue

            if value is None:
                setattr(self, key, None)
                continue

            props = param_props[key]
            type_data = props['type']

            try:
                self._validate(value,type_data,props)
            except ValueError:
                raise

            setattr(self, key, value)

    def write_file(self, case_path: Path):
        output_dir = case_path / self.folder
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / self.name
        with open(output_path, "w") as f:
            f.write(self._get_string())


    def get_editable_parameters(self):
        return {
            'selected_solver': {
                'label': 'Caso/Solver a usar.',
                'tooltip': 'El archivo cambia según esto.', 
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
                                'type': 'int',
                                'default': 1
                            },
                            {
                                'name': 'nCorrectors',
                                'label': 'PIMPLE nCorrectors',
                                'tooltip': 'Número de correctores internos en el algoritmo PIMPLE.',
                                'type': 'int',
                                'default': 3
                            },
                            {
                                'name': 'nNonOrthogonalCorrectors',
                                'label': 'PIMPLE nNonOrthogonalCorrectors',
                                'tooltip': 'Número de correctores no ortogonales en el algoritmo PIMPLE.',
                                'type': 'int',
                                'default': 0
                            }
                        ]
                    },
                    {
                        'name': 'waterChannelOpenFoam',
                        'label': 'waterChannel - OpenFOAM',
                        'parameters' : [
                            {
                                'name': 'nAlphaCorr',
                                'label': 'nAlphaCorr',
                                'tooltip': 'Número de correctores para la ecuación de alpha.',
                                'type': 'int',
                                'default': 1
                            },
                            {
                                'name': 'nAlphaSubCycles',
                                'label': 'nAlphaSubCycles',
                                'tooltip': 'Número de sub-ciclos para la ecuación de alpha.',
                                'type': 'int',
                                'default': 1
                            },
                            {
                                'name': 'cAlpha',
                                'label': 'cAlpha',
                                'tooltip': 'Factor de compresión de la interfaz.',
                                'type': 'float',
                                'default': 1.0
                            },
                            {
                                'name': 'nLimiterIter',
                                'label': 'nLimiterIter',
                                'tooltip': 'Número de iteraciones del limitador MULES.',
                                'type': 'int',
                                'default': 3
                            },
                            {
                                'name': 'alpha_water_tolerance',
                                'label': 'alpha.water Tolerancia',
                                'tooltip': 'Tolerancia para el solver alpha.water.',
                                'type': 'float',
                                'default': 1e-8
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
                                'default': 5e-9
                            },
                            {
                                'name': 'p_rgh_relTol',
                                'label': 'p_rgh Rel. Tolerancia',
                                'tooltip': 'Tolerancia relativa para el solver p_rgh.',
                                'type': 'float',
                                'default': 0.01
                            },
                            {
                                'name': 'p_rgh_maxIter',
                                'label': 'p_rgh maxIter',
                                'tooltip': 'Máximo de iteraciones para el solver p_rgh.',
                                'type': 'int',
                                'default': 50
                            },
                            {
                                'name': 'U_k_omega_s_tolerance',
                                'label': 'U,k,omega,s Tolerancia',
                                'tooltip': 'Tolerancia para los solvers de U, k, omega, s.',
                                'type': 'float',
                                'default': 1e-6
                            },
                            {
                                'name': 'U_k_omega_s_relTol',
                                'label': 'U,k,omega,s Rel. Tolerancia',
                                'tooltip': 'Tolerancia relativa para los solvers de U, k, omega, s.',
                                'type': 'float',
                                'default': 0.1
                            },
                            {
                                'name': 'U_k_omega_s_nSweeps',
                                'label': 'U,k,omega,s nSweeps',
                                'tooltip': 'Número de "sweeps" para los solvers de U, k, omega, s.',
                                'type': 'int',
                                'default': 1
                            },
                            {
                                'name': 'nCorrectors',
                                'label': 'PIMPLE nCorrectors',
                                'tooltip': 'Número de correctores en el algoritmo PIMPLE.',
                                'type': 'int',
                                'default': 2
                            },
                            {
                                'name': 'nNonOrthogonalCorrectors',
                                'label': 'PIMPLE nNonOrthogonalCorrectors',
                                'tooltip': 'Número de correctores no ortogonales en el algoritmo PIMPLE.',
                                'type': 'int',
                                'default': 0
                            }
                        ]
                    },
                    {
                        'name': '2DChannelSedFoam',
                        'label': '2DChannel - SedFOAM',
                        'parameters' : [
                            {
                                'name': 'p_rbgh_tolerance',
                                'label': 'p_rbgh Tolerancia',
                                'tooltip': 'Tolerancia para el solver p_rbgh.',
                                'type': 'float',
                                'default': 1e-06
                            },
                            {
                                'name': 'p_rbgh_relTol',
                                'label': 'p_rbgh Rel. Tolerancia',
                                'tooltip': 'Tolerancia relativa para el solver p_rbgh.',
                                'type': 'float',
                                'default': 0.0
                            },
                            {
                                'name': 'p_rbgh_nPreSweeps',
                                'label': 'p_rbgh nPreSweeps',
                                'tooltip': 'Número de "pre-sweeps" para el solver p_rbgh.',
                                'type': 'int',
                                'default': 0
                            },
                            {
                                'name': 'p_rbgh_nPostSweeps',
                                'label': 'p_rbgh nPostSweeps',
                                'tooltip': 'Número de "post-sweeps" para el solver p_rbgh.',
                                'type': 'int',
                                'default': 2
                            },
                            {
                                'name': 'p_rbgh_nFinestSweeps',
                                'label': 'p_rbgh nFinestSweeps',
                                'tooltip': 'Número de "finest-sweeps" para el solver p_rbgh.',
                                'type': 'int',
                                'default': 2
                            },
                            {
                                'name': 'k_epsilon_omega_pa_alpha_tolerance',
                                'label': 'k,epsilon,omega,pa,alpha Tolerancia',
                                'tooltip': 'Tolerancia para los solvers de k, epsilon, omega, pa, alphaPlastic.',
                                'type': 'float',
                                'default': 1e-09
                            },
                            {
                                'name': 'k_epsilon_omega_pa_alpha_relTol',
                                'label': 'k,epsilon,omega,pa,alpha Rel. Tolerancia',
                                'tooltip': 'Tolerancia relativa para los solvers de k, epsilon, omega, pa, alphaPlastic.',
                                'type': 'float',
                                'default': 1e-05
                            },
                            {
                                'name': 'nCorrectors',
                                'label': 'PIMPLE nCorrectors',
                                'tooltip': 'Número de correctores en el algoritmo PIMPLE.',
                                'type': 'int',
                                'default': 1
                            },
                            {
                                'name': 'nNonOrthogonalCorrectors',
                                'label': 'PIMPLE nNonOrthogonalCorrectors',
                                'tooltip': 'Número de correctores no ortogonales en el algoritmo PIMPLE.',
                                'type': 'int',
                                'default': 0
                            },
                            {
                                'name': 'nAlphaCorr',
                                'label': 'nAlphaCorr',
                                'tooltip': 'Número de correctores para la ecuación de alpha.',
                                'type': 'int',
                                'default': 0
                            }
                        ]
                    },
                    {
                        'name': '2DPipelineScour',
                        'label': '2DPipelineScour - SedFOAM',
                        'parameters' : [
                            {
                                'name': 'p_rbgh_tolerance',
                                'label': 'p_rbgh Tolerancia',
                                'tooltip': 'Tolerancia para el solver p_rbgh.',
                                'type': 'float',
                                'default': 1e-06
                            },
                            {
                                'name': 'p_rbgh_relTol',
                                'label': 'p_rbgh Rel. Tolerancia',
                                'tooltip': 'Tolerancia relativa para el solver p_rbgh.',
                                'type': 'float',
                                'default': 0.0001
                            },
                            {
                                'name': 'p_rbgh_nPreSweeps',
                                'label': 'p_rbgh nPreSweeps',
                                'tooltip': 'Número de "pre-sweeps" para el solver p_rbgh.',
                                'type': 'int',
                                'default': 0
                            },
                            {
                                'name': 'p_rbgh_nPostSweeps',
                                'label': 'p_rbgh nPostSweeps',
                                'tooltip': 'Número de "post-sweeps" para el solver p_rbgh.',
                                'type': 'int',
                                'default': 2
                            },
                            {
                                'name': 'p_rbgh_nFinestSweeps',
                                'label': 'p_rbgh nFinestSweeps',
                                'tooltip': 'Número de "finest-sweeps" para el solver p_rbgh.',
                                'type': 'int',
                                'default': 2
                            },
                            {
                                'name': 'k_epsilon_pa_alpha_tolerance',
                                'label': 'k,epsilon,pa,alpha Tolerancia',
                                'tooltip': 'Tolerancia para los solvers de k, epsilon, pa, alphaPlastic.',
                                'type': 'float',
                                'default': 1e-5
                            },
                            {
                                'name': 'k_epsilon_pa_alpha_relTol',
                                'label': 'k,epsilon,pa,alpha Rel. Tolerancia',
                                'tooltip': 'Tolerancia relativa para los solvers de k, epsilon, pa, alphaPlastic.',
                                'type': 'float',
                                'default': 0
                            },
                            {
                                'name': 'omega_b_tolerance',
                                'label': 'omega.b Tolerancia',
                                'tooltip': 'Tolerancia para el solver omega.b.',
                                'type': 'float',
                                'default': 1e-9
                            },
                            {
                                'name': 'omega_b_relTol',
                                'label': 'omega.b Rel. Tolerancia',
                                'tooltip': 'Tolerancia relativa para el solver omega.b.',
                                'type': 'float',
                                'default': 0
                            },
                            {
                                'name': 'nCorrectors',
                                'label': 'PIMPLE nCorrectors',
                                'tooltip': 'Número de correctores en el algoritmo PIMPLE.',
                                'type': 'int',
                                'default': 2
                            },
                            {
                                'name': 'nNonOrthogonalCorrectors',
                                'label': 'PIMPLE nNonOrthogonalCorrectors',
                                'tooltip': 'Número de correctores no ortogonales en el algoritmo PIMPLE.',
                                'type': 'int',
                                'default': 1
                            },
                            {
                                'name': 'nAlphaCorr',
                                'label': 'nAlphaCorr',
                                'tooltip': 'Número de correctores para la ecuación de alpha.',
                                'type': 'int',
                                'default': 1
                            },
                            {
                                'name': 'pRefValue',
                                'label': 'pRefValue',
                                'tooltip': 'Valor de referencia de la presión.',
                                'type': 'float',
                                'default': 0
                            }
                        ]
                    }
                ]
            },
                'customContent': {
                'label': 'Contenido de experto',
                'tooltip': 'Cosas que van directamente al archivo',
                'type': 'string',
                'default': "",
                'current': self.customContent,
                'optional': True
            }
        }
        
    