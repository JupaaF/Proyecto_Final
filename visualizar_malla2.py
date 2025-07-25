# import sys
# import os
# import random
# from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
# import pyvista as pv
# from pyvistaqt import QtInteractor
# from vtkmodules.vtkRenderingCore import vtkPropPicker  # Picker de VTK para seleccionar actores

# class MainWindow(QMainWindow):
#     def __init__(self, parent=None):
#         super(MainWindow, self).__init__(parent)
#         self.setWindowTitle("Visualizador de Malla con PyQt6 y PyVista")
#         self.setGeometry(100, 100, 1024, 768)

#         # ---- Layout principal ----
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#         layout = QVBoxLayout(central_widget)

#         # Label informativa para mostrar qué patches están seleccionados
#         self.info_label = QLabel("Selecciona un patch con el mouse")
#         layout.addWidget(self.info_label)

#         # Widget para mostrar la escena 3D con PyVista integrado en PyQt
#         self.plotter = QtInteractor(self)
#         layout.addWidget(self.plotter.interactor)

#         # ---- Estructuras auxiliares ----
#         self.original_colors = {}     # Guardamos el color original de cada patch: {patch_name: (r,g,b)}
#         self.selected_patches = set() # Conjunto de patches actualmente seleccionados
#         self.actors = {}              # Relación entre patch_name y su vtkActor: {patch_name: actor}

#         # Picker de VTK que detecta el actor clickeado
#         self.picker = vtkPropPicker()

#         # ---- Cargar la malla ----
#         self.load_and_plot_mesh('interfaz')  # Carpeta que contiene subcarpetas con .vtk de cada patch

#         # Inicializamos el interactor para que reciba eventos del mouse
#         self.plotter.interactor.Initialize()

#         # Activamos la selección por clic
#         self.enable_patch_selection()

#     def load_and_plot_mesh(self, base_folder):
#         """
#         Recorre la carpeta indicada, carga los archivos .vtk correspondientes a los patches
#         y los añade a la escena con colores aleatorios.
#         """
#         if not os.path.isdir(base_folder):
#             print(f"Carpeta no encontrada: {base_folder}")
#             return

#         for root, dirs, files in os.walk(base_folder):
#             for file in files:
#                 if file.endswith(".vtk"):
#                     filepath = os.path.join(root, file)
#                     patch_name = os.path.basename(root)  # Nombre del patch = nombre de la carpeta
#                     try:
#                         # Leer el mesh del patch
#                         mesh = pv.read(filepath)

#                         # Asignar un color aleatorio (para distinguir patches)
#                         color = (random.random(), random.random(), random.random())
#                         self.original_colors[patch_name] = color

#                         # Agregar el mesh al plotter y guardar el actor para luego cambiar su color
#                         actor = self.plotter.add_mesh(mesh, color=color, name=patch_name, pickable=True)
#                         self.actors[patch_name] = actor

#                     except Exception as e:
#                         print(f"Error leyendo {filepath}: {e}")

#         # Ajustes de la escena
#         self.plotter.add_axes()
#         self.plotter.set_background('white')
#         self.plotter.camera_position = 'iso'

#     def enable_patch_selection(self):
#         """
#         Habilita la selección de patches completos usando un evento VTK.
#         Cuando el usuario hace clic izquierdo, detectamos qué actor (patch) fue clickeado,
#         y alternamos entre resaltar (amarillo) o restaurar el color original.
#         """
#         def on_left_click(obj, event):
#             # Obtenemos la posición del clic en coordenadas de pantalla
#             click_pos = self.plotter.interactor.GetEventPosition()

#             # Usamos el picker para determinar qué actor hay en esa posición
#             self.picker.Pick(click_pos[0], click_pos[1], 0, self.plotter.renderer)
#             actor = self.picker.GetActor()
#             if actor is None:
#                 return  # No se clickeó sobre ningún objeto

#             # Buscar el nombre del patch correspondiente a ese actor
#             patch_name = None
#             for name, act in self.actors.items():
#                 if act == actor:
#                     patch_name = name
#                     break

#             if patch_name:
#                 if patch_name in self.selected_patches:
#                     # Si ya estaba seleccionado, restaurar color original
#                     actor.GetProperty().SetColor(self.original_colors[patch_name])
#                     self.selected_patches.remove(patch_name)
#                 else:
#                     # Si no estaba seleccionado, resaltar en amarillo
#                     actor.GetProperty().SetColor(1, 1, 0)
#                     self.selected_patches.add(patch_name)

#                 # Actualizar la etiqueta con la lista de patches seleccionados
#                 seleccionados = ", ".join(self.selected_patches) if self.selected_patches else "ninguno"
#                 self.info_label.setText(f"Patches seleccionados: {seleccionados}")

#                 # Forzar actualización de la vista
#                 self.plotter.render()

#         # Conectamos el callback al evento de clic izquierdo usando PyVistaQt
#         self.plotter.iren.add_observer("LeftButtonPressEvent", on_left_click)

# def main():
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec())

# if __name__ == '__main__':
#     main()

