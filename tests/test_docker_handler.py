import pytest
from pathlib import Path
import sys
import os
import subprocess
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.docker_handler.dockerHandler import DockerHandler
from src.docker_handler.exceptions import DockerNotInstalledError, DockerDaemonError, ContainerExecutionError

@pytest.fixture
def docker_handler(tmp_path: Path) -> DockerHandler:
    """Fixture para crear una instancia de DockerHandler con una ruta de caso temporal."""
    case_path = tmp_path / "test_case"
    case_path.mkdir()
    return DockerHandler(case_path)

# Se patchea el subprocess.run de las funciones del dockerHandler
# Esta línea le dice a Python que mientras dure esta función de test, cada vez que el código dentro 
# de src.docker_handler.dockerHandler intente usar subprocess.run, use el objeto falso 'mock' en su lugar.
@patch('src.docker_handler.dockerHandler.subprocess.run')
def test_is_docker_running_success(mock_run, docker_handler: DockerHandler):
    """Prueba si is_docker_running se devuelve correctamente cuando Docker se está ejecutando."""
    mock_run.return_value = None
    
    # El método no debería devolver ninguna excepción
    docker_handler.is_docker_running()
    
    # Verifica que el comando que se llamó fue el correcto
    mock_run.assert_called_once_with(
        ["docker", "info"],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

@patch('src.docker_handler.dockerHandler.subprocess.run')
def test_is_docker_running_daemon_error(mock_run, docker_handler: DockerHandler):
    """Prueba si is_docker_running devuelve un DockerDaemonError cuando el comando docker falla."""
    mock_run.side_effect = subprocess.CalledProcessError(1, "docker info")
    
    with pytest.raises(DockerDaemonError):
        docker_handler.is_docker_running()
    mock_run.assert_called_once()

@patch('src.docker_handler.dockerHandler.subprocess.run')
def test_is_docker_running_not_found(mock_run, docker_handler: DockerHandler):
    """Prueba si is_docker_running da un DockerNotInstalledError cuando el comando no se encuentra."""
    mock_run.side_effect = FileNotFoundError
    
    with pytest.raises(DockerNotInstalledError):
        docker_handler.is_docker_running()
    mock_run.assert_called_once()

@patch('src.docker_handler.dockerHandler.subprocess.run')
def test_prepare_case_for_paraview_success(mock_run, docker_handler: DockerHandler):
    """Prueba prepare_case_for_paraview en una ejecución satisfactoria."""
    mock_run.return_value = None
    
    # El método no debería devolver ninguna excepción
    docker_handler.prepare_case_for_paraview()
    mock_run.assert_called_once()


@patch('src.docker_handler.dockerHandler.subprocess.run')
def test_prepare_case_for_paraview_failure(mock_run, docker_handler: DockerHandler):
    """Prueba que prepare_case_for_paraview devuelva ContainerExecutionError en un fallo."""
    mock_run.side_effect = subprocess.CalledProcessError(1, "docker run ...")
    
    with pytest.raises(ContainerExecutionError):
        docker_handler.prepare_case_for_paraview()
    mock_run.assert_called_once()

@patch('src.docker_handler.dockerHandler.subprocess.run')
def test_prepare_case_for_paraview_not_found(mock_run, docker_handler: DockerHandler):
    """Prueba que prepare_case_for_paraview devuelva DockerNotInstalledError cuando un comando no se encuentra."""
    mock_run.side_effect = FileNotFoundError
    
    with pytest.raises(DockerNotInstalledError):
        docker_handler.prepare_case_for_paraview()
    mock_run.assert_called_once()


@patch('src.docker_handler.dockerHandler.subprocess.Popen')
def test_execute_script_in_docker_success(mock_popen, docker_handler: DockerHandler):
    """Prueba execute_script_in_docker en una ejecución del script correcta."""
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = ['line 1', 'line 2', '']
    mock_process.wait.return_value = 0 # No error
    mock_popen.return_value = mock_process

    script_name = "test_script.sh"
    output = list(docker_handler.execute_script_in_docker(script_name))

    assert output == ["line 1", "line 2"]
    mock_popen.assert_called_once()

@patch('src.docker_handler.dockerHandler.subprocess.Popen')
def test_execute_script_in_docker_failure(mock_popen, docker_handler: DockerHandler):
<<<<<<< HEAD
    """Prueba si execute_script_in_docker devuelve un ContainerExecutionError en una falla del script."""
=======
    """Test execute_script_in_docker yields an error message and raises ContainerExecutionError on script failure."""
>>>>>>> 28ae9dc00b384cced3d3de59777e0f2b5e1c56c5
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = ['some output', '']
    mock_process.wait.return_value = 1  # Error code
    mock_popen.return_value = mock_process

    script_name = "failing_script.sh"
    generator = docker_handler.execute_script_in_docker(script_name)

    # The function should yield stdout lines first
    assert next(generator) == 'some output'
    
    # Then it should yield the user-facing error message
    assert 'Error: La ejecución de failing_script.sh falló' in next(generator)

    # Finally, it should raise the exception when the generator is exhausted
    with pytest.raises(ContainerExecutionError):
        list(generator)

@patch('src.docker_handler.dockerHandler.subprocess.Popen')
def test_execute_script_in_docker_not_found(mock_popen, docker_handler: DockerHandler):
<<<<<<< HEAD
    """Prueba que execute_script_in_docker devuelva un DockerNotInstalledError cuando un comando no se encuentra."""
=======
    """Test execute_script_in_docker yields an error and raises DockerNotInstalledError when command is not found."""
>>>>>>> 28ae9dc00b384cced3d3de59777e0f2b5e1c56c5
    mock_popen.side_effect = FileNotFoundError

    script_name = "any_script.sh"
    generator = docker_handler.execute_script_in_docker(script_name)

    # Check for the yielded error message first
    assert "Error: Comando 'docker' no encontrado" in next(generator)

    # The exception should be raised when the generator is exhausted
    with pytest.raises(DockerNotInstalledError):
        list(generator)

