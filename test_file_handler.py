
import sys
import os

# Paso 1: Añadir el directorio raíz del proyecto al sys.path
# Esto permite importar módulos directamente desde la raíz
# y subdirectorios como 'file_handler'
current_file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_file_dir)

# Paso 2: Importar lo que necesitas
# Ahora puedes importar FileHandler y U_class desde sus rutas de paquete
from file_handler.file_handler import fileHandler # Importa la clase FileHandler
from file_handler.file_class.U import U # Importa la clase U (asumiendo que la clase se llama U dentro de U.py)
from file_handler.file_class.U import foamFile
from initParam import RUTA_LOCAL # Importa RUTA_LOCAL desde initParam.py

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

