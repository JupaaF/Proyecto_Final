import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyvista as pv
from pyvistaqt import QtInteractor

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Visualizador de Malla con PyQt6 y PyVista")
        self.setGeometry(100, 100, 1024, 768)

        # Crear un widget central y un layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Crear el plotter de PyVista para Qt
        self.plotter = QtInteractor(self)
        layout.addWidget(self.plotter.interactor)

        # Cargar y mostrar la malla
        self.load_and_plot_mesh()

        # Es necesario inicializar el interactor de VTK para que capture los eventos del ratón.
        self.plotter.interactor.Initialize()

    def load_and_plot_mesh(self):
        """Carga la malla y los patches y los añade al plotter."""
        try:
            # Cargar los patches de la malla
            patch_atmosphere = pv.read('interfaz/atmosphere/atmosphere_0.vtk')
            patch_inlet = pv.read('interfaz/inlet/inlet_0.vtk')
            patch_outlet = pv.read('interfaz/outlet/outlet_0.vtk')
            patch_walls = pv.read('interfaz/walls/walls_0.vtk')
        except FileNotFoundError as e:
            print(f"Error al leer el archivo: {e}. Asegúrate de que las rutas son correctas.")
            return

        # Añadir los patches al plotter con colores distintivos
        self.plotter.add_mesh(patch_atmosphere, color='cyan', label='Atmosphere')
        self.plotter.add_mesh(patch_inlet, color='green', label='Inlet')
        self.plotter.add_mesh(patch_outlet, color='red', label='Outlet')
        self.plotter.add_mesh(patch_walls, color='blue', label='Walls')

        # Configuración de la visualización
        self.plotter.add_legend(bcolor=(0.1, 0.1, 0.1), border=True)
        self.plotter.set_background('white')
        self.plotter.camera_position = 'iso'
        self.plotter.add_axes()

def main():
    """Función principal para iniciar la aplicación PyQt."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    print("Mostrando la malla en una ventana de PyQt6. Cierra la ventana para finalizar.")
    sys.exit(app.exec())

if __name__ == '__main__':
    main()