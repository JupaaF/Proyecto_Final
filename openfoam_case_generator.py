

import os
from pathlib import Path

# -----------------------------------------------------------------------------
# Clases que modelan cada archivo de configuración de OpenFOAM
# -----------------------------------------------------------------------------

class FoamFile:
    """Clase base para archivos de OpenFOAM. Define el encabezado estándar."""
    def __init__(self, location, object_name):
        self.location = location
        self.object_name = object_name

    def get_header(self):
        return f"""/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \    /   O peration     | Version:  v2312                                 |
|   \  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{{
    format      ascii;
    class       dictionary;
    location    "{self.location}";
    object      {self.object_name};
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
"""

class ControlDict(FoamFile):
    """Genera el archivo 'system/controlDict'."""
    def __init__(self, solver, start_time, end_time, delta_t, write_interval):
        super().__init__("system", "controlDict")
        self.solver = solver
        self.start_time = start_time
        self.end_time = end_time
        self.delta_t = delta_t
        self.write_interval = write_interval

    def __str__(self):
        content = f"""
application     {self.solver};

startFrom       startTime;
startTime       {self.start_time};

stopAt          endTime;
endTime         {self.end_time};

deltaT          {self.delta_t};

writeControl    runTime;
writeInterval   {self.write_interval};

purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
writeCompression off;

timeFormat      general;
timePrecision   6;
"""
        return self.get_header() + content

class FvSchemes(FoamFile):
    """Genera el archivo 'system/fvSchemes'."""
    def __init__(self):
        super().__init__("system", "fvSchemes")
        # Podrías pasar esquemas como argumentos para mayor flexibilidad
        
    def __str__(self):
        content = """
ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      Gauss linearUpwindV grad(U);
    div(phi,alpha)  Gauss vanLeer;
    div(phirb,alpha) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}
"""
        return self.get_header() + content

class FvSolution(FoamFile):
    """Genera el archivo 'system/fvSolution'."""
    def __init__(self):
        super().__init__("system", "fvSolution")
        # Podrías pasar solvers y tolerancias como argumentos
        
    def __str__(self):
        content = """
solvers
{
    p_rgh
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-06;
        relTol          0.05;
    }

    p_rghFinal
    {
        $p_rgh;
        relTol          0;
    }

    "(U|k|epsilon|omega).*"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-05;
        relTol          0.1;
    }
}

PIMPLE
{
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}
"""
        return self.get_header() + content

# -----------------------------------------------------------------------------
# Clase Orquestadora para generar el caso completo
# -----------------------------------------------------------------------------

class CaseGenerator:
    """
    Orquesta la creación de una estructura de caso de OpenFOAM completa
    a partir de un diccionario de configuración.
    """
    def __init__(self, case_name, config_data):
        """
        :param case_name: Nombre del directorio del caso a crear.
        :param config_data: Diccionario con todos los parámetros del usuario.
        """
        self.case_path = Path(case_name)
        self.config = config_data
        self.file_objects = []

    def _prepare_file_objects(self):
        """Crea las instancias de los objetos de archivo basadas en la config."""
        # Extraer datos de la configuración
        system_cfg = self.config.get('system', {})
        initial_cond_cfg = self.config.get('initial_conditions', {})

        # Crear instancias
        self.file_objects.append(ControlDict(**system_cfg['controlDict']))
        self.file_objects.append(FvSchemes()) # Usando defaults
        self.file_objects.append(FvSolution()) # Usando defaults

        # Aquí añadirías más objetos de archivo (p_rgh, transportProperties, etc.)

    def _create_directory_structure(self):
        """Crea la estructura de directorios base del caso."""
        print(f"Creando directorios en: {self.case_path.resolve()}")
        self.case_path.mkdir(exist_ok=True)
        (self.case_path / "system").mkdir(exist_ok=True)
        (self.case_path / "constant").mkdir(exist_ok=True)
        (self.case_path / "0").mkdir(exist_ok=True)

    def generate(self):
        """Ejecuta el proceso completo de generación del caso."""
        print("--- Iniciando generación de caso de OpenFOAM ---")
        self._create_directory_structure()
        self._prepare_file_objects()

        for foam_file in self.file_objects:
            # Determinar la ruta de salida
            # El location puede ser "system", "constant" o '"0"'
            dir_name = foam_file.location.strip('"')
            file_path = self.case_path / dir_name / foam_file.object_name
            
            print(f"Escribiendo archivo: {file_path}")
            
            with open(file_path, 'w') as f:
                f.write(str(foam_file))
        
        print("--- Generación de caso completada. ---")


# -----------------------------------------------------------------------------
# Ejemplo de Uso
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # 1. Definir el nombre del caso de simulación
    output_case_name = "my_first_oop_case"

    # 2. Recopilar los datos (esto vendría de tu interfaz gráfica)
    #    La estructura de este diccionario la defines tú para que sea
    #    fácil de poblar desde la GUI.
    user_simulation_data = {
        "system": {
            "controlDict": {
                "solver": "interFoam",
                "start_time": 0,
                "end_time": 10.0,
                "delta_t": 0.005,
                "write_interval": 0.1
            }
        },
        "initial_conditions": {
            "U": {
                "internalField": "(0 0 0)",
                "boundaryField": [
                    {
                        "name": "inlet",
                        "params": {
                            "type": "fixedValue",
                            "value": "uniform (1.0 0 0)"
                        }
                    },
                    {
                        "name": "outlet",
                        "params": {
                            "type": "zeroGradient"
                        }
                    },
                    {
                        "name": "walls",
                        "params": {
                            "type": "noSlip"
                        }
                    },
                    {
                        "name": "atmosphere",
                        "params": {
                            "type": "pressureInletOutletVelocity",
                            "value": "uniform (0 0 0)"
                        }
                    }
                ]
            }
        }
        # Aquí irían más secciones como "constant", "turbulence", etc.
    }

    # 3. Crear una instancia del generador y ejecutarlo
    generator = CaseGenerator(output_case_name, user_simulation_data)
    generator.generate()

    print(f"\nContenido de la carpeta '{output_case_name}' generado exitosamente.")

