from pathlib import Path

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QComboBox, QHBoxLayout, QGroupBox, QMessageBox, QScrollArea)
from PySide6.QtGui import QIntValidator, QDoubleValidator, QFont

class ParameterEditorManager:
    """
    Gestiona la creación y actualización de la interfaz de usuario para la edición de parámetros.

    Esta clase se encarga de generar dinámicamente widgets de PySide6 (como QLineEdit,
    QComboBox, etc.) basados en un diccionario de parámetros extraído de un archivo.
    Permite al usuario modificar estos parámetros y guardarlos de nuevo en el archivo
    correspondiente.
    """
    def __init__(self, scroll_area: QScrollArea, file_handler, get_vtk_patch_names_func):
        """
        Inicializa el gestor del editor de parámetros.

        Args:
            scroll_area (QScrollArea): El QScrollArea donde se mostrarán los widgets de parámetros.
            file_handler: Una instancia de una clase controladora de archivos que debe
                          implementar `get_editable_parameters` y `modify_parameters`.
            get_vtk_patch_names_func : Una lista con los nombres de los patches
                                       (fronteras) obtenidos de un archivo VTK.
        """
        self.scroll_area = scroll_area
        self.file_handler = file_handler
        self.get_vtk_patch_names = get_vtk_patch_names_func
        self.parameter_widgets = {}  # Almacena los widgets generados para cada parámetro.
        self.current_file_path = None  # Ruta del archivo que se está editando actualmente.

    def open_parameters_view(self, file_path: Path):
        """
        Crea y muestra la vista del editor de parámetros para un archivo específico.

        Si ya hay un archivo abierto, intenta guardar los parámetros pendientes antes de
        abrir el nuevo. Luego, lee los parámetros editables del archivo especificado
        y genera la interfaz de usuario correspondiente.

        Args:
            file_path (Path): La ruta al archivo cuyos parámetros se van a editar.
        """
        # Guarda automáticamente los parámetros del archivo anterior antes de cambiar.
        if self.current_file_path and self.current_file_path != file_path:
            if not self.save_parameters():
                return  # Si el guardado falla (p.ej., por validación), aborta.

        self.current_file_path = file_path
        self.parameter_widgets.clear()
        
        # El título se establece en el dock, que es el padre del scroll area
        if self.scroll_area.parentWidget() and self.scroll_area.parentWidget().parentWidget():
            dock_widget = self.scroll_area.parentWidget().parentWidget()
            dock_widget.setWindowTitle(f"Editor de parámetros - {file_path.name}")


        # Contenedor principal para los widgets de parámetros.
        container = QWidget()
        layout = QVBoxLayout(container)
        form_layout = QFormLayout()

        # Obtiene los parámetros editables del archivo a través del file_handler.
        dict_parameters = self.file_handler.get_editable_parameters(file_path)

        if not dict_parameters:
            form_layout.addRow(QLabel("Este archivo no tiene parámetros editables."))
        else:
            # Itera sobre cada parámetro y crea el widget correspondiente.
            for param_name, param_props in dict_parameters.items():
                label = QLabel(param_props.get('label', param_name))
                label.setToolTip(param_props.get('tooltip', ''))
                widget = self._create_widget_for_parameter(param_props)
                form_layout.addRow(label, widget)
                self.parameter_widgets[param_name] = (widget, param_props)

        layout.addLayout(form_layout)
        
        # Ajusta el tamaño mínimo horizontal del contenedor para que quepan todos los widgets.
        # container.setMinimumWidth
        self.scroll_area.setMinimumWidth(form_layout.sizeHint().width() + 40)

        # Limpia el widget anterior del scroll area antes de establecer el nuevo.
        if self.scroll_area.widget():
            self.scroll_area.widget().deleteLater()
        
        self.scroll_area.setWidget(container)

    def save_parameters(self) -> bool:
        """
        Recopila los valores de los widgets de la UI, los valida y los guarda en el archivo.

        Itera sobre todos los widgets de parámetros creados, extrae sus valores actuales
        y los convierte al tipo de dato esperado. Si todos los valores son válidos,
        llama al `file_handler` para que escriba los cambios en el archivo.

        Returns:
            bool: True si los parámetros se guardaron correctamente o si no había nada que
                  guardar. False si ocurrió un error de validación.
        """
        if not self.current_file_path:
            return True

        new_params = {}
        # Recorre los widgets para obtener los nuevos valores.
        for param_name, (widget, props) in self.parameter_widgets.items():
            widget_type = props.get('type', 'string')
            try:
                # Extrae el valor del widget según su tipo.
                if widget_type == 'vector':
                    new_params[param_name] = self._get_vector_from_widget(widget)
                elif widget_type == 'patches':
                    new_params[param_name] = self._get_patches_from_widget(widget, props)
                elif widget_type == 'choice_with_options':
                    new_params[param_name] = self._get_choice_with_options_from_widget(widget, props)
                elif widget_type == 'choice':
                    new_params[param_name] = widget.currentData()
                elif widget_type == 'integer':
                    new_params[param_name] = int(widget.text())
                elif widget_type == 'float':
                    new_params[param_name] = float(widget.text())
                else:  # 'string' y otros casos por defecto.
                    new_params[param_name] = widget.text()
            except ValueError:
                # Si la conversión de tipo falla (p.ej., "abc" a int), muestra una advertencia.
                QMessageBox.warning(self.scroll_area, "Valor Inválido",
                                    "Existen valores inválidos. Por favor revise los parámetros.")
                return False

        # Si se recopilaron nuevos parámetros, se guardan en el archivo.
        if new_params:
            self.file_handler.modify_parameters(self.current_file_path, new_params)
        
        return True

    def _get_choice_with_options_from_widget(self, widget, props):
        """
        Extrae los valores de un widget complejo de tipo 'choice_with_options'.

        Este tipo de widget se compone de un QComboBox principal y una serie de
        sub-parámetros que aparecen o desaparecen según la opción seleccionada.

        Args:
            widget (QWidget): El widget contenedor para esta estructura.
            props (dict): Las propiedades del parámetro, incluyendo las opciones.

        Returns:
            list: Una lista de diccionarios, donde cada uno representa un parámetro
                  con su nombre y valor.
        """
        params = []
        layout = widget.layout()
        
        # El primer parámetro es siempre la opción seleccionada en el ComboBox principal.
        main_combo = layout.itemAt(0).widget()
        params.append({
            'param_name': 'solver_selected',  # TODO: Hardcodeado, considerar hacerlo dinámico.
            'value': main_combo.currentData()
        })

        # Encuentra el esquema de los sub-parámetros para la opción actualmente seleccionada.
        param_props_schema = next(
            (opt.get('parameters') for opt in props.get('options', [])
             if main_combo.currentData() == opt.get('name')),
            []
        )

        # Itera sobre los widgets de los sub-parámetros para extraer sus valores.
        for i, param_schema in enumerate(param_props_schema, start=1):
            box = layout.itemAt(i).widget()
            # Asume una estructura HBoxLayout: [QLabel, QWidget_del_parametro]
            param_widget = box.layout().itemAt(1).widget()
            value = self._get_value_from_widget(param_widget, param_schema)

            if value is not None:
                params.append({
                    'param_name': param_schema.get('name'),
                    'value': value
                })
        
        return params

    def _get_vector_from_widget(self, vector_widget: QWidget) -> dict:
        """
        Extrae los componentes x, y, z de un widget de vector.

        Args:
            vector_widget (QWidget): El widget que contiene tres QLineEdit para x, y, z.

        Returns:
            dict: Un diccionario con las claves 'x', 'y', 'z' y sus valores numéricos.
        """
        layout = vector_widget.layout()
        try:
            x = float(layout.itemAt(0).widget().text())
            y = float(layout.itemAt(1).widget().text())
            z = float(layout.itemAt(2).widget().text())
        except (ValueError, AttributeError):
            # En caso de error (texto no numérico, widget no encontrado), retorna un vector nulo.
            return {'x': 0.0, 'y': 0.0, 'z': 0.0}
        
        return {'x': x, 'y': y, 'z': z}

    def _get_patches_from_widget(self, container_widget: QWidget, props_schema: dict) -> list:
        """
        Recopila la configuración de todos los patches (fronteras) desde la UI.

        Args:
            container_widget (QWidget): El widget que contiene los GroupBox de cada patch.
            props_schema (dict): El esquema de configuración para los patches.

        Returns:
            list: Una lista de diccionarios, donde cada uno representa la configuración
                  de un patch.
        """
        patches = []
        layout = container_widget.layout()

        # Itera sobre cada GroupBox, que representa un patch individual.
        for i in range(layout.count()):
            groupbox = layout.itemAt(i).widget()
            if not isinstance(groupbox, QGroupBox): continue

            patch_name_label = groupbox.findChild(QLabel)
            patch_name = patch_name_label.text() if patch_name_label else "unknown_patch"

            form_layout = groupbox.findChild(QFormLayout)
            if not form_layout: continue

            # Extrae el tipo de condición de borde seleccionado (ej. 'fixedValue', 'zeroGradient').
            type_combo = form_layout.itemAt(0, QFormLayout.FieldRole).widget()
            selected_type_name = type_combo.currentData()

            patch_data = {'patchName': patch_name, 'type': selected_type_name}

            # Encuentra el esquema de parámetros para el tipo seleccionado.
            type_options = props_schema.get('schema', {}).get('type', {}).get('options', [])
            parameters_schema = next(
                (opt.get('parameters', []) for opt in type_options if opt.get('name') == selected_type_name),
                []
            )

            # Recorre los widgets de los parámetros y extrae sus valores.
            for idx, param_info in enumerate(parameters_schema, start=1):
                item = form_layout.itemAt(idx, QFormLayout.FieldRole)
                if not (item and item.widget()):
                    print(f"Advertencia: No se encontró widget para '{param_info.get('name')}' en patch '{patch_name}'.")
                    continue
                
                widget = item.widget()
                value = self._get_value_from_widget(widget, param_info)
                if value is not None:
                    patch_data[param_info.get('name')] = value

            patches.append(patch_data)
        return patches

    def _get_value_from_widget(self, widget: QWidget, param_schema: dict):
        """
        Extrae un único valor de un widget, convirtiéndolo al tipo correcto.

        Función auxiliar para generalizar la obtención de datos de QLineEdit,
        QComboBox y otros widgets simples.

        Args:
            widget (QWidget): El widget del cual extraer el valor.
            param_schema (dict): El esquema del parámetro, que incluye su tipo.

        Returns:
            El valor extraído, o None si el widget es inválido.
        """
        param_type = param_schema.get('type')
        value = None

        if isinstance(widget, QComboBox):
            value = widget.currentData()
        elif isinstance(widget, QLineEdit):
            text_value = widget.text()
            try:
                if param_type == 'float':
                    value = float(text_value)
                elif param_type == 'integer':
                    value = int(text_value)
                else:
                    value = text_value
            except ValueError:
                value = text_value  # Si falla la conversión, se mantiene como texto.
        elif hasattr(self, '_get_vector_from_widget') and widget.layout() is not None:
             # Comprueba si es un widget de vector (tiene layout con 3 hijos).
            if widget.layout().count() == 3:
                 value = self._get_vector_from_widget(widget)
        
        return value

    def _create_vector_widget(self, current_value: dict, props:dict) -> QWidget:
        """
        Crea un widget compuesto por tres QLineEdit para editar un vector (x, y, z).

        Args:
            current_value (dict): El valor actual del vector, p.ej., {'x': 1, 'y': 2, 'z': 3}.

        Returns:
            QWidget: El widget contenedor con los tres campos de texto.
        """
        vector_widget = QWidget()
        vector_layout = QHBoxLayout(vector_widget)
        vector_layout.setContentsMargins(0, 0, 0, 0)

        # Asegura que el valor de entrada sea un diccionario para evitar errores.
        safe_current_value = current_value if isinstance(current_value, dict) else {}

        # Crea los QLineEdit para cada componente del vector.
        x_edit = QLineEdit(str(safe_current_value.get('x', 0)))
        y_edit = QLineEdit(str(safe_current_value.get('y', 0)))
        z_edit = QLineEdit(str(safe_current_value.get('z', 0)))

        # Asigna validadores para asegurar que solo se puedan introducir números.
        double_validator = QDoubleValidator()

        if 'min' in props:
            double_validator.setBottom(props['min'])
        if 'max' in props:
            double_validator.setTop(props['max'])

        x_edit.setValidator(double_validator)
        y_edit.setValidator(double_validator)
        z_edit.setValidator(double_validator)

        vector_layout.addWidget(x_edit)
        vector_layout.addWidget(y_edit)
        vector_layout.addWidget(z_edit)

        return vector_widget

    def _create_widget_for_parameter(self, props: dict) -> QWidget:
        """
        Crea el widget apropiado para un parámetro según su tipo.

        Esta es una función fábrica que lee las propiedades de un parámetro (tipo,
        opciones, valor actual) y devuelve el widget de PySide6 más adecuado
        para su edición.

        Args:
            props (dict): Diccionario con las propiedades del parámetro.

        Returns:
            QWidget: El widget generado para el parámetro.
        """
        widget_type = props.get('type', 'string')
        current_value = props.get('current', '')
        widget = None

        # --- Creación de widgets básicos ---
        if widget_type == 'vector':
            widget = self._create_vector_widget(current_value,props=props)
        elif widget_type == 'string':
            widget = QLineEdit(str(current_value))
        elif widget_type == 'float':
            widget = QLineEdit(str(current_value))
            validator = QDoubleValidator()
            if 'min' in props:
                validator.setBottom(props['min'])
            if 'max' in props:
                validator.setTop(props['max'])
            widget.setValidator(validator)
        elif widget_type == 'integer':
            widget = QLineEdit(str(current_value))
            validator = QIntValidator()
            if 'min' in props:
                validator.setBottom(props['min'])
            if 'max' in props:
                validator.setTop(props['max'])
            widget.setValidator(validator)
        
        # --- Creación de QComboBox para opciones ---
        elif widget_type == 'choice':
            widget = QComboBox()
            options = props.get('options', [])
            
            # Soporta tanto listas de diccionarios como diccionarios de diccionarios.
            if isinstance(options, list):
                for option in options:
                    if isinstance(option, dict):
                        widget.addItem(option.get('label', option.get('name')), option.get('name'))
                    else: # Lista de strings simples
                        widget.addItem(str(option), option)
            elif isinstance(options, dict):
                for name, details in options.items():
                    widget.addItem(details.get('label', name), name)
            
            # Establece el valor actual seleccionado.
            if current_value:
                index = widget.findData(current_value)
                if index != -1:
                    widget.setCurrentIndex(index)

        # --- Creación de widgets complejos (anidados) ---
        elif widget_type == 'choice_with_options':
            widget = self._create_choice_with_options_widget(props)
        elif widget_type == 'patches':
            widget = self._create_patches_widget(props)
        
        # --- Widget por defecto ---
        else:
            # Si el tipo no coincide con ninguno de los anteriores, se crea un QLineEdit como fallback.
            widget = QLineEdit(str(current_value))
            
        return widget

    def _create_choice_with_options_widget(self, props: dict) -> QWidget:
        """
        Crea un widget para un parámetro de tipo 'choice_with_options'.

        Este widget consiste en un QComboBox principal que, al cambiar de opción,
        muestra dinámicamente un conjunto diferente de sub-parámetros.

        Args:
            props (dict): Propiedades del parámetro, incluyendo las opciones anidadas.

        Returns:
            QWidget: El widget contenedor.
        """
        current_value = props.get('current', [])
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # --- ComboBox Principal ---
        # Se crea el QComboBox que controlará qué sub-parámetros se muestran.
        main_combo = QComboBox()
        options = props.get('options', [])
        for option in options:
            if isinstance(option, dict):
                main_combo.addItem(option.get('label', option.get('name')), option.get('name'))
        container_layout.addWidget(main_combo)

        # --- Lógica para actualizar sub-parámetros ---
        # Esta función se conectará a la señal `currentIndexChanged` del ComboBox.
        def show_parameters(index):
            # Limpia los widgets de sub-parámetros anteriores para dar paso a los nuevos.
            while container_layout.count() > 1:
                child = container_layout.takeAt(1)
                if child.widget():
                    child.widget().deleteLater()

            # Obtiene el esquema de los nuevos sub-parámetros basado en la selección actual.
            selected_option_name = main_combo.itemData(index)
            parameters_schema = next(
                (opt.get('parameters', []) for opt in options if opt.get('name') == selected_option_name),
                []
            )

            # Comprueba si el valor actual cargado corresponde a la opción seleccionada.
            # Esto es útil para saber si debemos usar los valores actuales o los por defecto.
            is_current_selection = len(current_value) > 0 and current_value[0].get('value') == selected_option_name
            
            # Crea y añade los nuevos widgets de sub-parámetros.
            for param_props in parameters_schema:
                param_name = param_props.get('name')
                
                # Busca el valor actual para este sub-parámetro específico.
                current_sub_value = None
                if is_current_selection:
                    current_sub_value = next(
                        (p.get('value') for p in current_value if p.get('param_name') == param_name),
                        None
                    )
                
                # Decide si usar el valor actual (si existe) o el valor por defecto del esquema.
                value_for_widget = current_sub_value if current_sub_value is not None else param_props.get('default')


                # Prepara un diccionario de propiedades para crear el widget del sub-parámetro.
                sub_props = {
                    'type': param_props.get('type', 'string'),
                    'current': value_for_widget,
                    'options': param_props.get('options', []),
                    'label': param_props.get('label', param_name)
                }
                if param_props.get('min') is not None:
                    sub_props['min'] = param_props.get('min')
                
                if param_props.get('max') is not None:
                    sub_props['max'] = param_props.get('max')
                # Reutiliza la función principal de creación de widgets para mantener la consistencia.
                param_widget = self._create_widget_for_parameter(sub_props)
                
                # Añade el widget y su etiqueta a un layout horizontal para una mejor alineación.
                if param_widget:
                    row_widget = QWidget()
                    hlayout = QHBoxLayout(row_widget)
                    hlayout.addWidget(QLabel(sub_props['label']))
                    hlayout.addWidget(param_widget)
                    container_layout.addWidget(row_widget)
        
        # Conecta la función de actualización a la señal de cambio del ComboBox.
        main_combo.currentIndexChanged.connect(show_parameters)
        
        # Inicializa la vista con los parámetros de la opción seleccionada por defecto.
        # Esto es crucial para que la UI muestre los valores correctos al abrir el archivo.
        if current_value:
            initial_selection = current_value[0].get('value')
            idx = main_combo.findData(initial_selection)
            if idx != -1:
                main_combo.setCurrentIndex(idx)

        # Llama a la función una vez para poblar la UI con los widgets iniciales.
        show_parameters(main_combo.currentIndex())
        return container_widget

    def _create_patches_widget(self, props: dict) -> QWidget:
        """
        Crea la UI para editar las condiciones de borde de todos los patches.

        Genera un QGroupBox para cada patch (frontera de la malla), permitiendo
        configurar su tipo y parámetros asociados.

        Args:
            props (dict): Propiedades del parámetro 'patches'.

        Returns:
            QWidget: El widget contenedor con todos los GroupBox de los patches.
        """
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Obtiene los nombres de los patches y mapea los datos actuales para un acceso rápido.
        patch_names = self.get_vtk_patch_names()
        current_patches_map = {p.get('patchName'): p for p in props.get('current', [])}

        # Itera sobre los nombres de los patches obtenidos del archivo VTK.
        for patch_name in patch_names:
            patch_data = current_patches_map.get(patch_name, {})
            
            # Crea un GroupBox para agrupar visualmente la configuración de un patch.
            patch_groupbox = QGroupBox()
            group_layout = QVBoxLayout(patch_groupbox)

            # Etiqueta con el nombre del patch, en negrita para destacarlo.
            patch_name_label = QLabel(patch_name)
            font = QFont()
            font.setBold(True)
            patch_name_label.setFont(font)
            group_layout.addWidget(patch_name_label)

            patch_form_layout = QFormLayout()
            group_layout.addLayout(patch_form_layout)

            # --- ComboBox para seleccionar el tipo de condición de borde ---
            type_combo = QComboBox()
            type_options = props.get('schema', {}).get('type', {}).get('options', [])
            for option in type_options:
                type_combo.addItem(option.get('label'), option.get('name'))
            
            patch_form_layout.addRow("Tipo:", type_combo)

            # --- Lógica para actualizar los parámetros según el tipo --- #TODO: ver de unificar con la logica del choice_with_options
            # Se usa una función fábrica para capturar el estado (layouts, datos) de cada patch.
            def make_update_params_func(form_layout, combo, options, data):
                def update_value_input_visibility(index):
                    # Limpia los widgets de parámetros anteriores.
                    while form_layout.rowCount() > 1:
                        form_layout.removeRow(1)

                    # Obtiene el esquema de los nuevos parámetros a crear.
                    selected_type_name = combo.itemData(index)
                    parameters_schema = next(
                        (opt.get('parameters', []) for opt in options if opt.get('name') == selected_type_name),
                        []
                    )
                    
                    # Crea y añade los nuevos widgets basados en el esquema.
                    for param_props in parameters_schema:
                        param_name = param_props.get('name')
                        # Usa el valor actual del patch o el valor por defecto del esquema.
                        value = data.get(param_name, param_props.get('default'))
                        
                        sub_props = {
                            'type': param_props.get('type', 'string'),
                            'current': value,
                            'options': param_props.get('options', []),
                            'label': param_props.get('label', param_name)
                        }
                        
                        # Transfiere las propiedades de validación (min/max) al sub-widget.
                        if param_props.get('min') is not None:
                            sub_props['min'] = param_props.get('min')
                        
                        if param_props.get('max') is not None:
                            sub_props['max'] = param_props.get('max')

                        param_widget = self._create_widget_for_parameter(sub_props)
                        if param_widget:
                            form_layout.addRow(sub_props['label'], param_widget)
                return update_value_input_visibility

            # Crea la función de actualización específica para este patch y la conecta.
            update_func = make_update_params_func(patch_form_layout, type_combo, type_options, patch_data)
            type_combo.currentIndexChanged.connect(update_func)

            # Establece el valor inicial del ComboBox y dispara la primera actualización.
            initial_type = patch_data.get('type', props.get('schema', {}).get('type', {}).get('default'))
            if initial_type:
                index = type_combo.findData(initial_type)
                if index != -1:
                    type_combo.setCurrentIndex(index)
            
            # Llama manualmente a la función para poblar la UI con los valores iniciales.
            update_func(type_combo.currentIndex())
            
            container_layout.addWidget(patch_groupbox)

        return container_widget
