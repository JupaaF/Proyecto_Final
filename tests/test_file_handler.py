import pytest
from pathlib import Path
import sys
import os
import json
import builtins
from unittest.mock import mock_open

# Agregue la raíz del proyecto a sys.path para permitir importaciones desde src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.file_handler.file_handler import FileHandler
from src.file_handler.exceptions import TemplateError, FileHandlerError, ParameterError

# Plantilla mínima válida predeterminada para pruebas
VALID_TEMPLATE_CONTENT = json.dumps([
    {
        "id": "default",
        "name": "Default Template",
        "files": ["U", "controlDict", "fvSchemes", "fvSolution"]
    }
])


# Fixtures --------------------------

@pytest.fixture
def mock_templates_json(monkeypatch):
    """
    Fixture para simular condicionalmente la apertura de templates.json.
    Simula la apertura solo para templates.json y usa la apertura real para todos los demás archivos.
    """
    def _mock_template(content):
        # Cuando alguien intente leer del manejador de archivos (.read()), 
        # debe devolver el content que le pasamos 
        # (que sería el contenido simulado de nuestro templates.json).
        m_open = mock_open(read_data=content)

        # Guardamos una copia de la función open() 
        # real de Python en una variable.
        original_open = builtins.open

        # Esta es nuestra función "interceptora". 
        # Va a reemplazar temporalmente a open().
        def patched_open(file, mode='r', *args, **kwargs):
            if 'templates.json' in str(file):
                # no llama al open real, devuelve nuestro manejador de archivo falso (m_open)
                return m_open(file, mode, *args, **kwargs)
            return original_open(file, mode, *args, **kwargs)

        # Esta es la línea que activa el "parche".
        monkeypatch.setattr(builtins, 'open', patched_open)
    return _mock_template

@pytest.fixture
def file_handler(tmp_path: Path, mock_templates_json) -> FileHandler:
    """Accesorio para crear una instancia de FileHandler con un template predeterminada válida."""
    mock_templates_json(VALID_TEMPLATE_CONTENT)
    return FileHandler(tmp_path, template="default")


# Tests --------------------------

def test_file_handler_initialization(file_handler: FileHandler):
    """
    Comprueba que el FileHandler se inicializa correctamente, 
    creando el directorio del caso y el conjunto inicial de archivos del sistema.
    """
    case_path = file_handler.get_case_path()
    assert case_path.is_dir()
    
    assert (case_path / "system").is_dir()
    assert (case_path / "system" / "controlDict").is_file()
    assert (case_path / "system" / "fvSolution").is_file()
    assert (case_path / "system" / "fvSchemes").is_file()
    
    assert not (case_path / "0").exists()
    assert not (case_path / "constant").exists()

# Pruebas de condición de error para la inicialización
def test_init_raises_error_on_missing_template_file(tmp_path, monkeypatch):
    """
     Prueba que FileHandler genere TemplateError si no se encuentra templates.json.

    pytest automáticamente le proporciona dos "fixtures":
    tmp_path: Proporciona una ruta a un directorio temporal único para 
              este test, para que FileHandler tenga un lugar donde trabajar sin 
              afectar el sistema de archivos real.

    monkeypatch: Es la herramienta que nos permite modificar o "parchear" 
                 temporalmente el comportamiento del código para la prueba.
    '''
   """
    m = mock_open()

    # El atributo side_effect de un mock nos permite definir qué sucede 
    # cuando se le llama. Al asignarle FileNotFoundError, estamos diciendo: 
    # "Cuando cualquier código llame a la función que este mock reemplaza, 
    # no hagas nada más que lanzar inmediatamente una excepción FileNotFoundError".
    m.side_effect = FileNotFoundError

    # Aquí usamos monkeypatch para reemplazar la función open global 
    # de Python (que se encuentra en builtins) por nuestro mock (m). 
    # A partir de esta línea, y solo durante este test, cualquier llamada a open() en el código bajo prueba lanzará FileNotFoundError.
    monkeypatch.setattr(builtins, 'open', m)

    # Esperamos que lance una excepción de tipo TemplateError.
    # Además, con match="...", le pedimos que verifique que el mensaje de la excepción contenga el texto correcto.
    with pytest.raises(TemplateError, match="Archivo de configuración de template no encontrado"):
        FileHandler(tmp_path, template="default")
        """
        Intentamos crear una instancia de FileHandler. Internamente, el constructor de FileHandler llamará al método
        _get_template_config, que a su vez intentará hacer open('.../templates.json').
        Debido a nuestro parche/mock, esta llamada a open() no abrirá un archivo, sino que lanzará FileNotFoundError.
        El bloque try...except que escribimos dentro de _get_template_config está diseñado para capturar este FileNotFoundError y, 
        en respuesta, lanzar nuestra excepción personalizada: TemplateError("No se pudo decodificar JSON ...")."""

