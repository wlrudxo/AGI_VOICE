import { writable } from 'svelte/store';
import { requestJson } from '$lib/backend';

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

  async function persistSettings(nextState: AppSettings) {
    try {
      const currentAppSettings = await requestJson<Record<string, unknown>>('/api/settings/app');
      await requestJson('/api/settings/app', {
        method: 'PUT',
        body: {
          ...currentAppSettings,
          minimizeToTray: nextState.minimizeToTray
        }
      });
    } catch (error) {
      console.error('Failed to persist app settings:', error);
      throw error;
    }
  }

  return {
    subscribe,
    setMinimizeToTray: async (value: boolean) => {
      const previousState = currentState;
      const nextState = { ...previousState, minimizeToTray: value };

      applyState(nextState);

      if (typeof window !== 'undefined') {
        try {
          localStorage.setItem('agi_voice_app_settings', JSON.stringify(nextState));
        } catch (error) {
          console.error('Failed to save settings:', error);
        }
      }

      try {
        await persistSettings(nextState);
      } catch (error) {
        applyState(previousState);
        if (typeof window !== 'undefined') {
          try {
            localStorage.setItem('agi_voice_app_settings', JSON.stringify(previousState));
          } catch (storageError) {
            console.error('Failed to rollback settings:', storageError);
          }
        }
        throw error;
      }
    },
    loadSettings: async () => {
      const localState = loadInitialSettings();
      applyState(localState);

      try {
        const appSettings = await requestJson<{ minimizeToTray?: boolean }>('/api/settings/app');
        const nextState = {
          minimizeToTray: Boolean(appSettings.minimizeToTray)
        };

        applyState(nextState);

        if (typeof window !== 'undefined') {
          try {
            localStorage.setItem('agi_voice_app_settings', JSON.stringify(nextState));
          } catch (error) {
            console.error('Failed to cache settings:', error);
          }
        }
      } catch (error) {
        console.error('Failed to load app settings from backend:', error);
      }
    }
  };
}

export const settingsStore = createSettingsStore();
