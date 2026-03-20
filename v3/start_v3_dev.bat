@echo off
setlocal

set "V3_ROOT=%~dp0"
if "%V3_ROOT:~-1%"=="\" set "V3_ROOT=%V3_ROOT:~0,-1%"

set "FRONTEND_DIR=%V3_ROOT%\apps\frontend"
set "ELECTRON_DIR=%V3_ROOT%\apps\desktop-electron"
set "PYTHON_API_DIR=%V3_ROOT%\services\python-api"

echo ========================================
echo AGI Voice V3 Dev Launcher
echo Root: %V3_ROOT%
echo ========================================
echo.

if not exist "%FRONTEND_DIR%\package.json" (
  echo [ERROR] Frontend package.json not found:
  echo         %FRONTEND_DIR%\package.json
  exit /b 1
)

if not exist "%ELECTRON_DIR%\package.json" (
  echo [ERROR] Electron package.json not found:
  echo         %ELECTRON_DIR%\package.json
  exit /b 1
)

if not exist "%PYTHON_API_DIR%\pyproject.toml" (
  echo [ERROR] Python API pyproject.toml not found:
  echo         %PYTHON_API_DIR%\pyproject.toml
  exit /b 1
)

start "AGI Voice V3 Frontend" cmd /k "cd /d \"%FRONTEND_DIR%\" && if not exist node_modules (echo [ERROR] Frontend dependencies are missing. Run: npm install) else (echo [INFO] Starting frontend on http://127.0.0.1:4173 && npm run dev)"

start "AGI Voice V3 Python API" cmd /k "cd /d \"%PYTHON_API_DIR%\" && if exist .venv\Scripts\python.exe (echo [INFO] Starting Python API on http://127.0.0.1:8000 && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000) else (echo [ERROR] Python virtualenv is missing. Create it first: py -3.11 -m venv .venv ^&^& .venv\Scripts\python.exe -m pip install -e .)"

start "AGI Voice V3 Electron" cmd /k "cd /d \"%ELECTRON_DIR%\" && if not exist node_modules (echo [ERROR] Electron dependencies are missing. Run: npm install) else (echo [INFO] Starting Electron shell && npm run dev)"

echo [INFO] Launched V3 dev consoles.
echo [INFO] Close each console individually when finished.

endlocal

