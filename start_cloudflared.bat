@echo off
setlocal

cd /d "%~dp0"

echo ========================================
echo  Flower Web Cloudflare Tunnel
echo ========================================
echo.
echo Please run start_flask.bat first, then run this script.
echo Local Flask address: http://127.0.0.1:5000
echo.
echo Starting cloudflared temporary public tunnel...
echo Look for the generated trycloudflare.com link in this window.
echo.
echo Do not close this window while using the public link.
echo.

"D:\Download\Edge\cloudflared.exe" tunnel --url http://127.0.0.1:5000

echo.
echo cloudflared has stopped. The public link is no longer available.
pause
