@echo off
cd /d "%~dp0"

if not exist venv (
    echo Creando virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Instalando dependencias...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo Iniciando Blink Print Proxy en puerto 8073...
python print_proxy.py
pause
