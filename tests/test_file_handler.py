import pytest
from pathlib import Path
import sys
import os
import json
import builtins
from unittest.mock import mock_open, patch

# Add project root to sys.path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.file_handler.file_handler import FileHandler
from src.file_handler.exceptions import TemplateError, FileHandlerError, ParameterError

# Default minimal valid template for tests
VALID_TEMPLATE_CONTENT = json.dumps([
    {
        "id": "default",
        "name": "Default Template",
        "files": ["U", "controlDict", "fvSchemes", "fvSolution", "transportProperties", "turbulenceProperties"]
    },
    {
        "id": "new_template_name",
        "name": "New Template",
        "files": ["U", "controlDict", "fvSchemes", "fvSolution"]
    }
])

@pytest.fixture
def mock_templates_json(monkeypatch):
    """
    Fixture to conditionally mock the opening of templates.json.
    It mocks 'open' only for 'templates.json' and uses the real 'open' for all other files.
    """
    def _mock_template(content):
        m_open = mock_open(read_data=content)
        original_open = builtins.open

        def patched_open(file, mode='r', *args, **kwargs):
            # Convert Path object to string for comparison
            if 'templates.json' in str(file):
                return m_open(file, mode, *args, **kwargs)
            return original_open(file, mode, *args, **kwargs)

        monkeypatch.setattr(builtins, 'open', patched_open)
    return _mock_template

@pytest.fixture
def file_handler(tmp_path: Path, mock_templates_json) -> FileHandler:
    """
    Fixture to create a FileHandler instance with a valid default template.
    We mock load_all_parameters_from_json to prevent it from trying to read
    default.json (which doesn't exist or shouldn't be read in unit tests).
    """
    mock_templates_json(VALID_TEMPLATE_CONTENT)

    # Patch the class method for the duration of the test using this fixture
    with patch('src.file_handler.file_handler.FileHandler.load_all_parameters_from_json') as mock_load:
        fh = FileHandler(tmp_path, template="default")
        # Ensure it was called (it's called in __init__)
        assert mock_load.called
        yield fh

def test_file_handler_initialization(file_handler: FileHandler):
    """
    Tests that the FileHandler initializes correctly, creating the case directory
    and the initial set of system files.
    """
    case_path = file_handler.get_case_path()
    assert case_path.is_dir()
    
    assert (case_path / "system").is_dir()
    assert (case_path / "system" / "controlDict").is_file()
    assert (case_path / "system" / "fvSolution").is_file()
    assert (case_path / "system" / "fvSchemes").is_file()
    
    assert not (case_path / "0").exists()
    assert not (case_path / "constant").exists()

# Error condition tests for initialization
def test_init_raises_error_on_missing_template_file(tmp_path, monkeypatch):
    """Test that FileHandler raises TemplateError if templates.json is not found."""
    m = mock_open()
    m.side_effect = FileNotFoundError
    monkeypatch.setattr(builtins, 'open', m)

    with pytest.raises(TemplateError, match="Template configuration file not found"):
        FileHandler(tmp_path, template="default")

def test_init_raises_error_on_invalid_template_json(tmp_path, mock_templates_json):
    """Test that FileHandler raises TemplateError for malformed JSON."""
    mock_templates_json("this is not valid json")
    with pytest.raises(TemplateError, match="Failed to decode JSON"):
        FileHandler(tmp_path, template="default")

def test_init_raises_error_on_missing_template_id(tmp_path, mock_templates_json):
    """Test that FileHandler raises TemplateError if the template ID is not found."""
    mock_templates_json(VALID_TEMPLATE_CONTENT)
    with pytest.raises(TemplateError, match="Template with id 'nonexistent' not found"):
        FileHandler(tmp_path, template="nonexistent")

def test_init_raises_error_on_unknown_file_in_template(tmp_path, mock_templates_json):
    """Test TemplateError when a file in the template is not in FILE_CLASS_MAP."""
    template_with_unknown_file = json.dumps([
        {"id": "default", "files": ["U", "controlDict", "fvSchemes", "fvSolution", "unknownFile"]}
    ])
    mock_templates_json(template_with_unknown_file)
    with pytest.raises(TemplateError, match="Class for file 'unknownFile' not found"):
        FileHandler(tmp_path, template="default")

