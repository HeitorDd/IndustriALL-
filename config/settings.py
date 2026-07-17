import os

# Configurações do servidor
HOST = "127.0.0.1"
PORT = 8000

# Diretórios base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Garante que o diretório static exista
os.makedirs(STATIC_DIR, exist_ok=True)
