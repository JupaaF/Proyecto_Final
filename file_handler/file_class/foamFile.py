from abc import ABC, abstractmethod


class foamFile(ABC):
    
    def __init__(self, carpeta, clase, nombre):
        self.carpeta = carpeta
        self.clase = clase
        self. nombre = nombre

    def get_header(self):
        return f"""/*--------------------------------*- C++ -*----------------------------------*\
                    | =========                 |                                                 |
                    | \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
                    |  \\    /   O peration     | Version:  v2506                                 |
                    |   \\  /    A nd           | Website:  www.openfoam.com                      |
                    |    \\/     M anipulation  |                                                 |
                    \*---------------------------------------------------------------------------*/

                    FoamFile
                    {{
                        version     2.0;
                        format      ascii;
                        class       {self.clase};
                        object      {self.nombre};
                    }}
                    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
                    """
    
    def get_header_location(self):
        return f"""/*--------------------------------*- C++ -*----------------------------------*\
                    | =========                 |                                                 |
                    | \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
                    |  \\    /   O peration     | Version:  v2506                                 |
                    |   \\  /    A nd           | Website:  www.openfoam.com                      |
                    |    \\/     M anipulation  |                                                 |
                    \*---------------------------------------------------------------------------*/

                    FoamFile
                    {{
                        version     2.0;
                        format      ascii;
                        class       {self.clase};
                        location    "{self.carpeta}";
                        object      {self.nombre};
                    }}
                    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
                    """
    