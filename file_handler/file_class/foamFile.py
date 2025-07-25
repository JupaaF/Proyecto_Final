from abc import ABC, abstractmethod


class foamFile(ABC):
    
    def __init__(self, carpeta, nombre):
        self.carpeta = carpeta
        self. nombre = nombre

    def get_header(self):
        return f"""/*--------------------------------*- C++ -*----------------------------------*\
                    | =========                 |                                                 |
                    | \      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
                    |  \    /   O peration     | Version:  v2312                                 |
                    |   \  /    A nd           | Web:      www.OpenFOAM.com                      |
                    |    \/     M anipulation  |                                                 |
                    \*---------------------------------------------------------------------------*/
                    FoamFile
                    {{
                        format      ascii;
                        class       dictionary;
                        location    "{self.carpeta}";
                        object      {self.nombre};
                    }}
                    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
                    """
    