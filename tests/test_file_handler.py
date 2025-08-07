
import sys
import os

# 1: Añadir el directorio raíz del proyecto al sys.path
current_file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_file_dir)

# 2: 
from file_handler.file_handler import fileHandler 
from file_handler.file_class.U import U 
from file_handler.file_class.U import foamFile
from initParam import RUTA_LOCAL 

fileHandler1 = fileHandler("caso1","damBreak")

# Crear archivo U
U_file = U()
U_file_path = fileHandler1.create_empty_file(U_file)

# Escribir archivo U
patchList= ['leftWall','rightWall', 'lowerWall', 'atmosphere', 'defaultFaces']
patchContent = ['type            noSlip;', 'type            noSlip;', 'type            noSlip;', '''type            pressureInletOutletVelocity;
        value           uniform (0 0 0);
''',  'type            empty;']

U_file.write_file(U_file_path,patchList,patchContent,internalField_value='uniform (0 0 0)' )

print(U_file_path)

