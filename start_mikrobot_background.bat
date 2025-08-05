@echo off
echo STARTING MIKROBOT CONTINUOUS TRADING SYSTEM
echo ============================================
echo System will run in background monitoring all EA signals
echo Press Ctrl+C to stop
echo.

cd /d "C:\Users\HP\Dev\Mikrobot Fastversion"
python mikrobot_background_service.py
pause