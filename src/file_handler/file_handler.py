from pathlib import Path
from typing import Dict, Any

from .openfoam_models.foam_file import FoamFile
from .openfoam_models.U import U
from .openfoam_models.controlDict import controlDict
from .openfoam_models.fvSchemes import fvSchemes
from .openfoam_models.fvSolution import fvSolution

class FileHandler:
    """Manages the creation, modification, and access of OpenFOAM case files."""

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
        self.create_case_files()

    def get_case_path(self) -> Path:
        """Returns the root path of the case directory."""
        return self.case_path

    def _initialize_file_objects(self) -> None:
        """Initializes the objects representing each OpenFOAM file."""
        # Based on the template, different files would be initialized.
        self.files = {
            "U": U(),
            "controlDict": controlDict(),
            "fvSchemes": fvSchemes(),
            "fvSolution": fvSolution(),
        }

    def create_case_files(self) -> None:
        """
        Creates the basic directory structure and writes all initialized OpenFOAM files.
        This should be called after the user confirms the initial setup.
        """
        self._create_base_dirs()
        for file_obj in self.files.values():
            file_obj.write_file(self.case_path)

    def _create_base_dirs(self) -> None:
        """Creates the essential directories for an OpenFOAM case (0, system, constant)."""
        self.case_path.mkdir(exist_ok=True)
        for folder in ['0', 'system', 'constant']:
            (self.case_path / folder).mkdir(exist_ok=True)

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
            file_obj.modify_parameters(new_params)
            file_obj.write_file(self.case_path) # Rewrite the file with updated parameters