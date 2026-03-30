$ErrorActionPreference = 'Stop'

$RootDir = Split-Path -Parent $PSScriptRoot
$FrontendDir = Join-Path $RootDir 'apps\frontend'
$ElectronDir = Join-Path $RootDir 'apps\desktop-electron'
$PythonApiDir = Join-Path $RootDir 'services\python-api'

function Write-Info($Message) {
  Write-Host "[INFO] $Message"
}

function Write-WarnMsg($Message) {
  Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Resolve-PythonExe {
  $pythonExe = Join-Path $PythonApiDir '.venv\Scripts\python.exe'
  if (Test-Path $pythonExe) {
    return $pythonExe
  }

  Write-Info 'Python virtualenv is missing. Creating .venv...'
  $launchers = @(
    @('py', @('-3.11', '-m', 'venv', '.venv')),
    @('py', @('-3', '-m', 'venv', '.venv')),
    @('python', @('-m', 'venv', '.venv')),
    @('python3', @('-m', 'venv', '.venv'))
  )

  foreach ($launcher in $launchers) {
    $cmd = $launcher[0]
    $args = $launcher[1]
    try {
      $proc = Start-Process -FilePath $cmd -ArgumentList $args -WorkingDirectory $PythonApiDir -Wait -PassThru -WindowStyle Hidden -ErrorAction Stop
      if ($proc.ExitCode -eq 0 -and (Test-Path $pythonExe)) {
        return $pythonExe
      }
    } catch {
      continue
    }
  }

  throw 'Failed to create Python virtualenv'
}

function Ensure-NodeDeps($Dir, $Marker) {
  if (Test-Path (Join-Path $Dir $Marker)) {
    return
  }

  Write-Info "Installing/updating dependencies in $Dir..."
  $proc = Start-Process -FilePath 'cmd.exe' -ArgumentList @('/d', '/s', '/c', 'npm.cmd install') -WorkingDirectory $Dir -Wait -PassThru -NoNewWindow
  if ($proc.ExitCode -ne 0) {
    throw "npm install failed in $Dir"
  }
}

function Ensure-PythonPackage($PythonExe) {
  $stampPath = Join-Path $PythonApiDir '.editable-install.stamp'
  $pyprojectPath = Join-Path $PythonApiDir 'pyproject.toml'

  $importReady = $false
  try {
    $probe = Start-Process -FilePath $PythonExe -ArgumentList @('-c', 'import fastapi, uvicorn, app.main; print("ok")') -WorkingDirectory $PythonApiDir -Wait -PassThru -WindowStyle Hidden
    $importReady = ($probe.ExitCode -eq 0)
  } catch {
    $importReady = $false
  }

  $stampMissing = -not (Test-Path $stampPath)
  $pyprojectNewer = $false
  if ((Test-Path $stampPath) -and (Test-Path $pyprojectPath)) {
    $pyprojectNewer = ((Get-Item $stampPath).LastWriteTimeUtc -lt (Get-Item $pyprojectPath).LastWriteTimeUtc)
  }

  if ($importReady -and ($stampMissing -or $pyprojectNewer)) {
    Set-Content -Path $stampPath -Value ([DateTime]::UtcNow.ToString('o')) -Encoding UTF8
    return
  }

  if ($importReady -and -not $pyprojectNewer) {
    return
  }

  Write-Info 'Installing/updating Python API package...'
  $proc = Start-Process -FilePath $PythonExe -ArgumentList @('-m', 'pip', 'install', '-e', '.') -WorkingDirectory $PythonApiDir -Wait -PassThru -NoNewWindow
  if ($proc.ExitCode -ne 0) {
    throw 'pip install -e . failed'
  }
  Set-Content -Path $stampPath -Value ([DateTime]::UtcNow.ToString('o')) -Encoding UTF8
}

function Test-PortAvailable([int]$Port) {
  $listener = $null
  try {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Parse('127.0.0.1'), $Port)
    $listener.Start()
    return $true
  } catch {
    return $false
  } finally {
    if ($listener) {
      $listener.Stop()
    }
  }
}

function Select-BackendPort {
  foreach ($port in @(8000, 8010, 18000)) {
    if (Test-PortAvailable $port) {
      return $port
    }
  }
  throw 'No usable backend port found'
}

function Start-DevWindow($Title, $WorkingDir, $Command) {
  $argList = @('/d', '/k', "title $Title && cd /d `"$WorkingDir`" && $Command")
  return Start-Process -FilePath 'cmd.exe' -ArgumentList $argList -PassThru
}

function Stop-ProcessTree([int]$Pid) {
  try {
    Start-Process -FilePath 'taskkill.exe' -ArgumentList @('/PID', $Pid, '/T', '/F') -Wait -PassThru -WindowStyle Hidden | Out-Null
  } catch {
    # ignore shutdown failures
  }
}

Write-Host '========================================'
Write-Host 'AGI Voice V3 Dev Launcher'
Write-Host "Root: $RootDir"
Write-Host 'Mode: 3 windows + linked shutdown'
Write-Host '========================================'
Write-Host ''

Ensure-NodeDeps $FrontendDir 'node_modules\.package-lock.json'
Ensure-NodeDeps $ElectronDir 'node_modules\.bin\electronmon.cmd'
$pythonExe = Resolve-PythonExe
Ensure-PythonPackage $pythonExe
$backendPort = Select-BackendPort
$backendUrl = "http://127.0.0.1:$backendPort"

Write-Info 'Starting frontend window...'
$frontend = Start-DevWindow 'AGI Voice V3 Frontend' $FrontendDir 'npm run dev'
Write-Info "Starting backend window on $backendUrl ..."
$backendCmd = "`"$pythonExe`" -m uvicorn app.main:app --reload --host 127.0.0.1 --port $backendPort --no-access-log"
$backend = Start-DevWindow 'AGI Voice V3 Python API' $PythonApiDir $backendCmd
Write-Info "Starting electron window with backend $backendUrl ..."
$electronCmd = "set V3_FRONTEND_URL=http://127.0.0.1:4173 && set V3_BACKEND_URL=$backendUrl && npm run dev"
$electron = Start-DevWindow 'AGI Voice V3 Electron' $ElectronDir $electronCmd

$children = @($frontend, $backend, $electron)
Write-Info 'All windows started. If any one exits, the other two will also be closed.'

while ($true) {
  Start-Sleep -Milliseconds 700
  foreach ($child in $children) {
    if ($child.HasExited) {
      Write-WarnMsg "Detected exit: PID $($child.Id). Closing remaining windows..."
      foreach ($other in $children) {
        if (-not $other.HasExited) {
          Stop-ProcessTree $other.Id
        }
      }
      exit 0
    }
  }
}
