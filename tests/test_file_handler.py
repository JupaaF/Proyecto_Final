import pytest
from pathlib import Path
import sys
import os

# Add project root to sys.path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.file_handler.file_handler import FileHandler

@pytest.fixture
def file_handler(tmp_path: Path) -> FileHandler:
    """Fixture to create a FileHandler instance in a temporary directory."""
    return FileHandler(tmp_path)


def test_file_handler_initialization(file_handler: FileHandler):
    """
    Tests that the FileHandler initializes correctly, creating the case directory
    and the initial set of system files.
    """
    case_path = file_handler.get_case_path()
    assert case_path.is_dir()
    
    # The constructor writes three files, which should create the 'system' directory.
    assert (case_path / "system").is_dir()
    assert (case_path / "system" / "controlDict").is_file()
    assert (case_path / "system" / "fvSolution").is_file()
    assert (case_path / "system" / "fvSchemes").is_file()
    
    # It should NOT create the '0' or 'constant' directories on initialization.
    assert not (case_path / "0").exists()
    assert not (case_path / "constant").exists()


def test_create_base_dirs(file_handler: FileHandler):
    """Test that _create_base_dirs creates the required directories."""
    case_path = file_handler.get_case_path()
    
    file_handler._create_base_dirs()
    
    assert (case_path / "0").is_dir()
    assert (case_path / "system").is_dir()
    assert (case_path / "constant").is_dir()


def test_create_case_files_creates_all_files_and_dirs(file_handler: FileHandler):
    """
    Test that create_case_files creates all defined OpenFOAM files
    and the complete directory structure.
    """
    case_path = file_handler.get_case_path()
    
    file_handler.create_case_files()

    assert (case_path / "0").is_dir()
    assert (case_path / "system").is_dir()
    assert (case_path / "constant").is_dir()

    for file_obj in file_handler.files.values():
        # Corrected attribute from .location to .folder
        expected_path = case_path / file_obj.folder / file_obj.name
        assert expected_path.is_file(), f"File '{expected_path}' was not created."


def test_get_editable_parameters(file_handler: FileHandler):
    """Test that get_editable_parameters returns a non-empty dict for a valid file."""
    case_path = file_handler.get_case_path()
    u_file_path = case_path / "0" / "U"
    
    params = file_handler.get_editable_parameters(u_file_path)
    assert isinstance(params, dict)
    assert "internalField" in params
    assert "boundaryField" in params

def test_modify_parameters_updates_object_in_memory(file_handler: FileHandler):
    """Test that modify_parameters updates the parameters of the FoamFile object."""
    u_file_name = "U"
    u_file_obj = file_handler.files[u_file_name]

    original_value = u_file_obj.get_editable_parameters()['internalField']['current']
    
    new_params = {
        "internalField": {"x": 1, "y": 2, "z": 3}
    }
    
    u_file_path = file_handler.get_case_path() / u_file_obj.folder / u_file_obj.name
    file_handler.modify_parameters(u_file_path, new_params)
    
    updated_value = u_file_obj.get_editable_parameters()['internalField']['current']
    assert updated_value != original_value
    assert updated_value == new_params["internalField"]

def test_write_files_after_modification(file_handler: FileHandler):
    """Test that write_files persists modified parameters to disk."""
    case_path = file_handler.get_case_path()
    u_file_name = "U"
    u_file_obj = file_handler.files[u_file_name]
    u_file_path = case_path / u_file_obj.folder / u_file_obj.name

    new_internal_field = {"x": 9, "y": 8, "z": 7}
    new_params = {"internalField": new_internal_field}
    file_handler.modify_parameters(u_file_path, new_params)
    
    file_handler.write_files()
    
    assert u_file_path.is_file()
    file_content = u_file_path.read_text()
    
    # The exact format depends on the Jinja2 template. 
    # Let's check for the presence of the values.
    assert "9 8 7" in file_content


import json

def test_save_all_parameters_to_json(file_handler: FileHandler):
    """Test that all parameters are saved to a JSON file correctly."""
    case_path = file_handler.get_case_path()
    json_path = case_path / file_handler.JSON_PARAMS_FILE

    # Modify a parameter to ensure non-default values are saved
    u_file_obj = file_handler.files["U"]
    new_internal_field = {"x": 5, "y": 5, "z": 5}
    u_file_path = case_path / u_file_obj.folder / u_file_obj.name
    file_handler.modify_parameters(u_file_path, {"internalField": new_internal_field})

    file_handler.save_all_parameters_to_json()

    assert json_path.is_file()

    with open(json_path, 'r') as f:
        data = json.load(f)

    assert "template" in data
    assert "parameters" in data
    assert "U" in data["parameters"]
    assert data["parameters"]["U"]["internalField"] == new_internal_field

