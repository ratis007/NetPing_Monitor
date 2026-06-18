@echo off
chcp 65001 >nul
title Construction de NetPing Monitor en .exe
echo.
echo ========================================
echo    NetPing Monitor - Build .exe
echo ========================================
echo.
echo Ce script construit un exécutable Windows .exe
echo.

REM Vérifier PyInstaller
echo Vérification de PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller n'est pas installé.
    echo Installation en cours...
    pip install pyinstaller
    if errorlevel 1 (
        echo Échec de l'installation de PyInstaller.
        echo Veuillez l'installer manuellement: pip install pyinstaller
        pause
        exit /b 1
    )
    echo ✅ PyInstaller installé.
) else (
    echo ✅ PyInstaller déjà installé.
)

echo.
echo Construction de l'exécutable...
echo.

REM Construire l'exécutable
echo Options de construction:
echo - onefile: Un seul fichier .exe
echo - windowed: Pas de console
echo - name: NetPingMonitor.exe
echo - icon: icon.ico (si disponible)
echo.

REM Vérifier si l'icône existe
if exist "icon.ico" (
    set ICON_OPTION=--icon=icon.ico
    echo Icône détectée: icon.ico
) else (
    set ICON_OPTION=
    echo Aucune icône trouvée (icon.ico)
)

REM Exécuter PyInstaller
pyinstaller --onefile --windowed --name="NetPingMonitor" %ICON_OPTION% --clean main.py

if errorlevel 1 (
    echo.
    echo ❌ Erreur lors de la construction.
    echo.
    echo Problèmes possibles:
    echo 1. Fichiers manquants
    echo 2. Problèmes de dépendances
    echo 3. Problèmes avec PyInstaller
    echo.
    echo Essayez de construire manuellement:
    echo pyinstaller --onefile --windowed main.py
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Construction réussie !
echo.
echo Fichiers générés:
echo - dist\NetPingMonitor.exe : L'exécutable principal
echo - build\                  : Fichiers temporaires de construction
echo.
echo Pour nettoyer les fichiers de construction:
echo pyinstaller --clean
echo ou supprimez les dossiers build et dist
echo.

REM Copier les fichiers nécessaires
echo Copie des fichiers de support...
if not exist "dist\logs" mkdir "dist\logs"
copy "README.md" "dist\" >nul 2>&1
copy "requirements.txt" "dist\" >nul 2>&1
copy "start.bat" "dist\" >nul 2>&1

echo.
echo ========================================
echo INSTRUCTIONS D'UTILISATION
echo ========================================
echo.
echo 1. L'exécutable se trouve dans: dist\NetPingMonitor.exe
echo.
echo 2. Vous pouvez le copier n'importe où sur votre système.
echo.
echo 3. Au premier lancement, il créera:
echo    - Un dossier "logs" pour l'historique
echo    - Un fichier "targets.json" pour les cibles
echo.
echo 4. Pour distribuer l'application:
echo    - Copiez seulement dist\NetPingMonitor.exe
echo    - Les autres fichiers seront créés automatiquement
echo.
echo 5. Options avancées:
echo    - Ajoutez une icône: créez un fichier icon.ico
echo    - Personnalisez le nom: modifiez --name dans le script
echo.
echo ========================================
echo.

REM Tester l'exécutable
echo Voulez-vous tester l'exécutable maintenant ? (O/N)
set /p TEST_CHOICE=
if /i "%TEST_CHOICE%"=="O" (
    echo.
    echo Lancement de NetPingMonitor.exe...
    echo.
    start "" "dist\NetPingMonitor.exe"
)

echo.
echo Construction terminée.
pause