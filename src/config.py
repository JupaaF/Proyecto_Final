from pathlib import Path

# Construye una ruta al directorio 'CasosOpenFOAM' en la carpeta de inicio del usuario.
# Esto funciona tanto en Windows (C:\Users\username\CasosOpenFOAM) como en Linux (/home/username/CasosOpenFOAM).
RUTA_LOCAL = Path.home() / "CasosOpenFOAM"

def create_dir():    
    # Crea el directorio si no existe para asegurar que esté disponible.
    RUTA_LOCAL.mkdir(exist_ok=True)
