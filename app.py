from flask import Flask, render_template, request
import os
import mysql.connector
from datetime import datetime
import socket
import sys
import platform

app = Flask(__name__)

def get_db_connection():
    """
    Establece conexión a la base de datos MySQL utilizando variables de entorno.
    Retorna None si no se puede conectar o si DB_HOST es 'localhost'
    """
    db_host = os.getenv('DB_HOST', 'localhost')
    
    if db_host != 'localhost':
        try:
            conn = mysql.connector.connect(
                host=db_host,
                port=os.getenv('DB_PORT', '3306'),
                user=os.getenv('DB_USER', 'db_user'),
                password=os.getenv('DB_PASSWORD', 'db_password'),
                database=os.getenv('DB_NAME', 'db_name'),
                connect_timeout=5
            )
            return conn
        except mysql.connector.Error as e:
            print(f"Error de conexión a BD: {e}")
            return None
    return None

def get_system_info():
    """Recopila información detallada del sistema y entorno"""
    return {
        'hostname': socket.gethostname(),
        'ip_address': socket.gethostbyname(socket.gethostname()),
        'python_version': sys.version,
        'platform': platform.platform(),
        'working_directory': os.getcwd(),
        'flask_version': Flask.__version__
    }

@app.route('/')
def index():
    """Endpoint principal que muestra información de depuración del sistema"""
    # Información de la aplicación desde variables de entorno
    app_info = {
        'title': os.getenv('TITLE', 'Aplicación Sin Título'),
        'microservice': os.getenv('MICROSERVICE', 'Microservicio No Configurado'),
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'version': os.getenv('VERSION', '1.0.0'),
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Información del sistema
    system_info = get_system_info()
    
    # Información de la base de datos
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', 'No configurado'),
        'user': os.getenv('DB_USER', 'No configurado'),
        'name': os.getenv('DB_NAME', 'No configurado'),
        'status': 'No configurada'
    }
    
    # Verificar conexión a base de datos
    conn = get_db_connection()
    db_tables = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SHOW TABLES')
            tables = cursor.fetchall()
            db_tables = [table[0] for table in tables]
            db_config['status'] = 'Conectada'
            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            db_config['status'] = f'Error: {e}'
    
    # Variables de entorno (excluyendo sensibles)
    env_vars = {}
    for key, value in os.environ.items():
        if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
            env_vars[key] = '*** OCULTO POR SEGURIDAD ***'
        else:
            env_vars[key] = value
    
    # Información de la request HTTP
    request_info = {
        'remote_addr': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'No disponible'),
        'method': request.method,
        'url': request.url
    }
    
    return render_template(
        'index.html',
        app_info=app_info,
        system_info=system_info,
        db_config=db_config,
        db_tables=db_tables,
        env_vars=env_vars,
        request_info=request_info
    )

@app.route('/health')
def health_check():
    """Endpoint simple para verificación de salud del servicio"""
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}

@app.route('/error/<int:error_code>')
def handle_error(error_code):
    """Maneja y muestra páginas de error HTTP personalizadas"""
    error_messages = {
        400: {
            'message': '400 Solicitud Incorrecta',
            'description': 'El servidor no puede procesar la solicitud debido a un error del cliente.'
        },
        401: {
            'message': '401 No Autorizado',
            'description': 'Se requiere autenticación para acceder al recurso.'
        },
        403: {
            'message': '403 Acceso Denegado',
            'description': 'El cliente no tiene permisos para acceder a este recurso.'
        },
        404: {
            'message': '404 Recurso No Encontrado',
            'description': 'La página o recurso solicitado no existe en el servidor.'
        },
        409: {
            'message': '409 Conflicto',
            'description': 'La solicitud entra en conflicto con el estado actual del servidor.'
        },
        500: {
            'message': '500 Error Interno del Servidor',
            'description': 'Error interno en el servidor. Contacte al administrador.'
        },
        501: {
            'message': '501 No Implementado',
            'description': 'El servidor no soporta la funcionalidad solicitada.'
        },
        502: {
            'message': '502 Puerta de Enlace Inválida',
            'description': 'El servidor recibió una respuesta inválida de un servidor upstream.'
        },
        503: {
            'message': '503 Servicio No Disponible',
            'description': 'El servicio no está disponible temporalmente.'
        },
        504: {
            'message': '504 Tiempo de Espera Agotado',
            'description': 'El servidor no recibió respuesta a tiempo de un servidor upstream.'
        },
    }
    
    error = error_messages.get(error_code, {
        'message': f'{error_code} Error Desconocido',
        'description': 'Ha ocurrido un error no especificado.'
    })
    
    return render_template(
        'error.html',
        error_code=error_code,
        message=error['message'],
        description=error['description']
    ), error_code

@app.route('/<path:path>')
def catch_all(path):
    """Captura todas las rutas no definidas y redirige al índice"""
    return index()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