def test_init_raises_error_on_invalid_template_json(tmp_path, mock_templates_json):
    """Prueba que FileHandler genere TemplateError para JSON mal formado."""
    # Haces un mock con un "json" que no es válido (no le pasas VALID_TEMPLATE_CONTENT)
    mock_templates_json("esto no es un json válido")
    with pytest.raises(TemplateError, match="No se pudo decodificar JSON"):
        FileHandler(tmp_path, template="default")

def test_init_raises_error_on_missing_template_id(tmp_path, mock_templates_json):
    """Prueba que FileHandler genere TemplateError si no se encuentra el ID del template."""
    mock_templates_json(VALID_TEMPLATE_CONTENT)
    with pytest.raises(TemplateError, match="Template con id 'nonexistent' no encontrado"):
        FileHandler(tmp_path, template="nonexistent") #<-- acá le pasas un id no válido

def test_init_raises_error_on_unknown_file_in_template(tmp_path, mock_templates_json):
    """Prueba TemplateError cuando un archivo del template no está en FILE_CLASS_MAP."""
    # Creamos un json provisiorio con un archivo desconocido
    template_with_unknown_file = json.dumps([
        {"id": "default", "files": ["U", "controlDict", "fvSchemes", "fvSolution", "unknownFile"]}
    ])
    mock_templates_json(template_with_unknown_file)
    with pytest.raises(TemplateError, match="La clase para el archivo 'unknownFile' no se encuentra"):
        FileHandler(tmp_path, template="default")

def test_init_raises_error_on_missing_essential_files(tmp_path, mock_templates_json):
    """Prueba TemplateError si hay archivos esenciales que faltan en el template."""
    template_missing_essentials = json.dumps([
        {"id": "default", "files": ["U"]}
    ])
    mock_templates_json(template_missing_essentials)
    with pytest.raises(TemplateError, match="Al template le falta uno de los archivos esenciales"):
        FileHandler(tmp_path, template="default")

def test_create_base_dirs(file_handler: FileHandler):
    """Pruebe que _create_base_dirs cree los directorios requeridos."""
    case_path = file_handler.get_case_path()
    
    file_handler._create_base_dirs()
    
    assert (case_path / "0").is_dir()
    assert (case_path / "system").is_dir()
    assert (case_path / "constant").is_dir()


