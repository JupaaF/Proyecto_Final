
import subprocess
import logging
from pathlib import Path
from initParam import RUTA_LOCAL

# --- Configuración del Logging ---
# Se crea un logger para registrar información, advertencias y errores.
# Esto es más flexible que usar print().
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("simulacion.log"), # Guarda los logs en un archivo
        logging.StreamHandler() # Muestra los logs en la consola
    ]
)

# --- Constantes ---
# Definir las imágenes de Docker como constantes hace el código más legible y fácil de mantener.
IMAGEN_OPENFOAM = "openfoam/openfoam10-paraview510"
IMAGEN_SEDFOAM = "cbonamy/sedfoam_2312_ubuntu"

def ejecutar_simulacion(nameCase: str, solver: int) -> bool:
    """
    Ejecuta una simulación de OpenFOAM dentro de un contenedor Docker.

    Args:
        nameCase: El nombre del directorio del caso.
        solver: El tipo de solver a utilizar (0 o 1 para OpenFOAM, otros para SedFOAM).

    Returns:
        True si la simulación fue exitosa, False en caso contrario.
        
    Raises:
        TypeError: Si los argumentos no son del tipo esperado.
        ValueError: Si los argumentos tienen valores no válidos.
        FileNotFoundError: Si no se encuentra el script de ejecución del caso.
    """
    # --- 1. Validación de Entradas ---
    # Se lanzan excepciones específicas para cada tipo de error,
    # lo que permite al código que llama a esta función decidir cómo manejarlos.
    if not isinstance(nameCase, str) or not nameCase:
        raise TypeError("El argumento 'nameCase' debe ser un string no vacío.")
    if not isinstance(solver, int):
        raise TypeError("El argumento 'solver' debe ser un entero.")

    # --- 2. Configuración de Rutas con pathlib ---
    # pathlib es la forma moderna y recomendada de manejar rutas de sistema de archivos.
    # Es más legible y funciona correctamente en diferentes sistemas operativos.
    ruta_caso = Path(RUTA_LOCAL) / nameCase
    ruta_script = ruta_caso / "run_openfoam.sh"

    if not ruta_script.is_file():
        raise FileNotFoundError(f"Error: No se encontró el script de ejecución en '{ruta_script}'.")

    # --- 3. Selección de Imagen Docker ---
    if solver in [0, 1]:
        imagen = IMAGEN_OPENFOAM
    else:
        imagen = IMAGEN_SEDFOAM
    logging.info(f"Usando la imagen de Docker: {imagen}")

    # --- 4. Ejecución del Comando Docker ---
    # Se convierte la ruta a formato POSIX (con '/') para que sea compatible con Docker.
    ruta_docker_volumen = ruta_caso.as_posix()

    comando_docker = [
            "docker", "run", "-it", "--rm",
	            "-v", f"{ruta_docker_volumen}:/case",
	            "-v", f"{ruta_script}:/run_openfoam.sh", # Monta el script
	            "--entrypoint", "bash", # Sobrescribe el ENTRYPOINT a bash
	            imagen,
	            "/run_openfoam.sh", str(solver) # Pasa el script como argumento a bash
    ]

    logging.info(f"Iniciando simulación para el caso '{nameCase}' con solver {solver}.")
    logging.debug(f"Comando a ejecutar: {' '.join(comando_docker)}")

    try:
        # Al no usar 'capture_output', la salida del proceso se mostrará en tiempo real en la consola.
        proceso = subprocess.run(
            comando_docker,
            check=True       # Lanza CalledProcessError si el comando falla.
        )
        logging.info("Simulación completada con éxito.")
        # Se registra la salida estándar para futura referencia, especialmente si hay advertencias.
        if proceso.stdout:
            logging.debug(f"Salida estándar (stdout):\n{proceso.stdout}")
        if proceso.stderr:
            logging.warning(f"Salida de error estándar (stderr):\n{proceso.stderr}")
        return True

    except FileNotFoundError:
        # Este error ocurre si el comando 'docker' no existe en el sistema.
        logging.error("Error crítico: El comando 'docker' no se encontró.")
        logging.error("Por favor, asegúrate de que Docker esté instalado y en el PATH del sistema.")
        raise

    except subprocess.CalledProcessError as e:
        # Este es el error principal si la simulación dentro de Docker falla.
        logging.error(f"La simulación falló con código de retorno {e.returncode}.")
        # Se registra la salida de error para poder diagnosticar el problema fácilmente.
        if e.stdout:
            logging.error(f"Salida estándar (stdout):\n{e.stdout}")
        if e.stderr:
            logging.error(f"Salida de error (stderr):\n{e.stderr}")
        return False
        
    except Exception as e:
        # Captura cualquier otro error inesperado.
        logging.critical(f"Ocurrió un error inesperado: {e}", exc_info=True)
        raise


# --- Flujo de Ejecución Principal ---
if __name__ == "__main__":
    try:
        # Se llama a la función principal y se comprueba el resultado.
        success = ejecutar_simulacion("caso0", 0)
        if success:
            logging.info("Proceso finalizado correctamente.")
        else:
            logging.warning("El proceso finalizó con errores. Revisa el log 'simulacion.log' para más detalles.")
            
    except (TypeError, ValueError, FileNotFoundError) as e:
        # Se capturan los errores de configuración y se informa al usuario.
        logging.error(f"Error de configuración: {e}")
    except Exception as e:
        # Se captura cualquier otra excepción que no haya sido manejada.
        logging.error(f"Ha ocurrido un error fatal durante la ejecución: {e}")