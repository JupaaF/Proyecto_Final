import json
import logging
from pathlib import Path
from typing import Dict, Any

from .exceptions import FileHandlerError, ParameterError, TemplateError
from .openfoam_models.foam_file import FoamFile
from .openfoam_models.U import U
from .openfoam_models.controlDict import controlDict
from .openfoam_models.fvSchemes import fvSchemes
from .openfoam_models.fvSolution import fvSolution
from .openfoam_models.alpha_water import alpha_water
from .openfoam_models.g import g
from .openfoam_models.k import k
from .openfoam_models.nut import nut
from .openfoam_models.epsilon import epsilon
from .openfoam_models.p_rgh import p_rgh
from .openfoam_models.setFieldsDict import setFieldsDict
from .openfoam_models.transportProperties import transportProperties
from .openfoam_models.turbulenceProperties import turbulenceProperties
from .openfoam_models.nuTilda import nuTilda
from .openfoam_models.s import s
from .openfoam_models.omega import omega

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Diccionario que mapea nombres de archivo a sus clases correspondientes
# Esto permite la instanciación dinámica de objetos a partir de los nombres en el JSON
FILE_CLASS_MAP = {
    "U": U,
    "controlDict": controlDict,
    "fvSchemes": fvSchemes,
    "fvSolution": fvSolution,
    "alpha.water": alpha_water,
    "g": g,
    "k": k,
    "nuTilda": nuTilda,
    "nut": nut,
    "epsilon": epsilon,
    "p_rgh": p_rgh,
    "setFieldsDict": setFieldsDict,
    "transportProperties": transportProperties,
    "turbulenceProperties": turbulenceProperties,
    "s": s,
    "omega": omega,
}

