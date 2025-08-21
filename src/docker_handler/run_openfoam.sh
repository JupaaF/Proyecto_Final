source /usr/lib/openfoam/openfoam2312/etc/bashrc
# cd /case
# ideasUnvToFoam malla.unv
# foamToVTK

# Cambia al directorio del caso
cd /case

blockMesh

# Check if the setFieldsDict file exists
if [ -f "system/setFieldsDict" ]; then
    echo "setFieldsDict found. Running setFields..."
    setFields
else
    echo "setFieldsDict not found. Skipping setFields."
fi

interFoam