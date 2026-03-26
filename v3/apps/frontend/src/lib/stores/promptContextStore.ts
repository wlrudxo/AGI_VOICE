import { writable } from 'svelte/store';
import { requestJson } from '$lib/backend';

export const DEFAULT_FINAL_MESSAGE_TEMPLATE = `## Final Checkout

- Check if all required tags are properly formatted
- Ensure the response is clear and professional
- Verify technical accuracy of autonomous driving concepts
- Provide relevant references or examples when appropriate`;

export interface PromptContextSettings {
  userName: string;
  userInfo: string;
  finalMessage: string;
}

const DEFAULT_SETTINGS: PromptContextSettings = {
  userName: '',
  userInfo: '',
  finalMessage: DEFAULT_FINAL_MESSAGE_TEMPLATE,
};

const STORAGE_KEY = 'agi_voice_v3_prompt_context';

function loadInitialSettings(): PromptContextSettings {
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
    console.error('Failed to load prompt context cache:', error);
    return DEFAULT_SETTINGS;
  }
}

function persistLocalCache(settings: PromptContextSettings) {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  } catch (error) {
    console.error('Failed to cache prompt context settings:', error);
  }
}

function createPromptContextStore() {
  const initialState = loadInitialSettings();
  const { subscribe, set } = writable<PromptContextSettings>(initialState);
  let currentState = initialState;

  function applyState(nextState: PromptContextSettings) {
    currentState = nextState;
    persistLocalCache(nextState);
    set(nextState);
  }

  return {
    subscribe,
    getCurrentState: () => currentState,
    loadSettings: async () => {
      const settings = await requestJson<PromptContextSettings>('/api/settings/prompt-context');
      applyState(settings);
      return settings;
    },
    saveSettings: async (nextState: PromptContextSettings) => {
      const saved = await requestJson<PromptContextSettings>('/api/settings/prompt-context', {
        method: 'PUT',
        body: nextState,
      });
      applyState(saved);
      return saved;
    },
  };
}

export const promptContextStore = createPromptContextStore();
