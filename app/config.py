import os
import jwt
import time
from typing import Optional

# Variables de entorno para GitHub App (solo lo esencial)
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")  # App ID de la GitHub App (número)
GITHUB_PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY")  # Contenido del archivo PEM o path al archivo
GITHUB_PRIVATE_KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH")  # Path al archivo PEM

# Webhook Configuration (opcional)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "test_secret")
TARGET_USERNAME = os.getenv("TARGET_USERNAME", "codeok")

# Configuración del servidor
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

def get_github_app_id() -> str:
    """Obtiene el App ID de la GitHub App"""
    if not GITHUB_APP_ID:
        return "123456"  # Para desarrollo
    return GITHUB_APP_ID

def get_github_private_key() -> str:
    """Obtiene la private key (desde archivo o variable de entorno)"""
    # Prioridad: 1. Path al archivo, 2. Contenido directo
    if GITHUB_PRIVATE_KEY_PATH:
        try:
            with open(GITHUB_PRIVATE_KEY_PATH, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise Exception(f"Archivo de clave privada no encontrado: {GITHUB_PRIVATE_KEY_PATH}")
        except Exception as e:
            raise Exception(f"Error leyendo archivo de clave privada: {e}")
    
    elif GITHUB_PRIVATE_KEY:
        return GITHUB_PRIVATE_KEY
    
    else:
        # Private key de prueba (no válida para producción)
        return """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAvxJdaHqr0Sxbzip7T4Du9Hx1aRPOP9itY9HxLSqFbXn4MX0I
UMMSJ1WzJ4ms4S5PltOHMJnOLuFtlzRkq0Rj4L4QngL9CN0gIPe2relfK88qhgyq
Ha4W6GqJvUFBuEvJivek/bjL/6De3fC+WK+m+PNq6qNqjKHPB7NYnsgYbDdSH2Gq
4JPMND3R5oX3VQlq4nshL42D5cQm5Cg+5G5L5r5J5K5L5M5N5O5P5Q5R5S5T5U5V
5W5X5Y5Z5a5b5c5d5e5f5g5h5i5j5k5l5m5n5o5p5q5r5s5t5u5v5w5x5y5z5a5b
5c5d5e5f5g5h5i5j5k5l5m5n5o5p5q5r5s5t5u5v5w5x5y5z5a5b5c5d5e5f5g5h
-----END RSA PRIVATE KEY-----"""

def get_github_installation_id() -> str:
    """Obtiene el Installation ID (no requerido para JWT)"""
    return "987654"  # No necesario para generar JWT

def get_webhook_secret() -> str:
    """Obtiene el secreto del webhook"""
    return WEBHOOK_SECRET

def get_target_username() -> str:
    """Obtiene el usuario objetivo"""
    return TARGET_USERNAME

def get_server_config() -> tuple[str, int]:
    """Get server configuration"""
    return HOST, PORT
