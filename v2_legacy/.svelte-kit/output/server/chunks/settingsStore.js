import { w as writable } from "./index.js";
function loadInitialSettings() {
  if (typeof window === "undefined") {
    return {
      minimizeToTray: false
    };
  }
  try {
    const stored = localStorage.getItem("agi_voice_app_settings");
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error("Failed to load settings:", error);
  }
  return {
    minimizeToTray: false
  };
}
function createSettingsStore() {
  const { subscribe, set, update } = writable(loadInitialSettings());
  return {
    subscribe,
    setMinimizeToTray: (value) => {
      update((state) => {
        const newState = { ...state, minimizeToTray: value };
        if (typeof window !== "undefined") {
          try {
            localStorage.setItem("agi_voice_app_settings", JSON.stringify(newState));
          } catch (error) {
            console.error("Failed to save settings:", error);
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
createSettingsStore();
