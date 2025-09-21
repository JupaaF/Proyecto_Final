from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader

class decomposeParDict(FoamFile):

    def __init__(self):
        super().__init__(name="decomposeParDict", folder="system", class_type="dictionary")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

        # Default values
        self.numberOfSubdomains = 2
        self.method = []
        self.customContent = None

    def _get_string(self):
        template = self.jinja_env.get_template("decomposeParDict_template.jinja2")
        
        method_name = self.method[0]
        method_params = self.method[1]

        # Convert vector dict to string for template
        if 'n' in method_params and isinstance(method_params['n'], dict):
            n_vector = method_params['n']
            method_params['n_str'] = f"({n_vector['x']} {n_vector['y']} {n_vector['z']})"

        context = {
            'numberOfSubdomains': self.numberOfSubdomains,
            'method': method_name,
            'params': method_params,
            'customContent': self.customContent
        }
        content = template.render(context)
        return self.get_header() + content
    
    def update_parameters(self, params: dict):
        if not isinstance(params, dict):
            raise ValueError("A dictionary is required to update parameters.")
        
        param_props = self.get_editable_parameters()

        for key, value in params.items():
            if not hasattr(self, key):
                continue
            
            props = param_props[key]
            type_data = props['type']

            try:
                self._validate(value, type_data, props)
            except ValueError as e:
                raise ValueError(f"Validation failed for parameter '{key}': {e}")

            setattr(self, key, value)

    def write_file(self, case_path: Path): 
        output_dir = case_path / self.folder
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / self.name
        with open(output_path, "w") as f:
            f.write(self._get_string())

    def get_editable_parameters(self):
        return {
            'numberOfSubdomains': {
                'label': 'Número de Subdominios',
                'tooltip': 'Número total de subdominios para la descomposición.',
                'type': 'int',
                'current': self.numberOfSubdomains,
                'min': 1,
                'group': 'Configuración General'
            },
            'method': {
                'label': 'Método de Descomposición',
                'tooltip': 'Algoritmo a utilizar para la descomposición del dominio.',
                'type': 'choice_with_options',
                'current': self.method,
                'group': 'Algoritmo',
                'options': [
                    {
                        'name': 'simple',
                        'label': 'Simple',
                        'parameters': [
                            {
                                'name': 'n',
                                'label': 'Divisiones (n)',
                                'tooltip': 'Número de divisiones en cada dirección (x y z).',
                                'type': 'vector',
                                'default': {'x': 2, 'y': 1, 'z': 1}
                            },
                            {
                                'name': 'delta',
                                'label': 'Delta',
                                'tooltip': 'Tolerancia geométrica.',
                                'type': 'float',
                                'default': 0.001,
                                'optional': True
                            }
                        ]
                    },
                    {
                        'name': 'hierarchical',
                        'label': 'Hierarchical',
                        'parameters': [
                            {
                                'name': 'n',
                                'label': 'Divisiones (n)',
                                'tooltip': 'Número de divisiones en cada dirección.',
                                'type': 'vector',
                                'default': {'x': 2, 'y': 1, 'z': 1}
                            },
                            {
                                'name': 'order',
                                'label': 'Orden',
                                'tooltip': 'Orden de la descomposición (xyz, xzy, etc.).',
                                'type': 'choice',
                                'options': ['xyz', 'xzy', 'yxz', 'yzx', 'zxy', 'zyx'],
                                'default': 'xyz'
                            },
                            {
                                'name': 'delta',
                                'label': 'Delta',
                                'tooltip': 'Tolerancia geométrica.',
                                'type': 'float',
                                'default': 0.001
                            }
                        ]
                    },
                    {
                        'name': 'scotch',
                        'label': 'Scotch',
                        'parameters': []
                    },
                    {
                        'name': 'metis',
                        'label': 'Metis',
                        'parameters': [
                            {
                                'name': 'method',
                                'label': 'Método Metis',
                                'tooltip': 'Algoritmo específico de Metis.',
                                'type': 'choice',
                                'options': ['k-way', 'recursive'],
                                'default': 'k-way'
                            }
                        ]
                    }
                ]
            },
            'customContent': {
                'label': 'Contenido de experto',
                'tooltip': 'Cosas que van directamente al archivo',
                'type': 'string',
                'default': "",
                'current': self.customContent,
                'optional': True
            }
        }
