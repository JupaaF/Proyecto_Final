source /usr/lib/openfoam/openfoam2312/etc/bashrc
# cd /case
# ideasUnvToFoam malla.unv
# foamToVTK

# Cambia al directorio del caso
cd /case

# Asegúrate de que las carpetas existen
mkdir -p constant/polyMesh

# Mueve la malla a la ubicación correcta
mv malla.unv constant/polyMesh/

# Ejecuta ideasUnvToFoam desde la raíz del caso, pasándole el archivo .unv
echo "Ejecutando ideasUnvToFoam..."
ideasUnvToFoam constant/polyMesh/malla.unv

# Ahora, foamToVTK se ejecutará en la raíz del caso
echo "Ejecutando foamToVTK..."
foamToVTK