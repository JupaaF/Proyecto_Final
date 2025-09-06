class DockerHandlerError(Exception):
    """Base exception for errors in the docker_handler module."""
    pass

class DockerNotInstalledError(DockerHandlerError):
    """Raised when the Docker command is not found in the system's PATH."""
    pass

class DockerDaemonError(DockerHandlerError):
    """Raised when the Docker daemon is not running or is inaccessible."""
    pass

class ContainerExecutionError(DockerHandlerError):
    """Raised when a command execution inside a Docker container fails."""
    pass
