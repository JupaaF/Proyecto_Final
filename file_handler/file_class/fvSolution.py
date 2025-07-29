from foamFile import foamFile

class fvSolution(foamFile):  # por ahora no es editable

    def __init__(self, divSchemes, laplacianSchemes, interpolationSchemes, snGradSchemes, ddtSchemes = 'Euler', gradSchemes = 'Gauss Linear'): #Posiblemente saque los valores
        super().__init__("system", "dictionary", "fvSolution")
        

    def __getString__(self):
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
        tolerance       1e-8;
        relTol          0;
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
        tolerance       1e-07;
        relTol          0.05;
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
        tolerance       1e-06;
        relTol          0;
    }}
}}

PIMPLE
{{
    momentumPredictor   no;
    nOuterCorrectors    1;
    nCorrectors         3;
    nNonOrthogonalCorrectors 0;
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
    
    def write_file(self,archivo):
        archivo.write(self.__getString__())

    