import pytest
from pathlib import Path
import sys
import os

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
