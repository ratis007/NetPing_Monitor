@echo off
chcp 65001 >nul
title NetPing Monitor - Surveillance Réseau
echo.
echo ========================================
echo    NetPing Monitor - Version 1.0
echo ========================================
echo.
echo Lancement de l'application de surveillance réseau...
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installé ou n'est pas dans le PATH.
    echo.
    echo Veuillez installer Python 3.7 ou supérieur depuis:
    echo https://www.python.org/downloads/
    echo.
    echo Assurez-vous de cocher "Add Python to PATH" lors de l'installation.
    echo.
    pause
    exit /b 1
)

REM Vérifier la version de Python
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set "PYVER=%%I"
echo Python %PYVER% détecté.
echo.

REM Vérifier Tkinter
python -c "import tkinter; print('Tkinter OK')" >nul 2>&1
if errorlevel 1 (
    echo AVERTISSEMENT: Tkinter n'est pas installé.
    echo.
    echo Sous Windows, Tkinter est généralement inclus avec Python.
    echo Si ce n'est pas le cas, réinstallez Python en cochant "tcl/tk".
    echo.
    echo Voulez-vous continuer quand même ? (O/N)
    set /p CHOICE=
    if /i not "%CHOICE%"=="O" (
        exit /b 1
    )
)

REM Créer le répertoire de logs s'il n'existe pas
if not exist "logs" (
    echo Création du répertoire de logs...
    mkdir logs
)

REM Lancer l'application
echo Lancement de NetPing Monitor...
echo.
echo ========================================
echo Appuyez sur Ctrl+C pour quitter.
echo ========================================
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ERREUR: L'application a rencontré un problème.
    echo.
    echo Solutions possibles:
    echo 1. Vérifiez que tous les fichiers sont présents
    echo 2. Réinstallez Python avec Tkinter
    echo 3. Exécutez en tant qu'administrateur
    echo.
    pause
    exit /b 1
)

echo.
echo Application terminée.
pause