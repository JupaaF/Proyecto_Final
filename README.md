# Proyecto Final - Interfaz para Simulaciones Hidrosedimentológicas

Este repositorio contiene el proyecto final de carrera de **Martina Varrone** y **Juan Pablo Fernandez**. El objetivo principal es ofrecer una herramienta de software que simplifica la ejecución de simulaciones hidrosedimentológicas mediante una interfaz gráfica de usuario (GUI) intuitiva.

## Descripción General

La aplicación permite a los usuarios configurar y lanzar simulaciones de Dinámica de Fluidos Computacional (CFD) sin necesidad de tener conocimientos avanzados sobre la estructura de archivos de OpenFOAM o de instalarlo directamente en su sistema. Para lograrlo, el proyecto se apoya en dos componentes clave:

1.  **Interfaz Gráfica de Usuario (GUI):** Desarrollada con `PySide6`, ofrece un asistente que guía al usuario a través de la selección de plantillas de simulación y la configuración de parámetros clave.
2.  **Ejecución en Contenedores:** Utiliza **Docker** para ejecutar las simulaciones de OpenFOAM en un entorno aislado, eliminando la necesidad de que el usuario instale OpenFOAM de forma nativa.

## Arquitectura

El software está diseñado siguiendo el patrón **Modelo-Vista-Controlador (MVC)**, con una estructura de proyecto organizada para separar las responsabilidades.

```
+---------------------+      +----------------------+      +--------------------+
|        Vista        |----->|     Controlador      |----->|       Modelo       |
| (PySide6 UI Files)  |      | (Controllers)        |      | (File & Docker     |
|                     |<-----|                      |<-----|      Handlers)     |
+---------------------+      +----------------------+      +--------------------+
```

*   **`src/`**: Contiene todo el código fuente de la aplicación.
    *   **Modelo:**
        *   `src/docker_handler/dockerHandler.py`: Gestiona la interacción con el motor de Docker para iniciar, supervisar y detener los contenedores de simulación. Se encarga de ejecutar los scripts de OpenFOAM en un entorno aislado.
        *   `src/file_handler/file_handler.py`: Se encarga de generar dinámicamente los archivos de configuración del caso de OpenFOAM. Utiliza un sistema de plantillas para crear los archivos del caso a partir de los parámetros introducidos por el usuario.
        *   `src/file_handler/openfoam_models/`: Contiene clases que representan y manipulan archivos específicos de OpenFOAM (e.g., `controlDict.py`, `U.py`). Cada clase se encarga de un archivo de OpenFOAM y proporciona métodos para modificar sus parámetros.
    *   **Vista:**
        *   `src/interface/ui/`: Contiene los archivos `.ui` de Qt Designer que definen la apariencia de la interfaz. Estos archivos son cargados por los controladores para construir la GUI.
    *   **Controlador:**
        *   `src/interface/controllers/`: Controladores de PySide6 que cargan las vistas, gestionan los eventos de la GUI y conectan las acciones del usuario con la lógica del modelo.
            *   `main_window_controller.py`: Es el controlador principal de la aplicación. Se encarga de la ventana principal y de coordinar los demás controladores.
            *   `simulation_wizard_controller.py`: Es el controlador del asistente de simulación. Guía al usuario a través de los pasos para crear una nueva simulación.
            *   `file_browser_manager.py`: Gestiona el explorador de archivos del caso, permitiendo al usuario navegar por los archivos del caso y abrirlos en el editor de parámetros.
            *   `parameter_editor_manager.py`: Gestiona el editor de parámetros, permitiendo al usuario modificar los parámetros de los archivos de OpenFOAM.
*   **`main.py`**: Punto de entrada de la aplicación, ubicado en `src/main.py`.
*   **`scripts/`**: Contiene scripts de utilidad y automatización que no forman parte del núcleo de la aplicación (por ejemplo, para visualización o tareas de mantenimiento).
*   **`tests/`**: Pruebas unitarias y de integración para asegurar la calidad y el correcto funcionamiento del código.

## Características

