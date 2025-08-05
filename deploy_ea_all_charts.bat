@echo off
echo MIKROBOT FASTVERSION EA - MULTI-CHART DEPLOYMENT
echo ====================================================
echo Deploying EA to 13 charts...
echo.

echo Symbols to deploy:
echo - EURUSD
echo - GBPUSD
echo - USDJPY
echo - USDCHF
echo - AUDUSD
echo - USDCAD
echo - NZDUSD
echo - BTCUSD
echo - ETHUSD
echo - LTCUSD
echo - BCHUSD
echo - XRPUSD
echo - NAS100

echo.
echo Instructions:
echo 1. Make sure MetaTrader 5 is open
echo 2. Make sure AutoTrading button is GREEN
echo 3. Open Navigator panel (Ctrl+N)
echo 4. Expand "Expert Advisors" section
echo 5. For EACH symbol above:
echo    - Open EURUSD chart (or any symbol from list)
echo    - Drag "MikrobotFastversionEA" to the chart
echo    - Repeat for other symbols if desired
echo.
echo EA will automatically:
echo - Monitor M5 BOS + M1 retest signals
echo - Apply 0.6 ylipip trigger system  
echo - Use ATR dynamic positioning (4-15 pips)
echo - Track XPWS weekly profits
echo - Manage positions with Dual Phase TP
echo.
echo Press any key to continue...
pause > nul

echo.
echo Checking MT5 connection...
python "C:\Users\HP\Dev\Mikrobot Fastversion\verify_ea_deployment.py"

echo.
echo DEPLOYMENT COMPLETE!
echo EA is now ready for multi-chart trading
pause
