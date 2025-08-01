# Proyecto Final - Interfaz para Simulaciones Hidrosedimentológicas

Este repositorio contiene el proyecto final de carrera de **Martina Varrone** y **Juan Pablo Fernandez**. El objetivo principal es ofrecer una herramienta de software que simplifica la ejecución de simulaciones hidrosedimentológicas mediante una interfaz gráfica de usuario (GUI) intuitiva.

## Descripción General

La aplicación permite a los usuarios configurar y lanzar simulaciones de Dinámica de Fluidos Computacional (CFD) sin necesidad de tener conocimientos avanzados sobre la estructura de archivos de OpenFOAM o de instalarlo directamente en su sistema. Para lograrlo, el proyecto se apoya en dos componentes clave:

1.  **Interfaz Gráfica de Usuario (GUI):** Desarrollada con `PySide6`, ofrece un asistente que guía al usuario a través de la selección de plantillas de simulación y la configuración de parámetros clave.
2.  **Ejecución en Contenedores:** Utiliza **Docker** para ejecutar las simulaciones de OpenFOAM en un entorno aislado, eliminando la necesidad de que el usuario instale OpenFOAM de forma nativa.

## Arquitectura

El software está diseñado siguiendo el patrón **Modelo-Vista-Controlador (MVC)**:

*   **Modelo:**
    *   `dockerFiles/dockerHandler.py`: Gestiona la interacción con el motor de Docker para iniciar, supervisar y detener los contenedores de simulación.
    *   `file_handler/file_handler.py`: Se encarga de generar dinámicamente los archivos de configuración del caso de OpenFOAM basándose en las plantillas y los parámetros seleccionados por el usuario.
*   **Vista:**
    *   `interfaz/ui/`: Contiene los archivos `.ui` de Qt Designer.
    *   `interfaz/controllers/`: Controladores de PySide6 que cargan las vistas y gestionan los eventos de la GUI.
*   **Controlador:**
    *   La lógica principal reside en los controladores de la interfaz (`interfaz/controllers/`), que conectan las acciones del usuario en la Vista con las operaciones del Modelo.

## Características

*   **Asistente de Configuración:** Guía intuitiva para preparar una nueva simulación.
*   **Basado en Plantillas:** El usuario puede elegir entre una serie de casos de estudio preconfigurados.
*   **Independencia de la Instalación:** El único prerrequisito es tener Docker instalado y en funcionamiento.
*   **Visualización de Resultados:** Integra librerías como `VTK` y `PyVista` para el análisis de los datos generados.

## Prerrequisitos

*   Tener **Docker Engine** o **Docker Desktop** instalado y en ejecución en su sistema operativo.

## Instalación y Uso

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/Proyecto_Final.git
    ```
2.  **Navegar al directorio del proyecto:**
    ```bash
    cd Proyecto_Final
    ```
3.  **Instalar las dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Ejecutar la aplicación:**
    ```bash
    python main.py
    ```

---

## Contexto para Asistentes de IA

Esta sección está destinada a proporcionar un resumen rápido para agentes de IA (como Gemini CLI) para facilitar el desarrollo.

*   **Stack tecnológico:** `Python`, `PySide6`, `Docker`, `VTK`, `PyVista`.
*   **Punto de entrada:** `main.py`.
*   **Estructura del proyecto:**
    *   `main.py`: Inicia la aplicación y muestra la ventana principal.
    *   `interfaz/`: Contiene todo lo relacionado con la GUI.
        *   `ui/`: Archivos de diseño de la interfaz (`.ui`).
        *   `controllers/`: Lógica de la interfaz (controladores de la vista). El `main_window_controller.py` es el principal.
    *   `file_handler/`: Módulo para la creación y manipulación de archivos de casos de OpenFOAM.
        *   `file_handler.py`: Orquesta la creación de archivos.
        *   `file_class/`: Clases que representan y manipulan archivos específicos de OpenFOAM (e.g., `controlDict.py`, `U.py`).
    *   `dockerFiles/`: Lógica para la interacción con Docker.
        *   `dockerHandler.py`: Clase principal para manejar los contenedores de Docker.
        *   `run_openfoam.sh`, `run_transform.sh`: Scripts que se ejecutan dentro del contenedor.
    *   `VTK/`: Directorio de salida para los archivos de visualización (`.vtk`).
*   **Flujo de trabajo principal:**
    1.  El usuario inicia la app (`main.py`).
    2.  Abre el asistente de simulación desde la ventana principal.
    3.  El usuario introduce los parámetros en el asistente (`simulation_wizard_controller.py`).
    4.  Al finalizar, los datos se usan para generar los archivos del caso a través de `file_handler.py`.
    5.  `dockerHandler.py` se utiliza para iniciar un contenedor Docker que ejecuta la simulación de OpenFOAM con los archivos generados.
    6.  Los resultados se guardan en el directorio `VTK/`.

---
*Este proyecto es el resultado del trabajo de final de carrera de Martina Varrone y Juan Pablo Fernandez.*