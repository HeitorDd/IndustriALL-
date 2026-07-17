"""
Módulo de Inicialização do Sistema IndustriALL

Este script inicializa o servidor FastAPI e hospeda a interface e a API
de otimização do cronograma semanal de manutenção.

Requisitos de Instalação:
    pip install -r requirements.txt

Como Executar:
    - Windows: Duplo clique no atalho "start.bat" na raiz do projeto.
    - Outros: Rode "pip install -r requirements.txt" e então "python app.py".

Acesso no Navegador:
    http://127.0.0.1:8000/
"""

import uvicorn
from fastapi import FastAPI
from routes import solve_routes
from config import settings

app = FastAPI(
    title="IndustriALL - Sistema de Otimização de Manutenção",
    description="Interface de planejamento e escalonamento semanal de manutenção industrial."
)

# Registra os roteadores da API
app.include_router(solve_routes.router)

if __name__ == "__main__":
    print(f"Iniciando o servidor do IndustriALL em http://{settings.HOST}:{settings.PORT}")
    uvicorn.run("app:app", host=settings.HOST, port=settings.PORT, reload=True)
