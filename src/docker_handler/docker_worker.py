import subprocess
from PySide6.QtCore import QObject, Signal

class DockerWorker(QObject):
    """
    A worker QObject that executes a Docker command in a separate thread.
    """
    started = Signal()
    finished = Signal(int)
    output = Signal(str)

    def __init__(self, docker_command: list[str]):
        """
        Args:
            docker_command (list[str]): The full Docker command to execute.
        """
        super().__init__()
        self.docker_command = docker_command
        self._is_running = False

    def run(self):
        """
        Executes the Docker command.
        This method should be run in a separate thread.
        """
        if self._is_running:
            return

        self._is_running = True
        self.started.emit()

        try:
            process = subprocess.Popen(
                self.docker_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Read output line by line in real-time
            for line in iter(process.stdout.readline, ''):
                self.output.emit(line.strip())

            process.stdout.close()
            return_code = process.wait()
            self.finished.emit(return_code)

        except FileNotFoundError:
            self.output.emit("Error: 'docker' command not found. Is Docker installed and in your PATH?")
            self.finished.emit(-1)
        except Exception as e:
            self.output.emit(f"An unexpected error occurred: {e}")
            self.finished.emit(-1)
        finally:
            self._is_running = False
