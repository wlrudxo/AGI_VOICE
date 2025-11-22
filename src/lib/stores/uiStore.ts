import { writable } from 'svelte/store';

interface UiState {
  isSidebarCollapsed: boolean;
  isChatOpen: boolean;
  chatViewMode: 'chat' | 'history' | 'settings';
  currentConversationId: number | null;
  currentConversationTitle: string | null;
  isWidgetMode: boolean;
  wasWidgetModeBeforeTray: boolean; // 트레이로 이동하기 전 위젯 모드였는지
  isChatExpanded: boolean; // 채팅 위젯 확장 상태
}

// localStorage에서 초기 상태 로드
function loadInitialState(): UiState {
  if (typeof window === 'undefined') {
    return {
      isSidebarCollapsed: false,
      isChatOpen: false,
      chatViewMode: 'chat',
      currentConversationId: null,
      currentConversationTitle: null,
      isWidgetMode: false,
      wasWidgetModeBeforeTray: false,
      isChatExpanded: false
    };
  }

  try {
    const storedViewMode = localStorage.getItem('agi_voice_chat_view_mode');
    const storedConversationId = localStorage.getItem('agi_voice_conversation_id');
    const storedWasWidgetMode = localStorage.getItem('agi_voice_was_widget_mode_before_tray');

    return {
      isSidebarCollapsed: false,
      isChatOpen: false,
      chatViewMode: storedViewMode === 'history' ? 'history' : storedViewMode === 'settings' ? 'settings' : 'chat',
      currentConversationId: storedConversationId ? parseInt(storedConversationId, 10) : null,
      currentConversationTitle: null,
      isWidgetMode: false,
      wasWidgetModeBeforeTray: storedWasWidgetMode === 'true',
      isChatExpanded: false
    };
  } catch (error) {
    console.error('Failed to load initial state:', error);
    return {
      isSidebarCollapsed: false,
      isChatOpen: false,
      chatViewMode: 'chat',
      currentConversationId: null,
      currentConversationTitle: null,
      isWidgetMode: false,
      wasWidgetModeBeforeTray: false,
      isChatExpanded: false
    };
  }
}

function createUiStore() {
  const { subscribe, set, update } = writable<UiState>(loadInitialState());

  return {
    subscribe,
    toggleSidebar: () => update(state => ({
      ...state,
      isSidebarCollapsed: !state.isSidebarCollapsed
    })),
    setSidebarCollapsed: (collapsed: boolean) => update(state => ({
      ...state,
      isSidebarCollapsed: collapsed
    })),
    toggleChat: () => update(state => ({
      ...state,
      isChatOpen: !state.isChatOpen
    })),
    setChatOpen: (open: boolean) => update(state => ({
      ...state,
      isChatOpen: open
    })),
    setChatViewMode: (mode: 'chat' | 'history' | 'settings') => {
      update(state => ({
        ...state,
        chatViewMode: mode
      }));
      // localStorage에 저장
      if (typeof window !== 'undefined') {
        try {
          localStorage.setItem('agi_voice_chat_view_mode', mode);
        } catch (error) {
          console.error('Failed to save chat view mode:', error);
        }
      }
    },
    setCurrentConversationId: (id: number | null) => {
      update(state => ({
        ...state,
        currentConversationId: id
      }));
      // localStorage에 저장
      if (typeof window !== 'undefined') {
        try {
          if (id === null) {
            localStorage.removeItem('agi_voice_conversation_id');
          } else {
            localStorage.setItem('agi_voice_conversation_id', id.toString());
          }
        } catch (error) {
          console.error('Failed to save conversation id:', error);
        }
      }
    },
    setCurrentConversationTitle: (title: string | null) => {
      update(state => ({
        ...state,
        currentConversationTitle: title
      }));
    },
    setWidgetMode: (isWidgetMode: boolean) => {
      update(state => ({
        ...state,
        isWidgetMode,
        isChatOpen: isWidgetMode ? true : state.isChatOpen
      }));
    },
    saveWidgetModeBeforeTray: (wasWidgetMode: boolean) => {
      update(state => ({
        ...state,
        wasWidgetModeBeforeTray: wasWidgetMode
      }));
      // localStorage에 저장
      if (typeof window !== 'undefined') {
        try {
          localStorage.setItem('agi_voice_was_widget_mode_before_tray', wasWidgetMode.toString());
        } catch (error) {
          console.error('Failed to save widget mode before tray:', error);
        }
      }
    },
    restoreModeFromTray: () => {
      update(state => {
        const shouldBeWidgetMode = state.wasWidgetModeBeforeTray;
        return {
          ...state,
          isWidgetMode: shouldBeWidgetMode,
          isChatOpen: shouldBeWidgetMode ? true : state.isChatOpen
        };
      });
    },
    setChatExpanded: (isExpanded: boolean) => update(state => ({
      ...state,
      isChatExpanded: isExpanded
    }))
  };
}

export const uiStore = createUiStore();
