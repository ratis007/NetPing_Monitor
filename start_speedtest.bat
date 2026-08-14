@echo off
title NetPing Monitor Pro avec SpeedTest
cd /d "%~dp0"
echo Demarrage de NetPing Monitor Pro...
echo Installation des dependances SpeedTest...
pip install speedtest-cli requests openpyxl pandas matplotlib
echo.
echo Lancement de l'application...
python main_with_speedtest.py
pause
