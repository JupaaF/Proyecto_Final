from initParam import RUTA_LOCAL
from pathlib import Path
from file_handler.file_class.U import U

class fileHandler:
    
    def __init__(self,casePath:str,template:str=None):
        self.casePath = Path(RUTA_LOCAL) / casePath
        self.template = template
        self.files = {}
        self._create_base_dirs()
        self._create_files()

    def get_casePath(self):
        return self.casePath

    def _create_files(self) -> None:

        #Logica de template TODO
        self.files["U"] = U()

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
        file = filePath.split('/')[-1]
        if file in self.files:
            return self.files[file].get_editable_parameters()
        
       

