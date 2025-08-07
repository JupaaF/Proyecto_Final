from pathlib import Path

# RUTA_LOCAL define el directorio base donde se guardarán los casos de simulación.
# Se utiliza Path.home() para asegurar que sea compatible con Windows, Linux y macOS.
RUTA_LOCAL = Path.home() / "CasosOpenFOAM"

from .openfoam_models.U import U
from .openfoam_models.controlDict import controlDict

class fileHandler:
    
    def __init__(self,casePath:str,template:str=None):
        # Asegurarse de que el directorio base exista
        RUTA_LOCAL.mkdir(exist_ok=True)
        self.casePath = RUTA_LOCAL / casePath
        self.template = template
        self.files = {}
        self._create_base_dirs()
        self._create_files()
        ## Crea el archivo controlDict una vez que termina el wizard. Esto se hace
        ## para que posteriormente podamos transformar la malla .unv a foam y
        ## posteriormente a .vtk

        ## TODO Tenemos que pasarle los datos del wizard a este constructor
        ## y con esos datos escribir el archivo
        ## De momento tiene los valores por defecto
        with open(self.casePath / "system" / "controlDict", "w") as f:
            self.files["controlDict"].writeFile(f)

    def get_casePath(self):
        return self.casePath

    def _create_files(self) -> None:

        #Logica de template TODO
        self.files["U"] = U()

        ##Agregue este archivo y le agregue el get_editable_parameters()
        ## al controlDict
        self.files["controlDict"] = controlDict()

        for file in self.files:
            self._create_empty_file(self.files[file])

    def _create_base_dirs(self) -> None:
        """Crea los directorios básicos si no existen"""
        self.casePath.mkdir(exist_ok=True)
        for folder in ['0', 'system', 'constant']:
            (self.casePath / folder).mkdir(exist_ok=True)

    def _create_empty_file(self, foam_obj) -> str:
        """Crea el archivo vacío en la ubicación correcta"""
        file_path = self.casePath / foam_obj.folder / foam_obj.name
        file_path.touch()  # Crea el archivo vacío
        print(f"Archivo creado (vacío): {file_path}")
        return file_path
    
    def get_editable_parameters(self,filePath) -> dict:
        file = Path(filePath).name
        if file in self.files:
            return self.files[file].get_editable_parameters()