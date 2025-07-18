import re

def modificar_condicion_borde(ruta_archivo, patch_nombre, campo_a_modificar, nuevo_valor):
    """
    Modifica un campo específico dentro de un patch en un archivo de OpenFOAM,
    preservando la indentación original de las líneas dentro del patch.

    Args:
        ruta_archivo (str): Ruta al archivo de condiciones de borde (ej. '0/U', '0/alpha.water').
        patch_nombre (str): Nombre del patch a modificar (ej. 'inlet', 'outlet').
        campo_a_modificar (str): Nombre del campo dentro del patch a modificar (ej. 'type', 'value').
        nuevo_valor (str): El nuevo valor para el campo (ej. 'fixedValue;', 'uniform (0.5 0 0);').
    """
    try:
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()

        # Patrón para encontrar el bloque del patch, capturando el contenido y la indentación de la primera línea dentro
        # Capturamos también los caracteres antes del nombre del patch para inferir su indentación
        patch_pattern = re.compile(
            rf"(?P<pre_patch_indent>\s*){re.escape(patch_nombre)}\s*\{{\s*\n(?P<patch_content>.*?)\s*}}",
            re.DOTALL
        )
        match_patch = patch_pattern.search(contenido)

        if not match_patch:
            print(f"Error: No se encontró el patch '{patch_nombre}' en el archivo.")
            print("Asegúrate de que el nombre del patch sea exacto y el formato consistente.")
            return

        pre_patch_indent = match_patch.group('pre_patch_indent') # Indentación antes del nombre del patch
        patch_content_original = match_patch.group('patch_content')
        full_patch_block_original = match_patch.group(0)

        # --- Obtener la indentación del contenido del patch ---
        # Buscamos la indentación de la primera línea no vacía dentro del contenido del patch.
        # Esto es crucial para replicar la indentación.
        first_line_match = re.search(r"^\s*([^\n\s].*)", patch_content_original, re.MULTILINE)
        if first_line_match:
            # Extraemos la indentación de la primera línea real del contenido.
            # match.group(0) es la línea completa, match.group(1) es el contenido de la línea sin indentación
            # La diferencia en longitud nos da la indentación.
            indent_level = len(first_line_match.group(0)) - len(first_line_match.group(1))
            # Creamos una cadena de indentación basada en el número de espacios (o tabulaciones)
            base_indent = ' ' * indent_level if indent_level > 0 else ''
        else:
            # Si el patch está vacío o solo tiene saltos de línea, asumimos una indentación predeterminada (ej. 4 espacios)
            base_indent = '    ' # O la que sea común en tus archivos

        # Patrón para encontrar el campo específico dentro del contenido del patch
        campo_pattern = re.compile(
            rf"(\s*{re.escape(campo_a_modificar)}\s*)(.*?);",
            re.DOTALL
        )
        match_campo = campo_pattern.search(patch_content_original)

        if not match_campo:
            print(f"Error: No se encontró el campo '{campo_a_modificar}' dentro del patch '{patch_nombre}'.")
            return

        # Construimos la nueva línea completa con la indentación del campo original
        # match_campo.group(1) ya contiene la indentación y el nombre del campo como estaba originalmente
        old_field_line_full = match_campo.group(0) # Ejemplo: "    value           uniform (0 0 0);"
        new_field_line_content = f"{match_campo.group(1)}{nuevo_valor};" # Ejemplo: "    value           uniform (0.5 0 0);"

        # Reemplazar la línea del campo dentro del contenido del patch
        patch_content_modificado = patch_content_original.replace(
            old_field_line_full,
            new_field_line_content,
            1 # Asegura que solo se reemplace la primera ocurrencia encontrada
        )

        # --- Reconstruir el bloque del patch completo con la indentación deseada ---
        # Dividimos el contenido modificado en líneas y aplicamos la indentación base
        # a cada línea, excepto a la primera si es que el bloque comienza inmediatamente.
        # El .strip() inicial es para quitar posibles saltos de línea iniciales/finales
        # antes de dividir para asegurar que la primera línea no tenga una indentación extra.
        modified_lines = patch_content_modificado.strip().split('\n')
        # Filtramos líneas vacías que puedan haber surgido del split
        modified_lines = [line for line in modified_lines if line.strip()]

        indented_patch_content = "\n".join([f"{base_indent}{line}" for line in modified_lines])

        # Construir el bloque final para reemplazar
        # Aseguramos que el nombre del patch y la llave de apertura estén en su línea
        # y que el contenido indentado esté dentro.
        # Añadimos un salto de línea al final del contenido indentado antes del cierre de llave
        # para imitar el formato común de OpenFOAM.
        new_full_patch_block = (
            f"{pre_patch_indent}{patch_nombre}\n"
            f"{pre_patch_indent}{{\n"
            f"{indented_patch_content}\n"
            f"{pre_patch_indent}}}"
        )

        # Reemplazar el bloque completo del patch en el contenido general del archivo
        contenido_modificado = contenido.replace(
            full_patch_block_original,
            new_full_patch_block
        )

        with open(ruta_archivo, 'w') as f:
            f.write(contenido_modificado)
        print(f"Se modificó el campo '{campo_a_modificar}' del patch '{patch_nombre}' en '{ruta_archivo}', preservando la indentación.")

    except FileNotFoundError:
        print(f"Error: El archivo '{ruta_archivo}' no se encontró.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

# --- EJEMPLO DE USO ---
# Suponiendo que tienes un archivo '0/U' o '0/alpha.water' en tu directorio de trabajo
# Para probar, podrías crear un archivo de ejemplo con el contenido de OpenFOAM de arriba.

# Ejemplo 1: Modificar el valor de 'inlet' en '0/U'
# Asegúrate de que el 'nuevo_valor' incluya el 'uniform' si es un vector o el formato esperado por OpenFOAM.
modificar_condicion_borde('C:/Users/piliv/OneDrive/Documentos/FACU/PFC/Proyecto_Final/Proyecto_Final-1/U', 'inlet', 'value', 'uniform (0.5 0 0)')

# Ejemplo 2: Modificar el tipo de 'outlet' en '0/U'
# modificar_condicion_borde('0/U', 'outlet', 'type', 'fixedValue') # Esto también requerirá añadir un 'value' para que sea válido en OF

# Ejemplo 3: Modificar un campo en un archivo alpha.water
# Asume que tienes un archivo '0/alpha.water' con un 'inlet' patch
# modificar_condicion_borde('0/alpha.water', 'inlet', 'value', 'uniform 1')






def agregar_campo_a_patch(ruta_archivo, patch_nombre, nuevo_campo, nuevo_valor):
    """
    Agrega un nuevo campo con su valor dentro de un patch específico en un archivo de OpenFOAM,
    preservando la indentación original.

    Args:
        ruta_archivo (str): Ruta al archivo de condiciones de borde (ej. '0/U', '0/alpha.water').
        patch_nombre (str): Nombre del patch donde se agregará el campo.
        nuevo_campo (str): Nombre del nuevo campo a agregar (ej. 'fixedInternalValue').
        nuevo_valor (str): El valor para el nuevo campo (ej. 'uniform (0 0 0)').
    """
    try:
        with open(ruta_archivo, 'r') as f:
            contenido = f.read()

        # Patrón para encontrar el bloque del patch, capturando el contenido y la indentación del bloque.
        # También capturamos la indentación antes del nombre del patch.
        patch_pattern = re.compile(
            rf"(?P<pre_patch_indent>\s*){re.escape(patch_nombre)}\s*\{{\s*\n(?P<patch_content>.*?)(?P<closing_brace_indent>\s*)}}",
            re.DOTALL
        )
        match_patch = patch_pattern.search(contenido)

        if not match_patch:
            print(f"Error: No se encontró el patch '{patch_nombre}' en el archivo.")
            print("Asegúrate de que el nombre del patch sea exacto y el formato consistente.")
            return

        pre_patch_indent = match_patch.group('pre_patch_indent')
        patch_content_original = match_patch.group('patch_content')
        closing_brace_indent = match_patch.group('closing_brace_indent') # Esto capturará la indentación de la llave de cierre '}'
        full_patch_block_original = match_patch.group(0)

        # --- Determinar la indentación del contenido del patch ---
        # Buscamos la indentación de la primera línea no vacía dentro del contenido del patch.
        first_line_match = re.search(r"^\s*([^\n\s].*)", patch_content_original, re.MULTILINE)
        if first_line_match:
            indent_level = len(first_line_match.group(0)) - len(first_line_match.group(1))
            base_indent = ' ' * indent_level if indent_level > 0 else ''
        else:
            # Si el patch está vacío, o solo tiene saltos de línea, asumimos una indentación predeterminada.
            # Podría ser la indentación de la llave de cierre más 4 espacios, o simplemente 4 espacios.
            # Optamos por la indentación de la llave de cierre para consistencia si el patch estaba realmente vacío.
            base_indent = closing_brace_indent + ('    ' if closing_brace_indent.strip() == '' else '') # Añade 4 espacios si la indentación de la llave de cierre es solo un salto de línea
            base_indent = base_indent.replace('\n', '') # Aseguramos que no haya un salto de línea aquí

        # Construir la nueva línea del campo con la indentación correcta
        new_field_line = f"{base_indent}{nuevo_campo}{' ' * (15 - len(nuevo_campo) if len(nuevo_campo) < 15 else 1)}{nuevo_valor};"
        # Ajuste de espacios: 15 es un valor arbitrario para alinear, puedes ajustarlo si quieres más orden.

        # --- Insertar el nuevo campo ---
        # La forma más segura de insertar es justo antes de la indentación de la llave de cierre '}'
        # patch_content_original ya no incluye el último salto de línea ni la llave de cierre.
        # Por lo tanto, insertamos el nuevo campo seguido de un salto de línea.
        if patch_content_original.strip(): # Si ya hay contenido, añadir salto de línea antes del nuevo campo
            patch_content_modificado = patch_content_original + "\n" + new_field_line
        else: # Si el patch estaba vacío
            patch_content_modificado = new_field_line

        # --- Reconstruir el bloque del patch completo ---
        # Esto incluye el nombre del patch, las llaves y el contenido modificado.
        # Aseguramos un salto de línea después del contenido para que la llave de cierre vaya en su propia línea.
        new_full_patch_block = (
            f"{pre_patch_indent}{patch_nombre}\n"
            f"{pre_patch_indent}{{\n"
            f"{patch_content_modificado}\n"
            f"{closing_brace_indent}}}" # Usamos la indentación original de la llave de cierre
        )

        # Reemplazar el bloque completo del patch en el contenido general del archivo
        contenido_modificado = contenido.replace(
            full_patch_block_original,
            new_full_patch_block
        )

        with open(ruta_archivo, 'w') as f:
            f.write(contenido_modificado)
        print(f"Se agregó el campo '{nuevo_campo}' al patch '{patch_nombre}' en '{ruta_archivo}', preservando la indentación.")

    except FileNotFoundError:
        print(f"Error: El archivo '{ruta_archivo}' no se encontró.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")


# Este ejemplo agregará un campo 'fixedInternalValue' al patch 'inlet':
agregar_campo_a_patch('C:/Users/piliv/OneDrive/Documentos/FACU/PFC/Proyecto_Final/Proyecto_Final-1/U', 'inlet', 'fixedInternalValue', 'uniform (0 0 0)')

