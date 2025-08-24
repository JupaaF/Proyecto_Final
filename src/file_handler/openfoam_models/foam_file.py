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

    def _validate(self,param_value,param_type,param_props = {}):
        if param_type == "vector":
            if not isinstance(param_value,dict):
                raise ValueError("El vector no es un diccionario")

            if param_value.get('x') is None:
                raise KeyError("Falta x")
            if param_value.get('y') is None:
                raise KeyError("Falta y")
            if param_value.get('z') is None:
                raise KeyError("Falta z")

            if not isinstance(param_value['x'],(float,int)):
                raise ValueError("x no es un numero") 
            if not isinstance(param_value['y'],(float,int)):
                raise ValueError("y no es un numero")
            if not isinstance(param_value['z'],(float,int)):
                raise ValueError("z no es un numero")

        if param_type == "string":
            if not isinstance(param_value,str):
                raise ValueError("El string no es un string")

        if param_type == "float":
            if not isinstance(param_value,(float,int)):
                raise ValueError("El float no es un numero")

        if param_type == "int":
            if not isinstance(param_value,int):
                raise ValueError("El int no es un numero")
            
        if param_type == "choice":
            if not isinstance(param_value,str):
                raise ValueError("En el choice me diste cualquier cosa")
            
            if param_props.get('options') is None:
                raise ValueError("Faltan las opciones")

            if param_value not in param_props.get('options'):
                raise ValueError("Choice mal puesto")

        if param_type == "choice_with_options":
            if not isinstance(param_value,list):
                raise ValueError("Valor invalido, no es una lista")

            if param_props.get('options') is None:
                raise ValueError("Faltan las opciones, no hay opciones")

            if param_value[0].get('param_name') != 'solver_selected':
                raise ValueError("Valor invalido, no esta el solver")
            
            opciones = param_props.get('options')

            exist = False

            for opcion in opciones:
                if param_value[0].get('value') == opcion.get('name'):
                    exist = True
                    ## TODO: Falta poner que checkee si los parametros que agrega realemnte existen

            if not exist:
                raise ValueError("Valor invalido, no existe")
            
        if param_type == "patches":
            if not isinstance(param_value,list):
                raise ValueError("Valor invalido")
            
            for patch in param_value:
                if not isinstance(patch,dict):
                    raise ValueError("Valor invalido")
                
                if patch.get('patchName') is None:
                    raise ValueError("Valor invalido")

                if not isinstance(patch.get('patchName'), str):
                    raise ValueError("Valor invalido")
                
                if patch.get('type') is None:
                    raise ValueError("Valor invalido")

                if not isinstance(patch.get('type'),str):
                    raise ValueError("Valor invalido")
                
                possible_types = param_props.get('schema').get('type').get('options')

                exist = False

                for typi in possible_types:
                    if patch.get('type') == typi.get("name"):
                        exist = True
                        for param in typi.get('parameters'):
                            
                            valor_patch = patch.get(param.get('name'))
                            if valor_patch is None:
                                raise ValueError("Valor invalido")
                            
                            self._validate(valor_patch,param.get('type'))
                            
                            
                if not exist:
                    raise ValueError("Valor invalido")
