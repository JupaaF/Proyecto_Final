source /usr/lib/openfoam/openfoam2312/etc/bashrc

# Entra en el directorio del caso
cd /case

# Mueve el archivo blockMeshDict al directorio 'system'
# Esto es crucial porque blockMesh lo busca allí por defecto
echo "Moviendo blockMeshDict a la carpeta system..."
mv blockMeshDict system/

# Genera la malla
echo "Generando la malla con blockMesh..."
blockMesh

# Post-procesamiento opcional: convierte la malla a formato VTK
echo "Convirtiendo la malla a formato VTK..."
foamToVTK