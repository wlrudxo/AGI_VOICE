@echo off
title Claude CLI Test Server
echo ========================================
echo   Claude CLI Test Server
echo ========================================
echo.

cd /d "%~dp0"

python server.py

pause
