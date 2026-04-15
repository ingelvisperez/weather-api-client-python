import requests
import json
import time

# Cache para almacenar resultados del clima (clave: ciudad, valor: (datos, timestamp))
CACHE_CLIMA = {}
CACHE_EXPIRATION_HOURS = 1  # 1 hora en segundos
CACHE_EXPIRATION_SECONDS = CACHE_EXPIRATION_HOURS * 3600


def obtener_coordenadas(ciudad):
    """
    Obtiene las coordenadas geográficas de una ciudad usando la API de geocodificación de Open-Meteo.

    Esta función valida la entrada del usuario, realiza una petición HTTP a la API
    de Open-Meteo para geocodificar el nombre de la ciudad, y extrae las coordenadas
    (latitud y longitud) junto con el nombre oficial de la ciudad. Maneja diversos
    tipos de errores como timeouts, problemas de conexión, respuestas inválidas
    y ciudades no encontradas.

    Args:
        ciudad (str): Nombre de la ciudad a buscar. Debe ser una cadena no vacía
                     después de eliminar espacios en blanco. Ejemplos: "Madrid",
                     "Nueva York", "São Paulo".

    Returns:
        tuple or None: Una tupla de tres elementos (nombre_oficial, latitud, longitud)
                      si la ciudad se encuentra correctamente. Las coordenadas son
                      números flotantes. Retorna None si ocurre algún error, como
                      ciudad no encontrada, problemas de red o datos inválidos.

    Example:
        >>> obtener_coordenadas("Madrid")
        ('Madrid', 40.4168, -3.7038)

        >>> obtener_coordenadas("CiudadInexistente")
        Ciudad 'CiudadInexistente' no encontrada
        None

    Notas para desarrolladores:
        - La función utiliza un timeout de 10 segundos para evitar cuelgues.
        - Valida rangos geográficos implícitamente a través de la API.
        - Imprime mensajes de error en consola para depuración.
        - Depende de la librería 'requests' para peticiones HTTP.
        - La API devuelve resultados en español por configuración.
    """
    # Validar entrada
    if not ciudad or not isinstance(ciudad, str):
        print("Error: Nombre de ciudad inválido")
        return None

    ciudad = ciudad.strip()
    if not ciudad:
        print("Error: Nombre de ciudad vacío")
        return None

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": ciudad,
        "count": 1,
        "language": "es",
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Error: Timeout al conectar con la API de geocodificación")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Problema de conexión a internet")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP en geocodificación: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición de coordenadas: {e}")
        return None

    try:
        data = response.json()
    except ValueError:
        print("Error: Respuesta de API no es JSON válido")
        return None

    results = data.get("results", [])
    if not results:
        print(f"Ciudad '{ciudad}' no encontrada")
        return None

    city_data = results[0]
    name = city_data.get("name")
    latitude = city_data.get("latitude")
    longitude = city_data.get("longitude")

    if name is None or latitude is None or longitude is None:
        print("Error: Datos de ciudad incompletos en la respuesta")
        return None

    return name, latitude, longitude


def obtener_temperatura(latitud, longitud):
    """
    Obtiene la temperatura actual de una ubicación usando la API de Open-Meteo.

    Args:
        latitud (float): Latitud de la ubicación.
        longitud (float): Longitud de la ubicación.

    Returns:
        float or None: Temperatura en Celsius si se obtiene correctamente,
                      None si hay error.
    """
    # Validar entradas
    if not isinstance(latitud, (int, float)) or not isinstance(longitud, (int, float)):
        print("Error: Coordenadas inválidas")
        return None

    # Validar rangos geográficos
    if not (-90 <= latitud <= 90) or not (-180 <= longitud <= 180):
        print("Error: Coordenadas fuera de rango")
        return None

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitud,
        "longitude": longitud,
        "current_weather": True
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Error: Timeout al obtener datos del clima")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Problema de conexión a internet")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP en clima: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición del clima: {e}")
        return None

    try:
        data = response.json()
    except ValueError:
        print("Error: Respuesta de API no es JSON válido")
        return None

    current_weather = data.get("current_weather")
    if not current_weather:
        print("Error: Datos del clima no disponibles")
        return None

    temperature = current_weather.get("temperature")
    if temperature is None:
        print("Error: Temperatura no disponible en la respuesta")
        return None

    return temperature


def celsius_a_fahrenheit(celsius):
    """
    Convierte una temperatura de grados Celsius a Fahrenheit.

    Args:
        celsius (float or int): Temperatura en grados Celsius.

    Returns:
        float or None: Temperatura en grados Fahrenheit, o None si la entrada es inválida.
    """
    if not isinstance(celsius, (int, float)):
        print("Error: Temperatura debe ser un número")
        return None

    return (celsius * 9/5) + 32


