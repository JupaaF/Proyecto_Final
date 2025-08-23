import pytest
from pathlib import Path
import sys
import os
import tempfile
import shutil

# Add project root to sys.path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.file_handler.openfoam_models.U import U

@pytest.fixture
def u_instance() -> U:
    """Fixture to create a U instance."""
    return U()

def test_initialization(u_instance: U):
    """Test that the U object is initialized with default values."""
    assert u_instance.name == "U"
    assert u_instance.folder == "0"
    assert u_instance.class_type == "volVectorField"
    assert u_instance.internalField == {'x': 0, 'y': 0, 'z': 0}
    assert u_instance.boundaryField == []

def test_update_parameters_vector_valor_invalido(u_instance: U):
    """Test updating parameters."""
    params = {
        'internalField': {'x':'g', 'y': 2, 'z': 3},
        'boundaryField': []
    }
    with pytest.raises(ValueError,match="Valor invalido"):
        u_instance.update_parameters(params)

def test_update_parameters_vector_valor_faltante(u_instance: U):
    """Test updating parameters."""
    params = {
        'internalField': {'y': 2, 'z': 3},
        'boundaryField': []
    }
    with pytest.raises(KeyError,match="Falta x"):
        u_instance.update_parameters(params)

def test_update_parameters_patch_invalido(u_instance: U):
    """Test updating parameters."""
    params = {
        'internalField': {'x':1, 'y': 2, 'z': 3},
        'boundaryField': {}
    }
    with pytest.raises(ValueError,match="Valor invalido"):
        u_instance.update_parameters(params)

def test_update_parameters_patch_playground(u_instance: U):
    """Test updating parameters."""
    params = {
        'internalField': {'x':1, 'y': 2, 'z': 3},
        'boundaryField': [
            {
                'patchName' : 'asa',
                'type' : 'pressureInletOutletVelocity',
                'value' : {
                    'x': 1,
                    'y': 2,
                    'z': 'g'
                }
            }
        ]
    }
    with pytest.raises(ValueError,match="Valor invalido"):
        u_instance.update_parameters(params)


def test_update_parameters_successful(u_instance: U):
    """Test a successful parameter update."""
    params = {
        'internalField': {'x': 1.1, 'y': 2.2, 'z': 3.3},
        'boundaryField': [
            {'patchName': 'inlet', 'type': 'pressureInletOutletVelocity', 'value': {'x': 5, 'y': 0, 'z': 0}},
            {'patchName': 'outlet', 'type': 'noSlip'}
        ]
    }
    u_instance.update_parameters(params)
    assert u_instance.internalField == params['internalField']
    assert u_instance.boundaryField == params['boundaryField']


def test_update_parameters_non_existent(u_instance: U):
    """Test updating with a parameter that does not exist in the class."""
    params = {
        'internalField': {'x': 1, 'y': 2, 'z': 3},
        'boundaryField': [],
        'non_existent_param': 'should_be_ignored'
    }
    u_instance.update_parameters(params)
    assert u_instance.internalField == {'x': 1, 'y': 2, 'z': 3}
    assert u_instance.boundaryField == []
    assert not hasattr(u_instance, 'non_existent_param')


def test_write_file_success(u_instance: U):
    """Test that the U file is written correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        case_path = Path(tmpdir)
        u_instance.write_file(case_path)
        
        file_path = case_path / u_instance.folder / u_instance.name
        assert file_path.exists()
        
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Check for header
        assert "FoamFile" in content
        assert "class       volVectorField;" in content
        assert "object      U;" in content
        
        # Check for content
        assert "internalField   uniform (0 0 0);" in content
        assert "boundaryField" in content
        assert "{" in content
        assert "}" in content


def test_write_file_with_updated_params(u_instance: U):
    """Test that the U file is written correctly after updating parameters."""
    params = {
        'internalField': {'x': 1.5, 'y': 2.5, 'z': 3.5},
        'boundaryField': [
            {'patchName': 'walls', 'type': 'noSlip'}
        ]
    }
    u_instance.update_parameters(params)

    with tempfile.TemporaryDirectory() as tmpdir:
        case_path = Path(tmpdir)
        u_instance.write_file(case_path)
        
        file_path = case_path / u_instance.folder / u_instance.name
        assert file_path.exists()
        
        with open(file_path, 'r') as f:
            content = f.read()
            
        assert "internalField   uniform (1.5 2.5 3.5);" in content
        assert "walls" in content
        assert "type            noSlip;" in content


def test_write_file_no_directory(u_instance: U):
    """Test that write_file raises FileNotFoundError for a non-existent path."""
    non_existent_path = Path("non_existent_case_for_sure")
    
    if non_existent_path.exists():
        shutil.rmtree(non_existent_path)
        
    with pytest.raises(FileNotFoundError):
        u_instance.write_file(non_existent_path)


## TEST UPDATE PARAMETERS QUE NO EXISTEN

def test_get_editable_parameters(u_instance: U):
    """Test that get_editable_parameters returns the correct structure."""
    params = u_instance.get_editable_parameters()
    
    assert "internalField" in params
    assert params['internalField']['label'] == 'Campo Interno (Velocidad)'
    assert params['internalField']['type'] == 'vector'
    assert params['internalField']['current'] == {'x': 0, 'y': 0, 'z': 0}
    
    assert "boundaryField" in params
    assert params['boundaryField']['label'] == 'Condiciones de Borde'
    assert params['boundaryField']['type'] == 'patches'
    assert params['boundaryField']['current'] == []

def test_get_editable_parameters_after_update(u_instance: U):
    """Test get_editable_parameters reflects updated values."""
    new_params = {
        'internalField': {'x': 10, 'y': 20, 'z': 30},
        'boundaryField': [{'patchName': 'test', 'type': 'noSlip'}]
    }
    u_instance.update_parameters(new_params)
    
    editable_params = u_instance.get_editable_parameters()
    
    assert editable_params['internalField']['current'] == new_params['internalField']
    assert editable_params['boundaryField']['current'] == new_params['boundaryField']
