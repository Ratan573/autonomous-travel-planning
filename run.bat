@echo off
title LangGraph Travel Planning Multi-Agent System
echo ===============================================================
echo     LangGraph Travel Planning Multi-Agent System (FastAPI)
echo ===============================================================
echo.

cd /d "%~dp0"

set "PYTHON_EXE=venv\Scripts\python.exe"
if exist "frontend\venv\Scripts\python.exe" (
    set "PYTHON_EXE=frontend\venv\Scripts\python.exe"
) else if not exist "venv\Scripts\python.exe" (
    echo [!] Virtual environment not found. Creating venv...
    python -m venv venv
    call .\venv\Scripts\pip install -r requirements.txt
)

echo [*] Starting FastAPI Multi-Agent Server on http://127.0.0.1:8000 ...
echo [*] Press Ctrl+C to stop the server anytime.
echo.

%PYTHON_EXE% -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
pause
