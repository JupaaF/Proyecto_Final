from pathlib import Path
import subprocess

class DockerHandler():
    def __init__(self,case_path:Path):
        self.case_path = case_path
        self.IMAGEN_SEDFOAM = "cbonamy/sedfoam_2312_ubuntu" # imagen de Docker para ejecutar simulacion de SedFOAM 
        # self.IMAGEN_OPENFOAM = "openfoam/openfoam10-paraview510" # imagen de Docker para ejecutar simulacion de interFoam e icoFoam
        

    def execute_script_in_docker(self, script_name: str):
        """
        Ejecuta un script dentro de un contenedor Docker y transmite la salida.

        Args:
            script_name (str): El nombre del script a ejecutar (ej. "run_openfoam.sh").

        Yields:
            str: Una línea de la salida del script.

        Raises:
            FileNotFoundError: Si el comando 'docker' no se encuentra.
            subprocess.CalledProcessError: Si el script de Docker falla.
        """
        local_script_path = Path.cwd() / "src" / "docker_handler" / script_name
        script_in_container = f"/{script_name}"
        ruta_docker_volumen = self.case_path.as_posix()

        docker_command = [
            "docker", "run", "--rm",
            "-v", f"{ruta_docker_volumen}:/case",
            "-v", f"{local_script_path.as_posix()}:{script_in_container}",
            "--entrypoint", "bash",
            self.IMAGEN_SEDFOAM,
            script_in_container
        ]

        try:
            process = subprocess.Popen(
                docker_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    yield line.strip()

            process.stdout.close()
            return_code = process.wait()

            if return_code != 0:
                error_message = f"La ejecución de {script_name} falló con código de retorno {return_code}."
                raise subprocess.CalledProcessError(return_code, docker_command, output=error_message)


        except FileNotFoundError:
            yield "Error: Docker command not found. Please ensure Docker is installed and running."
            raise
        except subprocess.CalledProcessError as e:
            yield f"Error: Script execution failed with code {e.returncode}."
            raise
        except Exception as e:
            yield f"An unexpected error occurred: {e}"
            raise
        
    def is_docker_running(self) -> bool:
        """
        Verifica si el servicio de Docker está en ejecución.
        
        Returns:
            bool: True si Docker está corriendo y es accesible, False en caso contrario.
        """
        try:
            # El comando 'docker info' es ligero y no crea contenedores
            subprocess.run(
                ["docker", "info"],
                check=True,
                stdout=subprocess.DEVNULL, # No necesitamos ver la salida
                stderr=subprocess.DEVNULL  # No necesitamos ver los errores
            )
            # Docker está corriendo
            return True
        except FileNotFoundError:
            # El comando 'docker' no se encontró en el PATH
            return False
        except subprocess.CalledProcessError:
            # El comando 'docker info' falló, lo que indica que el servicio no está activo
            return False
        except Exception:
            # Captura cualquier otro error inesperado
            return False
    
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