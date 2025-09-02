from pathlib import Path
from .foam_file import FoamFile
from jinja2 import Environment, FileSystemLoader
import math

class DecomposeParDict(FoamFile):
    """
    Represents the decomposeParDict file for OpenFOAM.
    This file is used to configure the domain decomposition for parallel processing.
    """

    def __init__(self):
        super().__init__(name="decomposeParDict", folder="system", class_type="dictionary")
        
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

        # Default values
        self.numberOfSubdomains = 1
        self.method = "simple"
        self.n_x = 1
        self.n_y = 1
        self.n_z = 1

    def _get_string(self):
        """Generates the file content as a string from the Jinja2 template."""
        template = self.jinja_env.get_template("decomposeParDict_template.jinja2")

        context = {
            'numberOfSubdomains': self.numberOfSubdomains,
            'method': self.method,
            'n_x': self.n_x,
            'n_y': self.n_y,
            'n_z': self.n_z,
        }
        return template.render(context)

    def get_editable_parameters(self):
        """Returns a dictionary of parameters that can be edited by the user."""
        return {
            'numberOfSubdomains': {
                'label': 'Número de Subdominios',
                'tooltip': 'Coincide con el número de procesadores a usar en la simulación.',
                'type': 'int',
                'current': self.numberOfSubdomains,
                'required': True,
                'min': 1
            },
            'method': {
                'label': 'Método de Descomposición',
                'tooltip': 'Algoritmo utilizado para realizar la descomposición del dominio.',
                'type': 'choice',
                'current': self.method,
                'options': ['simple', 'hierarchical', 'scotch', 'metis'],
                'required': True
            },
            'n_x': {
                'label': 'Subdominios en dirección X.',
                'tooltip': 'El número de subdominios en dirección X.',
                'type': 'int',
                'current': self.n_x,
                'required': True
            },
            'n_y': {
                'label': 'Subdominios en dirección Y.',
                'tooltip': 'El número de subdominios en dirección Y.',
                'type': 'int',
                'current': self.n_y,
                'required': True
            },
            'n_z': {
                'label': 'Subdominios en dirección Z.',
                'tooltip': 'El número de subdominios en dirección Z.',
                'type': 'int',
                'current': self.n_z,
                'required': True
            }

        }

    def update_parameters(self, params: dict):
        """Updates the parameters from a dictionary."""
        if 'numberOfSubdomains' in params:
            num_domains = int(params['numberOfSubdomains'])
            if num_domains > 0:
                self.numberOfSubdomains = num_domains
            else:
                raise ValueError("El número de subdominios debe ser un entero positivo.")

        if 'method' in params:
            self.method = str(params['method'])

        if 'n_x' in params:
            self.n_x = int(params['n_x'])

        if 'n_y' in params:
            self.n_y = int(params['n_y'])

        if 'n_z' in params:
            self.n_z = int(params['n_z'])

    def write_file(self, case_path: Path):
        """Writes the complete file to the specified case path."""
        # This file should only be written if we are running in parallel
        if self.numberOfSubdomains > 1:
            output_dir = case_path / self.folder
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / self.name
            with open(output_path, "w") as f:
                f.write(self._get_string())
