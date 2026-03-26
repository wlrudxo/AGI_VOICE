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
  const { subscribe, set, update } = writable<AppSettings>(loadInitialSettings());

  return {
    subscribe,
    setMinimizeToTray: (value: boolean) => {
      update((state) => {
        const nextState = { ...state, minimizeToTray: value };

        if (typeof window !== 'undefined') {
          try {
            localStorage.setItem('agi_voice_app_settings', JSON.stringify(nextState));
          } catch (error) {
            console.error('Failed to save settings:', error);
          }
        }

        return nextState;
      });
    },
    loadSettings: () => {
      set(loadInitialSettings());
    },
  };
}

export const settingsStore = createSettingsStore();
