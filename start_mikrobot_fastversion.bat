
@echo off
echo Starting MIKROBOT FASTVERSION System...

echo Updating XPWS Status...
python "C:\Users\HP\Dev\Mikrobot Fastversion\xpws_weekly_tracker.py"

echo Starting Dual Phase TP Monitoring...
python "C:\Users\HP\Dev\Mikrobot Fastversion\dual_phase_tp_system.py"

echo Updating Universal Ylipip Configuration...
python "C:\Users\HP\Dev\Mikrobot Fastversion\universal_ylipip_trigger.py"

echo MIKROBOT FASTVERSION System Ready!
echo Account: 95244786
echo Strategy: MIKROBOT_FASTVERSION.md
echo Status: ACTIVE

pause
