@echo off
setlocal EnableExtensions

call "%~dp0v3\start_v3_dev.bat"
set "EXIT_CODE=%errorlevel%"

endlocal
exit /b %EXIT_CODE%
