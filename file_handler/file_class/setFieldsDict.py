from foamFile import foamFile

class setFieldsDict(foamFile):  # por ahora no es editable

    def __init__(self): 
        super().__init__("system", "dictionary", "setFieldsDict")
        

    def __getString__(self):
        content = f"""            
defaultFieldValues
(
    volScalarFieldValue alpha.water 0
);

regions
(
    boxToCell
    {{
        box (0 0 -1) (0.1461 0.292 1);
        fieldValues
        (
            volScalarFieldValue alpha.water 1
        );
    }}
);

"""    
        return self.get_header() + content
    
    def write_file(self,archivo):
        archivo.write(self.__getString__())

    