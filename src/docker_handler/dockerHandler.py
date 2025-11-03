# from pathlib import Path
# import subprocess
# import logging
# import uuid
# import tempfile
# import shutil
# from .exceptions import DockerNotInstalledError, ContainerExecutionError

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# class DockerHandler():
#     def __init__(self,case_path:Path):
#         self.case_path = case_path
#         self.IMAGEN_SEDFOAM = "cbonamy/sedfoam_2312_ubuntu"
#         self.process = None
#         self.was_stopped_by_user = False
#         self.container_name = None

#     # def execute_script_in_docker(self, script_name: str):
#     #     """
#     #     Ejecuta un script dentro de un contenedor Docker y transmite la salida.
        
#     #     Args:
#     #         script_name (str): El nombre del script a ejecutar (ej. "run_openfoam.sh").

#     #     Yields:
#     #         str: Una línea de la salida del script.

#     #     Raises:
#     #         DockerNotInstalledError: Si el comando 'docker' no se encuentra.
#     #         ContainerExecutionError: Si el script de Docker falla.
#     #     """
#     #     self.process = None
#     #     self.was_stopped_by_user = False

#     #     # Se genera un nombre único para el contenedor.
#     #     self.container_name = f"hidrosim-{self.case_path.name}-{uuid.uuid4().hex[:8]}"
        
#     #     local_script_path = Path.cwd() / "src" / "docker_handler" / script_name
#     #     script_in_container = f"/{script_name}"
#     #     ruta_docker_volumen = self.case_path.as_posix()

#     #     docker_command = [
#     #         "docker", "run", "--name", self.container_name,
#     #         "-v", f"{ruta_docker_volumen}:/case",
#     #         "-v", f"{local_script_path.as_posix()}:{script_in_container}",
#     #         "--entrypoint", "bash",
#     #         self.IMAGEN_SEDFOAM,
#     #         script_in_container
#     #     ]

#     #     try:
#     #         self.process = subprocess.Popen(
#     #             docker_command,
#     #             stdout=subprocess.PIPE,
#     #             stderr=subprocess.STDOUT,
#     #             text=True,
#     #             bufsize=1,
#     #             universal_newlines=True
#     #         )
#     #     except FileNotFoundError:
#     #         error_message = "Error: Comando 'docker' no encontrado. Asegúrese de que Docker esté instalado y en el PATH."
#     #         logger.error(error_message)
#     #         yield error_message
#     #         raise DockerNotInstalledError("Docker no está instalado o no se encuentra en el PATH del sistema.")

#     #     # Transmitir la salida del proceso
#     #     if self.process.stdout:
#     #         for line in iter(self.process.stdout.readline, ''):
#     #             yield line.strip()

#     #     # Esperar a que el proceso de 'docker run' termine. Este proceso finaliza
#     #     # cuando el contenedor se detiene (ya sea por completar su tarea o por
#     #     # ser detenido externamente).
#     #     if self.process.stdout:
#     #         self.process.stdout.close()
#     #     return_code = self.process.wait()

#     #     # Limpiar el contenedor después de que se detenga
#     #     logger.info(f"Limpiando el contenedor {self.container_name}...")
#     #     subprocess.run(["docker", "rm", self.container_name], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
#     #     # Si la bandera fue activada por `stop_simulation`, se informa al usuario
#     #     # y se termina la ejecución de forma controlada.
#     #     if self.was_stopped_by_user:
#     #         yield "La simulación fue detenida por el usuario."
#     #         return

#     #     if return_code != 0:
#     #         error_message = f"Error: La ejecución de {script_name} falló con código de retorno {return_code}."
#     #         logger.error(error_message)
#     #         yield error_message
#     #         raise ContainerExecutionError(error_message)



#     def execute_script_in_docker(self, script_name: str, num_processors: int = 1):
#         """
#         Ejecuta un script dentro de un contenedor Docker y transmite la salida.

#         Args:
#             script_name (str): El nombre del script a ejecutar (ej. "run_openfoam.sh").

#         Yields:
#             str: Una línea de la salida del script.
#             num_processors (int): El número de procesadores para correr la simulación.

#         Raises:
#             FileNotFoundError: Si el comando 'docker' no se encuentra.
#             subprocess.CalledProcessError: Si el script de Docker falla.
#         """
#         self.process = None
#         self.was_stopped_by_user = False

#         self.container_name = f"hidrosim-{self.case_path.name}-{uuid.uuid4().hex[:8]}"
#         local_script_path = Path.cwd() / "src" / "docker_handler" / script_name
#         script_in_container = f"/{script_name}"