*   **Asistente de Configuración Intuitivo:** Un asistente guía al usuario paso a paso en la creación de una nueva simulación, desde la selección de una plantilla hasta la configuración de los parámetros de la simulación.
*   **Sistema de Plantillas Flexibles:** La aplicación utiliza un sistema de plantillas basado en JSON para definir los casos de estudio. Esto permite a los usuarios crear sus propias plantillas y extender la funcionalidad de la aplicación.
*   **Ejecución de Simulaciones en Contenedores Docker:** La aplicación utiliza Docker para ejecutar las simulaciones de OpenFOAM en un entorno aislado. Esto elimina la necesidad de instalar OpenFOAM localmente y garantiza la reproducibilidad de las simulaciones.
*   **Visualización de Resultados Integrada:** La aplicación integra librerías como `VTK` y `PyVista` para visualizar los resultados de la simulación directamente en la interfaz. Los usuarios pueden visualizar la malla, los campos de velocidad y presión, y otros resultados de la simulación.
*   **Carga y Guardado de Simulaciones:** Los usuarios pueden guardar la configuración de una simulación en un archivo JSON y cargarla más tarde para continuar trabajando en ella. Esto facilita la gestión de múltiples simulaciones y la colaboración entre usuarios.
*   **Editor de Parámetros Avanzado:** La aplicación incluye un editor de parámetros que permite a los usuarios modificar los parámetros de los archivos de OpenFOAM de forma interactiva. El editor de parámetros proporciona validación de datos y ayuda contextual para guiar al usuario.

## Flujo de Trabajo

1.  **Crear una Nueva Simulación:** El usuario inicia la aplicación y abre el asistente de simulación. El asistente le guía a través de los siguientes pasos:
    *   **Seleccionar una Plantilla:** El usuario selecciona una plantilla de simulación de la lista de plantillas disponibles.
    *   **Configurar los Parámetros:** El usuario introduce los parámetros de la simulación, como el nombre del caso, la malla y los parámetros de la simulación.
2.  **Generar los Archivos del Caso:** Una vez que el usuario ha completado el asistente, la aplicación genera los archivos del caso de OpenFOAM utilizando el `file_handler`.
3.  **Ejecutar la Simulación:** El usuario ejecuta la simulación haciendo clic en el botón "Ejecutar Simulación". La aplicación utiliza el `docker_handler` para ejecutar la simulación en un contenedor Docker.
4.  **Visualizar los Resultados:** Una vez que la simulación ha finalizado, el usuario puede visualizar los resultados en la interfaz de la aplicación.

## Prerrequisitos

*   Tener **Docker Engine** o **Docker Desktop** instalado y en ejecución en su sistema operativo.
*   Python 3.8+

## Instalación y Uso

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/JupaaF/Proyecto_Final.git
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
    python src/main.py
    ```

---

## Contexto para Asistentes de IA

Esta sección está destinada a proporcionar un resumen rápido para agentes de IA (como Gemini CLI) para facilitar el desarrollo.

*   **Stack tecnológico:** `Python`, `PySide6`, `Docker`, `VTK`, `PyVista`.
*   **Punto de entrada:** `src/main.py`.
*   **Estructura del proyecto:**
    *   `src/main.py`: Inicia la aplicación y muestra la ventana principal.
    *   `src/interface/`: Contiene todo lo relacionado con la GUI.
        *   `ui/`: Archivos de diseño de la interfaz (`.ui`).
        *   `controllers/`: Lógica de la interfaz (controladores de la vista). El `main_window_controller.py` es el principal.
    *   `src/file_handler/`: Módulo para la creación y manipulación de archivos de casos de OpenFOAM.
        *   `file_handler.py`: Orquesta la creación de archivos.
        *   `openfoam_models/`: Clases que representan y manipulan archivos específicos de OpenFOAM (e.g., `controlDict.py`, `U.py`).
    *   `src/docker_handler/`: Lógica para la interacción con Docker.
        *   `dockerHandler.py`: Clase principal para manejar los contenedores de Docker.
        *   `run_openfoam.sh`, `run_transform_UNV.sh`, `run_transform_blockMeshDict.sh`: Scripts que se ejecutan dentro del contenedor.
    *   `VTK/`: Directorio de salida para los archivos de visualización (`.vtk`).
*   **Flujo de trabajo principal:**
    1.  El usuario inicia la app (`python src/main.py`).
    2.  Abre el asistente de simulación desde la ventana principal.
    3.  El usuario introduce los parámetros en el asistente (`simulation_wizard_controller.py`).
    4.  Al finalizar, los datos se usan para generar los archivos del caso a través de `file_handler.py`.
    5.  `dockerHandler.py` se utiliza para iniciar un contenedor Docker que ejecuta la simulación de OpenFOAM con los archivos generados.
    6.  Los resultados se guardan en el directorio `VTK/`.
*   **Testing:**
    *   Los tests se encuentran en el directorio `tests/`.
    *   Se utilizan `pytest` para ejecutar los tests.
    *   Para ejecutar los tests, corra `pytest` en la raíz del proyecto.

---
*Este proyecto es el resultado del trabajo de final de carrera de Martina Varrone y Juan Pablo Fernandez.*