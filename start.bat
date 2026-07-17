@echo off
title IndustriALL - Otimizador de Cronograma
echo ==========================================================
echo IndustriALL - Verificando e Instalando Dependencias
echo ==========================================================
py -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo Falha ao instalar dependencias com 'py -m pip'. Tentando 'python -m pip'...
    python -m pip install -r requirements.txt
)
echo.
echo ==========================================================
echo Iniciando o Servidor de PCM (FastAPI + Uvicorn)
echo ==========================================================
echo Acesse no navegador: http://127.0.0.1:8000/
echo.
py app.py
if %errorlevel% neq 0 (
    python app.py
)
pause
