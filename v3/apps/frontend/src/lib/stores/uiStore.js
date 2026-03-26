import { writable } from 'svelte/store';

function loadInitialState() {
  if (typeof window === 'undefined') {
    return {
      isSidebarCollapsed: false,
      isChatOpen: false,
      chatViewMode: 'chat',
      isChatExpanded: false,
      activeSection: 'autonomous-driving',
      activeSubView: 'vehicle-control',
    };
  }

  try {
    return {
      isSidebarCollapsed: localStorage.getItem('agi_voice_v3_sidebar_collapsed') === 'true',
      isChatOpen: localStorage.getItem('agi_voice_v3_chat_open') === 'true',
      chatViewMode: localStorage.getItem('agi_voice_v3_chat_view_mode') || 'chat',
      isChatExpanded: localStorage.getItem('agi_voice_v3_chat_expanded') === 'true',
      activeSection:
        localStorage.getItem('agi_voice_v3_active_section') || 'autonomous-driving',
      activeSubView:
        localStorage.getItem('agi_voice_v3_active_sub_view') || 'vehicle-control',
    };
  } catch {
    return {
      isSidebarCollapsed: false,
      isChatOpen: false,
      chatViewMode: 'chat',
      isChatExpanded: false,
      activeSection: 'autonomous-driving',
      activeSubView: 'vehicle-control',
    };
  }
}

function persist(key, value) {
  if (typeof window === 'undefined') {
    return;
  }
  try {
    localStorage.setItem(key, String(value));
  } catch {
    // noop
  }
}

function createUiStore() {
  const { subscribe, update } = writable(loadInitialState());

  return {
    subscribe,
    toggleSidebar() {
      update((state) => {
        const next = { ...state, isSidebarCollapsed: !state.isSidebarCollapsed };
        persist('agi_voice_v3_sidebar_collapsed', next.isSidebarCollapsed);
        return next;
      });
    },
    toggleChat() {
      update((state) => {
        const next = { ...state, isChatOpen: !state.isChatOpen };
        persist('agi_voice_v3_chat_open', next.isChatOpen);
        return next;
      });
    },
    setChatOpen(isChatOpen) {
      update((state) => {
        const next = { ...state, isChatOpen };
        persist('agi_voice_v3_chat_open', next.isChatOpen);
        return next;
      });
    },
    setChatViewMode(chatViewMode) {
      update((state) => {
        const next = { ...state, chatViewMode };
        persist('agi_voice_v3_chat_view_mode', next.chatViewMode);
        return next;
      });
    },
    setChatExpanded(isChatExpanded) {
      update((state) => {
        const next = { ...state, isChatExpanded };
        persist('agi_voice_v3_chat_expanded', next.isChatExpanded);
        return next;
      });
    },
    setSection(activeSection, activeSubView = null) {
      update((state) => {
        const next = {
          ...state,
          activeSection,
          activeSubView: activeSubView ?? state.activeSubView,
        };
        persist('agi_voice_v3_active_section', next.activeSection);
        persist('agi_voice_v3_active_sub_view', next.activeSubView);
        return next;
      });
    },
    setSubView(activeSubView) {
      update((state) => {
        const next = { ...state, activeSubView };
        persist('agi_voice_v3_active_sub_view', next.activeSubView);
        return next;
      });
    },
  };
}

export const uiStore = createUiStore();
