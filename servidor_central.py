import pyodbc  # Importa pyodbc para conectar con SQL Server
from flask import Flask, request, jsonify  # Importa Flask y otras utilidades para manejar solicitudes HTTP
from datetime import datetime  # Importa datetime para manejar fechas y horas
from auths import autenticar_clave_api  # Importa el decorador de autenticación desde auths.py

# Crea una instancia de la aplicación Flask
app = Flask(__name__)

# Función para obtener una conexión a la base de datos SQL Server
def obtener_conexion_bd():
    # Configura la conexión a SQL Server usando pyodbc
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'  # Especifica el controlador ODBC para SQL Server
        'SERVER=localhost;'  # Nombre o dirección IP del servidor SQL Server
        'DATABASE=logsdb;'  # Nombre de la base de datos
        'UID=tu_usuario;'  # Usuario para conectarse a la base de datos
        'PWD=tu_contraseña;'  # Contraseña para conectarse a la base de datos
    )
    return conn

# Ruta para manejar las solicitudes GET y POST en /logs
@app.route('/logs', methods=['GET', 'POST'])
@autenticar_clave_api  # Aplica el decorador de autenticación a esta ruta
def manejar_logs():
    if request.method == 'GET':
        return obtener_logs()  # Maneja las solicitudes GET
    elif request.method == 'POST':
        return registrar_log()  # Maneja las solicitudes POST

# Función para manejar las solicitudes GET y devolver los logs almacenados
def obtener_logs():
    # Obtiene los parámetros de consulta de la URL
    fecha_inicio = request.args.get('fechaInicio')
    fecha_fin = request.args.get('fechaFin')
    nombre_servicio = request.args.get('nombreServicio')

    # Construye la consulta SQL y una lista de parámetros para los filtros
    consulta = 'SELECT * FROM logs WHERE 1=1'
    parametros = []

    if fecha_inicio:
        try:
            # Convierte la fecha de inicio a un formato adecuado para la consulta SQL
            fecha_inicio_parseada = datetime.strptime(fecha_inicio, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
            parametros.append(fecha_inicio_parseada)
            consulta += ' AND timestamp >= ?'
        except ValueError:
            return jsonify({"error": "Formato de fecha de inicio inválido. Use YYYY-MM-DD"}), 400

    if fecha_fin:
        try:
            # Convierte la fecha de fin a un formato adecuado para la consulta SQL
            fecha_fin_parseada = datetime.strptime(fecha_fin, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
            parametros.append(fecha_fin_parseada)
            consulta += ' AND timestamp <= ?'
        except ValueError:
            return jsonify({"error": "Formato de fecha de fin inválido. Use YYYY-MM-DD"}), 400

    if nombre_servicio:
        # Añade el filtro por nombre de servicio si se proporciona
        parametros.append(nombre_servicio)
        consulta += ' AND nombre_servicio = ?'

    try:
        # Conecta a la base de datos y ejecuta la consulta
        conn = obtener_conexion_bd()
        cursor = conn.cursor()
        cursor.execute(consulta, parametros)
        logs = cursor.fetchall()

        # Retorna los logs en formato JSON
        return jsonify([dict(ix) for ix in logs]), 200
    except Exception as e:
        # Maneja cualquier error que ocurra durante la consulta
        print(e)
        return jsonify({"error": "Error consultando los logs"}), 500

# Función para manejar las solicitudes POST y almacenar un nuevo log
def registrar_log():
    # Obtiene el log en formato JSON del cuerpo de la solicitud
    log = request.get_json()
    if not log:
        return jsonify({"error": "Formato de log inválido"}), 400

    # Extrae los campos del log
    timestamp = log.get('timestamp')
    nombre_servicio = log.get('nombre_servicio')
    nivel_log = log.get('nivel_log')
    mensaje = log.get('mensaje')
    recibido_en = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    if not all([timestamp, nombre_servicio, nivel_log, mensaje]):
        return jsonify({"error": "Faltan campos en el log"}), 400

    try:
        # Conecta a la base de datos y crea la tabla de logs si no existe
        conn = obtener_conexion_bd()
        cursor = conn.cursor()
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='logs' AND xtype='U')
            CREATE TABLE logs (
                id INT IDENTITY(1,1) PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                nombre_servicio NVARCHAR(100) NOT NULL,
                nivel_log NVARCHAR(50) NOT NULL,
                mensaje NVARCHAR(MAX) NOT NULL,
                recibido_en DATETIME NOT NULL
            )
        ''')
        # Inserta el nuevo log en la tabla
        cursor.execute('INSERT INTO logs (timestamp, nombre_servicio, nivel_log, mensaje, recibido_en) VALUES (?, ?, ?, ?, ?)',
                       (timestamp, nombre_servicio, nivel_log, mensaje, recibido_en))
        conn.commit()

        # Retorna una confirmación de éxito
        return jsonify({"mensaje": "Log recibido"}), 200
    except Exception as e:
        # Maneja cualquier error que ocurra durante la inserción
        print(f"Error insertando el log: {e}")
        return jsonify({"error": "Error guardando el log"}), 500

# Punto de entrada para ejecutar la aplicación Flask
if __name__ == '__main__':
    # Ejecuta la aplicación en modo de depuración en el puerto 8080
    app.run(debug=True, host='0.0.0.0', port=8080)