def obtener_clima_con_cache(ciudad):
    """
    Obtiene los datos del clima de una ciudad con almacenamiento en caché durante 1 hora.

    Esta función verifica si los datos del clima para la ciudad especificada están
    almacenados en caché y aún son válidos (menos de 1 hora de antigüedad). Si los
    datos son válidos, los devuelve directamente del caché. De lo contrario, obtiene
    nuevos datos de la API, los almacena en caché y los devuelve.

    Args:
        ciudad (str): Nombre de la ciudad para la cual obtener el clima.

    Returns:
        dict or None: Diccionario con los datos del clima en formato:
                     {
                         "nombre_ciudad": str,
                         "temperatura_celsius": float,
                         "temperatura_fahrenheit": float
                     }
                     Retorna None si ocurre un error.

    Example:
        >>> obtener_clima_con_cache("Madrid")
        {
            "nombre_ciudad": "Madrid",
            "temperatura_celsius": 20.5,
            "temperatura_fahrenheit": 68.9
        }

    Notas para desarrolladores:
        - Utiliza un caché global con expiración de 1 hora.
        - Reduce llamadas a la API para mejorar rendimiento y evitar límites de rate.
        - El caché se almacena en memoria; se pierde al reiniciar la aplicación.
    """
    global CACHE_CLIMA

    # Verificar si hay datos en caché y son válidos
    if ciudad in CACHE_CLIMA:
        datos_cache, timestamp = CACHE_CLIMA[ciudad]
        if time.time() - timestamp < CACHE_EXPIRATION_SECONDS:
            print(f"Usando datos en caché para '{ciudad}' (válidos por {CACHE_EXPIRATION_HOURS} hora)")
            return datos_cache
        else:
            # Datos expirados, eliminar del caché
            del CACHE_CLIMA[ciudad]

    # Obtener nuevos datos
    datos_ciudad = obtener_coordenadas(ciudad)
    if not datos_ciudad:
        return None

    nombre, lat, lon = datos_ciudad

    temperatura_c = obtener_temperatura(lat, lon)
    if temperatura_c is None:
        return None

    temperatura_f = celsius_a_fahrenheit(temperatura_c)
    if temperatura_f is None:
        return None

    resultado = {
        "nombre_ciudad": nombre,
        "temperatura_celsius": temperatura_c,
        "temperatura_fahrenheit": round(temperatura_f, 2)
    }

    # Almacenar en caché
    CACHE_CLIMA[ciudad] = (resultado, time.time())
    print(f"Datos obtenidos de la API y almacenados en caché para '{ciudad}'")

    return resultado


def main():
    """
    Función principal de la aplicación del clima.

    Esta función ejecuta el flujo completo de la aplicación: solicita al usuario
    el nombre de una ciudad, obtiene sus coordenadas geográficas mediante la API
    de Open-Meteo, recupera la temperatura actual, la convierte a Fahrenheit,
    y muestra los resultados en formato JSON. Además, registra los resultados
    en un archivo para su posterior análisis.

    La función maneja errores de entrada, problemas de conexión y excepciones
    inesperadas, proporcionando mensajes informativos al usuario.

    Args:
        Ninguno. La función no recibe parámetros; obtiene la entrada del usuario
        de forma interactiva.

    Returns:
        Ninguno. La función no retorna valores; imprime resultados en consola
        y registra en archivo.

    Example:
        >>> main()  # Llamada interactiva
        Ingrese el nombre de una ciudad: Madrid

        Resultado en JSON:
        {
          "nombre_ciudad": "Madrid",
          "temperatura_celsius": 20.5,
          "temperatura_fahrenheit": 68.9
        }
        Resultado registrado en 'resultados_clima.json'

    Notas para desarrolladores:
        - La función es interactiva y espera entrada del usuario.
        - Maneja excepciones como KeyboardInterrupt para cancelaciones.
        - Registra resultados en 'resultados_clima.json' en modo append.
        - Depende de las funciones auxiliares: obtener_coordenadas,
          obtener_temperatura y celsius_a_fahrenheit.
    """
    try:
        ciudad = input("Ingrese el nombre de una ciudad: ").strip()

        if not ciudad:
            print("Error: Por favor, ingrese un nombre de ciudad válido")
            return

        resultado = obtener_clima_con_cache(ciudad)
        if not resultado:
            return

        print("\nResultado en JSON:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

        # Registrar en archivo (como se menciona en el README)
        try:
            with open("resultados_clima.json", "a", encoding="utf-8") as f:
                json.dump(resultado, f, ensure_ascii=False)
                f.write("\n")
            print("Resultado registrado en 'resultados_clima.json'")
        except IOError as e:
            print(f"Advertencia: No se pudo registrar en archivo: {e}")

    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario")
    except Exception as e:
        print(f"Error inesperado: {e}")


if __name__ == "__main__":
    main()