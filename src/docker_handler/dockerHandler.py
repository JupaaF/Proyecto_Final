from pathlib import Path
import subprocess
import logging

class DockerHandler():
    def __init__(self,case_path:Path):
        self.case_path = case_path
        self.logger = logging.getLogger(__name__)
        self.IMAGEN_SEDFOAM = "cbonamy/sedfoam_2312_ubuntu" # imagen de Docker para ejecutar simulacion de SedFOAM 
        # self.IMAGEN_OPENFOAM = "openfoam/openfoam10-paraview510" # imagen de Docker para ejecutar simulacion de interFoam e icoFoam

    def execute_script_in_docker(self, script_name: str) -> bool:
        """
        Ejecuta un script dentro de un contenedor Docker.

        Args:
            script_name (str): El nombre del script a ejecutar (ej. "run_openfoam.sh").

        Returns:
            bool: True si el comando se ejecutó con éxito, False en caso de error.
        """
        # Ruta del script en tu sistema de archivos local
        local_script_path = Path.cwd() / "src" / "docker_handler" / script_name
        
        # Nombre con el que el script será montado dentro del contenedor
        script_in_container = f"/{script_name}"

        ruta_docker_volumen = self.case_path.as_posix()

        docker_command = [
            "docker", "run", "-it", "--rm",
            "-v", f"{ruta_docker_volumen}:/case",
            "-v", f"{local_script_path.as_posix()}:{script_in_container}", # Monta el script con el nombre dinámico
            "--entrypoint", "bash",
            self.IMAGEN_SEDFOAM,
            script_in_container # Pasa el nombre del script montado como argumento
        ]

        try:
            self.logger.info(f"Iniciando ejecución de {script_name} en {self.IMAGEN_SEDFOAM}...")
            process = subprocess.run(
                docker_command,
                check=True
            )
            self.logger.info(f"Script {script_name} completado con éxito.")
            if process.stdout:
                self.logger.debug(f"Salida estándar (stdout):\n{process.stdout}")
            if process.stderr:
                self.logger.warning(f"Salida de error estándar (stderr):\n{process.stderr}")
            return True
        except FileNotFoundError:
            self.logger.error("Error crítico: El comando 'docker' no se encontró.")
            self.logger.error("Por favor, asegúrate de que Docker esté instalado y en el PATH del sistema.")
            raise
        except subprocess.CalledProcessError as e:
            self.logger.error(f"La ejecución de {script_name} falló con código de retorno {e.returncode}.")
            if e.stdout:
                self.logger.error(f"Salida estándar (stdout):\n{e.stdout}")
            if e.stderr:
                self.logger.error(f"Salida de error (stderr):\n{e.stderr}")
            return False
        except Exception as e:
            self.logger.critical(f"Ocurrió un error inesperado durante la ejecución de {script_name}: {e}", exc_info=True)
            raise

    
    # ----------------------------------------------------------------------------------
    # Estos ya no se usan, se generalizaron con la función de arriba, los dejo por las dudas igual:


    # def ejecutar_simulacion(self) -> bool:
    #     ruta_script = Path.cwd() / "src" / "docker_handler" / "run_openfoam.sh"
    #     ruta_docker_volumen = self.case_path.as_posix()

    #     comando_docker = [
    #         "docker", "run", "-it", "--rm",
    #             "-v", f"{ruta_docker_volumen}:/case",
    #             "-v", f"{ruta_script.as_posix()}:/run_openfoam.sh", # Monta el script
    #             "--entrypoint", "bash", # Sobrescribe el ENTRYPOINT a bash
    #             self.IMAGEN_SEDFOAM,
    #             "/run_openfoam.sh" # Pasa el script como argumento a bash
    #     ]
    #     try:
    #         # Al no usar 'capture_output', la salida del proceso se mostrará en tiempo real en la consola.
    #         proceso = subprocess.run(
    #             comando_docker,
    #             check=True       # Lanza CalledProcessError si el comando falla.
    #         )
    #         self.logger.info("Simulación completada con éxito.")
    #         # Se registra la salida estándar para futura referencia, especialmente si hay advertencias.
    #         if proceso.stdout:
    #             self.logger.debug(f"Salida estándar (stdout):\n{proceso.stdout}")
    #         if proceso.stderr:
    #             self.logger.warning(f"Salida de error estándar (stderr):\n{proceso.stderr}")
    #         return True

    #     except FileNotFoundError:
    #         # Este error ocurre si el comando 'docker' no existe en el sistema.
    #         self.logger.error("Error crítico: El comando 'docker' no se encontró.")
    #         self.logger.error("Por favor, asegúrate de que Docker esté instalado y en el PATH del sistema.")
    #         raise

    #     except subprocess.CalledProcessError as e:
    #         # Este es el error principal si la simulación dentro de Docker falla.
    #         self.logger.error(f"La simulación falló con código de retorno {e.returncode}.")
    #         # Se registra la salida de error para poder diagnosticar el problema fácilmente.
    #         if e.stdout:
    #             self.logger.error(f"Salida estándar (stdout):\n{e.stdout}")
    #         if e.stderr:
    #             self.logger.error(f"Salida de error (stderr):\n{e.stderr}")
    #         return False
            
    #     except Exception as e:
    #         # Captura cualquier otro error inesperado.
    #         self.logger.critical(f"Ocurrió un error inesperado: {e}", exc_info=True)
    #         raise

    # def transformar_malla(self)-> bool:
    #     ruta_script = Path.cwd() / "src" / "docker_handler" / "run_transform.sh"
    #     ruta_docker_volumen = self.case_path.as_posix()

    #     comando_docker = [
    #         "docker", "run", "-it", "--rm",
    #             "-v", f"{ruta_docker_volumen}:/case",
    #             "-v", f"{ruta_script.as_posix()}:/run_transform.sh", # Monta el script
    #             "--entrypoint", "bash", # Sobrescribe el ENTRYPOINT a bash
    #             self.IMAGEN_SEDFOAM,
    #             "/run_transform.sh" # Pasa el script como argumento a bash
    #     ]
    #     try:
    #         # Al no usar 'capture_output', la salida del proceso se mostrará en tiempo real en la consola.
    #         proceso = subprocess.run(
    #             comando_docker,
    #             check=True       # Lanza CalledProcessError si el comando falla.
    #         )
    #         self.logger.info("Simulación completada con éxito.")
    #         # Se registra la salida estándar para futura referencia, especialmente si hay advertencias.
    #         if proceso.stdout:
    #             self.logger.debug(f"Salida estándar (stdout):\n{proceso.stdout}")
    #         if proceso.stderr:
    #             self.logger.warning(f"Salida de error estándar (stderr):\n{proceso.stderr}")
    #         return True

    #     except FileNotFoundError:
    #         # Este error ocurre si el comando 'docker' no existe en el sistema.
    #         self.logger.error("Error crítico: El comando 'docker' no se encontró.")
    #         self.logger.error("Por favor, asegúrate de que Docker esté instalado y en el PATH del sistema.")
    #         raise

    #     except subprocess.CalledProcessError as e:
    #         # Este es el error principal si la simulación dentro de Docker falla.
    #         self.logger.error(f"La simulación falló con código de retorno {e.returncode}.")
    #         # Se registra la salida de error para poder diagnosticar el problema fácilmente.
    #         if e.stdout:
    #             self.logger.error(f"Salida estándar (stdout):\n{e.stdout}")
    #         if e.stderr:
    #             self.logger.error(f"Salida de error (stderr):\n{e.stderr}")
    #         return False
            
    #     except Exception as e:
    #         # Captura cualquier otro error inesperado.
    #         self.logger.critical(f"Ocurrió un error inesperado: {e}", exc_info=True)
    #         raise