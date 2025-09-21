source /usr/lib/openfoam/openfoam2312/etc/bashrc

# Get the number of processors from the first argument
# Default to 1 if not provided, though it should always be > 1 for this script
NUM_PROCS=${1:-1}

# Change to the case directory
cd /case

# Check if the setFieldsDict file exists
if [ -f "system/setFieldsDict" ]; then
    echo "setFieldsDict found. Running setFields..."
    setFields
else
    echo "setFieldsDict not found. Skipping setFields."
fi

# Check if we are actually running in parallel
if [ "$NUM_PROCS" -gt 1 ]; then
    echo "--- Starting parallel execution with $NUM_PROCS processors. ---"

    # Decompose the domain
    echo "Decomposing domain for parallel run..."
    decomposePar
    if [ $? -ne 0 ]; then
        echo "Error: decomposePar failed."
        exit 1
    fi

    # Run the solver in parallel
    echo "Running interFoam in parallel..."
    # Se usa -fileHandler collated para optimizar la E/S, como se recomienda para
    # flujos de trabajo modernos y para reducir el número de archivos de salida.
    mpirun -np "$NUM_PROCS" sedFoam_rbgh -parallel -fileHandler collated

    if [ $? -ne 0 ]; then
        echo "Error: mpirun failed."
        exit 1
    fi

    # Reconstruct the case
    echo "Reconstructing domain..."
    reconstructPar 
    if [ $? -ne 0 ]; then
        echo "Error: reconstructPar failed."
        exit 1
    fi
    
    echo "--- Parallel execution finished successfully. ---"
else
    echo "Warning: This script is intended for parallel execution, but the number of processors is 1."
    # echo "Running in serial mode as a fallback."
    # interFoam
fi

echo "Simulation finished."