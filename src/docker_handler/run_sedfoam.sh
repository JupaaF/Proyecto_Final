source /usr/lib/openfoam/openfoam2312/etc/bashrc


# Cambia al directorio del caso
cd /case

# # create input file from 1D computation for funkySetFields
# mkdir 1d_profil
# python3 -c "import fluidfoam; fluidfoam.create1dprofil('1D', '.', '1000', 'Y', ['U.a', 'U.b', 'alpha.a', 'k.b', 'p_rbgh', 'omega.b', 'Theta'])"
# ---> ??????????????????

# blockMesh

# Check if the setFieldsDict file exists
if [ -f "system/funkySetFieldsDict" ]; then
    echo "funkySetFieldsDict found. Running funkySetFields..."
    # Initialize the alpha field
    funkySetFields -time 0
else
    echo "funkySetFieldsDict not found. Skipping setFields."
fi

# # create the intial time folder
# cp -r 0_org 0

# run sedFoam
sedFoam_rbgh