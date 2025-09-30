
source /usr/lib/openfoam/openfoam2312/etc/bashrc

# Cambia al directorio del caso
cd /case

# Ejecutar extrudeMesh
extrudeMesh

# Convertir la nueva malla a formato VTK para visualización
foamToVTK -region region0