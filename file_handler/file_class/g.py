from foamFile import foamFile

class g(foamFile):

    def __init__(self): #----> No le pasas nada porque supongo que siempre es igual (PREGUNTAR A LUCAS)
        super().__init__("constant", "uniformDimensionedVectorField", "g")

    def __getString__(self):
        
        content = f"""
            dimensions      [0 1 -2 0 0 0 0];
            value            (0 -9.81 0);
        """
        
        return self.get_header() + content
   

    def write_file(self,archivo): 
        archivo.write(self.__getString__())

    