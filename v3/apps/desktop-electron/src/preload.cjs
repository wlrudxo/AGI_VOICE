const { contextBridge, ipcRenderer } = require('electron');

const invoke = (channel, ...args) => ipcRenderer.invoke(channel, ...args);
const on = (channel, handler) => {
  const listener = (_, payload) => handler(payload);
  ipcRenderer.on(channel, listener);
  return () => ipcRenderer.removeListener(channel, listener);
};

contextBridge.exposeInMainWorld('desktop', {
  window: {
    show: () => invoke('window:show'),
    hide: () => invoke('window:hide'),
    focus: () => invoke('window:focus'),
    minimize: () => invoke('window:minimize'),
    maximize: () => invoke('window:maximize'),
    unmaximize: () => invoke('window:unmaximize'),
    isMaximized: () => invoke('window:isMaximized'),
    outerSize: () => invoke('window:outerSize'),
    outerPosition: () => invoke('window:outerPosition'),
    setSize: (width, height) => invoke('window:setSize', width, height),
    setPosition: (x, y) => invoke('window:setPosition', x, y),
    isFullscreen: () => invoke('window:isFullscreen'),
    setFullscreen: (value) => invoke('window:setFullscreen', value),
    currentDisplay: () => invoke('window:currentDisplay'),
    currentMonitor: () => invoke('window:currentDisplay'),
    snapshot: () => invoke('window:snapshot'),
    close: () => invoke('window:requestClose'),
    requestClose: () => invoke('window:requestClose'),
    onEvent: (handler) => on('desktop:window-event', handler),
    onCloseRequested: (handler) => on('desktop:window-event', (event) => {
      if (event && event.eventName === 'close-requested') {
        handler(event);
      }
    }),
  },
  dialog: {
    openFile: (options) => invoke('dialog:openFile', options),
    saveFile: (options) => invoke('dialog:saveFile', options),
  },
  fs: {
    readTextFile: (filePath) => invoke('fs:readTextFile', filePath),
    writeTextFile: (filePath, contents) => invoke('fs:writeTextFile', filePath, contents),
  },
  shortcuts: {
    register: (accelerator) => invoke('shortcuts:register', accelerator),
    unregister: (accelerator) => invoke('shortcuts:unregister', accelerator),
  },
  backend: {
    ping: () => invoke('backend:ping'),
  },
});
