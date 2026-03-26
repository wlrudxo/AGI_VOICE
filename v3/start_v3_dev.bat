@echo off
setlocal EnableExtensions

set "V3_ROOT=%~dp0"
if "%V3_ROOT:~-1%"=="\" set "V3_ROOT=%V3_ROOT:~0,-1%"

cd /d "%V3_ROOT%"
node scripts\dev.mjs

endlocal
exit /b %errorlevel%
