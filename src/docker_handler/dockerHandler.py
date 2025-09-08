from pathlib import Path
import subprocess
import logging
from .exceptions import DockerHandlerError, DockerNotInstalledError, DockerDaemonError, ContainerExecutionError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DockerHandler():
    def __init__(self,case_path:Path):
        self.case_path = case_path
        self.IMAGEN_SEDFOAM = "cbonamy/sedfoam_2312_ubuntu"
        

    def execute_script_in_docker(self, script_name: str):
        """
        Ejecuta un script dentro de un contenedor Docker y transmite la salida.

        Args:
            script_name (str): El nombre del script a ejecutar (ej. "run_openfoam.sh").

        Yields:
            str: Una línea de la salida del script.

        Raises:
            DockerNotInstalledError: Si el comando 'docker' no se encuentra.
            ContainerExecutionError: Si el script de Docker falla.
            DockerHandlerError: Para otros errores relacionados con Docker.
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
        except FileNotFoundError:
            error_message = "Error: Comando 'docker' no encontrado. Asegúrese de que Docker esté instalado y en el PATH."
            logger.error(error_message)
            yield error_message
            raise DockerNotInstalledError("Docker no está instalado o no se encuentra en el PATH del sistema.")

        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                yield line.strip()

        process.stdout.close()
        return_code = process.wait()

        if return_code != 0:
            error_message = f"Error: La ejecución de {script_name} falló con código de retorno {return_code}."
            logger.error(error_message)
            yield error_message
            raise ContainerExecutionError(error_message)
        
    def is_docker_running(self) -> bool:
        """
        Verifica si el servicio de Docker está en ejecución y es accesible.
        
        Returns:
            bool: True si Docker está corriendo y es accesible, False en caso contrario.
        """
        try:
            subprocess.run(
                ["docker", "info"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except FileNotFoundError:
            logger.warning("Comando 'docker' no encontrado. Docker puede no estar instalado o no estar en el PATH.")
            return False
        except subprocess.CalledProcessError:
            logger.warning("El demonio de Docker no está corriendo o no es accesible (el comando 'docker info' falló).")
            return False
        
    def prepare_case_for_paraview(self):
        """
        Crea un archivo .foam en el directorio del caso para que ParaView lo reconozca.

        Raises:
            DockerNotInstalledError: Si el comando 'docker' no se encuentra.
            ContainerExecutionError: Si el comando para crear el archivo .foam falla.
        """
        ruta_docker_volumen = self.case_path.as_posix()
        nombre_caso = self.case_path.name
        
        # El comando 'touch' crea el archivo .foam
        command = f"cd /case && touch {nombre_caso}.foam"

        docker_command = [
            "docker", "run", "--rm",
            "-v", f"{ruta_docker_volumen}:/case",
            "--entrypoint", "bash",
            self.IMAGEN_SEDFOAM,
            "-c", f"source /usr/lib/openfoam/openfoam2312/etc/bashrc && {command}"
        ]

        try:
            subprocess.run(docker_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error al preparar el caso para ParaView: {e}")
            raise ContainerExecutionError(f"No se pudo crear el archivo .foam. Código de error: {e.returncode}")
        except FileNotFoundError:
            logger.error("Comando 'docker' no encontrado al preparar el caso para ParaView.")
            raise DockerNotInstalledError("Docker no está instalado o no se encuentra en el PATH del sistema.")