def test_load_all_parameters_from_json(file_handler: FileHandler):
    """Test that parameters are loaded correctly from a JSON file."""
    case_path = file_handler.get_case_path()
    json_path = case_path / file_handler.JSON_PARAMS_FILE
    
    # Prepare a JSON file with known parameters
    new_u_internal_field = {"x": 1.1, "y": 2.2, "z": 3.3}
    new_controlDict_startTime = 10
    
    test_data = {
        "template": "test_template",
        "parameters": {
            "U": {
                "internalField": new_u_internal_field
            },
            "controlDict": {
                "startTime": new_controlDict_startTime
            }
        }
    }
    with open(json_path, 'w') as f:
        json.dump(test_data, f)
        
    file_handler.load_all_parameters_from_json()
    
    assert file_handler.template == "test_template"
    
    u_file_obj = file_handler.files["U"]
    assert u_file_obj.internalField == new_u_internal_field
    
    controlDict_obj = file_handler.files["controlDict"]
    assert controlDict_obj.get_editable_parameters()['startTime']['current'] == new_controlDict_startTime


def test_load_from_malformed_json(file_handler: FileHandler, capsys):
    """Test graceful handling of a malformed JSON file."""
    case_path = file_handler.get_case_path()
    json_path = case_path / file_handler.JSON_PARAMS_FILE

    original_internal_field = file_handler.files["U"].internalField

    with open(json_path, 'w') as f:
        f.write("{'this is not valid json',}")

    file_handler.load_all_parameters_from_json()

    # Check that an error was printed to stderr (or stdout)
    captured = capsys.readouterr()
    assert "Error: Could not decode JSON" in captured.out

    # Verify that the parameters have not changed
    assert file_handler.files["U"].internalField == original_internal_field

def test_load_from_json_with_mismatched_params(file_handler: FileHandler):
    """Test handling of JSON with extra or missing parameters."""
    case_path = file_handler.get_case_path()
    json_path = case_path / file_handler.JSON_PARAMS_FILE

    original_u_internal_field = file_handler.files["U"].internalField
    original_controlDict_startTime = file_handler.files["controlDict"].get_editable_parameters()['startTime']['current']

    test_data = {
        "parameters": {
            "U": {
                "some_extra_param": "should_be_ignored"
            },
            "nonExistentFile": {
                "some_param": "should_be_ignored"
            }
        }
    }
    with open(json_path, 'w') as f:
        json.dump(test_data, f)

    file_handler.load_all_parameters_from_json()

    assert file_handler.files["U"].internalField == original_u_internal_field
    assert file_handler.files["controlDict"].get_editable_parameters()['startTime']['current'] == original_controlDict_startTime


from jinja2.exceptions import UndefinedError

def test_write_files_permission_error(file_handler: FileHandler, capsys):
    """Test graceful handling of file write permission errors."""
    case_path = file_handler.get_case_path()
    
    # Create a subdirectory to make read-only, to avoid affecting the case_path itself
    # which pytest might need to clean up.
    read_only_dir = case_path / "system"
    read_only_dir.mkdir(exist_ok=True)
    
    # Make the directory read-only
    os.chmod(read_only_dir, 0o555)
    
    # This should now be handled gracefully by write_files
    file_handler.write_files()
    
    # Set permissions back to writable so the fixture cleanup doesn't fail
    os.chmod(read_only_dir, 0o755)

    captured = capsys.readouterr()
    assert "Permission denied" in captured.out

def test_modify_parameters_with_invalid_type_and_write(file_handler: FileHandler):
    """
    Test the behavior of writing a file after modifying a parameter with an invalid data type.
    This test documents the current behavior, where Jinja2 fails silently on undefined
    attributes, producing a potentially invalid output file.
    """
    case_path = file_handler.get_case_path()
    u_file_obj = file_handler.files["U"]
    u_file_path = case_path / u_file_obj.folder / u_file_obj.name

    # Pass a string where a dictionary is expected
    new_params = {"internalField": "this-is-not-a-dict"}
    file_handler.modify_parameters(u_file_path, new_params)

    file_handler.write_files()

    written_content = u_file_path.read_text()
    
    # The actual behavior is that Jinja2 silently ignores the missing attributes (x, y, z)
    # on the string object, resulting in an empty vector in the output.
    assert "uniform (  )" in written_content
