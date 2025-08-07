from .foam_file import FoamFile

class fvSolution(FoamFile):

    def __init__(self):
        super().__init__("system", "dictionary", "fvSolution")
        self.alpha_water_tolerance = "1e-8"
        self.alpha_water_relTol = "0"
        self.p_rgh_tolerance = "1e-07"
        self.p_rgh_relTol = "0.05"
        self.U_tolerance = "1e-06"
        self.U_relTol = "0"
        self.nOuterCorrectors = "1"
        self.nCorrectors = "3"
        self.nNonOrthogonalCorrectors = "0"

    def _get_string(self):
        content = f"""
solvers
{{
    "alpha.water.*"
    {{
        nAlphaCorr      2;
        nAlphaSubCycles 1;
        cAlpha          1;

        MULESCorr       yes;
        nLimiterIter    5;

        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       {self.alpha_water_tolerance};
        relTol          {self.alpha_water_relTol};
    }}

    "pcorr.*"
    {{
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-5;
        relTol          0;
    }}

    p_rgh
    {{
        solver          PCG;
        preconditioner  DIC;
        tolerance       {self.p_rgh_tolerance};
        relTol          {self.p_rgh_relTol};
    }}

    p_rghFinal
    {{
        $p_rgh;
        relTol          0;
    }}

    U
    {{
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       {self.U_tolerance};
        relTol          {self.U_relTol};
    }}
}}

PIMPLE
{{
    momentumPredictor   no;
    nOuterCorrectors    {self.nOuterCorrectors};
    nCorrectors         {self.nCorrectors};
    nNonOrthogonalCorrectors {self.nNonOrthogonalCorrectors};
}}

relaxationFactors
{{
    equations
    {{
        ".*" 1;
    }}
}}
"""
        return self.get_header() + content

    def modify_parameters(self, alpha_water_tolerance, alpha_water_relTol, p_rgh_tolerance, p_rgh_relTol, U_tolerance, U_relTol, nOuterCorrectors, nCorrectors, nNonOrthogonalCorrectors):
        self.alpha_water_tolerance = alpha_water_tolerance
        self.alpha_water_relTol = alpha_water_relTol
        self.p_rgh_tolerance = p_rgh_tolerance
        self.p_rgh_relTol = p_rgh_relTol
        self.U_tolerance = U_tolerance
        self.U_relTol = U_relTol
        self.nOuterCorrectors = nOuterCorrectors
        self.nCorrectors = nCorrectors
        self.nNonOrthogonalCorrectors = nNonOrthogonalCorrectors

    def write_file(self, case_path):
        with open(case_path / self.folder / self.name, "w") as f:
            f.write(self._get_string())

    def get_editable_parameters(self):
        return {
            'alpha_water_tolerance': {
                'label': 'alpha.water Tolerancia',
                'tooltip': 'Tolerancia para el solver alpha.water.',
                'type': 'string',
                'default': '1e-8',
                'group': 'Solvers'
            },
            'alpha_water_relTol': {
                'label': 'alpha.water Rel. Tolerancia',
                'tooltip': 'Tolerancia relativa para el solver alpha.water.',
                'type': 'string',
                'default': '0',
                'group': 'Solvers'
            },
            'p_rgh_tolerance': {
                'label': 'p_rgh Tolerancia',
                'tooltip': 'Tolerancia para el solver p_rgh.',
                'type': 'string',
                'default': '1e-07',
                'group': 'Solvers'
            },
            'p_rgh_relTol': {
                'label': 'p_rgh Rel. Tolerancia',
                'tooltip': 'Tolerancia relativa para el solver p_rgh.',
                'type': 'string',
                'default': '0.05',
                'group': 'Solvers'
            },
            'U_tolerance': {
                'label': 'U Tolerancia',
                'tooltip': 'Tolerancia para el solver U.',
                'type': 'string',
                'default': '1e-06',
                'group': 'Solvers'
            },
            'U_relTol': {
                'label': 'U Rel. Tolerancia',
                'tooltip': 'Tolerancia relativa para el solver U.',
                'type': 'string',
                'default': '0',
                'group': 'Solvers'
            },
            'nOuterCorrectors': {
                'label': 'PIMPLE nOuterCorrectors',
                'tooltip': 'Número de correctores externos en el algoritmo PIMPLE.',
                'type': 'string',
                'default': '1',
                'group': 'PIMPLE'
            },
            'nCorrectors': {
                'label': 'PIMPLE nCorrectors',
                'tooltip': 'Número de correctores internos en el algoritmo PIMPLE.',
                'type': 'string',
                'default': '3',
                'group': 'PIMPLE'
            },
            'nNonOrthogonalCorrectors': {
                'label': 'PIMPLE nNonOrthogonalCorrectors',
                'tooltip': 'Número de correctores no ortogonales en el algoritmo PIMPLE.',
                'type': 'string',
                'default': '0',
                'group': 'PIMPLE'
            }
        }