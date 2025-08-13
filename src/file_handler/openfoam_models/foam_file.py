from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class FoamFile(ABC):
    """Abstract base class for all OpenFOAM configuration files."""

    def __init__(self, name: str, folder: str, class_type: str):
        """
        Initializes a FoamFile object.

        Args:
            name: The name of the file (e.g., 'controlDict').
            folder: The directory where the file is located (e.g., 'system').
            class_type: The OpenFOAM class type (e.g., 'dictionary').
        """
        self.name = name
        self.folder = folder
        self.class_type = class_type

    def get_header(self):
        return f"""
    /*--------------------------------*- C++ -*---------------------------------*\\
    | =========                 |                                                |
    | \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
    |  \\    /   O peration     | Version:  v2312                                 |
    |   \\  /    A nd           | Website:  www.openfoam.com                      |
    |    \\/     M anipulation  |                                                 |
    \*---------------------------------------------------------------------------*/

    FoamFile
    {{
        version     2.0;
        format      ascii;
        class       {self.class_type};
        object      {self.name};
    }}
    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
    """
    
    def get_header_location(self):
        return f"""
    /*--------------------------------*- C++ -*---------------------------------*\\
    | =========                 |                                                |
    | \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
    |  \\    /   O peration     | Version:  v2312                                 |
    |   \\  /    A nd           | Website:  www.openfoam.com                      |
    |    \\/     M anipulation  |                                                 |
    \*---------------------------------------------------------------------------*/

    FoamFile
    {{
        version     2.0;
        format      ascii;
        class       {self.class_type};
        location    "{self.folder}";
        object      {self.name};
    }}
    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
    """

    @abstractmethod
    def _get_string(self) -> str:
        """Returns the main content of the file as a string."""
        pass

    @abstractmethod
    def get_editable_parameters(self) -> Dict[str, Any]:
        """Returns a dictionary of parameters that can be edited by the user."""
        pass

    @abstractmethod
    def update_parameters(self, params: Dict[str, Any]) -> None:
        """Modifies the file's parameters based on user input."""
        pass

    @abstractmethod
    def write_file(self, case_path: Path) -> None:
        """
        Writes the complete file (header + content) to the specified path.
        Subclasses must implement this to choose the correct header.
        """
        pass