def test_create_case_files_creates_all_files_and_dirs(file_handler: FileHandler):
    """
    Comprueba que create_case_files crea todos los archivos OpenFOAM 
    definidos y la estructura completa del directorio.
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
    """Prueba que get_editable_parameters devuelva un diccionario no vacío para un archivo válido."""
    case_path = file_handler.get_case_path()
    u_file_path = case_path / "0" / "U"
    
    params = file_handler.get_editable_parameters(u_file_path)
    assert isinstance(params, dict)
    assert "internalField" in params
    assert "boundaryField" in params

def test_modify_parameters_updates_object_in_memory(file_handler: FileHandler):
    """Prueba que modify_parameters actualice los parámetros del objeto FoamFile."""
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
    """Prueba que write_files conserve los parámetros modificados en el disco."""
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
    
    # El formato exacto depende de la plantilla Jinja2. 
    # # Verificamos la presencia de los valores.
    assert "9 8 7" in file_content

def test_save_all_parameters_to_json(file_handler: FileHandler):
    """Prueba que los parámetros se guarden correctamente en un archivo JSON."""
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
    assert data["template"] == "default"
    assert "parameters" in data
    assert "U" in data["parameters"]
    assert data["parameters"]["U"]["internalField"] == new_internal_field

def test_load_all_parameters_from_json(file_handler: FileHandler):
    """Pruebe que los parámetros se carguen correctamente desde un archivo JSON."""
    case_path = file_handler.get_case_path()
    json_path = case_path / file_handler.JSON_PARAMS_FILE
    
    new_u_internal_field = {"x": 1.1, "y": 2.2, "z": 3.3}
    new_controlDict_startTime = 10
    
    test_data = {
        "template": "new_template_name",
        "parameters": {
            "U": {"internalField": new_u_internal_field},
            "controlDict": {"startTime": new_controlDict_startTime}
        }
    }
    with open(json_path, 'w') as f:
        json.dump(test_data, f)
        
    file_handler.load_all_parameters_from_json()
    
    assert file_handler.template == "new_template_name"
    
    u_file_obj = file_handler.files["U"]
    assert u_file_obj.internalField == new_u_internal_field
    
    controlDict_obj = file_handler.files["controlDict"]
    assert controlDict_obj.get_editable_parameters()['startTime']['current'] == new_controlDict_startTime

def test_load_all_parameters_from_json_raises_error_if_not_found(file_handler: FileHandler):
    """Comprueba que se genere FileHandlerError si el archivo JSON no existe."""
    with pytest.raises(FileHandlerError, match="Archivo JSON de parámetros no encontrado"):
        file_handler.load_all_parameters_from_json()

def test_load_from_malformed_json_raises_error(file_handler: FileHandler):
    """Comprueba que se genera FileHandlerError para un archivo JSON mal formado."""
    case_path = file_handler.get_case_path()
    json_path = case_path / file_handler.JSON_PARAMS_FILE
    json_path.write_text("{'this is not valid json',}")

    with pytest.raises(FileHandlerError, match="No se pudo decodificar JSON"):
        file_handler.load_all_parameters_from_json()

def test_load_from_json_with_invalid_params_raises_error(file_handler: FileHandler):
    """Comprueba que ParameterError se genere para parámetros no válidos en el JSON."""
    case_path = file_handler.get_case_path()
    json_path = case_path / file_handler.JSON_PARAMS_FILE

    test_data = {
        "template": "default",
        "parameters": {"U": {"internalField": "not-a-dict"}}
    }
    json_path.write_text(json.dumps(test_data))

    with pytest.raises(ParameterError, match="Parámetros inválidos para 'U'"):
        file_handler.load_all_parameters_from_json()

def test_write_files_permission_error(tmp_path, mock_templates_json, monkeypatch):
    """
    Test that FileHandlerError is raised on file write permission errors by mocking
    the 'open' call to raise PermissionError.
    """
    mock_templates_json(VALID_TEMPLATE_CONTENT)
    handler = FileHandler(tmp_path, template="default")

    m = mock_open()
    m.side_effect = PermissionError("Permission denied for test")
    monkeypatch.setattr(builtins, "open", m)

    with pytest.raises(FileHandlerError, match="Error al escribir archivo"):
        handler.write_files()

def test_modify_parameters_with_invalid_type_raises_error(file_handler: FileHandler):
    """
    Prueba que al modificar un parámetro con un tipo de dato no válido se genere ParameterError.
    """
    case_path = file_handler.get_case_path()
    u_file_obj = file_handler.files["U"]
    u_file_path = case_path / u_file_obj.folder / u_file_obj.name

    # Pass a string where a dictionary is expected
    new_params = {"internalField": "this-is-not-a-dict"}
    
    with pytest.raises(ParameterError, match="Parámetros proporcionados no válidos para U"):
        file_handler.modify_parameters(u_file_path, new_params)
