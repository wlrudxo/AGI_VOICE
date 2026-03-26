import { app, BrowserWindow, Menu, dialog, globalShortcut, ipcMain, screen } from 'electron';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const FRONTEND_URL = process.env.V3_FRONTEND_URL || 'http://localhost:4173';
const BACKEND_URL = process.env.V3_BACKEND_URL || 'http://127.0.0.1:8000';
const BACKEND_HEALTH_URL = `${BACKEND_URL}/health`;
const FRONTEND_CHECK_TIMEOUT_MS = 1200;

let mainWindow = null;
let isRendererClosing = false;

function toSizePayload(size) {
  if (!Array.isArray(size) || size.length < 2) {
    return null;
  }

  return {
    width: size[0],
    height: size[1],
  };
}

function toPositionPayload(position) {
  if (!Array.isArray(position) || position.length < 2) {
    return null;
  }

  return {
    x: position[0],
    y: position[1],
  };
}

function sendWindowEvent(eventName, payload = {}) {
  if (!mainWindow) {
    return;
  }

  mainWindow.webContents.send('desktop:window-event', {
    eventName,
    ...payload,
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    title: 'AGI Voice V3',
    show: false,
    frame: false,
    titleBarStyle: 'hidden',
    autoHideMenuBar: true,
    backgroundColor: '#111111',
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  mainWindow.on('focus', () => sendWindowEvent('focus'));
  mainWindow.on('blur', () => sendWindowEvent('blur'));
  mainWindow.on('maximize', () => sendWindowEvent('maximize'));
  mainWindow.on('unmaximize', () => sendWindowEvent('unmaximize'));
  mainWindow.on('enter-full-screen', () => sendWindowEvent('enter-full-screen'));
  mainWindow.on('leave-full-screen', () => sendWindowEvent('leave-full-screen'));
  mainWindow.on('resize', () => sendWindowEvent('resize', { size: toSizePayload(mainWindow?.getSize()) }));
  mainWindow.on('move', () => sendWindowEvent('move', { position: toPositionPayload(mainWindow?.getPosition()) }));
  mainWindow.on('close', (event) => {
    if (!isRendererClosing) {
      event.preventDefault();
      sendWindowEvent('close-requested', {
        window: getWindowSnapshot(),
      });
    }
  });

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  mainWindow.setMenuBarVisibility(false);
}

function getWindowSnapshot() {
  if (!mainWindow) {
    return null;
  }

  const bounds = mainWindow.getBounds();
  const position = mainWindow.getPosition();
  const size = mainWindow.getSize();
  const display = screen.getDisplayMatching(bounds);

  return {
    bounds,
    position: toPositionPayload(position),
    size: toSizePayload(size),
    isMaximized: mainWindow.isMaximized(),
    isFullscreen: mainWindow.isFullScreen(),
    display: display
      ? {
          bounds: display.bounds,
          workArea: display.workArea,
          scaleFactor: display.scaleFactor,
          rotation: display.rotation,
          id: display.id,
          label: display.label,
        }
      : null,
  };
}

async function canReachFrontend() {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), FRONTEND_CHECK_TIMEOUT_MS);
    const response = await fetch(FRONTEND_URL, {
      method: 'GET',
      signal: controller.signal,
    });
    clearTimeout(timeout);
    return response.ok;
  } catch {
    return false;
  }
}

async function loadInitialContent() {
  if (!mainWindow) {
    return;
  }

  const frontendReady = await canReachFrontend();
  if (frontendReady) {
    await mainWindow.loadURL(FRONTEND_URL);
    return;
  }

  await mainWindow.loadFile(path.join(__dirname, 'fallback.html'));
}

