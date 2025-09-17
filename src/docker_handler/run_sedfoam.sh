source /usr/lib/openfoam/openfoam2312/etc/bashrc


# Cambia al directorio del caso
cd /case

blockMesh

# # Check if the setFieldsDict file exists
# if [ -f "system/setFieldsDict" ]; then
#     echo "setFieldsDict found. Running setFields..."
#     setFields
# else
#     echo "setFieldsDict not found. Skipping setFields."
# fi

# # create the intial time folder
# cp -r 0_org 0

# funkySetFields -time 0

# run sedFoam
sedFoam_rbgh