def test_init_raises_error_on_missing_essential_files(tmp_path, mock_templates_json):
    """Test TemplateError if essential files are missing from the template."""
    template_missing_essentials = json.dumps([
        {"id": "default", "files": ["U"]}
    ])
    mock_templates_json(template_missing_essentials)

    # We must also mock load_all_parameters_from_json here because __init__ calls it before checking essentials?
    # No, __init__ calls _initialize_from_template which calls load_all...
    # Then __init__ checks essentials.
    # So if load_all fails, we get FileHandlerError, not TemplateError.
    with patch('src.file_handler.file_handler.FileHandler.load_all_parameters_from_json'):
        with pytest.raises(TemplateError, match="Template is missing one of the essential files"):
            FileHandler(tmp_path, template="default")

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
        "internalField": ['uniform', {'value': {'x': 1, 'y': 2, 'z': 3}}]
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

    new_internal_field = ['uniform', {'value': {'x': 9, 'y': 8, 'z': 7}}]
    new_params = {"internalField": new_internal_field}
    file_handler.modify_parameters(u_file_path, new_params)
    
    file_handler.write_files()
    
    assert u_file_path.is_file()
    file_content = u_file_path.read_text()
    assert "internalField   uniform (9 8 7);" in file_content

def test_save_all_parameters_to_json(file_handler: FileHandler):
    """Test that all parameters are saved to a JSON file correctly."""
    case_path = file_handler.get_case_path()
    json_path = case_path / file_handler.JSON_PARAMS_FILE

    # Modify a parameter to ensure non-default values are saved
    u_file_obj = file_handler.files["U"]
    new_internal_field = ['uniform', {'value': {'x': 5, 'y': 5, 'z': 5}}]
    u_file_path = case_path / u_file_obj.folder / u_file_obj.name
    file_handler.modify_parameters(u_file_path, {"internalField": new_internal_field})

    file_handler.save_all_parameters_to_json()

    assert json_path.is_file()

    with open(json_path, 'r') as f:
        data = json.load(f)

    assert "template" in data
    assert data["template"] == "default"
    assert "parameters" in data
    assert "U" in data["parameters"]
    assert data["parameters"]["U"]["internalField"] == new_internal_field

def test_load_all_parameters_from_json(tmp_path, mock_templates_json):
    """Test that parameters are loaded correctly from a JSON file."""
    mock_templates_json(VALID_TEMPLATE_CONTENT)

    # 1. Init without loading defaults (mocked)
    with patch('src.file_handler.file_handler.FileHandler.load_all_parameters_from_json'):
        handler = FileHandler(tmp_path, template="default")

    case_path = handler.get_case_path()
    json_path = case_path / handler.JSON_PARAMS_FILE
    
    new_u_internal_field = ['uniform', {'value': {'x': 1.1, 'y': 2.2, 'z': 3.3}}]
    new_controlDict_startTime = 10
    
    test_data = {
        "template": "new_template_name",
        "file_names": ["U", "controlDict", "fvSchemes", "fvSolution"],
        "parameters": {
            "U": {"internalField": new_u_internal_field},
            "controlDict": {"startTime": new_controlDict_startTime}
        }
    }
    with open(json_path, 'w') as f:
        json.dump(test_data, f)

    # We must patch the recursive calls inside load_all_parameters_from_json if they happen.
    # When template changes, it calls _initialize_from_template -> load_all_parameters_from_json(template_default_file)
    # We need to ensure THAT recursive call doesn't fail or doesn't mess up.
    # But wait, if we call load_all... manually, we want it to work.
    # The issue is the RECURSIVE call when template changes.
    # We should probably mock `_initialize_from_template` or just the internal call.

    # However, if we simply mock `load_all_parameters_from_json` again, we defeat the purpose of testing it.
    # The problem is that `new_template_name` is fake, so it has no `templates_parameters/new_template_name.json`.
    # So the recursive call WILL fail if unmocked.

    # Solution: We need to intercept the call where it tries to load the template defaults.
    # OR, we can just ensure that `load_all_parameters_from_json` handles the missing file gracefully? No, it raises.

    # Better Solution: Since we are testing logic, let's just create the fake default parameter file!
    # `src/file_handler/templates_parameters/new_template_name.json`
    # We can use `patch('pathlib.Path.exists')` maybe? Or just mock `open`?
    # Mocking `open` is already done by `mock_templates_json` but it passes through for non-templates.json.

    # Let's create the fake file in the real FS since the code uses `Path(__file__)`.
    # Actually, that's in `src/...`. We shouldn't write there in tests.

    # Let's use `pyfakefs`? No, not installed.
    # Let's mock `FileHandler._initialize_from_template` to NOT call `load_all...` but just do the other stuff.

    original_init_template = FileHandler._initialize_from_template

    def side_effect_init_template(self):
        # Do what original does but SKIP the load_all call
        template_config = self._get_template_config()
        self.file_names = template_config.get("files", [])
        self._initialize_from_names()
        # SKIP: self.load_all_parameters_from_json(...)
        
    with patch.object(FileHandler, '_initialize_from_template', side_effect=side_effect_init_template, autospec=True):
        handler.load_all_parameters_from_json()
    
    assert handler.template == "new_template_name"
    
    u_file_obj = handler.files["U"]
    assert u_file_obj.internalField == new_u_internal_field
    
    controlDict_obj = handler.files["controlDict"]
    assert controlDict_obj.get_editable_parameters()['startTime']['current'] == new_controlDict_startTime

