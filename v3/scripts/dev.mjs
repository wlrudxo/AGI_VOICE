import { spawn, spawnSync } from 'node:child_process';
import net from 'node:net';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { existsSync, mkdirSync } from 'node:fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');
const frontendDir = path.join(rootDir, 'apps', 'frontend');
const electronDir = path.join(rootDir, 'apps', 'desktop-electron');
const pythonApiDir = path.join(rootDir, 'services', 'python-api');

const isWindows = process.platform === 'win32';
const npmCmd = isWindows ? 'npm.cmd' : 'npm';
const pyLaunchers = isWindows
  ? [
      ['py', ['-3.11', '-m', 'venv', '.venv']],
      ['py', ['-3', '-m', 'venv', '.venv']],
      ['python', ['-m', 'venv', '.venv']],
      ['python3', ['-m', 'venv', '.venv']],
    ]
  : [['python3', ['-m', 'venv', '.venv']], ['python', ['-m', 'venv', '.venv']]];

const children = new Set();
let shuttingDown = false;

function log(message) {
  console.log(`[INFO] ${message}`);
}

function logWarn(message) {
  console.warn(`[WARN] ${message}`);
}

function logError(message) {
  console.error(`[ERROR] ${message}`);
}

function runOrThrow(command, args, cwd) {
  const result = spawnSync(command, args, {
    cwd,
    stdio: 'inherit',
    shell: false,
  });

  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(' ')} failed with exit code ${result.status}`);
  }
}

function ensureNodeDeps(dir, markerRelativePath) {
  const marker = path.join(dir, markerRelativePath);
  if (existsSync(marker)) {
    return;
  }
  log(`Installing/updating dependencies in ${path.relative(rootDir, dir)}...`);
  runOrThrow(npmCmd, ['install'], dir);
}

function detectPythonExecutable() {
  const pythonExe = isWindows
    ? path.join(pythonApiDir, '.venv', 'Scripts', 'python.exe')
    : path.join(pythonApiDir, '.venv', 'bin', 'python');

  if (existsSync(pythonExe)) {
    return pythonExe;
  }

  log('Python virtualenv is missing. Creating .venv...');
  mkdirSync(pythonApiDir, { recursive: true });
  for (const [command, args] of pyLaunchers) {
    const result = spawnSync(command, args, {
      cwd: pythonApiDir,
      stdio: 'ignore',
      shell: false,
    });
    if (result.status === 0 && existsSync(pythonExe)) {
      return pythonExe;
    }
  }

  throw new Error('Failed to create Python virtualenv');
}

function ensurePythonPackage(pythonExe) {
  log('Installing/updating Python API package...');
  runOrThrow(pythonExe, ['-m', 'pip', 'install', '-e', '.'], pythonApiDir);
}

function tryPort(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.once('error', () => resolve(false));
    server.once('listening', () => {
      server.close(() => resolve(true));
    });
    server.listen(port, '127.0.0.1');
  });
}

async function selectBackendPort() {
  for (const port of [8000, 8010, 18000]) {
    // Windows often blocks 8000 with WinError 10013 in this environment.
    if (await tryPort(port)) {
      return port;
    }
  }
  throw new Error('No usable backend port found');
}

function forwardOutput(child, prefix) {
  const write = (stream, target) => {
    stream.on('data', (chunk) => {
      const text = chunk.toString();
      const lines = text.split(/\r?\n/);
      for (let i = 0; i < lines.length; i += 1) {
        const line = lines[i];
        if (!line && i === lines.length - 1) {
          continue;
        }
        target.write(`[${prefix}] ${line}\n`);
      }
    });
  };

  if (child.stdout) write(child.stdout, process.stdout);
  if (child.stderr) write(child.stderr, process.stderr);
}

function spawnManaged(command, args, options) {
  const child = spawn(command, args, {
    cwd: options.cwd,
    env: options.env ?? process.env,
    stdio: ['ignore', 'pipe', 'pipe'],
    shell: false,
    detached: isWindows,
  });
  children.add(child);
  forwardOutput(child, options.name);

  child.on('exit', (code, signal) => {
    children.delete(child);
    if (shuttingDown) {
      return;
    }
    if (code !== null && code !== 0) {
      logWarn(`${options.name} exited with code ${code}`);
    } else if (signal) {
      logWarn(`${options.name} exited with signal ${signal}`);
    }
  });

  return child;
}

function shutdown() {
  if (shuttingDown) {
    return;
  }
  shuttingDown = true;
  log('Shutting down V3 dev stack...');
  for (const child of children) {
    try {
      if (isWindows) {
        spawnSync('taskkill', ['/pid', String(child.pid), '/t', '/f'], { stdio: 'ignore' });
      } else {
        child.kill('SIGTERM');
      }
    } catch {
      // ignore shutdown errors
    }
  }
  process.exit(0);
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

async function main() {
  console.log('========================================');
  console.log('AGI Voice V3 Dev Launcher');
  console.log(`Root: ${rootDir}`);
  console.log('Mode: single console (supervised)');
  console.log('========================================');
  console.log('');

  ensureNodeDeps(frontendDir, path.join('node_modules', '.package-lock.json'));
  ensureNodeDeps(electronDir, path.join('node_modules', '.bin', isWindows ? 'electronmon.cmd' : 'electronmon'));

  const pythonExe = detectPythonExecutable();
  ensurePythonPackage(pythonExe);
  const backendPort = await selectBackendPort();
  const backendUrl = `http://127.0.0.1:${backendPort}`;

  log(`Starting frontend on http://127.0.0.1:4173`);
  spawnManaged(npmCmd, ['run', 'dev'], {
    cwd: frontendDir,
    name: 'frontend',
  });

  log(`Starting Python API on ${backendUrl}`);
  spawnManaged(
    pythonExe,
    ['-m', 'uvicorn', 'app.main:app', '--reload', '--host', '127.0.0.1', '--port', String(backendPort)],
    {
      cwd: pythonApiDir,
      name: 'python',
    }
  );

  log(`Starting Electron shell with backend ${backendUrl}`);
  spawnManaged(npmCmd, ['run', 'dev'], {
    cwd: electronDir,
    env: {
      ...process.env,
      V3_BACKEND_URL: backendUrl,
    },
    name: 'electron',
  });
}

main().catch((error) => {
  logError(error instanceof Error ? error.message : String(error));
  shutdown();
});
