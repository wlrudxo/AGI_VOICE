<script>
  import '../app.css';
  import TitleBar from '$lib/components/TitleBar.svelte';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import AIChatWidget from '$lib/components/AIChatWidget.svelte';
  import Dialog from '$lib/components/Dialog.svelte';
  import ToastContainer from '$lib/components/ToastContainer.svelte';
  import { disableAutocomplete } from '$lib/actions/disableAutocomplete';
  import { uiStore } from '$lib/stores/uiStore';
  import { settingsStore } from '$lib/stores/settingsStore';
  import { dialogStore } from '$lib/stores/dialogStore.svelte';
  import { requestJson } from '$lib/backend';
  import { onMount } from 'svelte';

  let { children } = $props();
  let dialogComponent = $state();

  let isClosing = false;

  // Svelte 5 runes syntax
  const sidebarWidth = $derived($uiStore.isSidebarCollapsed ? '5.5rem' : '14rem');
  const isChatOpen = $derived($uiStore.isChatOpen);
  const isWidgetMode = $derived($uiStore.isWidgetMode);
  const isChatExpanded = $derived($uiStore.isChatExpanded);

  // 위젯 모드 변경 감지
  let lastWidgetMode = false;
  $effect(() => {
    if (isWidgetMode !== lastWidgetMode) {
      lastWidgetMode = isWidgetMode;
      handleWidgetModeChange(isWidgetMode);
    }
  });

  async function handleWidgetModeChange(widgetMode) {
    const win = window.desktop?.window;
    if (!win) return;

    try {
      if (widgetMode) {
        // Decision record:
        // V3에서는 위젯 모드 "복원" 기능을 의도적으로 제거했다.
        // 기존 복원 로직은 preload 표면과 맞지 않았고, 사용자도 기능 제거를 승인했다.
        // 따라서 위젯 진입은 단방향 크기 변경만 수행하고, 종료 시 이전 창 크기/위치를 복원하지 않는다.
        await win.setSize?.(450, 700);

        const display = await win.currentMonitor?.();
        const workArea = display?.workArea;
        if (workArea) {
          await win.setPosition?.(workArea.x + workArea.width - 470, workArea.y + workArea.height - 740);
        }
      }
    } catch (error) {
      console.error('Failed to change window size:', error);
    }
  }

  async function syncDbOnShutdown() {
    try {
      await requestJson('/api/settings/db/sync-shutdown', { method: 'POST' });
    } catch (error) {
      console.error('Failed to sync database on shutdown:', error);
    }
  }

  async function handleCloseRequest(event) {
    if (isClosing) {
      return;
    }

    const minimizeToTray = $settingsStore.minimizeToTray;

    if (minimizeToTray) {
      event?.preventDefault?.();
      uiStore.saveWidgetModeBeforeTray(isWidgetMode);
      await window.desktop?.window?.hide?.();
      return;
    }

    event?.preventDefault?.();
    isClosing = true;

    try {
      await syncDbOnShutdown();
    } finally {
      await window.desktop?.window?.requestClose?.();
    }
  }

  // 키보드 단축키 핸들러
  async function handleKeyDown(event) {
    if ((event.ctrlKey || event.metaKey) && event.key === 'w') {
      event.preventDefault();
      await handleCloseRequest(event);
    }
  }

  onMount(async () => {
    // 다이얼로그 컴포넌트 등록
    if (dialogComponent) {
      dialogStore.setDialogComponent(dialogComponent);
    }

    await settingsStore.loadSettings();

    // Ctrl+W 단축키 리스너 등록
    window.addEventListener('keydown', handleKeyDown);

    const unlistenCloseRequested = window.desktop?.window?.onCloseRequested?.(handleCloseRequest);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      unlistenCloseRequested?.();
    };
  });
</script>

<div class="layout" class:widget-mode={isWidgetMode} use:disableAutocomplete>
  {#if !isWidgetMode}
    <TitleBar />
    <Sidebar />
    <main class="main-content" class:chat-open={isChatOpen} class:chat-expanded={isChatExpanded} style="margin-left: {sidebarWidth};">
      {@render children?.()}
    </main>
  {/if}

  <!-- Floating Chat Widget -->
  {#if isChatOpen}
    <div class="chat-overlay" class:fullscreen={isWidgetMode}>
      <AIChatWidget />
    </div>
  {/if}
</div>

<!-- Global Dialog Component -->
<Dialog bind:this={dialogComponent} />

<!-- Global Toast Container -->
<ToastContainer />

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    overflow: hidden;
  }

  .layout {
    height: 100vh;
    background-color: var(--color-background, #f5f5f5);
    position: relative;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .layout.widget-mode {
    background-color: transparent;
  }

  .main-content {
    flex: 1;
    margin-top: 40px;
    padding: 2rem;
    overflow-y: auto;
    transition: margin-left 300ms ease-in-out, padding-right 300ms ease-in-out;
  }

  /* 작은 화면: 위젯이 메인 컨텐츠 위에 overlay */
  .main-content.chat-open {
    padding-right: 2rem;
  }

  /* 중간 화면 (1024px+): 위젯이 메인 컨텐츠를 밀어냄 (450px) */
  @media (min-width: 1024px) {
    .main-content.chat-open {
      padding-right: 29.25rem; /* 2rem + 450px + 2rem */
    }

    .main-content.chat-open.chat-expanded {
      padding-right: 43rem; /* 2rem + 640px + 2rem */
    }
  }

  /* 큰 화면 (1280px+): 위젯이 메인 컨텐츠를 밀어냄 (여유있게) */
  @media (min-width: 1280px) {
    .main-content.chat-open {
      padding-right: 31.25rem; /* 2rem + 450px + 2rem + 2rem(여유) */
    }

    .main-content.chat-open.chat-expanded {
      padding-right: 45rem; /* 2rem + 640px + 2rem + 2rem(여유) */
    }
  }

  .chat-overlay {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    z-index: 1000;
    box-shadow: var(--shadow-lg);
    border-radius: 12px;
    overflow: hidden;
  }

  /* 작은 화면에서는 위젯 크기 조정 */
  @media (max-width: 480px) {
    .chat-overlay {
      right: 1rem;
      bottom: 1rem;
    }

    .chat-overlay :global(.chat-widget) {
      width: calc(100vw - 2rem);
      max-width: 450px;
    }
  }

  .chat-overlay.fullscreen {
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: stretch;
    justify-content: stretch;
    background-color: transparent;
    box-shadow: none;
    border-radius: 0;
  }

  .chat-overlay.fullscreen :global(.chat-widget) {
    width: 100%;
    height: 100%;
    border-radius: 0;
  }
</style>
