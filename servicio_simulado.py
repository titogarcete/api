import requests  # Importa la biblioteca para hacer solicitudes HTTP
import json  # Importa la biblioteca para trabajar con JSON
import time  # Importa la biblioteca para manejar tiempos de espera
from datetime import datetime  # Importa datetime para manejar fechas y horas
from dotenv import load_dotenv  # Importa load_dotenv para cargar variables de entorno
import os  # Importa os para interactuar con el sistema operativo

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la clave API desde las variables de entorno
API_KEY = os.getenv('API_KEY')

# Función para generar y enviar un log al servidor central
def generar_log():
    # Crea un diccionario que representa un log con datos como fecha, hora, nombre del servicio, nivel de log y mensaje
    log = {
        "timestamp": datetime.utcnow().isoformat() + "Z",  # Marca de tiempo en formato ISO 8601
        "nombre_servicio": "Servicio1",
        "nivel_log": "INFO",
        "mensaje": "Este es un mensaje de log de ejemplo"
    }

    # Define las cabeceras HTTP, incluyendo la clave API para la autenticación
    cabeceras = {
        'Content-Type': 'application/json',  # Indica que el contenido es JSON
        'x-api-key': API_KEY  # Incluye la clave API para la autenticación
    }

    # Envía una solicitud POST al servidor central con el log
    respuesta = requests.post("http://localhost:8080/logs", data=json.dumps(log), headers=cabeceras)
    # Imprime la respuesta del servidor central
    print(respuesta.json())

# Punto de entrada del script
if __name__ == "__main__":
    while True:
        generar_log()  # Genera y envía un log
        time.sleep(10)  # Espera 10 segundos antes de generar otro log
