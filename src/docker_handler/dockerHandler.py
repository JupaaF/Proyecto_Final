from pathlib import Path
import subprocess
import logging
from PySide6.QtCore import QObject, Signal, QThread

from .docker_worker import DockerWorker

# --- Constants ---
DOCKER_IMAGE_SEDFOAM = "cbonamy/sedfoam_2312_ubuntu"

class DockerHandler(QObject):
    """
    Manages the execution of Docker commands in a non-blocking way.
    Emits signals to communicate the status of the execution to the UI.
    """
    process_started = Signal(str)
    process_finished = Signal(str, int)
    new_log_line = Signal(str)

    def __init__(self, case_path: Path):
        super().__init__()
        self.case_path = case_path
        self.logger = logging.getLogger(__name__)
        self.thread = None
        self.worker = None

    def execute_script_in_docker(self, script_name: str):
        """
        Executes a script inside a Docker container asynchronously.
        Args:
            script_name (str): The name of the script to execute (e.g., "run_openfoam.sh").
        """
        if self.thread and self.thread.isRunning():
            self.new_log_line.emit(f"A process is already running. Please wait for it to finish.")
            return

        local_script_path = Path.cwd() / "src" / "docker_handler" / script_name
        script_in_container = f"/{script_name}"
        case_volume_path = self.case_path.as_posix()

        docker_command = [
            "docker", "run", "--rm",
            "-v", f"{case_volume_path}:/case",
            "-v", f"{local_script_path.as_posix()}:{script_in_container}",
            "--entrypoint", "bash",
            DOCKER_IMAGE_SEDFOAM,
            script_in_container
        ]

        self.thread = QThread()
        self.worker = DockerWorker(docker_command)
        self.worker.moveToThread(self.thread)

        # Connect signals from worker to slots in this handler
        self.worker.started.connect(lambda: self._on_worker_started(script_name))
        self.worker.output.connect(self.new_log_line.emit)
        self.worker.finished.connect(lambda code: self._on_worker_finished(script_name, code))

        # Connect thread management signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def _on_worker_started(self, script_name: str):
        """Internal slot to handle the worker's started signal."""
        self.logger.info(f"Starting execution of {script_name} in {DOCKER_IMAGE_SEDFOAM}...")
        self.process_started.emit(script_name)

    def _on_worker_finished(self, script_name: str, return_code: int):
        """Internal slot to handle the worker's finished signal."""
        if return_code == 0:
            self.logger.info(f"Script {script_name} completed successfully.")
        else:
            self.logger.error(f"Execution of {script_name} failed with return code {return_code}.")
        self.process_finished.emit(script_name, return_code)

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