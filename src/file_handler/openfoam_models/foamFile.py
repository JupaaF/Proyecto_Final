from abc import ABC, abstractmethod


class foamFile(ABC):
    
    def __init__(self, folder, classType, name):
        self.folder = folder
        self.classType = classType
        self.name = name

    def get_header(self):
        return f"""
    /*--------------------------------*- C++ -*---------------------------------*\\
    | =========                 |                                                |
    | \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
    |  \\    /   O peration     | Version:  v2506                                 |
    |   \\  /    A nd           | Website:  www.openfoam.com                      |
    |    \\/     M anipulation  |                                                 |
    \*---------------------------------------------------------------------------*/

    FoamFile
    {{
        version     2.0;
        format      ascii;
        class       {self.classType};
        object      {self.name};
    }}
    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
    """
    
    def get_header_location(self):
        return f"""
    /*--------------------------------*- C++ -*---------------------------------*\\
    | =========                 |                                                |
    | \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
    |  \\    /   O peration     | Version:  v2506                                 |
    |   \\  /    A nd           | Website:  www.openfoam.com                      |
    |    \\/     M anipulation  |                                                 |
    \*---------------------------------------------------------------------------*/

    FoamFile
    {{
        version     2.0;
        format      ascii;
        class       {self.classType};
        location    "{self.folder}";
        object      {self.name};
    }}
    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
    """
    @abstractmethod
    def get_editable_parameters(self) -> dict:
        pass