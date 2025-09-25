
source /usr/lib/openfoam/openfoam2312/etc/bashrc

# Cambia al directorio del caso
cd /case

decomposePar


mpirun -np 4 snappyHexMesh -parallel -overwrite

reconstructParMesh -constant


# Convertir la nueva malla a formato VTK para visualización
# foamToVTK -region region0
foamToVTK