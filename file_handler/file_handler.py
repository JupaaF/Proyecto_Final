from initParam import RUTA_LOCAL
from pathlib import Path

class fileHandler:
    
    def __init__(self,casePath,template):
        
        self.casePath = casePath
        path = RUTA_LOCAL / casePath
        path.mkdir(exist_ok=True)

        self.template = template

        


    