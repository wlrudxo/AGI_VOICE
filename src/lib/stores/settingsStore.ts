import { writable } from 'svelte/store';

interface AppSettings {
  minimizeToTray: boolean;
}

// localStorage에서 초기 상태 로드
function loadInitialSettings(): AppSettings {
  if (typeof window === 'undefined') {
    return {
      minimizeToTray: false
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
    minimizeToTray: false
  };
}

function createSettingsStore() {
  const { subscribe, set, update } = writable<AppSettings>(loadInitialSettings());

  return {
    subscribe,
    setMinimizeToTray: (value: boolean) => {
      update(state => {
        const newState = { ...state, minimizeToTray: value };

        // localStorage에 저장
        if (typeof window !== 'undefined') {
          try {
            localStorage.setItem('agi_voice_app_settings', JSON.stringify(newState));
          } catch (error) {
            console.error('Failed to save settings:', error);
          }
        }

        return newState;
      });
    },
    loadSettings: () => {
      set(loadInitialSettings());
    }
  };
}

export const settingsStore = createSettingsStore();
