@echo off
setlocal EnableExtensions

set "V3_ROOT=%~dp0"
if "%V3_ROOT:~-1%"=="\" set "V3_ROOT=%V3_ROOT:~0,-1%"
set "LOG_FILE=%V3_ROOT%\dev-launcher.log"

cd /d "%V3_ROOT%"
echo [INFO] Logging to %LOG_FILE%
echo. > "%LOG_FILE%"
echo [%date% %time%] Starting V3 dev launcher >> "%LOG_FILE%"
node scripts\dev.mjs >> "%LOG_FILE%" 2>&1
set "EXIT_CODE=%errorlevel%"
echo.
echo [INFO] V3 launcher exited with code %EXIT_CODE%.
echo [INFO] See log: %LOG_FILE%
type "%LOG_FILE%"
pause

endlocal
exit /b %EXIT_CODE%
