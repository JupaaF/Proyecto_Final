source /usr/lib/openfoam/openfoam2312/etc/bashrc

# Get the number of processors from the first argument
# Default to 1 if not provided, though it should always be > 1 for this script
NUM_PROCS=${1:-1}

# Cambia al directorio del caso
cd /case

decomposePar

mpirun -np "$NUM_PROCS" snappyHexMesh -parallel -overwrite

reconstructParMesh -constant

