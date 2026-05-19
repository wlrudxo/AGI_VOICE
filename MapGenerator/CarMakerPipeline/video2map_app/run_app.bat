@echo off
cd /d "%~dp0"
set "PY311=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if exist "%PY311%" (
  "%PY311%" desktop_app.py
) else (
  python desktop_app.py
)
