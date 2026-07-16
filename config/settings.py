import os

# Server settings
HOST = "127.0.0.1"
PORT = 8000

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Ensure static directory exists
os.makedirs(STATIC_DIR, exist_ok=True)
