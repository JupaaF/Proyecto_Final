from pathlib import Path
import subprocess
import logging

class DockerHandler():
    def __init__(self,case_path:Path):
        self.case_path = case_path
        self.logger = logging.getLogger(__name__)
        self.IMAGEN_SEDFOAM = "cbonamy/sedfoam_2312_ubuntu" # imagen de Docker para ejecutar simulacion de SedFOAM 
        self.IMAGEN_OPENFOAM = "openfoam/openfoam10-paraview510" # imagen de Docker para ejecutar simulacion de interFoam e icoFoam

    
    def ejecutar_simulacion(self) -> bool:
        ruta_script = Path.cwd() / "src" / "docker_handler" / "run_openfoam.sh"
        ruta_docker_volumen = self.case_path.as_posix()

        comando_docker = [
            "docker", "run", "-it", "--rm",
                "-v", f"{ruta_docker_volumen}:/case",
                "-v", f"{ruta_script.as_posix()}:/run_openfoam.sh", # Monta el script
                "--entrypoint", "bash", # Sobrescribe el ENTRYPOINT a bash
                self.IMAGEN_SEDFOAM,
                "/run_openfoam.sh" # Pasa el script como argumento a bash
        ]
        try:
            # Al no usar 'capture_output', la salida del proceso se mostrará en tiempo real en la consola.
            proceso = subprocess.run(
                comando_docker,
                check=True       # Lanza CalledProcessError si el comando falla.
            )
            self.logger.info("Simulación completada con éxito.")
            # Se registra la salida estándar para futura referencia, especialmente si hay advertencias.
            if proceso.stdout:
                self.logger.debug(f"Salida estándar (stdout):\n{proceso.stdout}")
            if proceso.stderr:
                self.logger.warning(f"Salida de error estándar (stderr):\n{proceso.stderr}")
            return True

        except FileNotFoundError:
            # Este error ocurre si el comando 'docker' no existe en el sistema.
            self.logger.error("Error crítico: El comando 'docker' no se encontró.")
            self.logger.error("Por favor, asegúrate de que Docker esté instalado y en el PATH del sistema.")
            raise

        except subprocess.CalledProcessError as e:
            # Este es el error principal si la simulación dentro de Docker falla.
            self.logger.error(f"La simulación falló con código de retorno {e.returncode}.")
            # Se registra la salida de error para poder diagnosticar el problema fácilmente.
            if e.stdout:
                self.logger.error(f"Salida estándar (stdout):\n{e.stdout}")
            if e.stderr:
                self.logger.error(f"Salida de error (stderr):\n{e.stderr}")
            return False
            
        except Exception as e:
            # Captura cualquier otro error inesperado.
            self.logger.critical(f"Ocurrió un error inesperado: {e}", exc_info=True)
            raise

    def transformar_malla(self)-> bool:
        ruta_script = Path.cwd() / "src" / "docker_handler" / "run_transform.sh"
        ruta_docker_volumen = self.case_path.as_posix()

        comando_docker = [
            "docker", "run", "-it", "--rm",
                "-v", f"{ruta_docker_volumen}:/case",
                "-v", f"{ruta_script.as_posix()}:/run_transform.sh", # Monta el script
                "--entrypoint", "bash", # Sobrescribe el ENTRYPOINT a bash
                self.IMAGEN_SEDFOAM,
                "/run_transform.sh" # Pasa el script como argumento a bash
        ]
        try:
            # Al no usar 'capture_output', la salida del proceso se mostrará en tiempo real en la consola.
            proceso = subprocess.run(
                comando_docker,
                check=True       # Lanza CalledProcessError si el comando falla.
            )
            self.logger.info("Simulación completada con éxito.")
            # Se registra la salida estándar para futura referencia, especialmente si hay advertencias.
            if proceso.stdout:
                self.logger.debug(f"Salida estándar (stdout):\n{proceso.stdout}")
            if proceso.stderr:
                self.logger.warning(f"Salida de error estándar (stderr):\n{proceso.stderr}")
            return True

        except FileNotFoundError:
            # Este error ocurre si el comando 'docker' no existe en el sistema.
            self.logger.error("Error crítico: El comando 'docker' no se encontró.")
            self.logger.error("Por favor, asegúrate de que Docker esté instalado y en el PATH del sistema.")
            raise

        except subprocess.CalledProcessError as e:
            # Este es el error principal si la simulación dentro de Docker falla.
            self.logger.error(f"La simulación falló con código de retorno {e.returncode}.")
            # Se registra la salida de error para poder diagnosticar el problema fácilmente.
            if e.stdout:
                self.logger.error(f"Salida estándar (stdout):\n{e.stdout}")
            if e.stderr:
                self.logger.error(f"Salida de error (stderr):\n{e.stderr}")
            return False
            
        except Exception as e:
            # Captura cualquier otro error inesperado.
            self.logger.critical(f"Ocurrió un error inesperado: {e}", exc_info=True)
            raise