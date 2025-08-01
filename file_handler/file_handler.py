from initParam import RUTA_LOCAL
from pathlib import Path

class fileHandler:
    
    def __init__(self,casePath:str,template:str):
        
        self.casePath = casePath
        path = RUTA_LOCAL / casePath
        path.mkdir(exist_ok=True)

        self.template = template

    def crear_archivos():
        pass

    def modificarArchivos(): ##al final de el input de archivos
        pass

        


    