import sys
import os
import random
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QLabel, QHBoxLayout, QScrollArea, QCheckBox
)
import pyvista as pv
from pyvistaqt import QtInteractor
from vtkmodules.vtkRenderingCore import vtkPropPicker

class GeometryView(QWidget):
    patch_selection_changed = Signal(str, bool)
    deselect_all_patches_requested = Signal()
    def __init__(self, filePath, parent=None):
        super().__init__(parent)
        self.setGeometry(100, 100, 1280, 800)

        # Layout principal horizontal: [Panel lateral | Vista 3D]
        main_layout = QHBoxLayout(self)
        # central_widget = QWidget()
        # central_widget.setLayout(main_layout)

        # ---- Panel lateral con scroll para checkboxes ----
        self.sidebar_widget = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.addWidget(QLabel("Patches:"))

        # --- Agregar botón de deselección ---
        self.deselect_button = QPushButton("Deseleccionar todos")
        self.deselect_button.clicked.connect(self.deselect_all_patches)
        self.sidebar_layout.addWidget(self.deselect_button)

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
        self.load_and_plot_mesh(filePath)      # <--------- CARPETA DONDE ESTAN LOS VTK    

        # Inicializamos el interactor
        self.plotter.interactor.Initialize()

        # Activar selección y hover
        self.enable_patch_selection()
        self.enable_hover_preview()

    def load_and_plot_mesh(self, base_folder):
        """
        Recorre la carpeta indicada, carga los archivos .vtk o .vtp correspondientes a los patches,
        y los añade a la escena con colores aleatorios.
        """
        if not os.path.isdir(base_folder):
            print(f"Carpeta no encontrada: {base_folder}")
            return

        for root, dirs, files in os.walk(base_folder):
            for file in files:
                if file.endswith((".vtk", ".vtp")):
                    filepath = os.path.join(root, file)
                    patch_name, _ = os.path.splitext(file) # <-----  DEFINE CUAL ES EL PATCH NAME
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
                    self.patch_selection_changed.emit(patch_name, False)
                else:
                    # Resaltar en amarillo
                    actor.GetProperty().SetColor(1, 1, 0)
                    # Agregar a selected_patches
                    self.selected_patches.add(patch_name)
                    self.patch_selection_changed.emit(patch_name, True)

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
    
    def deselect_all_patches(self):
        """Deselecciona todos los patches seleccionados."""
        for patch_name in list(self.selected_patches):  # Usamos list() para crear una copia
            actor = self.actors.get(patch_name)
            if actor:
                # Restaurar color original
                actor.GetProperty().SetColor(self.original_colors[patch_name])
        
        # Limpiar el conjunto de seleccionados
        self.selected_patches.clear()
        self.deselect_all_patches_requested.emit()
        
        # Actualizar el label
        self.info_label.setText("Patches seleccionados: ninguno")
        self.plotter.render()

    def get_selected_patches(self):
        return self.selected_patches
        
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
