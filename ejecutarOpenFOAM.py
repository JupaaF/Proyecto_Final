import os
import subprocess
import time
from initParam import RUTA_LOCAL

# Asegúrate de que este script exista en esta ruta y tenga el formato de salto de línea Unix (LF)

def ejecutar_simulacion_interactiva_automatica(nameCase:str,solver:int):
    if not isinstance(nameCase,str):
        print("El nombre del caso tiene que ser un string")
        return
    if not isinstance(solver,int):
        print("El solver tiene que ser un entero")
        return
    RUTA_CASO_LOCAL = os.path.join(RUTA_LOCAL, nameCase)
    RUTA_SCRIPT_OPENFOAM = os.path.join(RUTA_CASO_LOCAL, "run_openfoam.sh")
    if solver == 0 or solver == 1:
        imagen = "openfoam/openfoam10-paraview510"
    else:
        imagen = "cbonamy/sedfoam_2312_ubuntu"

    ruta_docker = RUTA_CASO_LOCAL.replace("\\", "/")
    
    # Asegúrate de que el script run_openfoam.sh exista localmente
    if not os.path.exists(RUTA_SCRIPT_OPENFOAM):
        print(f"Error: No se encontró el script '{RUTA_SCRIPT_OPENFOAM}'.")

        return

    print("Iniciando simulación automática de OpenFOAM...")
    try:
        subprocess.run([
            "docker", "run", "-it", "--rm",
            "-v", f"{ruta_docker}:/case",
            "-v", f"{RUTA_SCRIPT_OPENFOAM.replace(os.sep, '/')}:/run_openfoam.sh", # Monta el script
            "--entrypoint", "bash", # Sobrescribe el ENTRYPOINT a bash
            imagen,
            "/run_openfoam.sh", str(solver) # Pasa el script como argumento a bash
        ], check=True) # check=True lanzará una excepción si el comando docker falla
        print("\n Simulación completada y contenedor eliminado.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar la simulación en Docker: {e}")
        print(f"Código de retorno: {e.returncode}")
        if e.stderr:
            print(f"Salida de error: {e.stderr.decode()}")
        if e.stdout:
            print(f"Salida estándar: {e.stdout.decode()}")
    except FileNotFoundError:
        print("Error: Docker no parece estar instalado o no está en el PATH.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")


# --- Flujo de Ejecución Principal ---
if __name__ == "__main__":
    
    ejecutar_simulacion_interactiva_automatica("caso0",1)