def test_load_all_parameters_from_json_raises_error_if_not_found(tmp_path, mock_templates_json):
    """Test that FileHandlerError is raised if the JSON file doesn't exist."""
    mock_templates_json(VALID_TEMPLATE_CONTENT)
    with patch('src.file_handler.file_handler.FileHandler.load_all_parameters_from_json'):
        handler = FileHandler(tmp_path, template="default")

    with pytest.raises(FileHandlerError, match="Parameters JSON file not found"):
        handler.load_all_parameters_from_json()

def test_load_from_malformed_json_raises_error(tmp_path, mock_templates_json):
    """Test that FileHandlerError is raised for a malformed JSON file."""
    mock_templates_json(VALID_TEMPLATE_CONTENT)
    with patch('src.file_handler.file_handler.FileHandler.load_all_parameters_from_json'):
        handler = FileHandler(tmp_path, template="default")

    case_path = handler.get_case_path()
    json_path = case_path / handler.JSON_PARAMS_FILE
    json_path.write_text("{'this is not valid json',}")

    with pytest.raises(FileHandlerError, match="Failed to decode JSON"):
        handler.load_all_parameters_from_json()

def test_load_from_json_with_invalid_params_raises_error(tmp_path, mock_templates_json):
    """Test that ParameterError is raised for invalid parameters in the JSON."""
    mock_templates_json(VALID_TEMPLATE_CONTENT)
    with patch('src.file_handler.file_handler.FileHandler.load_all_parameters_from_json'):
        handler = FileHandler(tmp_path, template="default")

    case_path = handler.get_case_path()
    json_path = case_path / handler.JSON_PARAMS_FILE

    test_data = {
        "template": "default",
        "parameters": {"U": {"internalField": "not-a-valid-structure"}}
    }
    json_path.write_text(json.dumps(test_data))

    with pytest.raises(ParameterError, match="Invalid parameters for 'U'"):
        handler.load_all_parameters_from_json()

def test_write_files_permission_error(tmp_path, mock_templates_json, monkeypatch):
    """
    Test that FileHandlerError is raised on file write permission errors by mocking
    the 'open' call to raise PermissionError.
    """
    mock_templates_json(VALID_TEMPLATE_CONTENT)

    # We need to successfully init first, so we mock the init loader
    with patch('src.file_handler.file_handler.FileHandler.load_all_parameters_from_json'):
        handler = FileHandler(tmp_path, template="default")

    # 2. Now, patch builtins.open to raise PermissionError for the next call.
    m = mock_open()
    m.side_effect = PermissionError("Permission denied for test")
    monkeypatch.setattr(builtins, "open", m)

    # 3. Call write_files and assert that it raises the correct wrapped error.
    with pytest.raises(FileHandlerError, match="Failed to write file"):
        handler.write_files()

def test_modify_parameters_with_invalid_type_raises_error(file_handler: FileHandler):
    """
    Test that modifying a parameter with an invalid data type raises ParameterError.
    """
    case_path = file_handler.get_case_path()
    u_file_obj = file_handler.files["U"]
    u_file_path = case_path / u_file_obj.folder / u_file_obj.name

    # Pass a string where a list is expected for 'internalField'
    new_params = {"internalField": "this-is-not-a-list"}
    
    with pytest.raises(ParameterError, match="Invalid parameters provided for U"):
        file_handler.modify_parameters(u_file_path, new_params)

def test_initialize_parameters_from_schema(file_handler: FileHandler):
    """Test that initialize_parameters_from_schema correctly sets default values."""
    patch_names = ["inlet", "outlet", "walls"]
    file_handler.initialize_parameters_from_schema(patch_names)
    
    u_params = file_handler.files['U'].get_editable_parameters()
    
    # Check boundaryField initialization
    boundary_field = u_params['boundaryField']['current']
    assert len(boundary_field) == 3
    assert boundary_field[0]['patchName'] == 'inlet'
    assert boundary_field[0]['type'] == 'noSlip'

    # Check internalField initialization
    internal_field = u_params['internalField']['current']
    assert internal_field[0] == 'uniform'
    assert 'value' in internal_field[1]

def test_get_solver_and_processors(file_handler: FileHandler):
    """Test that get_solver and get_number_of_processors return correct values from JSON."""
    case_path = file_handler.get_case_path()
    json_path = case_path / file_handler.JSON_PARAMS_FILE

    test_data = {
        "parameters": {
            "controlDict": {"application": "icoFoam"},
            "decomposeParDict": {"numberOfSubdomains": 8}
        }
    }
    json_path.write_text(json.dumps(test_data))

    solver = file_handler.get_solver()
    num_processors = file_handler.get_number_of_processors()

    assert solver == "icoFoam"
    assert num_processors == 8