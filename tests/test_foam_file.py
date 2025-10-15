import pytest
from pathlib import Path
import sys
import os
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.file_handler.openfoam_models.foam_file import FoamFile

# A concrete implementation of the abstract FoamFile class for testing purposes
class ConcreteFoamFile(FoamFile):
    def _get_string(self) -> str:
        return "dummy content"

    def get_editable_parameters(self) -> dict:
        return {}

    def update_parameters(self, params: dict) -> None:
        pass

    def write_file(self, case_path: Path) -> None:
        pass

@pytest.fixture
def foam_file_instance():
    """Fixture to create an instance of the concrete FoamFile for testing."""
    return ConcreteFoamFile(name="testFile", folder="system", class_type="dictionary")

def test_get_header(foam_file_instance: ConcreteFoamFile):
    """Test that the get_header method generates a correct header."""
    header = foam_file_instance.get_header()
    assert "class       dictionary;" in header
    assert "object      testFile;" in header

def test_get_header_with_object_name(foam_file_instance: ConcreteFoamFile):
    """Test that the get_header method uses object_name when provided."""
    foam_file_instance.object_name = "customObject"
    header = foam_file_instance.get_header()
    assert "object      customObject;" in header

def test_get_header_location(foam_file_instance: ConcreteFoamFile):
    """Test that the get_header_location method generates a correct header with location."""
    header = foam_file_instance.get_header_location()
    assert 'location    "system";' in header
    assert "object      testFile;" in header

# Tests for the _validate method
def test_validate_vector_valid(foam_file_instance: ConcreteFoamFile):
    """Test vector validation with valid input."""
    foam_file_instance._validate({'x': 1, 'y': 2, 'z': 3}, "vector", {'label': 'position'})

def test_validate_vector_invalid_type(foam_file_instance: ConcreteFoamFile):
    """Test vector validation with wrong input type."""
    with pytest.raises(ValueError, match="no es un diccionario"):
        foam_file_instance._validate([1, 2, 3], "vector", {'label': 'position'})

def test_validate_vector_missing_component(foam_file_instance: ConcreteFoamFile):
    """Test vector validation with a missing component."""
    with pytest.raises(KeyError, match="Falta la componente 'x'"):
        foam_file_instance._validate({'y': 2, 'z': 3}, "vector", {'label': 'position'})

def test_validate_vector_invalid_component_type(foam_file_instance: ConcreteFoamFile):
    """Test vector validation with a non-numeric component."""
    with pytest.raises(ValueError, match="no es un numero"):
        foam_file_instance._validate({'x': 'a', 'y': 2, 'z': 3}, "vector", {'label': 'position'})

def test_validate_string_valid(foam_file_instance: ConcreteFoamFile):
    """Test string validation with valid input."""
    foam_file_instance._validate("hello", "string", {'label': 'greeting'})

def test_validate_string_invalid_type(foam_file_instance: ConcreteFoamFile):
    """Test string validation with non-string input."""
    with pytest.raises(ValueError, match="no es un string"):
        foam_file_instance._validate(123, "string", {'label': 'greeting'})

def test_validate_float_valid(foam_file_instance: ConcreteFoamFile):
    """Test float validation with valid input."""
    foam_file_instance._validate(1.23, "float", {'label': 'value'})
    foam_file_instance._validate(10, "float", {'label': 'value'}) # Also accepts ints

def test_validate_float_invalid_type(foam_file_instance: ConcreteFoamFile):
    """Test float validation with non-numeric input."""
    with pytest.raises(ValueError, match="no es un numero de punto flotante"):
        foam_file_instance._validate("abc", "float", {'label': 'value'})

def test_validate_int_valid(foam_file_instance: ConcreteFoamFile):
    """Test int validation with valid input."""
    foam_file_instance._validate(123, "int", {'label': 'count'})

def test_validate_int_invalid_type(foam_file_instance: ConcreteFoamFile):
    """Test int validation with non-integer input."""
    with pytest.raises(ValueError, match="no es un entero"):
        foam_file_instance._validate(1.23, "int", {'label': 'count'})

def test_validate_choice_valid(foam_file_instance: ConcreteFoamFile):
    """Test choice validation with a valid option."""
    props = {'label': 'mode', 'options': ['on', 'off']}
    foam_file_instance._validate("on", "choice", props)

def test_validate_choice_invalid_option(foam_file_instance: ConcreteFoamFile):
    """Test choice validation with an invalid option."""
    props = {'label': 'mode', 'options': ['on', 'off']}
    with pytest.raises(ValueError, match="no es una opcion valida"):
        foam_file_instance._validate("invalid", "choice", props)

def test_validate_choice_missing_options(foam_file_instance: ConcreteFoamFile):
    """Test choice validation when the options property is missing."""
    with pytest.raises(ValueError, match="Faltan las opciones"):
        foam_file_instance._validate("on", "choice", {'label': 'mode'})

def test_validate_choice_with_options_valid(foam_file_instance: ConcreteFoamFile):
    """Test choice_with_options validation with valid input."""
    props = {
        'label': 'solver',
        'options': [{
            'name': 'PCG',
            'parameters': [{'name': 'preconditioner', 'type': 'string'}]
        }]
    }
    foam_file_instance._validate(['PCG', {'preconditioner': 'DIC'}], "choice_with_options", props)

def test_validate_choice_with_options_invalid_structure(foam_file_instance: ConcreteFoamFile):
    """Test choice_with_options with incorrect list structure."""
    props = {'label': 'solver', 'options': []}
    with pytest.raises(ValueError, match="debe ser un diccionario"):
        foam_file_instance._validate(['PCG', 'DIC'], "choice_with_options", props)

def test_validate_patches_valid(foam_file_instance: ConcreteFoamFile):
    """Test patches validation with valid input."""
    props = {
        'label': 'boundary',
        'schema': {
            'type': {
                'options': [{'name': 'fixedValue', 'parameters': [{'name': 'value', 'type': 'vector'}]}]
            }
        }
    }
    patches = [{'patchName': 'inlet', 'type': 'fixedValue', 'value': {'x': 1, 'y': 0, 'z': 0}}]
    foam_file_instance._validate(patches, "patches", props)

def test_validate_patches_invalid_type(foam_file_instance: ConcreteFoamFile):
    """Test patches validation with a non-list input."""
    with pytest.raises(ValueError, match="no es una lista"):
        foam_file_instance._validate({}, "patches", {'label': 'boundary'})

def test_validate_patches_missing_patchname(foam_file_instance: ConcreteFoamFile):
    """Test patches validation with a patch missing its name."""
    props = {'label': 'boundary', 'schema': {'type': {'options': []}}}
    patches = [{'type': 'fixedValue'}]
    with pytest.raises(ValueError, match="Falta el nombre del patch"):
        foam_file_instance._validate(patches, "patches", props)

def test_validate_patches_invalid_patch_type(foam_file_instance: ConcreteFoamFile):
    """Test patches validation with an invalid patch type."""
    props = {
        'label': 'boundary',
        'schema': {
            'type': {'options': [{'name': 'zeroGradient'}]}
        }
    }
    patches = [{'patchName': 'outlet', 'type': 'invalidType'}]
    with pytest.raises(ValueError, match="no es valido para el patch"):
        foam_file_instance._validate(patches, "patches", props)