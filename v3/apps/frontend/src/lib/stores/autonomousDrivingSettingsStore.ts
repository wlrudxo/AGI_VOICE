import { writable } from 'svelte/store';
import { requestJson } from '$lib/backend';
import { carmakerStore } from '$lib/stores/carmakerStore.svelte';

export interface AutonomousDrivingSettings {
  host: string;
  port: number;
  duration: number;
  controlMode: string;
  vehicleCommandParsingEnabled: boolean;
}

const DEFAULT_SETTINGS: AutonomousDrivingSettings = {
  host: 'localhost',
  port: 16660,
  duration: 2000,
  controlMode: 'Abs',
  vehicleCommandParsingEnabled: false,
};

const STORAGE_KEY = 'agi_voice_v3_autonomous_driving_settings';

function loadInitialSettings(): AutonomousDrivingSettings {
  if (typeof window === 'undefined') {
    return DEFAULT_SETTINGS;
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return DEFAULT_SETTINGS;
    }

    return {
      ...DEFAULT_SETTINGS,
      ...JSON.parse(stored),
    };
  } catch (error) {
    console.error('Failed to load autonomous driving settings cache:', error);
    return DEFAULT_SETTINGS;
  }
}

function persistLocalCache(settings: AutonomousDrivingSettings) {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  } catch (error) {
    console.error('Failed to cache autonomous driving settings:', error);
  }
}

function applyToCarMakerStore(settings: AutonomousDrivingSettings) {
  // Decision record:
  // V2에서는 renderer localStorage를 여러 컴포넌트가 각자 읽었다.
  // V3에서는 동일한 동작을 유지하되 단일 백엔드 설정을 기준으로 맞추기 위해
  // 자율주행 설정 응답을 CarMaker store에도 즉시 반영한다.
  carmakerStore.host = settings.host;
  carmakerStore.port = String(settings.port);
  carmakerStore.duration = String(settings.duration);
  carmakerStore.controlMode = settings.controlMode;
}

function createAutonomousDrivingSettingsStore() {
  const initialState = loadInitialSettings();
  const { subscribe, set } = writable<AutonomousDrivingSettings>(initialState);
  let currentState = initialState;

  function applyState(nextState: AutonomousDrivingSettings) {
    currentState = nextState;
    persistLocalCache(nextState);
    applyToCarMakerStore(nextState);
    set(nextState);
  }

  return {
    subscribe,
    getCurrentState: () => currentState,
    loadSettings: async () => {
      const settings = await requestJson<AutonomousDrivingSettings>('/api/settings/autonomous-driving');
      applyState(settings);
      return settings;
    },
    saveSettings: async (nextState: AutonomousDrivingSettings) => {
      const saved = await requestJson<AutonomousDrivingSettings>('/api/settings/autonomous-driving', {
        method: 'PUT',
        body: nextState,
      });
      applyState(saved);
      return saved;
    },
  };
}

export const autonomousDrivingSettingsStore = createAutonomousDrivingSettingsStore();
