source /usr/lib/openfoam/openfoam2312/etc/bashrc

# Entra en el directorio del caso
cd /case

# Genera la malla
echo "Generando la malla con blockMesh..."
blockMesh

# Post-procesamiento opcional: convierte la malla a formato VTK
echo "Convirtiendo la malla a formato VTK..."
foamToVTK