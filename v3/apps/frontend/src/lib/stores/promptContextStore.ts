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

function createPromptContextStore() {
  const { subscribe, set } = writable<PromptContextSettings>(DEFAULT_SETTINGS);
  let currentState = DEFAULT_SETTINGS;

  function applyState(nextState: PromptContextSettings) {
    currentState = nextState;
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
