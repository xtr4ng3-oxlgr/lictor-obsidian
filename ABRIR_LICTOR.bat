@echo off
title LICTOR
color 4F
chcp 65001 >nul
cd /d "%~dp0"

set PYTHON_CMD=
where py >nul 2>nul
if %errorlevel%==0 set PYTHON_CMD=py -3
if "%PYTHON_CMD%"=="" (
    where python >nul 2>nul
    if %errorlevel%==0 set PYTHON_CMD=python
)
if "%PYTHON_CMD%"=="" (
    echo Python no encontrado.
    echo Instale Python 3.10 o superior desde python.org.
    pause
    exit /b 1
)

%PYTHON_CMD% lictor.py gui
if %errorlevel% neq 0 (
    echo.
    echo LICTOR no pudo iniciar la interfaz grafica.
    echo Ejecute VALIDAR_LICTOR.bat para revisar el entorno.
)
pause
