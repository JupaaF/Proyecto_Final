from initParam import RUTA_LOCAL
from pathlib import Path
from file_handler.file_class.U import U

class fileHandler:
    
    def __init__(self,casePath:str,template:str=None):
        self.casePath = Path(RUTA_LOCAL) / casePath
        self.template = template
        self._create_base_dirs()

    def _create_base_dirs(self):
        """Crea los directorios básicos si no existen"""
        self.casePath.mkdir(exist_ok=True)
        for folder in ['0', 'system', 'constant']:
            (self.casePath / folder).mkdir(exist_ok=True)

    def create_empty_file(self, foam_obj):
        """Crea el archivo vacío en la ubicación correcta"""
        file_path = self.casePath / foam_obj.folder / foam_obj.name
        file_path.touch()  # Crea el archivo vacío
        print(f"Archivo creado (vacío): {file_path}")
        return file_path
    

        
       

