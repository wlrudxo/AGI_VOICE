<script>
  import TitleBar from './lib/components/TitleBar.svelte';
  import Sidebar from './lib/components/Sidebar.svelte';
  import SubSidebar from './lib/components/SubSidebar.svelte';
  import AIChatWidget from './lib/components/AIChatWidget.svelte';
  import { uiStore } from './lib/stores/uiStore.js';
  import { disableAutocomplete } from './lib/disableAutocomplete.js';
  import SettingsView from './lib/views/SettingsView.svelte';
  import ChatView from './lib/views/ChatView.svelte';
  import ChatSettingsView from './lib/views/ChatSettingsView.svelte';
  import UserInfoView from './lib/views/UserInfoView.svelte';
  import FinalMessageView from './lib/views/FinalMessageView.svelte';
  import ManualControlView from './lib/views/ManualControlView.svelte';
  import TriggerSettingsView from './lib/views/TriggerSettingsView.svelte';
  import VehicleControlView from './lib/views/VehicleControlView.svelte';

  const sectionDefaults = {
    dashboard: 'dashboard-home',
    'autonomous-driving': 'vehicle-control',
    'map-settings': 'map-generator',
    'ai-settings': 'chat-settings',
    'app-settings': 'app-general',
  };

  const sectionConfigs = {
    dashboard: {
      title: '대시보드',
      icon: 'solar:widget-2-bold-duotone',
      items: [{ id: 'dashboard-home', icon: 'solar:widget-2-bold-duotone', label: '대시보드' }],
    },
    'autonomous-driving': {
      title: '자율주행',
      icon: 'solar:wheel-bold-duotone',
      items: [
        { id: 'vehicle-control', icon: 'solar:widget-2-bold-duotone', label: '차량 제어' },
        { id: 'manual-control', icon: 'solar:gameboy-bold-duotone', label: '메뉴얼 제어' },
        { id: 'triggers', icon: 'solar:atom-bold-duotone', label: '트리거 설정' },
        { id: 'settings', icon: 'solar:settings-bold-duotone', label: '설정' },
      ],
    },
    'map-settings': {
      title: 'Map 설정',
      icon: 'solar:map-point-wave-bold-duotone',
      items: [
        { id: 'map-generator', icon: 'solar:map-bold-duotone', label: 'Map 생성' },
        { id: 'map-library', icon: 'solar:folder-with-files-bold-duotone', label: 'Map 라이브러리' },
        { id: 'map-rag-test', icon: 'solar:magnifer-zoom-in-bold-duotone', label: 'RAG 테스트' },
      ],
    },
    'ai-settings': {
      title: 'AI 설정',
      icon: 'solar:settings-bold-duotone',
      items: [
        { id: 'chat-settings', icon: 'solar:chat-round-dots-bold-duotone', label: '채팅 설정' },
        { id: 'system-messages', icon: 'solar:document-text-bold-duotone', label: '시스템 메시지' },
        { id: 'characters', icon: 'solar:user-bold-duotone', label: '캐릭터' },
        { id: 'commands', icon: 'solar:code-bold-duotone', label: '명령어 템플릿' },
        { id: 'user-info', icon: 'solar:users-group-rounded-bold-duotone', label: '유저 정보' },
        { id: 'final-message', icon: 'solar:check-read-bold-duotone', label: '최종 메시지' },
      ],
    },
    'app-settings': {
      title: '앱 설정',
      icon: 'solar:settings-bold-duotone',
      items: [{ id: 'app-general', icon: 'solar:settings-bold-duotone', label: '일반 설정' }],
    },
  };

  let sidebarWidth = $derived($uiStore.isSidebarCollapsed ? '5.5rem' : '14rem');
  let isChatOpen = $derived($uiStore.isChatOpen);
  let activeSection = $derived($uiStore.activeSection);
  let activeSubView = $derived($uiStore.activeSubView);
  let currentSection = $derived(sectionConfigs[activeSection]);
</script>

<svelte:head>
  <title>AGI Voice V3 Autonomous Driving</title>
  <meta
    name="description"
    content="V3 autonomous driving frontend backed by the Python CarMaker API."
  />
</svelte:head>

<div class="layout" use:disableAutocomplete>
  <TitleBar />
  <Sidebar {sectionDefaults} />

  <main class="main-content" style={`margin-left: ${sidebarWidth};`}>
    <SubSidebar
      title={currentSection.title}
      icon={currentSection.icon}
      items={currentSection.items}
      activeItem={activeSubView}
      onSelect={(id) => uiStore.setSubView(id)}
    >
      {#if activeSection === 'autonomous-driving' && activeSubView === 'vehicle-control'}
        <VehicleControlView />
      {:else if activeSection === 'autonomous-driving' && activeSubView === 'manual-control'}
        <ManualControlView />
      {:else if activeSection === 'autonomous-driving' && activeSubView === 'triggers'}
        <TriggerSettingsView />
      {:else if activeSection === 'autonomous-driving' && activeSubView === 'settings'}
        <SettingsView />
      {:else if activeSection === 'ai-settings' && activeSubView === 'chat-settings'}
        <ChatSettingsView />
      {:else if activeSection === 'ai-settings' && activeSubView === 'user-info'}
        <UserInfoView />
      {:else if activeSection === 'ai-settings' && activeSubView === 'final-message'}
        <FinalMessageView />
      {:else if activeSection === 'ai-settings' && activeSubView === 'characters'}
        <SettingsView />
      {:else if activeSection === 'dashboard'}
        <div class="placeholder-page">
          <h1>대시보드</h1>
          <p>V2 메인 대시보드 화면 이식 전입니다. 현재는 자율주행과 채팅 흐름을 우선 이식 중입니다.</p>
        </div>
      {:else if activeSection === 'app-settings'}
        <div class="placeholder-page">
          <h1>앱 설정</h1>
          <p>앱 설정 페이지는 다음 단계에서 V2 구조 그대로 이식합니다.</p>
        </div>
      {:else if activeSection === 'map-settings'}
        <div class="placeholder-page">
          <h1>Map 설정</h1>
          <p>Map 생성/라이브러리/RAG 테스트 화면은 이후 블록에서 V2 구조로 이식합니다.</p>
        </div>
      {:else if activeSection === 'ai-settings'}
        <div class="placeholder-page">
          <h1>AI 설정</h1>
          <p>채팅 설정 외 나머지 AI 설정 페이지는 다음 단계에서 V2 구조 그대로 이식합니다.</p>
        </div>
      {/if}
    </SubSidebar>
  </main>

  {#if isChatOpen}
    <div class="chat-overlay">
      <AIChatWidget />
    </div>
  {/if}
</div>

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

  .main-content {
    flex: 1;
    margin-top: 40px;
    overflow: hidden;
    transition: margin-left 300ms ease-in-out;
  }

  .chat-overlay {
    position: fixed;
    right: 24px;
    bottom: 24px;
    z-index: 5000;
  }

  .placeholder-page {
    height: 100%;
    padding: 2rem;
    background: var(--color-background);
  }
</style>
