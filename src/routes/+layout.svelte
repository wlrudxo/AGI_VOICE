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
  import { getCurrentWindow, LogicalSize, LogicalPosition } from '@tauri-apps/api/window';
  import { currentMonitor } from '@tauri-apps/api/window';
  import { register } from '@tauri-apps/plugin-global-shortcut';
  import { invoke } from '@tauri-apps/api/core';
  import { onMount } from 'svelte';

  let { children } = $props();
  let dialogComponent = $state();

  const appWindow = getCurrentWindow();
  let previousSize = null;
  let previousPosition = null;
  let isClosing = false; // 종료 중 플래그

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
    try {
      if (widgetMode) {
        // 현재 창 크기와 위치 저장
        const size = await appWindow.outerSize();
        const position = await appWindow.outerPosition();
        previousSize = size;
        previousPosition = position;

        // 위젯 크기로 변경 (450px width, 700px height)
        await appWindow.setSize(new LogicalSize(450, 700));

        // 화면 우하단으로 이동
        const monitor = await currentMonitor();
        if (monitor) {
          const screenWidth = monitor.size.width;
          const screenHeight = monitor.size.height;
          await appWindow.setPosition(new LogicalPosition(screenWidth - 470, screenHeight - 740));
        }
      } else {
        // 원래 크기로 복원
        if (previousSize && previousPosition) {
          await appWindow.setSize(new LogicalSize(previousSize.width, previousSize.height));
          await appWindow.setPosition(new LogicalPosition(previousPosition.x, previousPosition.y));
        }
      }
    } catch (error) {
      console.error('Failed to change window size:', error);
    }
  }

  // Rust에서 보내는 트레이 이벤트 처리
  async function setupTrayListeners() {
    // "열기" 또는 트레이 아이콘 클릭 시 - 이전 모드로 복원
    await appWindow.listen('tray-restore', () => {
      uiStore.restoreModeFromTray();
    });

    // "위젯" 메뉴 선택 시 - 위젯 모드로 전환
    await appWindow.listen('tray-widget', () => {
      uiStore.setWidgetMode(true);
    });
  }

  async function handleCloseRequest(event) {
    // 이미 종료 중이면 리턴 (무한 루프 방지)
    if (isClosing) {
      return;
    }

    const minimizeToTray = $settingsStore.minimizeToTray;

    if (minimizeToTray) {
      // 현재 위젯 모드 상태 저장
      uiStore.saveWidgetModeBeforeTray(isWidgetMode);

      // 트레이로 최소화
      event.preventDefault();
      await appWindow.hide();
    } else {
      // 앱 완전 종료: DB 동기화 후 종료
      event.preventDefault();
      isClosing = true; // 종료 플래그 설정

      try {
        console.log('🔄 Shutting down: Syncing database...');
        const result = await invoke('sync_db_on_shutdown');
        console.log('✅ Database synced successfully:', result);
      } catch (error) {
        console.error('⚠️ Database sync error:', error);
      } finally {
        // 동기화 성공 여부와 관계없이 앱 종료
        await appWindow.close();
      }
    }
  }

  // Ctrl+W 단축키 핸들러
  function handleKeyDown(event) {
    if ((event.ctrlKey || event.metaKey) && event.key === 'w') {
      event.preventDefault();
      handleCtrlW();
    }
  }

  async function handleCtrlW() {
    const minimizeToTray = $settingsStore.minimizeToTray;

    if (minimizeToTray) {
      // 현재 위젯 모드 상태 저장
      uiStore.saveWidgetModeBeforeTray(isWidgetMode);
      // 트레이로 최소화
      await appWindow.hide();
    } else {
      // 앱 종료
      await appWindow.close();
    }
  }

  onMount(async () => {
    // 다이얼로그 컴포넌트 등록
    if (dialogComponent) {
      dialogStore.setDialogComponent(dialogComponent);
    }

    // 트레이 이벤트 리스너 설정
    await setupTrayListeners();

    // 창 닫기 이벤트 리스너 등록
    const unlisten = await appWindow.onCloseRequested(handleCloseRequest);

    // Ctrl+W 단축키 리스너 등록
    window.addEventListener('keydown', handleKeyDown);

    // 글로벌 단축키 등록 (Ctrl+Shift+A)
    try {
      await register('CommandOrControl+Shift+A', async () => {
        // 1. 창 표시 및 포커스
        await appWindow.show();
        await appWindow.setFocus();

        // 2. 채팅 위젯 열기 (위젯 모드 활성화)
        uiStore.setChatOpen(true);
        uiStore.setWidgetMode(true);

        // 3. 메시지 입력창에 포커스 (약간의 지연 후)
        setTimeout(() => {
          const input = document.querySelector('.input-container input');
          if (input) {
            input.focus();
          }
        }, 300);
      });
      console.log('Global shortcut registered: Ctrl+Shift+A');
    } catch (error) {
      // 개발 중 hot reload 시 이미 등록된 경우 무시
      if (!error?.toString().includes('already registered')) {
        console.error('Failed to register global shortcut:', error);
      }
    }

    return () => {
      unlisten();
      window.removeEventListener('keydown', handleKeyDown);
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
