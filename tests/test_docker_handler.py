import pytest
from pathlib import Path
import sys
import os
import subprocess
from unittest.mock import patch, MagicMock

# Add project root to sys.path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.docker_handler.dockerHandler import DockerHandler

@pytest.fixture
def docker_handler(tmp_path: Path) -> DockerHandler:
    """Fixture to create a DockerHandler instance with a temporary case path."""
    case_path = tmp_path / "test_case"
    case_path.mkdir()
    return DockerHandler(case_path)


@patch('src.docker_handler.dockerHandler.subprocess.run')
def test_is_docker_running_success(mock_run, docker_handler: DockerHandler):
    """Test is_docker_running when Docker is running."""
    # Configure the mock to simulate a successful command execution
    mock_run.return_value = None  # The function doesn't check the return value, just that it doesn't raise

    assert docker_handler.is_docker_running() is True
    mock_run.assert_called_once_with(
        ["docker", "info"],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

@patch('src.docker_handler.dockerHandler.subprocess.run')
def test_is_docker_running_failure(mock_run, docker_handler: DockerHandler):
    """Test is_docker_running when the docker command fails."""
    # Configure the mock to simulate a failed command execution
    mock_run.side_effect = subprocess.CalledProcessError(1, "docker info")

    assert docker_handler.is_docker_running() is False
    mock_run.assert_called_once()


@patch('src.docker_handler.dockerHandler.subprocess.run')
def test_prepare_case_for_paraview_success(mock_run, docker_handler: DockerHandler):
    """Test prepare_case_for_paraview on successful execution."""
    mock_run.return_value = None  # Simulate successful run

    result = docker_handler.prepare_case_for_paraview()

    assert result is True
    mock_run.assert_called_once()
    # You could also add more detailed assertions about the call arguments here

@patch('src.docker_handler.dockerHandler.subprocess.run')
def test_prepare_case_for_paraview_failure(mock_run, docker_handler: DockerHandler):
    """Test prepare_case_for_paraview when the docker command fails."""
    mock_run.side_effect = subprocess.CalledProcessError(1, "docker run ...")

    result = docker_handler.prepare_case_for_paraview()

    assert result is False
    mock_run.assert_called_once()


@patch('src.docker_handler.dockerHandler.subprocess.Popen')
def test_execute_script_in_docker_success(mock_popen, docker_handler: DockerHandler):
    """Test execute_script_in_docker for successful script execution."""
    mock_process = MagicMock()
    mock_process.stdout = MagicMock()
    mock_process.stdout.readline.side_effect = ['line 1', 'line 2', '']
    mock_process.wait.return_value = 0
    mock_popen.return_value = mock_process

    script_name = "test_script.sh"
    output = list(docker_handler.execute_script_in_docker(script_name))

    assert output == ["line 1", "line 2"]
    mock_popen.assert_called_once()

@patch('src.docker_handler.dockerHandler.subprocess.Popen')
def test_execute_script_in_docker_failure(mock_popen, docker_handler: DockerHandler):
    """Test execute_script_in_docker for a script that fails."""
    mock_process = MagicMock()
    mock_process.stdout = MagicMock()
    mock_process.stdout.readline.side_effect = ['error line', '']
    mock_process.wait.return_value = 1
    mock_popen.return_value = mock_process

    script_name = "failing_script.sh"
    generator = docker_handler.execute_script_in_docker(script_name)

    # The function should yield stdout lines first
    assert 'error line' == next(generator)

    # Then it should yield the error message from the except block
    assert 'Error: Script execution failed with code 1' in next(generator)

    # Finally, it should re-raise the exception
    with pytest.raises(subprocess.CalledProcessError):
        next(generator)

@patch('src.docker_handler.dockerHandler.subprocess.Popen')
def test_execute_script_in_docker_not_found(mock_popen, docker_handler: DockerHandler):
    """Test execute_script_in_docker when docker command is not found."""
    mock_popen.side_effect = FileNotFoundError

    script_name = "any_script.sh"
    generator = docker_handler.execute_script_in_docker(script_name)

    # Check for the yielded error message
    assert "Error: Docker command not found" in next(generator)

    # Check that the exception is raised when the generator is exhausted
    with pytest.raises(FileNotFoundError):
        list(generator)

@patch('src.docker_handler.dockerHandler.subprocess.run')
def test_is_docker_running_not_found(mock_run, docker_handler: DockerHandler):
    """Test is_docker_running when the docker command is not found."""
    # Configure the mock to simulate the command not being found
    mock_run.side_effect = FileNotFoundError

    assert docker_handler.is_docker_running() is False
    mock_run.assert_called_once()
