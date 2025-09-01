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
    
    def prepare_case_for_paraview(self):
        """
        Crea un archivo .foam en el directorio del caso para que ParaView lo reconozca.
        """

        #TODO: Agregar codigo que está en la bitacora 21/08 para cuando ejecutas el caso en paralelo++

        # Usar una imagen de Docker que incluya OpenFOAM
        imagen = "openfoam/openfoam10-paraview510" 
        
        ruta_docker_volumen = self.case_path.as_posix()
        nombre_caso = self.case_path.name
        
        # El comando 'touch' crea el archivo .foam
        command = f"cd /case && touch {nombre_caso}.foam"

        docker_command = [
            "docker", "run", "--rm",
            "-v", f"{ruta_docker_volumen}:/case",
            "--entrypoint", "bash",
            imagen,
            "-c", f"source /opt/openfoam*/etc/bashrc && {command}"
        ]

        try:
            subprocess.run(docker_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error al preparar el caso: {e}")
            return False
        except FileNotFoundError:
            print("Error: El comando 'docker' no se encontró.")
            return False