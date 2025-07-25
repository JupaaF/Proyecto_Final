#!/bin/bash

# Activa el entorno de OpenFOAM
source /opt/openfoam10/etc/bashrc

# Navega al directorio del caso montado
cd /case

# Ejecuta blockMesh
echo "▶️ Ejecutando blockMesh..."
blockMesh

if [ $? -ne 0 ]; then
    echo "❌ blockMesh falló. Revisar la salida anterior."
    # Muestra los últimos 20 líneas de la salida de blockMesh
    blockMesh | tail -n 20
    read -p "Presiona ENTER para salir del contenedor..."
    exit 1
fi

# Lista el contenido del directorio 0 para verificar los archivos
echo "📁 Contenido del directorio 0 después de blockMesh:"
ls 0

# Ejecuta solver
echo "▶️ Ejecutando solver..."

if [ "$1" -eq 0 ]; then
    interFoam
fi
if [ "$1" -eq 1 ]; then
    sicoFoam
fi

if [ $? -ne 0 ]; then
    echo "❌ solver falló. Revisar la salida anterior."
    read -p "Presiona ENTER para salir del contenedor..."
    exit 1
fi

echo "✅ Simulación de OpenFOAM completada."

# Mantén el contenedor abierto hasta que el usuario presione ENTER
read -p "Presiona ENTER para salir del contenedor..."

exit 0