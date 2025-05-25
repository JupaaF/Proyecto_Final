import os
import subprocess
import time

# CONFIGURACIÓN
IMAGEN = "openfoam/openfoam10-paraview510"
RUTA_CASO_LOCAL = r"C:\\Users\\juanp\\CasosOpenFOAM\\caso0"  # Ajusta esta ruta
# Asegúrate de que este script exista en esta ruta y tenga el formato de salto de línea Unix (LF)
RUTA_SCRIPT_OPENFOAM = os.path.join(RUTA_CASO_LOCAL, "run_openfoam.sh")

def ejecutar_simulacion_interactiva_automatica():
    """
    Lanza el contenedor Docker en modo interactivo, ejecutando los comandos de OpenFOAM
    de forma automática a través de un script.
    """
    ruta_docker = RUTA_CASO_LOCAL.replace("\\", "/")
    
    # Asegúrate de que el script run_openfoam.sh exista localmente
    if not os.path.exists(RUTA_SCRIPT_OPENFOAM):
        print(f"❌ Error: No se encontró el script '{RUTA_SCRIPT_OPENFOAM}'.")
        print("Por favor, crea el archivo 'run_openfoam.sh' con el contenido correcto y asegúrate de que esté en la ruta especificada.")
        print("Recuerda guardarlo con saltos de línea de Unix (LF).")
        return

    print("▶️ Iniciando simulación automática de OpenFOAM en modo interactivo...")
    print(f"El caso '{RUTA_CASO_LOCAL}' se montará en '/case' dentro del contenedor.")
    print(f"El script '{RUTA_SCRIPT_OPENFOAM}' se montará en '/run_openfoam.sh' y se ejecutará.")
    print("Verás la salida de los comandos de OpenFOAM directamente aquí.")
    print("El contenedor esperará tu confirmación ('Enter') antes de cerrarse.\n")

    try:
        subprocess.run([
            "docker", "run", "-it", "--rm",
            "-v", f"{ruta_docker}:/case",
            "-v", f"{RUTA_SCRIPT_OPENFOAM.replace(os.sep, '/')}:/run_openfoam.sh", # Monta el script
            "--entrypoint", "bash", # Sobrescribe el ENTRYPOINT a bash
            IMAGEN,
            "/run_openfoam.sh" # Pasa el script como argumento a bash
        ], check=True) # check=True lanzará una excepción si el comando docker falla
        print("\n✅ Simulación completada y contenedor eliminado.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar la simulación en Docker: {e}")
        print(f"Código de retorno: {e.returncode}")
        if e.stderr:
            print(f"Salida de error: {e.stderr.decode()}")
        if e.stdout:
            print(f"Salida estándar: {e.stdout.decode()}")
    except FileNotFoundError:
        print("❌ Error: Docker no parece estar instalado o no está en el PATH.")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")


# --- Flujo de Ejecución Principal ---
if __name__ == "__main__":
    ejecutar_simulacion_interactiva_automatica()