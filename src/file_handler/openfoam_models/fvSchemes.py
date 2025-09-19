from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

#por ahora solo pueden configurarse los default!!!

class fvSchemes(FoamFile):

    def __init__(self):
        super().__init__(name="fvSchemes", folder="system", class_type="dictionary")

        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

        # Valores por defecto
        self.ddtSchemes = 'Euler'
        self.gradSchemes = 'Gauss linear'
        self.divSchemes = 'damBreak'
        self.laplacianSchemes = 'Gauss linear'
        self.interpolationSchemes = 'linear'
        self.snGradSchemes = 'corrected'
        self.wallDist = None

    def _get_string(self):
        template = self.jinja_env.get_template("fvSchemes_template.jinja2")
        context = {
            'ddtSchemes': self.ddtSchemes,
            'gradSchemes': self.gradSchemes,
            'divSchemes': self.divSchemes,
            'laplacianSchemes': self.laplacianSchemes,
            'interpolationSchemes': self.interpolationSchemes,
            'snGradSchemes': self.snGradSchemes,
            'wallDist': self.wallDist
        }
        content = template.render(context)
        return self.get_header() + content

    def update_parameters(self, params: dict):
        """
        Actualiza los parámetros desde un diccionario.
        """
        if not isinstance(params,dict):
            raise ValueError("Me tenes que dar un diccionario")
        
        param_props = self.get_editable_parameters()

        for key, value in params.items():

            if not hasattr(self,key):
                continue

            if value is None:
                setattr(self, key, None)
                continue

            props = param_props[key]
            type_data = props['type']

            try:
                self._validate(value,type_data,props)
            except ValueError:
                raise

            setattr(self, key, value)

    def write_file(self, case_path: Path):
        output_dir = case_path / self.folder
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / self.name
        with open(output_path, "w") as f:
            f.write(self._get_string())

    def get_editable_parameters(self):
        return {
            'ddtSchemes': {
                'label': 'ddtSchemes',
                'tooltip': '''Esquema de discretización para las primeras derivadas:
                - steadyState: establece las derivadas temporales en cero.
                - Euler: transitorio, implícito de primer orden, acotado.
                - backward: transitorio, implícito de segundo orden, potencialmente ilimitado.
                - CrankNicolson: transitorio, implícito de segundo orden, acotado; requiere un coeficiente de descentrado. 
                  (Generalmente = 0,9 se utiliza para estabilizar el esquema en problemas prácticos de ingeniería.)
                - localEuler: pseudotransitorio para acelerar una solución al estado estacionario mediante escalonamiento temporal local; implícito de primer orden.''',
                'type': 'choice',
                'options': ['steadyState','Euler','backward','CrankNicolson 0.9','localEuler'],
                'current': self.ddtSchemes,
                'group': 'Esquemas Temporales'
            },
            'gradSchemes': {
                'label': 'gradSchemes',
                'tooltip': '''Esquema de discretización para gradientes:
                -  Gauss linear: especifica la discretización estándar de volumen finito con integración gaussiana.''',
                'type': 'choice',
                'options': ['Gauss linear'], # TODO ver si agregar lo de cellLimited (doc 4.5.2)
                'current': self.gradSchemes,
                'group': 'Esquemas de Gradiente'
            },
            'divSchemes': {
                'label': 'divSchemes', # TODO generalizar esto, solo configuro del dambreak por ahora en el template (doc 4.5.3)
                'tooltip': '''Esquema de discretización para divergencia (según el caso):
                - damBreak: configuración correcta para este caso.''',
                'type': 'choice',
                'current': self.divSchemes,
                'group': 'Esquemas de Divergencia',
                'options': [
                    'damBreak',
                    'waterChannel',
                    '2DChannel',
                    '3DScourSqr'
                ]
            },
            'laplacianSchemes': {
                'label': 'laplacianSchemes',
                'tooltip': '''Esquema de discretización para laplacianos.
En todos los casos, se utiliza el esquema de interpolación lineal para la interpolación de la difusividad. 
Se utiliza la misma matriz de esquemas snGradSchemes basada en la no ortogonalidad máxima de la malla.''',
                'type': 'choice',
                'options': ['Gauss linear', '2DChannel', '3DScourSqr'],
                'current': self.laplacianSchemes,
                'group': 'Esquemas de Laplaciano'
            },
            'interpolationSchemes': {
                'label': 'interpolationSchemes',
                'tooltip': '''Esquema de interpolación.
Existen numerosos esquemas en OpenFOAM, pero la interpolación lineal se utiliza en casi todos los casos.''',
                'type': 'choice',
                'options': ['linear'],
                'current': self.interpolationSchemes,
                'group': 'Esquemas de Interpolación'
            },
            'snGradSchemes': {
                'label': 'snGradSchemes',
                'tooltip': '''Los términos de gradiente normal son necesarios para evaluar un término laplaciano mediante integración gaussiana. 
Un gradiente normal a la superficie se evalúa en una cara de celda.
                              - uncorrected y orthogonal: solo se recomiendan para mallas con muy baja no ortogonalidad (p. ej., un máximo de 5 grados). 
                              - corrected: se recomienda generalmente, pero...
                              - limited: puede requerirse para una no ortogonalidad máxima por encima de 75 grados. 
                              Con una no ortogonalidad superior a 85 eqn, la convergencia suele ser difícil de lograr.''',
                'type': 'choice',
                'options': ['corrected','uncorrected','orthogonal','limited corrected 0.33','limited corrected 0.5'],
                'current': self.snGradSchemes,
                'group': 'Esquemas de Gradiente de Superficie'
            },
            'wallDist': {
                'label': 'wallDist',
                'tooltip': 'Método para calcular la distancia a la pared',
                'type': 'choice_with_options',
                'options': [
                    {
                        'name': 'meshWave',
                        'label': 'meshWave',
                        'parameters':[
                            {
                                'name': 'correctWalls',
                                'label': 'correctWalls',
                                'tooltip': 'Opcionalmente, corrige la distancia desde las celdas cercanas a la pared hasta el límite.',
                                'type': 'string',
                                'default': 'false'
                            }]
                    },
                    {
                        'name': 'directionalMeshWave',
                        'label': 'directionalMeshWave',
                        'parameters':[
                            {
                                'name': 'normal',
                                'label': 'normal',
                                'tooltip': 'La componente de dirección a ignorar.',
                                'type': 'vector',
                                'default': {'x': 0, 'y': 0, 'z': 1}
                            }]

                    }],
                'current': self.wallDist,
                'group': 'Esquemas de Gradiente de Superficie',
                'optional' : True
            }
        }