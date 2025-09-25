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
from .openfoam_models.alpha import alpha
from .openfoam_models.g import g
from .openfoam_models.k import k
from .openfoam_models.nut import nut
from .openfoam_models.epsilon import epsilon
from .openfoam_models.p_rgh import p_rgh
from .openfoam_models.setFieldsDict import setFieldsDict
from .openfoam_models.transportProperties import transportProperties
from .openfoam_models.turbulenceProperties import turbulenceProperties
from .openfoam_models.granularRheologyProperties import granularRheologyProperties
from .openfoam_models.filterProperties import filterProperties
from .openfoam_models.forceProperties import forceProperties
from .openfoam_models.interfacialProperties import interfacialProperties
from .openfoam_models.kineticTheoryProperties import kineticTheoryProperties
from .openfoam_models.twophaseRASProperties import twophaseRASProperties
from .openfoam_models.ppProperties import ppProperties
from .openfoam_models.pa import pa
from .openfoam_models.p_rbgh import p_rbgh
from .openfoam_models.nuTilda import nuTilda
from .openfoam_models.s import s
from .openfoam_models.omega import omega
from .openfoam_models.Theta import Theta
from .openfoam_models.delta import delta
from .openfoam_models.alphaPlastic import alphaPlastic
from .openfoam_models.funkySetFieldsDict import funkySetFieldsDict
from .openfoam_models.decomposeParDict import decomposeParDict

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
    "alpha": alpha,
    "g": g,
    "k": k,
    "nuTilda": nuTilda,
    "nut": nut,
    "epsilon": epsilon,
    "p_rgh": p_rgh,
    "setFieldsDict": setFieldsDict,
    "transportProperties": transportProperties,
    "turbulenceProperties": turbulenceProperties,
    "granularRheologyProperties": granularRheologyProperties,
    "filterProperties": filterProperties,
    "forceProperties": forceProperties,
    "interfacialProperties": interfacialProperties,
    "kineticTheoryProperties": kineticTheoryProperties,
    "twophaseRASProperties": twophaseRASProperties,
    "ppProperties": ppProperties,
    "p_rbgh": p_rbgh,
    "pa": pa,
    "s": s,
    "omega": omega,
    "Theta": Theta,
    "delta": delta,
    "alphaPlastic": alphaPlastic,
    "funkySetFieldsDict": funkySetFieldsDict,
    "decomposeParDict": decomposeParDict
}

