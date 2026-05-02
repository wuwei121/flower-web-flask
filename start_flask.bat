@echo off
setlocal

cd /d "%~dp0"

echo ========================================
echo  Flower Web Flask
echo ========================================
echo.
echo Project directory:
echo %cd%
echo.
echo Starting Flask server...
echo Visit: http://127.0.0.1:5000
echo.
echo Press Ctrl+C in this window to stop the service.
echo.

python app.py

echo.
echo Flask service has stopped.
pause
