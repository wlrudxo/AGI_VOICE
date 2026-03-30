@echo off
setlocal EnableExtensions

set "V3_ROOT=%~dp0"
if "%V3_ROOT:~-1%"=="\" set "V3_ROOT=%V3_ROOT:~0,-1%"

powershell -NoProfile -ExecutionPolicy Bypass -File "%V3_ROOT%\scripts\dev-windows.ps1"
set "EXIT_CODE=%errorlevel%"

endlocal
exit /b %EXIT_CODE%
