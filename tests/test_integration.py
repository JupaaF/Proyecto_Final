import pytest
import json
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch, call
import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.file_handler.file_handler import FileHandler
from src.docker_handler.dockerHandler import DockerHandler
from src.file_handler.exceptions import FileHandlerError

# Helper to load the real templates.json to check validity of test data
def get_real_templates():
    base_path = Path(__file__).parent.parent / "src" / "file_handler"
    with open(base_path / "templates.json", "r") as f:
        return json.load(f)

class TestIntegration:

    @pytest.fixture
    def setup_case(self, tmp_path):
        """Setup a temporary case directory."""
        case_dir = tmp_path / "integration_case"
        case_dir.mkdir()
        return case_dir

    def test_full_case_lifecycle_damBreak(self, setup_case):
        """
        Integration Test:
        1. Initialize FileHandler with 'damBreak' template.
        2. Verify automatic parameter loading.
        3. Verify file creation.
        4. Modify a parameter (controlDict endTime).
        5. Save and Reload.
        6. Verify persistence.
        """
        # 1. Initialize & 2. Automatic Load
        # damBreak.json should be loaded automatically by __init__
        handler = FileHandler(setup_case, template="damBreak")

        # 3. Create Files
        handler.create_case_files()

        assert (setup_case / "0").exists()
        assert (setup_case / "system").exists()
        assert (setup_case / "constant").exists()
        assert (setup_case / "system" / "controlDict").exists()
        assert (setup_case / "0" / "U").exists()

        # Check content of controlDict (should have default endTime 1.0)
        control_dict_file = setup_case / "system" / "controlDict"
        content = control_dict_file.read_text()
        assert "endTime         1.0;" in content

        # 4. Modify Parameter
        cd_path = setup_case / "system" / "controlDict"
        handler.modify_parameters(cd_path, {"endTime": 5.0})

        # Write changes to disk
        handler.write_files()

        content_modified = control_dict_file.read_text()
        assert "endTime         5.0;" in content_modified

        # 5. Save state to JSON
        handler.save_all_parameters_to_json()
        saved_json_path = setup_case / "parameters.json"
        assert saved_json_path.exists()

        # 6. Reload from JSON (Simulate reopening the app)
        new_handler = FileHandler(setup_case, template="damBreak")
        new_handler.load_all_parameters_from_json(saved_json_path)

        # Verify the parameter is loaded correctly in memory
        # Note: We need to get params for controlDict.
        # Since we reloaded, the handler should have updated the object in memory.
        cd_path = setup_case / "system" / "controlDict"
        cd_params = new_handler.get_editable_parameters(cd_path)
        assert cd_params['endTime']['current'] == 5.0

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    def test_docker_simulation_workflow(self, mock_run, mock_popen, setup_case):
        """
        Integration Test: FileHandler -> Docker Execution (Mocked)
        Verifies that the DockerHandler correctly constructs the command based on the case.
        """
        # Setup Case
        handler = FileHandler(setup_case, template="damBreak")
        handler.create_case_files()

        # Initialize DockerHandler
        docker_handler = DockerHandler(case_path=setup_case)

        # Mock Popen context manager for execute_script_in_docker
        process_mock = MagicMock()
        process_mock.stdout.readline.side_effect = ["Starting simulation...", "Running...", ""]
        process_mock.wait.return_value = 0
        mock_popen.return_value = process_mock

        # Run a script (e.g., run_openfoam.sh)
        script_name = "run_openfoam.sh"
        generator = docker_handler.execute_script_in_docker(script_name, num_processors=4)

        # Consume the generator
        output = list(generator)

        assert "Starting simulation..." in output
        assert "Running..." in output

        # Verify Popen was called with correct arguments
        assert mock_popen.called
        args, kwargs = mock_popen.call_args

        # args[0] is the command list
        cmd_list = args[0]
        assert cmd_list[0] == "docker"
        assert cmd_list[1] == "run"

        # Check volume mount
        expected_vol = f"{setup_case.as_posix()}:/case"
        assert any(expected_vol in arg for arg in cmd_list)

        # Check script name in container
        assert f"/{script_name}" in cmd_list

        # Check num processors passed as argument
        assert cmd_list[-1] == "4"

    def test_templates_integrity(self):
        """
        Verify that all templates defined in templates.json have a corresponding
        parameters JSON file and can be initialized without crashing.
        """
        real_templates = get_real_templates()

        for tpl in real_templates:
            tpl_id = tpl['id']
            # Construct path to params
            param_file = Path(__file__).parent.parent / 'src' / 'file_handler' / 'templates_parameters' / (tpl_id + ".json")

            if not param_file.exists():
                pytest.fail(f"Missing parameters file for template: {tpl_id}")

            # Try to initialize (dry run)
            tmp_path = Path(f"/tmp/test_integrity_{tpl_id}_{os.getpid()}")
            if tmp_path.exists():
                shutil.rmtree(tmp_path)
            tmp_path.mkdir()

            try:
                # With auto-loading enabled, just initializing should trigger the load
                handler = FileHandler(tmp_path, template=tpl_id)

                # Ensure essential files are created in memory object
                assert len(handler.files) > 0, f"No files initialized for {tpl_id}"

                # Check create_case_files works
                handler.create_case_files()
                assert (tmp_path / "system").exists()

            except Exception as e:
                pytest.fail(f"Failed to initialize template {tpl_id}: {e}")
            finally:
                if tmp_path.exists():
                    shutil.rmtree(tmp_path)
