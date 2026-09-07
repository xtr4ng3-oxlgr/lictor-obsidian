@echo off
title LICTOR - Validate
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
    pause
    exit /b 1
)

echo [1/3] Compilando modulos...
%PYTHON_CMD% -m py_compile lictor.py lictor\core.py lictor\cli.py lictor\gui.py
if %errorlevel% neq 0 (
    echo Error de sintaxis.
    pause
    exit /b 1
)

echo [2/3] Ejecutando tests...
%PYTHON_CMD% tests\test_lictor.py
if %errorlevel% neq 0 (
    echo Tests fallaron.
    pause
    exit /b 1
)

echo [3/3] Verificando JSON...
%PYTHON_CMD% lictor.py init --json > nul
if %errorlevel% neq 0 (
    echo init --json fallo.
    pause
    exit /b 1
)

echo.
echo LICTOR validado correctamente.
pause
