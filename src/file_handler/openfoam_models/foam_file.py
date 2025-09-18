from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class FoamFile(ABC):
    """Abstract base class for all OpenFOAM configuration files."""

    def __init__(self, name: str, folder: str, class_type: str, object_name=None):
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
        self.object_name = object_name

    def get_header(self):
        if self.object_name is not None:
            object = self.object_name
        else:
            object = self.name
            
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
        object      {object};
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
        param_label = param_props.get('label', '')

        if param_type == "vector":
            if not isinstance(param_value,dict):
                raise ValueError(f"El parametro '{param_label}' no es un diccionario, es un vector.")

            if param_value.get('x') is None:
                raise KeyError(f"Falta la componente 'x' en el vector del parametro '{param_label}'.")
            if param_value.get('y') is None:
                raise KeyError(f"Falta la componente 'y' en el vector del parametro '{param_label}'.")
            if param_value.get('z') is None:
                raise KeyError(f"Falta la componente 'z' en el vector del parametro '{param_label}'.")

            if not isinstance(param_value['x'],(float,int)):
                raise ValueError(f"La componente 'x' del vector en '{param_label}' no es un numero.")
            if not isinstance(param_value['y'],(float,int)):
                raise ValueError(f"La componente 'y' del vector en '{param_label}' no es un numero.")
            if not isinstance(param_value['z'],(float,int)):
                raise ValueError(f"La componente 'z' del vector en '{param_label}' no es un numero.")

        if param_type == "string":
            if not isinstance(param_value,str):
                raise ValueError(f"El parametro '{param_label}' no es un string.")

        if param_type == "float":
            if not isinstance(param_value,(float,int)):
                raise ValueError(f"El parametro '{param_label}' no es un numero de punto flotante.")

        if param_type == "int":
            if not isinstance(param_value,int):
                raise ValueError(f"El parametro '{param_label}' no es un entero.")
            
        if param_type == "choice":
            if not isinstance(param_value,str):
                raise ValueError(f"El parametro '{param_label}' no es un string, es un choice.")
            
            options = param_props.get('options')
            if options is None:
                raise ValueError(f"Faltan las opciones en el parametro '{param_label}'.")

            if param_value not in options:
                raise ValueError(f"El valor '{param_value}' no es una opcion valida para el parametro '{param_label}'. Opciones validas: {options}")

        if param_type == "choice_with_options":
            if not isinstance(param_value, list):
                raise ValueError(f"El parametro '{param_label}' no es una lista. Es un 'choice_with_options'")

            options = param_props.get('options')
            if options is None:
                raise ValueError(f"Faltan las opciones en el parametro '{param_label}'.")

            if not isinstance(param_value[0], str):
                raise ValueError(f"El primer elemento de la lista en '{param_label}' debe ser un string.")

            if not isinstance(param_value[1], dict):
                raise ValueError(f"El segundo elemento de la lista en '{param_label}' debe ser un diccionario.")

            chosen_option_name = param_value[0]
            chosen_option_params = param_value[1]
            
            option_schema = None
            for option in options:
                if option.get('name') == chosen_option_name:
                    option_schema = option
                    break
            
            if option_schema is None:
                raise ValueError(f"La opcion '{chosen_option_name}' no es valida para el parametro '{param_label}'.")

            for param in option_schema.get('parameters', []):
                param_name = param.get('name')
                param_type = param.get('type')
                is_optional = param.get('optional', False)
                
                value = chosen_option_params.get(param_name)

                if value is None:
                    if not is_optional:
                        raise ValueError(f"Falta el parametro obligatorio '{param_name}' en la opcion '{chosen_option_name}' del parametro '{param_label}'.")
                    else:
                        continue

                self._validate(value, param_type, param)
            
        if param_type == "patches":
            if not isinstance(param_value,list):
                raise ValueError(f"El parametro '{param_label}' no es una lista. Es un 'patches'")
            
            for patch in param_value:
                if not isinstance(patch,dict):
                    raise ValueError(f"El patch '{patch}' en '{param_label}' no es un diccionario.")
                
                patch_name = patch.get('patchName')
                if patch_name is None:
                    raise ValueError(f"Falta el nombre del patch ('patchName') en '{param_label}'.")

                if not isinstance(patch_name, str):
                    raise ValueError(f"El nombre del patch ('patchName') en '{param_label}' no es un string.")
                
                patch_type = patch.get('type')
                if patch_type is None:
                    raise ValueError(f"Falta el tipo ('type') en el patch '{patch_name}' del parametro '{param_label}'.")

                if not isinstance(patch_type,str):
                    raise ValueError(f"El tipo ('type') en el patch '{patch_name}' del parametro '{param_label}' no es un string.")
                
                possible_types = param_props.get('schema').get('type').get('options')

                exist = False

                for typi in possible_types:
                    if patch_type == typi.get("name"):
                        exist = True
                        for param in typi.get('parameters', []):
                            param_name = param.get('name')
                            param_type = param.get('type')
                            is_optional = param.get('optional', False)

                            valor_patch = patch.get(param_name)
                            
                            if valor_patch is None:
                                if not is_optional:
                                    raise ValueError(f"Falta el parametro obligatorio '{param_name}' en el patch '{patch_name}' del parametro '{param_label}'.")
                                else:
                                    continue
                            
                            self._validate(valor_patch, param_type, param)
                            
                if not exist:
                    raise ValueError(f"El tipo '{patch_type}' no es valido para el patch '{patch_name}' del parametro '{param_label}'.")