async function pingBackend() {
  try {
    const response = await fetch(BACKEND_HEALTH_URL);
    const data = await response.json().catch(() => ({}));

    return {
      ok: response.ok,
      status: response.status,
      url: BACKEND_HEALTH_URL,
      data,
    };
  } catch (error) {
    return {
      ok: false,
      status: 0,
      url: BACKEND_HEALTH_URL,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

function registerDefaultShortcuts() {
  globalShortcut.register('CommandOrControl+Shift+I', () => {
    mainWindow?.webContents.toggleDevTools();
  });
}

app.whenReady().then(async () => {
  Menu.setApplicationMenu(null);
  createWindow();
  await loadInitialContent();
  registerDefaultShortcuts();

  const status = await pingBackend();
  if (!status.ok) {
    console.warn(`Backend health check failed: ${status.url}`);
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
      void loadInitialContent();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

ipcMain.handle('window:snapshot', () => {
  return getWindowSnapshot();
});

ipcMain.handle('window:show', () => {
  mainWindow?.show();
  return true;
});

ipcMain.handle('window:hide', () => {
  mainWindow?.hide();
  return true;
});

ipcMain.handle('window:focus', () => {
  mainWindow?.focus();
  return true;
});

ipcMain.handle('window:minimize', () => {
  mainWindow?.minimize();
  return true;
});

ipcMain.handle('window:maximize', () => {
  mainWindow?.maximize();
  return true;
});

ipcMain.handle('window:toggleMaximize', () => {
  if (!mainWindow) {
    return false;
  }

  if (mainWindow.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow.maximize();
  }

  return true;
});

ipcMain.handle('window:unmaximize', () => {
  mainWindow?.unmaximize();
  return true;
});

ipcMain.handle('window:setSize', (_, width, height) => {
  if (!mainWindow) {
    return false;
  }

  mainWindow.setSize(width, height);
  return true;
});

ipcMain.handle('window:setPosition', (_, x, y) => {
  if (!mainWindow) {
    return false;
  }

  mainWindow.setPosition(x, y);
  return true;
});

ipcMain.handle('window:outerSize', () => {
  if (!mainWindow) {
    return null;
  }

  return toSizePayload(mainWindow.getSize());
});

ipcMain.handle('window:outerPosition', () => {
  if (!mainWindow) {
    return null;
  }

  return toPositionPayload(mainWindow.getPosition());
});

ipcMain.handle('window:isMaximized', () => {
  return mainWindow?.isMaximized() ?? false;
});

ipcMain.handle('window:isFullscreen', () => {
  return mainWindow?.isFullScreen() ?? false;
});

ipcMain.handle('window:setFullscreen', (_, value) => {
  if (!mainWindow) {
    return false;
  }

  mainWindow.setFullScreen(Boolean(value));
  return true;
});

ipcMain.handle('window:currentDisplay', () => {
  if (!mainWindow) {
    return null;
  }

  const display = screen.getDisplayMatching(mainWindow.getBounds());
  return display
    ? {
        id: display.id,
        label: display.label,
        bounds: display.bounds,
        workArea: display.workArea,
        size: display.size,
        workAreaSize: display.workAreaSize,
        scaleFactor: display.scaleFactor,
        rotation: display.rotation,
      }
    : null;
});

ipcMain.handle('window:requestClose', async () => {
  if (!mainWindow) {
    return false;
  }

  isRendererClosing = true;
  mainWindow.close();
  isRendererClosing = false;
  return true;
});

ipcMain.handle('dialog:openFile', async (_, options = {}) => {
  const result = await dialog.showOpenDialog(mainWindow ?? undefined, options);
  return result;
});

ipcMain.handle('dialog:saveFile', async (_, options = {}) => {
  const result = await dialog.showSaveDialog(mainWindow ?? undefined, options);
  return result;
});

ipcMain.handle('fs:readTextFile', async (_, filePath) => {
  return fs.readFile(filePath, 'utf8');
});

ipcMain.handle('fs:writeTextFile', async (_, filePath, contents) => {
  await fs.writeFile(filePath, contents, 'utf8');
  return true;
});

ipcMain.handle('shortcuts:register', async (_, accelerator) => {
  if (typeof accelerator !== 'string' || accelerator.trim() === '') {
    throw new Error('accelerator is required');
  }

  return globalShortcut.register(accelerator, () => {
    mainWindow?.show();
    mainWindow?.focus();
  });
});

ipcMain.handle('shortcuts:unregister', async (_, accelerator) => {
  if (typeof accelerator !== 'string' || accelerator.trim() === '') {
    return false;
  }

  return globalShortcut.unregister(accelerator);
});

ipcMain.handle('backend:ping', async () => {
  return pingBackend();
});