class FileHandler:
    """Maneja la creación, modificación y acceso a archivos de casos de OpenFOAM."""

    JSON_PARAMS_FILE = "parameters.json"
    
    def __init__(self, case_path: Path, template: str = None):
        """
        Inicializa el FileHandler para un caso dado.

        Args:
            case_path: Ruta absoluta al directorio del caso de simulación.
            template: Nombre de la plantilla a utilizar.

        Raises:
            TemplateError: Si el template no es válido o faltan archivos esenciales.
            FileHandlerError: Si hay un problema al escribir los archivos iniciales.
        """
        self.case_path = case_path
        self.template = template
        self.files: Dict[str, FoamFile] = {}
        
        try:
            self._initialize_file_objects()
        except TemplateError as e:
            logger.error(f"No se pudieron inicializar los objetos de archivo desde la plantilla: {e}")
            raise

        essential_files = ['controlDict', 'fvSolution', 'fvSchemes']
        if not all(f in self.files for f in essential_files):
            raise TemplateError(f"Al template le falta uno de los archivos esenciales: {', '.join(essential_files)}")
        
        try:
            for file_name in essential_files:
                self.files[file_name].write_file(self.case_path)
        except (FileNotFoundError, PermissionError) as e:
            raise FileHandlerError(f"No se pudieron escribir archivos esenciales durante la inicialización: {e}")

    def get_case_path(self) -> Path:
        """Devuelve la ruta raíz del directorio del caso."""
        return self.case_path

    def _get_template_config(self) -> Dict[str, Any]:
        """
        Carga la configuración del template desde el archivo JSON.
        Devuelve la configuración del template seleccionado.

        Raises:
            TemplateError: Si no se encuentra templates.json, está mal formado o falta el ID del template.
        """
        base_path = Path(__file__).parent
        json_path = base_path / "templates.json"

        try:
            with open(json_path, 'r') as f:
                templates = json.load(f)
        except FileNotFoundError:
            raise TemplateError(f"Archivo de configuración de template no encontrado en {json_path}")
        except json.JSONDecodeError:
            raise TemplateError(f"No se pudo decodificar JSON desde {json_path}")

        for t in templates:
            if t.get("id") == self.template:
                return t

        raise TemplateError(f"Template con id '{self.template}' no encontrado en templates.json")

    def _initialize_file_objects(self) -> None:
        """
        Inicializa los objetos FoamFile según el template seleccionado.
        Lee la configuración del template e instancia únicamente los archivos necesarios.

        Raises:
        TemplateError: Si no se encuentra un archivo de la plantilla en FILE_CLASS_MAP.
        """
        template_config = self._get_template_config()
        required_files = template_config.get("files", [])
        
        initialized_files = {}
        for file_name in required_files:
            if file_name in FILE_CLASS_MAP:
                foam_class = FILE_CLASS_MAP[file_name]
                initialized_files[file_name] = foam_class()
            else:
                raise TemplateError(f"La clase para el archivo '{file_name}' no se encuentra en FILE_CLASS_MAP.")

        self.files = initialized_files

    def create_case_files(self) -> None:
        """
        Crea la estructura básica de directorios y escribe todos los archivos OpenFOAM inicializados.
        Debe ejecutarse después de que el usuario confirme la configuración inicial.

        Raises:
        FileHandlerError: Si se produce un error durante la escritura del archivo.
        """
        self._create_base_dirs()
        try:
            for file_obj in self.files.values():  #TODO: habría que sacar este logger/print
                logger.info(f"Creando archivo {file_obj.name} en {file_obj.folder}")
                file_obj.write_file(self.case_path)
        except (FileNotFoundError, PermissionError) as e:
            raise FileHandlerError(f"No se pudo crear el archivo del caso: {e}")

    def _create_base_dirs(self) -> None:
        """Crea los directorios esenciales para un caso de OpenFOAM (0, system, constant)."""
        try:
            self.case_path.mkdir(exist_ok=True)
            for folder in ['0', 'system', 'constant']:
                (self.case_path / folder).mkdir(exist_ok=True)
        except PermissionError as e:
            raise FileHandlerError(f"No se pudieron crear los directorios base: {e}")

    def initialize_parameters_from_choice_with_options(self,param_props):
        options = param_props.get('options', [])
        if not options:
            return []

        default_option = options[0]
        default_option_name = default_option.get('name')
        
        # NOTE: ''solver_selected' está codificado en el código de UI original, por lo que replicamos esa suposición aquí.
        default_value = {}
        
        sub_params_schema = default_option.get('parameters', [])
        for sub_param in sub_params_schema:
            # Al inicializar, solo se añaden los parámetros que NO son opcionales.
            if not sub_param.get('optional'):
                if sub_param.get('type') == 'choice_with_options':
                    default_value[sub_param.get('name')] = self.initialize_parameters_from_choice_with_options(sub_param)
                elif 'default' in sub_param:
                    default_value[sub_param.get('name')] = sub_param.get('default')
        
        return [default_option_name, default_value]

    def initialize_parameters_from_schema(self, patch_names: list[str]):
        """
        Itera a través de todos los archivos foam y sus parámetros, inicializando 
        tipos complejos como 'patches' y 'choice_with_options' con valores 
        predeterminados basados en sus esquemas.
        """
        for foam_file in self.files.values():
            params_schema = foam_file.get_editable_parameters()
            
            new_params_to_update = {}

            for param_name, param_props in params_schema.items():
                param_type = param_props.get('type')
                current_value = param_props.get('current')

                # Inicializar los parámetros 'patches' si aún no están configurados
                if param_type == 'patches' and not current_value:
                    default_type = param_props.get('schema', {}).get('type', {}).get('default', 'empty')
                    type_options = param_props.get('schema', {}).get('type', {}).get('options', [])
                    option_schema_for_default = next((opt for opt in type_options if opt['name'] == default_type), None)

                    new_boundary_field = []
                    for patch_name in patch_names:
                        patch_data = {'patchName': patch_name, 'type': default_type}
                        
                        if option_schema_for_default and 'parameters' in option_schema_for_default:
                            for param in option_schema_for_default['parameters']:
                                if 'default' in param:
                                    patch_data[param['name']] = param['default']
                        new_boundary_field.append(patch_data)
                    
                    new_params_to_update[param_name] = new_boundary_field

                # Inicializar los parámetros 'choice_with_options' si aún no están configurados
                elif param_type == 'choice_with_options' and not current_value:
                    
                    new_params_to_update[param_name] = self.initialize_parameters_from_choice_with_options(param_props)

            if new_params_to_update:
                foam_file.update_parameters(new_params_to_update)

    def get_editable_parameters(self, file_path: Path) -> Dict[str, Any]:
        """
        Recupera los parámetros editables de un archivo determinado.

        Args:
        file_path: La ruta del archivo cuyos parámetros se solicitan.

        Returns:
        Un diccionario de parámetros editables o un diccionario vacío si no se encuentra el archivo.
        """
        file_name = file_path.name
        if file_name in self.files:
            return self.files[file_name].get_editable_parameters()
        return {}

    def modify_parameters(self, file_path: Path, new_params: Dict[str, Any]) -> None:
        """
        Modifica los parámetros de un archivo específico.

        Args:
        file_path: La ruta del archivo que se va a modificar.
        new_params: Un diccionario con los nuevos parámetros que se aplicarán.

        Raises:
        ParameterError: Si no se encuentra el archivo o los parámetros no son válidos.
        """
        file_name = file_path.name
        if file_name not in self.files:
            raise ParameterError(f"Archivo '{file_name}' no administrado por esta instancia de FileHandler.")

        try:
            file_obj = self.files[file_name]
            file_obj.update_parameters(new_params)
        except (KeyError, AttributeError, TypeError, ValueError) as e:
            logger.error(f"Parámetros invalidos para {file_name}: {e}")
            raise ParameterError(f"Parámetros proporcionados no válidos para {file_name}: {e}")

    def write_files(self):
        """
        Escribe todos los archivos administrados en el directorio del caso.

        Genera:
        FileHandlerError: Si se produce un error durante la escritura del archivo.
        """
        try:
            for _, file_obj in self.files.items():
                file_obj.write_file(self.case_path)
        except (FileNotFoundError, PermissionError) as e:
            raise FileHandlerError(f"Error al escribir archivo: {e}")

    def save_all_parameters_to_json(self) -> None:
        """
        Guarda todos los parámetros editables de todos los objetos FoamFile en un único archivo JSON.

        Genera:
        FileHandlerError: Si no se puede escribir en el archivo JSON.
        """
        all_params_values = {}
        for file_name, file_obj in self.files.items():
            editable_params = file_obj.get_editable_parameters()
            file_values = {param_name: props.get('current') for param_name, props in editable_params.items()}
            all_params_values[file_name] = file_values

        saved_data = {
            "template": self.template,
            "parameters": all_params_values
        }

        json_path = self.case_path / self.JSON_PARAMS_FILE
        try:
            with open(json_path, 'w') as f:
                json.dump(saved_data, f, indent=4)
        except (IOError, PermissionError) as e:
            raise FileHandlerError(f"No se pudieron guardar los parámetros en el archivo JSON en {json_path}: {e}")

    def load_all_parameters_from_json(self) -> None:
        """
        Carga todos los parámetros del archivo JSON y actualiza los objetos FoamFile correspondientes.

        Genera:
        FileHandlerError: Si el archivo JSON no se encuentra o no se puede analizar.
        ParameterError: Si los parámetros del JSON no son válidos.
        """
        json_path = self.case_path / self.JSON_PARAMS_FILE
        if not json_path.exists():
            raise FileHandlerError(f"Archivo JSON de parámetros no encontrado en {json_path}")

        try:
            with open(json_path, 'r') as f:
                saved_data = json.load(f)
        except json.JSONDecodeError:
            raise FileHandlerError(f"No se pudo decodificar JSON desde {json_path}")

        loaded_template = saved_data.get("template")
        if loaded_template and loaded_template != self.template:
            logger.warning(f"El template cargado '{loaded_template}' difiere del template inicial '{self.template}'.")
            self.template = loaded_template
            #Una implementación más robusta podría reinicializar los archivos acá

        loaded_params = saved_data.get("parameters", {})
        for file_name, params in loaded_params.items():
            if file_name in self.files:
                try:
                    self.files[file_name].update_parameters(params)
                except (KeyError, AttributeError, TypeError, ValueError) as e:
                    raise ParameterError(f"Parámetros inválidos para '{file_name}' en el archivo JSON: {e}")