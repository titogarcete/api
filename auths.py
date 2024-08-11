import os  # Importa el módulo para interactuar con el sistema operativo
from functools import wraps  # Importa wraps para crear decoradores
from flask import request, jsonify  # Importa las funciones necesarias de Flask
from dotenv import load_dotenv  # Importa load_dotenv para cargar variables de entorno desde un archivo .env

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la clave API desde las variables de entorno
API_KEY = os.getenv('API_KEY')

# Definir un decorador para autenticar las solicitudes HTTP
def autenticar_clave_api(f):
    @wraps(f)  # Mantiene la información del decorador original
    def funcion_decorada(*args, **kwargs):
        # Obtiene la clave API de las cabeceras de la solicitud
        clave_api = request.headers.get('x-api-key')
        # Verifica si la clave API es válida
        if clave_api y clave_api == API_KEY:
            return f(*args, **kwargs)  # Si es válida, ejecuta la función decorada
        else:
            # Si no es válida, retorna un mensaje de error y un código 401 (No Autorizado)
            return jsonify({"mensaje": "No autorizado"}), 401
    return funcion_decorada
