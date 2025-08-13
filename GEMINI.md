# Gemini Code Assistant Context

## Project Overview

This project is a desktop application for running hydro-sedimentological simulations using OpenFOAM. It provides a user-friendly graphical interface (GUI) built with PySide6 that allows users to configure and run simulations without needing to directly interact with the command line or manage OpenFOAM's complex file structure. The application uses Docker to run the simulations in a containerized environment, which means the user doesn't need to install OpenFOAM locally.

The application follows a Model-View-Controller (MVC) architecture:

*   **Model:** The model is responsible for managing the simulation data and business logic. It consists of two main parts:
    *   `file_handler`: This module is responsible for creating, reading, and writing the OpenFOAM case files. It uses a set of classes that represent the different OpenFOAM dictionaries (e.g., `controlDict`, `fvSchemes`, `fvSolution`).
    *   `docker_handler`: This module is responsible for interacting with the Docker daemon to run the OpenFOAM simulations. It builds the Docker command, mounts the necessary volumes, and executes the simulation script.
*   **View:** The view is the user interface of the application. It is defined in `.ui` files, which are created using Qt Designer.
*   **Controller:** The controller is responsible for handling user input and updating the model and view accordingly. The main controller is `MainWindowController`, which manages the main window and the simulation wizard.

## Building and Running

To build and run the project, you need to have Python and Docker installed.

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the application:**
    ```bash
    python src/main.py
    ```

## Development Conventions

*   **Coding Style:** The project follows the PEP 8 style guide for Python code.
*   **Testing:** The project has a `tests` directory, but it is currently empty. New tests should be added to this directory.
*   **Contribution Guidelines:** There are no explicit contribution guidelines, but the code is well-structured and easy to follow.

## Key Files

*   `src/main.py`: The entry point of the application.
*   `src/interface/controllers/main_window_controller.py`: The main controller of the application. It handles the main window and the simulation wizard.
*   `src/file_handler/file_handler.py`: The main file for managing the OpenFOAM case files.
*   `src/docker_handler/dockerHandler.py`: The main file for interacting with Docker.
*   `src/interface/ui/main_window_dock.ui`: The UI definition for the main window.
*   `src/interface/controllers/simulation_wizard_controller.py`: The controller for the simulation wizard.
*   `requirements.txt`: The list of Python dependencies.
*   `README.md`: The project's README file.