class FileHandler:
    """Manages the creation, modification, and access of OpenFOAM case files."""


    JSON_PARAMS_FILE = "parameters.json"
    
    def __init__(self, case_path: Path, template: str = None, file_names: list = None):
        """
        Initializes the FileHandler for a given case.

        Args:
            case_path: The absolute path to the simulation case directory.
            template: The name of the template to use.
            file_names: A list of file names to initialize.

        Raises:
            ValueError: If both or neither template and file_names are provided.
            TemplateError: If the template is invalid or essential files are missing.
            FileHandlerError: If there's an issue writing initial files.
        """
        self.case_path = case_path
        self.template = template
        self.file_names = file_names
        self.files: Dict[str, FoamFile] = {}

        if template and file_names:
            raise ValueError("Provide either a template or a list of file names, not both.")
        
        if not template and not file_names:
            raise ValueError("Provide either a template or a list of file names.")

        try:
            if template:
                self._initialize_from_template()
            elif file_names:
                self._initialize_from_names()
        except (TemplateError, FileHandlerError) as e:
            logger.error(f"Failed to initialize file objects: {e}")
            raise

        essential_files = ['controlDict', 'fvSolution', 'fvSchemes']
        if not all(f in self.files for f in essential_files):
            raise TemplateError(f"Template is missing one of the essential files: {', '.join(essential_files)}")
        
        try:
            for file_name in essential_files:
                self.files[file_name].write_file(self.case_path)
        except (FileNotFoundError, PermissionError) as e:
            raise FileHandlerError(f"Failed to write essential files on initialization: {e}")

    def get_case_path(self) -> Path:
        """Returns the root path of the case directory."""
        return self.case_path
    
    def get_template(self) -> str :
        """Returns the template name."""
        return self.template
    
    def _get_template_config(self) -> Dict[str, Any]:
        """
        Loads the template configuration from the JSON file.
        Returns the configuration for the selected template.

        Raises:
            TemplateError: If templates.json is not found, malformed, or the template ID is missing.
        """
        base_path = Path(__file__).parent
        json_path = base_path / "templates.json"

        try:
            with open(json_path, 'r') as f:
                templates = json.load(f)
        except FileNotFoundError:
            raise TemplateError(f"Template configuration file not found at {json_path}")
        except json.JSONDecodeError:
            raise TemplateError(f"Failed to decode JSON from {json_path}")

        for t in templates:
            if t.get("id") == self.template:
                return t

        raise TemplateError(f"Template with id '{self.template}' not found in templates.json")

    def _initialize_from_template(self) -> None:
        """
        Initializes the FoamFile objects based on the selected template.
        It reads the template configuration and instantiates only the required files.

        Raises:
            TemplateError: If a file in the template is not found in FILE_CLASS_MAP.
        """
        template_config = self._get_template_config()
        self.file_names = template_config.get("files", [])
        self._initialize_from_names()
        # self.load_all_parameters_from_json(Path(__file__).parent / 'templates_parameters' / (self.template + '.json')) ##COMENTA ESTA LINEA ANTES DE EMPEZAR A CONFIGURAR LOS VALORES POR DEFECTO

    def _initialize_from_names(self) -> None:
        """
        Initializes the FoamFile objects from a list of file names.
        It instantiates the required files with their default values.

        Raises:
            TemplateError: If a file in the list is not found in FILE_CLASS_MAP.
        """
        initialized_files = {}
        for file_name in self.file_names:
            second_part = None
            parts_of_file_name = file_name.split('.')
            file_name_aux = file_name
            if len(parts_of_file_name) > 1:
                file_name = parts_of_file_name[0]
                second_part = parts_of_file_name[1]

            if file_name in FILE_CLASS_MAP:
                foam_class = FILE_CLASS_MAP[file_name]
                if second_part is not None:
                    initialized_files[file_name_aux] = foam_class(second_part)
                else:
                    initialized_files[file_name] = foam_class()
            else:
                raise TemplateError(f"Class for file '{file_name}' not found in FILE_CLASS_MAP.")
        
        self.files = initialized_files

    def create_case_files(self) -> None:
        """
        Creates the basic directory structure and writes all initialized OpenFOAM files.
        This should be called after the user confirms the initial setup.

        Raises:
            FileHandlerError: If an error occurs during file writing.
        """
        self._create_base_dirs()
        try:
            for file_obj in self.files.values():
                logger.info(f"Creating file {file_obj.name} in {file_obj.folder}")
                file_obj.write_file(self.case_path)
        except (FileNotFoundError, PermissionError) as e:
            raise FileHandlerError(f"Failed to create case file: {e}")

    def _create_base_dirs(self) -> None:
        """Creates the essential directories for an OpenFOAM case (0, system, constant)."""
        try:
            self.case_path.mkdir(exist_ok=True)
            for folder in ['0', 'system', 'constant']:
                (self.case_path / folder).mkdir(exist_ok=True)
        except PermissionError as e:
            raise FileHandlerError(f"Could not create base directories: {e}")

    def initialize_parameters_from_choice_with_options(self,param_props):
        options = param_props.get('options', [])
        if not options:
            return []

        default_option = options[0]
        default_option_name = default_option.get('name')
        
        # NOTE: 'solver_selected' is hardcoded in the original UI code, so we replicate that assumption here.
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
        Iterates through all foam files and their parameters, initializing complex
        types like 'patches' and 'choice_with_options' with default values based
        on their schemas.
        """
        for foam_file in self.files.values():
            params_schema = foam_file.get_editable_parameters()
            
            new_params_to_update = {}

            for param_name, param_props in params_schema.items():
                param_type = param_props.get('type')
                current_value = param_props.get('current')

                # Initialize 'patches' parameters if they are not already set
                if param_type == 'patches' and not current_value:
                    default_type = param_props.get('schema', {}).get('type', {}).get('default', 'empty')
                    type_options = param_props.get('schema', {}).get('type', {}).get('options', [])
                    option_schema_for_default = next((opt for opt in type_options if opt['name'] == default_type), None)

                    new_boundary_field = []
                    for patch_name in patch_names:
                        patch_data = {'patchName': patch_name, 'type': default_type}
                        
                        if option_schema_for_default and 'parameters' in option_schema_for_default:
                            for param in option_schema_for_default['parameters']:
                                if 'default' in param and not 'optional' in param:
                                    patch_data[param['name']] = param['default']
                        new_boundary_field.append(patch_data)
                    
                    new_params_to_update[param_name] = new_boundary_field

                # Initialize 'choice_with_options' parameters if they are not already set
                elif param_type == 'choice_with_options' and not current_value and not param_props.get('optional'):
                    
                    new_params_to_update[param_name] = self.initialize_parameters_from_choice_with_options(param_props)

            if new_params_to_update:
                foam_file.update_parameters(new_params_to_update)

    def get_editable_parameters(self, file_path: Path) -> Dict[str, Any]:
        """
        Retrieves the editable parameters for a given file.

        Args:
            file_path: The path to the file whose parameters are requested.

        Returns:
            A dictionary of editable parameters, or an empty dict if the file is not found.
        """
        file_name = file_path.name
        if file_name in self.files:
            return self.files[file_name].get_editable_parameters()
        return {}

    def modify_parameters(self, file_path: Path, new_params: Dict[str, Any]) -> None:
        """
        Modifies the parameters of a specific file.
        Args:
            file_path: The path to the file to be modified.
            new_params: A dictionary with the new parameters to apply.

        Raises:
            ParameterError: If the file is not found or parameters are invalid.
        """
        file_name = file_path.name
        if file_name not in self.files:
            raise ParameterError(f"File '{file_name}' not managed by this FileHandler instance.")

        try:
            file_obj = self.files[file_name]
            file_obj.update_parameters(new_params)
        except (KeyError, AttributeError, TypeError, ValueError) as e:
            logger.error(f"Invalid parameters for {file_name}: {e}")
            raise ParameterError(f"Invalid parameters provided for {file_name}: {e}")

    def write_files(self):
        """
        Writes all managed files to the case directory.

        Raises:
            FileHandlerError: If an error occurs during file writing.
        """
        try:
            for _, file_obj in self.files.items():
                file_obj.write_file(self.case_path)
        except (FileNotFoundError, PermissionError) as e:
            raise FileHandlerError(f"Failed to write file: {e}")

    def save_all_parameters_to_json(self) -> None:
        """
        Saves all editable parameters from all FoamFile objects to a single JSON file.

        Raises:
            FileHandlerError: If the JSON file cannot be written.
        """
        all_params_values = {}
        for file_name, file_obj in self.files.items():
            editable_params = file_obj.get_editable_parameters()
            file_values = {param_name: props.get('current') for param_name, props in editable_params.items()}
            all_params_values[file_name] = file_values

        saved_data = {
            "template": self.template,
            "file_names": self.file_names,
            "parameters": all_params_values
        }

        json_path = self.case_path / self.JSON_PARAMS_FILE
        try:
            with open(json_path, 'w') as f:
                json.dump(saved_data, f, indent=4)
        except (IOError, PermissionError) as e:
            raise FileHandlerError(f"Could not save parameters to JSON file at {json_path}: {e}")

    def load_all_parameters_from_json(self,json_path : Path = None) -> None:
        """
        Loads all parameters from the JSON file and updates the corresponding FoamFile objects.
        If the template or file list in the JSON differs from the current one, it re-initializes the files.
        """
        if json_path is None:
            json_path = self.case_path / self.JSON_PARAMS_FILE

        if not json_path.exists():
            raise FileHandlerError(f"Parameters JSON file not found at {json_path}")

        try:
            with open(json_path, 'r') as f:
                saved_data = json.load(f)
        except json.JSONDecodeError:
            raise FileHandlerError(f"Failed to decode JSON from {json_path}")

        loaded_template = saved_data.get("template")
        loaded_file_names = saved_data.get("file_names")

        # Check if the configuration has changed and re-initialize if needed
        if loaded_template and loaded_template != self.template:
            logger.warning(f"Template changed from '{self.template}' to '{loaded_template}'. Re-initializing files.")
            self.template = loaded_template
            self.file_names = None
            self._initialize_from_template()
        elif loaded_file_names and loaded_file_names != self.file_names:
            logger.warning("File list changed. Re-initializing files.")
            self.file_names = loaded_file_names
            self.template = None
            self._initialize_from_names()

        loaded_params = saved_data.get("parameters", {})
        for file_name, params in loaded_params.items():
            if file_name in self.files:
                try:
                    self.files[file_name].update_parameters(params)
                except (KeyError, AttributeError, TypeError, ValueError) as e:
                    raise ParameterError(f"Invalid parameters for '{file_name}' in JSON file: {e}")
    
    def get_number_of_processors(self) -> int:
        json_path = self.case_path / self.JSON_PARAMS_FILE
        if not json_path.exists():
            raise FileHandlerError(f"Parameters JSON file not found at {json_path}")
        try:
            with open(json_path, 'r') as f:
                saved_data = json.load(f)
        except json.JSONDecodeError:
            raise FileHandlerError(f"Failed to decode JSON from {json_path}")

        try:
            numberOfSubdomains_value = saved_data['parameters']['decomposeParDict']['numberOfSubdomains']
            return numberOfSubdomains_value
        except KeyError as e:
            print(f"Error: La clave {e} no se encontró en el JSON.")

    def get_solver(self) -> str:
        json_path = self.case_path / self.JSON_PARAMS_FILE
        if not json_path.exists():
            raise FileHandlerError(f"Parameters JSON file not found at {json_path}")
        try:
            with open(json_path, 'r') as f:
                saved_data = json.load(f)
        except json.JSONDecodeError:
            raise FileHandlerError(f"Failed to decode JSON from {json_path}")

        try:
            solver_value = saved_data['parameters']['controlDict']['application']
            return solver_value
        except KeyError as e:
            print(f"Error: La clave {e} no se encontró en el JSON.")