import pytest
import sys
import os

# Add project root to sys.path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all the models to be tested
from src.file_handler.openfoam_models.alpha import alpha
from src.file_handler.openfoam_models.g import g
from src.file_handler.openfoam_models.k import k
from src.file_handler.openfoam_models.nuTilda import nuTilda
from src.file_handler.openfoam_models.nut import nut
from src.file_handler.openfoam_models.epsilon import epsilon
from src.file_handler.openfoam_models.p_rgh import p_rgh
from src.file_handler.openfoam_models.setFieldsDict import setFieldsDict
from src.file_handler.openfoam_models.granularRheologyProperties import granularRheologyProperties
from src.file_handler.openfoam_models.filterProperties import filterProperties
from src.file_handler.openfoam_models.forceProperties import forceProperties
from src.file_handler.openfoam_models.interfacialProperties import interfacialProperties
from src.file_handler.openfoam_models.kineticTheoryProperties import kineticTheoryProperties
from src.file_handler.openfoam_models.twophaseRASProperties import twophaseRASProperties
from src.file_handler.openfoam_models.ppProperties import ppProperties
from src.file_handler.openfoam_models.p_rbgh import p_rbgh
from src.file_handler.openfoam_models.pa import pa
from src.file_handler.openfoam_models.s import s
from src.file_handler.openfoam_models.omega import omega
from src.file_handler.openfoam_models.Theta import Theta
from src.file_handler.openfoam_models.delta import delta
from src.file_handler.openfoam_models.alphaPlastic import alphaPlastic
from src.file_handler.openfoam_models.funkySetFieldsDict import funkySetFieldsDict
from src.file_handler.openfoam_models.decomposeParDict import decomposeParDict

# List of models to test with their expected name and folder
MODELS_TO_TEST = [
    (alpha, "alpha", "0"),
    (g, "g", "constant"),
    (k, "k", "0"),
    (nuTilda, "nuTilda", "0"),
    (nut, "nut", "0"),
    (epsilon, "epsilon", "0"),
    (p_rgh, "p_rgh", "0"),
    (setFieldsDict, "setFieldsDict", "system"),
    (granularRheologyProperties, "granularRheologyProperties", "constant"),
    (filterProperties, "filterProperties", "constant"),
    (forceProperties, "forceProperties", "constant"),
    (interfacialProperties, "interfacialProperties", "constant"),
    (kineticTheoryProperties, "kineticTheoryProperties", "constant"),
    (twophaseRASProperties, "twophaseRASProperties", "constant"),
    (ppProperties, "ppProperties", "constant"),
    (p_rbgh, "p_rbgh", "0"),
    (pa, "pa", "0"),
    (s, "s", "0"),
    (omega, "omega", "0"),
    (Theta, "Theta", "0"),
    (delta, "delta", "0"),
    (alphaPlastic, "alphaPlastic", "0"),
    (funkySetFieldsDict, "funkySetFieldsDict", "system"),
    (decomposeParDict, "decomposeParDict", "system"),
]

@pytest.mark.parametrize("model_class, expected_name, expected_folder", MODELS_TO_TEST)
def test_model_initialization_and_parameters(model_class, expected_name, expected_folder):
    """
    Tests that each OpenFOAM model class can be initialized correctly and that
    get_editable_parameters returns a non-empty dictionary.
    """
    # Test initialization
    instance = model_class()
    assert instance.name == expected_name
    assert instance.folder == expected_folder
    
    # Test get_editable_parameters
    params = instance.get_editable_parameters()
    assert isinstance(params, dict)
    assert len(params) > 0, f"Model {expected_name} has no editable parameters."
    
    # Test update_parameters with no params (should not fail)
    instance.update_parameters({})
    
    # Test update_parameters with a non-existent parameter (should not fail)
    instance.update_parameters({'non_existent_param': 'test'})