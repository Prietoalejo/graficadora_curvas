# function_parser.py
import numpy as np

# Diccionario seguro de funciones matemáticas permitidas
# Solo permitimos funciones de numpy que no tengan efectos secundarios.
SAFE_MATH_FUNCTIONS = {
    'sin': np.sin,
    'cos': np.cos,
    'tan': np.tan,
    'arcsin': np.arcsin,
    'arccos': np.arccos,
    'arctan': np.arctan,
    'arctan2': np.arctan2,
    'sinh': np.sinh,
    'cosh': np.cosh,
    'tanh': np.tanh,
    'sqrt': np.sqrt,
    'log': np.log,      # log natural
    'log10': np.log10,  # log base 10
    'exp': np.exp,
    'power': np.power,  # para potencias, ej: np.power(x, 2)
    'abs': np.abs,
    'pi': np.pi,
    'e': np.e,
    'min': np.minimum,  # np.minimum para arrays
    'max': np.maximum,  # np.maximum para arrays
    'floor': np.floor,
    'ceil': np.ceil,
    # Añade más si consideras que el usuario las necesitará
}

def parse_function(func_str):
    """
    Parsea una cadena de texto de función f(x, y) de forma segura.

    Args:
        func_str (str): La cadena de la función (ej. "x**2 + y**2", "np.sin(x) + np.cos(y)").

    Returns:
        tuple: Una tupla (callable_func, error_message).
               callable_func es una función que acepta (x, y) arrays de NumPy.
               error_message es None si no hay error, o una cadena con el error.
    """
    # Preparar el entorno de ejecución para eval()
    # Solo permitimos 'x', 'y' y las funciones seguras de numpy
    local_vars = {
        'x': None,  # Se reemplazará con el array x en tiempo de ejecución
        'y': None,  # Se reemplazará con el array y en tiempo de ejecución
        'np': np    # Permitimos el acceso a numpy como 'np'
    }
    # Añadimos las funciones seguras directamente al scope local_vars
    local_vars.update(SAFE_MATH_FUNCTIONS)

    # Reemplazar operadores de potencia comunes si el usuario los escribe como ^
    # aunque Python usa **. numpy.power es más robusto.
    parsed_func_str = func_str.replace('^', '**')

    try:
        # Intentamos compilar la expresión primero. Esto ayuda a detectar
        # errores de sintaxis antes de la evaluación real.
        code_obj = compile(parsed_func_str, '<string>', 'eval')

        # Devolvemos una función lambda que evaluará la expresión con x e y (arrays de NumPy)
        # La función eval() se ejecuta en un entorno controlado (globals=None para evitar acceso
        # a globales del módulo, locals=local_vars para las variables permitidas).
        def callable_func(x_array, y_array):
            local_vars['x'] = x_array
            local_vars['y'] = y_array
            return eval(code_obj, {"__builtins__": {}}, local_vars)

        return callable_func, None # No hay error

    except SyntaxError as e:
        return None, f"Error de sintaxis en la función: {e}"
    except NameError as e:
        # Esto ocurre si el usuario intenta usar una función no permitida (ej. 'os.system()')
        return None, f"Nombre no permitido o desconocido en la función: {e}. Asegúrate de usar funciones como np.sin, np.cos, etc."
    except Exception as e:
        # Captura cualquier otro error durante la compilación o evaluación inicial
        return None, f"Error al parsear la función: {e}"

if __name__ == "__main__":
    # Ejemplos de prueba para function_parser.py
    print("--- Pruebas de function_parser.py ---")

    # Prueba 1: Función válida
    func_str_1 = "np.sin(x) + y**2"
    func_1, error_1 = parse_function(func_str_1)
    if func_1:
        x_test = np.array([0, np.pi/2])
        y_test = np.array([1, 2])
        result_1 = func_1(x_test, y_test)
        print(f"'{func_str_1}' -> Resultado para x={x_test}, y={y_test}: {result_1}")
    else:
        print(f"Error al parsear '{func_str_1}': {error_1}")

    # Prueba 2: Función válida con solo x
    func_str_2 = "x**3 - 2*x"
    func_2, error_2 = parse_function(func_str_2)
    if func_2:
        x_test = np.array([1, 2])
        y_test = np.array([0, 0]) # Y debe ser siempre provisto, aunque no se use
        result_2 = func_2(x_test, y_test)
        print(f"'{func_str_2}' -> Resultado para x={x_test}: {result_2}")
    else:
        print(f"Error al parsear '{func_str_2}': {error_2}")

    # Prueba 3: Función inválida (sintaxis)
    func_str_3 = "x** + y"
    func_3, error_3 = parse_function(func_str_3)
    if func_3:
        pass
    else:
        print(f"Error esperado al parsear '{func_str_3}': {error_3}")

    # Prueba 4: Función con nombre no permitido (seguridad)
    func_str_4 = "__import__('os').system('dir')"
    func_4, error_4 = parse_function(func_str_4)
    if func_4:
        pass
    else:
        print(f"Error esperado al parsear '{func_str_4}': {error_4}")

    # Prueba 5: Uso de pow en lugar de np.power
    func_str_5 = "pow(x, 2) + y" # pow es una built-in
    func_5, error_5 = parse_function(func_str_5)
    if func_5:
        x_test = np.array([2])
        y_test = np.array([3])
        result_5 = func_5(x_test, y_test)
        print(f"'{func_str_5}' -> Resultado para x={x_test}, y={y_test}: {result_5}")
    else:
        print(f"Error esperado al parsear '{func_str_5}': {error_5}")