import sys
import os
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QScrollArea, QCheckBox
)
import pyvista as pv
from pyvistaqt import QtInteractor
from vtkmodules.vtkRenderingCore import vtkPropPicker

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Visualizador de Malla con PyQt6 y PyVista")
        self.setGeometry(100, 100, 1280, 800)

        # Layout principal horizontal: [Panel lateral | Vista 3D]
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # ---- Panel lateral con scroll para checkboxes ----
        self.sidebar_widget = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.addWidget(QLabel("Patches:"))

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.sidebar_widget)
        main_layout.addWidget(scroll_area, 1)  # 1 = ancho relativo

        # ---- Contenedor principal para la vista 3D y label ----
        viewer_container = QVBoxLayout()
        main_layout.addLayout(viewer_container, 4)  # 4 = ancho relativo

        # Label informativa para mostrar qué patches están seleccionados
        self.info_label = QLabel("Selecciona un patch con el mouse")
        viewer_container.addWidget(self.info_label)

        # Widget para mostrar la escena 3D
        self.plotter = QtInteractor(self)
        viewer_container.addWidget(self.plotter.interactor)

        # ---- Estructuras auxiliares ----
        self.original_colors = {}       # {patch_name: (r,g,b)}
        self.selected_patches = set()   # Parches seleccionados
        self.actors = {}                # {patch_name: vtkActor}
        self.checkboxes = {}            # {patch_name: QCheckBox}
        self.hovered_patch = None       # Último patch resaltado por hover

        # Picker de VTK para clic y hover
        self.picker = vtkPropPicker()

        # ---- Cargar la malla ----
        self.load_and_plot_mesh('interfaz')      # <--------- CARPETA DONDE ESTAN LOS VTK    

        # Inicializamos el interactor
        self.plotter.interactor.Initialize()

        # Activar selección y hover
        self.enable_patch_selection()
        self.enable_hover_preview()

    def load_and_plot_mesh(self, base_folder):
        """
        Recorre la carpeta indicada, carga los archivos .vtk correspondientes a los patches,
        y los añade a la escena con colores aleatorios.
        """
        if not os.path.isdir(base_folder):
            print(f"Carpeta no encontrada: {base_folder}")
            return

        for root, dirs, files in os.walk(base_folder):
            for file in files:
                if file.endswith(".vtk"):
                    filepath = os.path.join(root, file)
                    patch_name = os.path.basename(root)  # <-----  DEFINE CUAL ES EL PATCH NAME
                    try:
                        # Leer el mesh VTK con PyVista
                        mesh = pv.read(filepath)
                        # Genera color aleatorio
                        color = (random.random(), random.random(), random.random())
                        self.original_colors[patch_name] = color

                        # Agregar al plotter
                        actor = self.plotter.add_mesh(mesh, color=color, name=patch_name, pickable=True)
                        # Guarda referencia
                        self.actors[patch_name] = actor

                        # Crear checkbox para mostrar/ocultar en el panel lateral
                        checkbox = QCheckBox(patch_name)
                        checkbox.setChecked(True)
                        checkbox.stateChanged.connect(lambda state, name=patch_name: self.toggle_patch_visibility(name, state))
                        self.sidebar_layout.addWidget(checkbox)
                        self.checkboxes[patch_name] = checkbox

                    except Exception as e:
                        print(f"Error leyendo {filepath}: {e}")

        self.plotter.add_axes()
        self.plotter.set_background('white')
        self.plotter.camera_position = 'iso'

    def toggle_patch_visibility(self, patch_name, state):
        """Muestra u oculta un patch según el estado del checkbox."""
        actor = self.actors.get(patch_name)
        if actor:
            actor.SetVisibility(state == 2)  # 2 = Checked
            self.plotter.render()

    def enable_patch_selection(self):
        """Selecciona/deselecciona patches completos con clic izquierdo."""
        def on_left_click(obj, event):
            click_pos = self.plotter.interactor.GetEventPosition()
            self.picker.Pick(click_pos[0], click_pos[1], 0, self.plotter.renderer)

            actor = self.picker.GetActor()
            if actor is None:
                return

            # Buscar patch por actor
            patch_name = next((name for name, act in self.actors.items() if act == actor), None)
            
            # El usuario toca con un click para seleccionar al patch,
            #  y con otro click lo deselecciona:
            
            if patch_name:
                if patch_name in self.selected_patches: # Si está seleccionado 
                    # Restaurar color original
                    actor.GetProperty().SetColor(self.original_colors[patch_name])
                    self.selected_patches.remove(patch_name)
                else:
                    # Resaltar en amarillo
                    actor.GetProperty().SetColor(1, 1, 0)
                    # Agregar a selected_patches
                    self.selected_patches.add(patch_name)

                # Actualiza el QLabel con la lista de patches seleccionados:
                seleccionados = ", ".join(self.selected_patches) if self.selected_patches else "ninguno"
                self.info_label.setText(f"Patches seleccionados: {seleccionados}")
                self.plotter.render()

        # Conecta evento de clic:
        self.plotter.iren.add_observer("LeftButtonPressEvent", on_left_click)

    def enable_hover_preview(self):
        """Resalta temporalmente un patch cuando el mouse pasa por encima."""
        def on_mouse_move(obj, event):
            pos = self.plotter.interactor.GetEventPosition()
            self.picker.Pick(pos[0], pos[1], 0, self.plotter.renderer)
            actor = self.picker.GetActor()

            # Si ya había un patch resaltado, restaurarlo (si no está seleccionado)
            if self.hovered_patch and self.hovered_patch not in self.selected_patches:
                self.actors[self.hovered_patch].GetProperty().SetColor(self.original_colors[self.hovered_patch])
                self.hovered_patch = None

            if actor:
                patch_name = next((name for name, act in self.actors.items() if act == actor), None)
                if patch_name and patch_name not in self.selected_patches:
                    actor.GetProperty().SetColor(1, 0.5, 0)  # Naranja para hover
                    self.hovered_patch = patch_name

            self.plotter.render()

        # Conecta evento de movimiento:
        self.plotter.iren.add_observer("MouseMoveEvent", on_mouse_move)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