#         scripts_without_0_dir = [
#             'run_blockMeshDict.sh', 'run_extrudeMesh.sh',
#             'run_transform_blockMeshDict.sh', 'run_transform_UNV.sh', 'run_foamToVTK.sh'
#         ]

#         temp_dir = None
#         try:
#             if script_name in scripts_without_0_dir:
#                 temp_dir = tempfile.mkdtemp()
#                 shutil.copytree(self.case_path / "system", Path(temp_dir) / "system")
#                 if (self.case_path / "constant").exists():
#                     shutil.copytree(self.case_path / "constant", Path(temp_dir) / "constant")
#                 ruta_docker_volumen = temp_dir
#             else:
#                 ruta_docker_volumen = self.case_path.as_posix()

#             docker_command = [
#                 "docker", "run", "--name", self.container_name,
#                 "-v", f"{ruta_docker_volumen}:/case",
#                 "-v", f"{local_script_path.as_posix()}:{script_in_container}",
#                 "--entrypoint", "bash", self.IMAGEN_SEDFOAM,
#                 script_in_container, str(num_processors)
#             ]
            
#             process = subprocess.Popen(
#                 docker_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
#                 text=True, bufsize=1, universal_newlines=True
#             )

#             if process.stdout:
#                 for line in iter(process.stdout.readline, ''):
#                     yield line.strip()
            
#             process.stdout.close()
#             return_code = process.wait()

#             if return_code != 0:
#                 raise ContainerExecutionError(f"La ejecución de {script_name} falló con código de retorno {return_code}.")

#             if temp_dir:
#                 shutil.copytree(temp_dir, self.case_path, dirs_exist_ok=True)

#         except Exception as e:
#             logger.error(f"Error durante la ejecución de Docker: {e}")
#             yield str(e)
#             raise

#         finally:
#             if temp_dir:
#                 shutil.rmtree(temp_dir)
            
#             logger.info(f"Limpiando el contenedor {self.container_name}...")
#             subprocess.run(["docker", "rm", self.container_name], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
#             if self.was_stopped_by_user:
#                 yield "La simulación fue detenida por el usuario."




        
#     def stop_simulation(self):
#         """
#         Detiene el contenedor de Docker en curso usando su nombre.
#         """
#         if self.container_name:
#             logger.info(f"Intentando detener el contenedor: {self.container_name}")
#             self.was_stopped_by_user = True
            
#             # Usar 'docker stop' que envía SIGTERM y después de un tiempo SIGKILL
#             # Este comando es bloqueante y espera a que el contenedor se detenga.
#             result = subprocess.run(
#                 ["docker", "stop", self.container_name],
#                 capture_output=True,
#                 text=True
#             )
            
#             if result.returncode == 0:
#                 logger.info(f"Contenedor {self.container_name} detenido exitosamente.")
#                 return True
#             else:
#                 # Es posible que el contenedor ya se haya detenido, lo cual no es un error.
#                 # Si el contenedor ya no existe (porque terminó justo antes de la
#                 # llamada a stop), no se considera un error.
#                 if "No such container" in result.stderr:
#                     logger.warning(f"El contenedor {self.container_name} no fue encontrado, puede que ya se haya detenido.")
#                     return True
#                 logger.error(f"Error al detener el contenedor {self.container_name}: {result.stderr.strip()}")
#                 return False
#         else:
#             logger.warning("No hay ningún nombre de contenedor registrado para detener.")
#             return False
        
#     def is_docker_running(self) -> bool:
#         """
#         Verifica si el servicio de Docker está en ejecución y es accesible.
        
#         Returns:
#             bool: True si Docker está corriendo y es accesible, False en caso contrario.
#         """
#         try:
#             subprocess.run(
#                 ["docker", "info"],
#                 check=True,
#                 stdout=subprocess.DEVNULL,
#                 stderr=subprocess.DEVNULL
#             )
#             return True
#         except FileNotFoundError:
#             logger.warning("Comando 'docker' no encontrado. Docker puede no estar instalado o no estar en el PATH.")
#             return False
#         except subprocess.CalledProcessError:
#             logger.warning("El demonio de Docker no está corriendo o no es accesible (el comando 'docker info' falló).")
#             return False
        
#     def prepare_case_for_paraview(self):
#         """
#         Crea un archivo .foam en el directorio del caso para que ParaView lo reconozca.

#         Raises:
#             DockerNotInstalledError: Si el comando 'docker' no se encuentra.
#             ContainerExecutionError: Si el comando para crear el archivo .foam falla.
#         """
#         ruta_docker_volumen = self.case_path.as_posix()
#         nombre_caso = self.case_path.name
        
#         # El comando 'touch' crea el archivo .foam
#         command = f"cd /case && touch {nombre_caso}.foam"

