@echo off
title LICTOR - Optional EXE Builder
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

%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install pyinstaller
%PYTHON_CMD% -m PyInstaller --onefile --name LICTOR lictor.py

echo.
echo EXE de consola creado en dist\LICTOR.exe
echo Para GUI con consola visible, use: dist\LICTOR.exe gui
pause
