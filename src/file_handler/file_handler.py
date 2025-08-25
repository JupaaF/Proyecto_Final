import json
from pathlib import Path
from typing import Dict, Any

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

class FileHandler:
    """Manages the creation, modification, and access of OpenFOAM case files."""
    JSON_PARAMS_FILE = "parameters.json"
    
    def __init__(self, case_path: Path, template: str = None):
        """
        Initializes the FileHandler for a given case.

        Args:
            case_path: The absolute path to the simulation case directory.
            template: The name of the template to use (currently not implemented).
        """
        self.case_path = case_path
        self.template = template  # TODO: Implement template logic
        self.files: Dict[str, FoamFile] = {}
        
        self._initialize_file_objects()
        
        self.files['controlDict'].write_file(self.case_path)
        self.files['fvSolution'].write_file(self.case_path)
        self.files['fvSchemes'].write_file(self.case_path)

    def get_case_path(self) -> Path:
        """Returns the root path of the case directory."""
        return self.case_path

    def _initialize_file_objects(self) -> None:
        """Initializes the objects representing each OpenFOAM file."""
        # TODO: Based on the template, different files would be initialized.
        self.files = {
            "U": U(),
            "controlDict": controlDict(),
            "fvSchemes": fvSchemes(),
            "fvSolution": fvSolution(),
            "alpha.water": alpha_water(),
            "g": g(),
            "k": k(),
            "nuTilda" : nuTilda(),
            "nut": nut(),
            "epsilon": epsilon(),
            "p_rgh": p_rgh(),
            "setFieldsDict": setFieldsDict(),
            "transportProperties": transportProperties(),
            "turbulenceProperties": turbulenceProperties(),
        }

    def create_case_files(self) -> None:
        """
        Creates the basic directory structure and writes all initialized OpenFOAM files.
        This should be called after the user confirms the initial setup.
        """
        self._create_base_dirs()
        for file_obj in self.files.values():
            print(f"Se creo el archivo {file_obj.name}")
            file_obj.write_file(self.case_path)

    def _create_base_dirs(self) -> None:
        """Creates the essential directories for an OpenFOAM case (0, system, constant)."""
        self.case_path.mkdir(exist_ok=True)
        for folder in ['0', 'system', 'constant']:
            (self.case_path / folder).mkdir(exist_ok=True)

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
                                if 'default' in param:
                                    patch_data[param['name']] = param['default']
                        new_boundary_field.append(patch_data)
                    
                    new_params_to_update[param_name] = new_boundary_field

                # Initialize 'choice_with_options' parameters if they are not already set
                elif param_type == 'choice_with_options' and not current_value:
                    options = param_props.get('options', [])
                    if not options:
                        continue

                    default_option = options[0]
                    default_option_name = default_option.get('name')
                    
                    # NOTE: 'solver_selected' is hardcoded in the original UI code, so we replicate that assumption here.
                    default_value = [{'param_name': 'solver_selected', 'value': default_option_name}]
                    
                    sub_params_schema = default_option.get('parameters', [])
                    for sub_param in sub_params_schema:
                        if 'default' in sub_param:
                            default_value.append({
                                'param_name': sub_param.get('name'),
                                'value': sub_param.get('default')
                            })
                    
                    new_params_to_update[param_name] = default_value

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
        Modifies the parameters of a specific file and rewrites it.
        Args:
            file_path: The path to the file to be modified.
            new_params: A dictionary with the new parameters to apply.
        """
        file_name = file_path.name
        if file_name in self.files:
            file_obj = self.files[file_name]
            file_obj.update_parameters(new_params)

    def write_files(self):
        for _,file_obj in self.files.items():
            try:
                file_obj.write_file(self.case_path)
            except PermissionError as e:
                print(f"Error writing file {file_obj.name}: {e}")

    def save_all_parameters_to_json(self) -> None:
        """Saves all editable parameters from all FoamFile objects to a single JSON file."""
        all_params_values = {}
        for file_name, file_obj in self.files.items():
            editable_params = file_obj.get_editable_parameters()
            file_values = {}
            for param_name, param_props in editable_params.items():
                # Extract only the 'current' value
                file_values[param_name] = param_props.get('current')
            all_params_values[file_name] = file_values

        # Add template to the saved JSON
        saved_data = {
            "template": self.template,
            "parameters": all_params_values
        }

        json_path = self.case_path / self.JSON_PARAMS_FILE
        with open(json_path, 'w') as f:
            json.dump(saved_data, f, indent=4)

    def load_all_parameters_from_json(self) -> None:
        """Loads all parameters from the JSON file and updates the corresponding FoamFile objects."""
        json_path = self.case_path / self.JSON_PARAMS_FILE
        if not json_path.exists():
            return

        try:
            with open(json_path, 'r') as f:
                saved_data = json.load(f)
        except json.JSONDecodeError:
            print("Error: Could not decode JSON from file.")
            return

        # Extract template and parameters
        loaded_template = saved_data.get("template")
        loaded_params = saved_data.get("parameters", {})

        # Update self.template if loaded_template is different
        if loaded_template and loaded_template != self.template:
            # This scenario needs careful handling.
            # If the template changes, the initialized FoamFile objects might be different.
            # For now, I'll just update self.template, but a more robust solution
            # might involve re-initializing file objects based on the new template.
            # This is beyond the current scope of just loading parameters.
            self.template = loaded_template

        for file_name, params in loaded_params.items():
            if file_name in self.files:
                self.files[file_name].update_parameters(params)