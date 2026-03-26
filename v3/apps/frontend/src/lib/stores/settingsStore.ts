import { writable } from 'svelte/store';

interface AppSettings {
  minimizeToTray: boolean;
}

function loadInitialSettings(): AppSettings {
  if (typeof window === 'undefined') {
    return {
      minimizeToTray: false,
    };
  }

  try {
    const stored = localStorage.getItem('agi_voice_app_settings');
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error('Failed to load settings:', error);
  }

  return {
    minimizeToTray: false,
  };
}

function createSettingsStore() {
  const { subscribe, set } = writable<AppSettings>(loadInitialSettings());
  let currentState = loadInitialSettings();

  function applyState(nextState: AppSettings) {
    currentState = nextState;
    set(nextState);
  }

  return {
    subscribe,
    setMinimizeToTray: async (value: boolean) => {
      // Keep this local-only to match V2: minimizeToTray was never part of the Tauri settings model.
      const nextState = { ...currentState, minimizeToTray: value };

      applyState(nextState);

      if (typeof window !== 'undefined') {
        try {
          localStorage.setItem('agi_voice_app_settings', JSON.stringify(nextState));
        } catch (error) {
          console.error('Failed to save settings:', error);
        }
      }
    },
    loadSettings: async () => {
      const localState = loadInitialSettings();
      applyState(localState);
    }
  };
}

export const settingsStore = createSettingsStore();
