@echo off
echo ================================================================
echo MIKROBOT 4-PHASE AUTOMATED TRADING SYSTEM
echo ================================================================
echo.
echo Starting continuous signal monitoring and execution...
echo.
echo FEATURES:
echo - Real-time 4-phase BOS signal detection
echo - Automatic YLIPIP trigger execution
echo - 0.55%% risk-based position sizing
echo - FOK (Fill or Kill) order execution
echo - Multi-asset support (forex, indices, commodities)
echo.
echo Press Ctrl+C to stop the system
echo.

cd /d "C:\Users\HP\Dev\Mikrobot Fastversion"
python continuous_4phase_executor.py

echo.
echo Trading system stopped.
pause