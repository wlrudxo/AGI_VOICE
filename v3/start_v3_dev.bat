@echo off
setlocal EnableExtensions

if /i "%~1"=="__frontend" goto :run_frontend
if /i "%~1"=="__python_api" goto :run_python_api
if /i "%~1"=="__electron" goto :run_electron

set "V3_ROOT=%~dp0"
if "%V3_ROOT:~-1%"=="\" set "V3_ROOT=%V3_ROOT:~0,-1%"
set "PORT_FILE=%V3_ROOT%\.backend_port"
if exist "%PORT_FILE%" del "%PORT_FILE%"

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

start "AGI Voice V3 Frontend" cmd /k call "%~f0" __frontend
start "AGI Voice V3 Python API" cmd /k call "%~f0" __python_api
start "AGI Voice V3 Electron" cmd /k call "%~f0" __electron

echo [INFO] Launched V3 dev consoles.
echo [INFO] Close each console individually when finished.

endlocal
exit /b 0

:run_frontend
set "V3_ROOT=%~dp0"
if "%V3_ROOT:~-1%"=="\" set "V3_ROOT=%V3_ROOT:~0,-1%"
set "FRONTEND_DIR=%V3_ROOT%\apps\frontend"
cd /d "%FRONTEND_DIR%"
if not exist node_modules (
  echo [INFO] Frontend dependencies are missing. Running npm install...
  call npm install
  if errorlevel 1 (
    echo [ERROR] Frontend npm install failed.
    goto :eof
  )
)
echo [INFO] Starting frontend on http://127.0.0.1:4173
call npm run dev
goto :eof

:run_python_api
set "V3_ROOT=%~dp0"
if "%V3_ROOT:~-1%"=="\" set "V3_ROOT=%V3_ROOT:~0,-1%"
set "PORT_FILE=%V3_ROOT%\.backend_port"
set "PYTHON_API_DIR=%V3_ROOT%\services\python-api"
cd /d "%PYTHON_API_DIR%"

if not exist .venv\Scripts\python.exe (
  echo [INFO] Python virtualenv is missing. Creating .venv...
  call :create_venv
  if errorlevel 1 (
    echo [ERROR] Failed to create Python virtualenv.
    echo [INFO] Tried: py -3.11, py -3, python, python3
    goto :eof
  )
)

echo [INFO] Installing/updating Python API package...
call .venv\Scripts\python.exe -m pip install -e .
if errorlevel 1 (
  echo [ERROR] Python package install failed.
  goto :eof
)

call :try_start_backend 8000
if not errorlevel 1 goto :eof
call :try_start_backend 8010
if not errorlevel 1 goto :eof
call :try_start_backend 18000
if not errorlevel 1 goto :eof

echo [ERROR] Failed to start Python API on all fallback ports.
goto :eof

:run_electron
set "V3_ROOT=%~dp0"
if "%V3_ROOT:~-1%"=="\" set "V3_ROOT=%V3_ROOT:~0,-1%"
set "PORT_FILE=%V3_ROOT%\.backend_port"
set "ELECTRON_DIR=%V3_ROOT%\apps\desktop-electron"
cd /d "%ELECTRON_DIR%"
if not exist node_modules (
  echo [INFO] Electron dependencies are missing. Running npm install...
  call npm install
  if errorlevel 1 (
    echo [ERROR] Electron npm install failed.
    goto :eof
  )
)
set "BACKEND_PORT=8000"
for /l %%I in (1,1,30) do (
  if exist "%PORT_FILE%" (
    set /p BACKEND_PORT=<"%PORT_FILE%"
    goto :got_backend_port
  )
  timeout /t 1 /nobreak >nul
)
:got_backend_port
if not defined BACKEND_PORT set "BACKEND_PORT=8000"
set "V3_BACKEND_URL=http://127.0.0.1:%BACKEND_PORT%"
echo [INFO] Starting Electron shell with backend %V3_BACKEND_URL%
call npm run dev
goto :eof

:try_start_backend
set "BACKEND_PORT=%~1"
set "V3_ROOT=%~dp0"
if "%V3_ROOT:~-1%"=="\" set "V3_ROOT=%V3_ROOT:~0,-1%"
set "PORT_FILE=%V3_ROOT%\.backend_port"
echo [INFO] Starting Python API on http://127.0.0.1:%BACKEND_PORT%
> "%PORT_FILE%" echo %BACKEND_PORT%
call .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port %BACKEND_PORT%
if errorlevel 1 (
  echo [WARN] Python API failed on port %BACKEND_PORT%. Trying next fallback if available...
  exit /b 1
)
exit /b 0

:create_venv
py -3.11 -m venv .venv >nul 2>&1
if exist .venv\Scripts\python.exe exit /b 0
py -3 -m venv .venv >nul 2>&1
if exist .venv\Scripts\python.exe exit /b 0
python -m venv .venv >nul 2>&1
if exist .venv\Scripts\python.exe exit /b 0
python3 -m venv .venv >nul 2>&1
if exist .venv\Scripts\python.exe exit /b 0
exit /b 1