#         docker_command = [
#             "docker", "run", "--rm",
#             "-v", f"{ruta_docker_volumen}:/case",
#             "--entrypoint", "bash",
#             self.IMAGEN_SEDFOAM,
#             "-c", f"source /usr/lib/openfoam/openfoam2312/etc/bashrc && {command}"
#         ]

#         try:
#             subprocess.run(docker_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#             return True
#         except subprocess.CalledProcessError as e:
#             logger.error(f"Error al preparar el caso para ParaView: {e}")
#             raise ContainerExecutionError(f"No se pudo crear el archivo .foam. Código de error: {e.returncode}")
#         except FileNotFoundError:
#             logger.error("Comando 'docker' no encontrado al preparar el caso para ParaView.")
#             raise DockerNotInstalledError("Docker no está instalado o no se encuentra en el PATH del sistema.")




import os
from pathlib import Path
import subprocess
import logging
import uuid
import tempfile
import shutil
from .exceptions import DockerNotInstalledError, ContainerExecutionError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DockerHandler():
    def __init__(self,case_path:Path):
        self.case_path = case_path
        self.IMAGEN_SEDFOAM = "cbonamy/sedfoam_2312_ubuntu"
        self.process = None
        self.was_stopped_by_user = False
        self.container_name = None

        # Configuración para subprocesos en Windows para evitar la apertura de una consola
        self.subprocess_kwargs = {}
        if os.name == 'nt':
            self.subprocess_kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

    # def execute_script_in_docker(self, script_name: str):
    #     """
    #     Ejecuta un script dentro de un contenedor Docker y transmite la salida.
        
    #     Args:
    #         script_name (str): El nombre del script a ejecutar (ej. "run_openfoam.sh").

    #     Yields:
    #         str: Una línea de la salida del script.

    #     Raises:
    #         DockerNotInstalledError: Si el comando 'docker' no se encuentra.
    #         ContainerExecutionError: Si el script de Docker falla.
    #     """
    #     self.process = None
    #     self.was_stopped_by_user = False

    #     # Se genera un nombre único para el contenedor.
    #     self.container_name = f"hidrosim-{self.case_path.name}-{uuid.uuid4().hex[:8]}"
        
    #     local_script_path = Path.cwd() / "src" / "docker_handler" / script_name
    #     script_in_container = f"/{script_name}"
    #     ruta_docker_volumen = self.case_path.as_posix()

    #     docker_command = [
    #         "docker", "run", "--name", self.container_name,
    #         "-v", f"{ruta_docker_volumen}:/case",
    #         "-v", f"{local_script_path.as_posix()}:{script_in_container}",
    #         "--entrypoint", "bash",
    #         self.IMAGEN_SEDFOAM,
    #         script_in_container
    #     ]

    #     try:
    #         self.process = subprocess.Popen(
    #             docker_command,
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.STDOUT,
    #             text=True,
    #             bufsize=1,
    #             universal_newlines=True
    #         )
    #     except FileNotFoundError:
    #         error_message = "Error: Comando 'docker' no encontrado. Asegúrese de que Docker esté instalado y en el PATH."
    #         logger.error(error_message)
    #         yield error_message
    #         raise DockerNotInstalledError("Docker no está instalado o no se encuentra en el PATH del sistema.")

    #     # Transmitir la salida del proceso
    #     if self.process.stdout:
    #         for line in iter(self.process.stdout.readline, ''):
    #             yield line.strip()

    #     # Esperar a que el proceso de 'docker run' termine. Este proceso finaliza
    #     # cuando el contenedor se detiene (ya sea por completar su tarea o por
    #     # ser detenido externamente).
    #     if self.process.stdout:
    #         self.process.stdout.close()
    #     return_code = self.process.wait()

    #     # Limpiar el contenedor después de que se detenga
    #     logger.info(f"Limpiando el contenedor {self.container_name}...")
    #     subprocess.run(["docker", "rm", self.container_name], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    #     # Si la bandera fue activada por `stop_simulation`, se informa al usuario
    #     # y se termina la ejecución de forma controlada.
    #     if self.was_stopped_by_user:
    #         yield "La simulación fue detenida por el usuario."
    #         return

    #     if return_code != 0:
    #         error_message = f"Error: La ejecución de {script_name} falló con código de retorno {return_code}."
    #         logger.error(error_message)
    #         yield error_message
    #         raise ContainerExecutionError(error_message)



    def execute_script_in_docker(self, script_name: str, num_processors: int = 1):
        """
        Ejecuta un script dentro de un contenedor Docker y transmite la salida.
        Args:
            script_name (str): El nombre del script a ejecutar (ej. "run_openfoam.sh").
        Yields:
            str: Una línea de la salida del script.
            num_processors (int): El número de procesadores para correr la simulación.
        Raises:
            DockerNotInstalledError: Si el comando 'docker' no se encuentra.
            ContainerExecutionError: Si el script de Docker falla.
        """
        self.process = None
        self.was_stopped_by_user = False

        # self.container_name = f"hidrosim-{self.case_path.name}-{uuid.uuid4().hex[:8]}"
        self.container_name = f"hidrosim-{self.case_path.name.replace(' ', '-')}-{uuid.uuid4().hex[:8]}"
        local_script_path = Path(__file__).parent / script_name
        script_in_container = f"/{script_name}"

        scripts_without_0_dir = [
            'run_blockMeshDict.sh', 'run_extrudeMesh.sh',
            'run_transform_blockMeshDict.sh', 'run_transform_UNV.sh', 'run_foamToVTK.sh'
        ]

        temp_dir = None
        try:
            if script_name in scripts_without_0_dir:
                temp_dir = tempfile.mkdtemp()
                system_path = self.case_path / "system"
                if system_path.exists():
                    shutil.copytree(system_path, Path(temp_dir) / "system")

                constant_path = self.case_path / "constant"
                if constant_path.exists():
                    shutil.copytree(constant_path, Path(temp_dir) / "constant")
                ruta_docker_volumen = temp_dir
            else:
                ruta_docker_volumen = self.case_path.as_posix()

            docker_command = [
                "docker", "run", "--name", self.container_name,
                "-v", f"{ruta_docker_volumen}:/case",
                "-v", f"{local_script_path.as_posix()}:{script_in_container}",
                "--entrypoint", "bash", self.IMAGEN_SEDFOAM,
                script_in_container, str(num_processors)
            ]
            
            try:
                self.process = subprocess.Popen(
                    docker_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1, universal_newlines=True, **self.subprocess_kwargs
                )
            except FileNotFoundError:
                yield "Error: Comando 'docker' no encontrado"
                raise DockerNotInstalledError("Docker no está instalado o no se encuentra en el PATH del sistema.")

            if self.process.stdout:
                for line in iter(self.process.stdout.readline, ''):
                    if self.was_stopped_by_user:
                        break
                    yield line.strip()
            
            if self.process.stdout:
                self.process.stdout.close()
            return_code = self.process.wait()

            if temp_dir:
                shutil.copytree(temp_dir, self.case_path, dirs_exist_ok=True)

            if self.was_stopped_by_user:
                yield "La simulación fue detenida por el usuario."
                return

            if return_code != 0:
                error_message = f"La ejecución de {script_name} falló con código de retorno {return_code}."
                yield f"Error: La ejecución de {script_name} falló"
                raise ContainerExecutionError(error_message)

        finally:
            if temp_dir:
                shutil.rmtree(temp_dir)
            
            if self.container_name:
                logger.info(f"Limpiando el contenedor {self.container_name}...")
                subprocess.run(["docker", "rm", self.container_name], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **self.subprocess_kwargs)




        
    def stop_simulation(self):
        """
        Detiene el contenedor de Docker en curso usando su nombre.
        """
        if self.container_name:
            logger.info(f"Intentando detener el contenedor: {self.container_name}")
            self.was_stopped_by_user = True
            
            # Usar 'docker stop' que envía SIGTERM y después de un tiempo SIGKILL
            # Este comando es bloqueante y espera a que el contenedor se detenga.
            result = subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True,
                text=True,
                **self.subprocess_kwargs
            )
            
            if result.returncode == 0:
                logger.info(f"Contenedor {self.container_name} detenido exitosamente.")
                return True
            else:
                # Es posible que el contenedor ya se haya detenido, lo cual no es un error.
                # Si el contenedor ya no existe (porque terminó justo antes de la
                # llamada a stop), no se considera un error.
                if "No such container" in result.stderr:
                    logger.warning(f"El contenedor {self.container_name} no fue encontrado, puede que ya se haya detenido.")
                    return True
                logger.error(f"Error al detener el contenedor {self.container_name}: {result.stderr.strip()}")
                return False
        else:
            logger.warning("No hay ningún nombre de contenedor registrado para detener.")
            return False
        
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
                stderr=subprocess.DEVNULL,
                **self.subprocess_kwargs
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
            subprocess.run(docker_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **self.subprocess_kwargs)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error al preparar el caso para ParaView: {e}")
            raise ContainerExecutionError(f"No se pudo crear el archivo .foam. Código de error: {e.returncode}")
        except FileNotFoundError:
            logger.error("Comando 'docker' no encontrado al preparar el caso para ParaView.")
            raise DockerNotInstalledError("Docker no está instalado o no se encuentra en el PATH del sistema.")