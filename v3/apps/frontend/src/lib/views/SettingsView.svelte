<script>
  import { onMount } from 'svelte';
  import Icon from '@iconify/svelte';
  import HelpModal from '../components/HelpModal.svelte';
  import { carmakerStore } from '../stores/carmakerStore.svelte.js';

  const SETTINGS_STORAGE_KEY = 'agi_voice_v3_autonomous_settings';
  const controlModes = ['Abs', 'Off', 'Fac', 'AbsRamp', 'FacRamp'];
  const claudeModels = ['sonnet', 'haiku', 'opus'];

  let saving = $state(false);
  let message = $state(null);
  let vehicleCommandParsingEnabled = $state(false);

  let showMonitoringHelpModal = $state(false);
  let showOneTimeHelpModal = $state(false);
  let showChatSettingsHelpModal = $state(false);

  let characters = $state([]);
  let promptTemplates = $state([]);
  let excludeHistory = $state(true);
  let selectedCharacterId = $state('');
  let selectedPromptTemplateId = $state('');
  let selectedModel = $state('sonnet');

  function loadSettings() {
    carmakerStore.loadPersistedSettings();

    if (typeof localStorage === 'undefined') {
      return;
    }

    try {
      const raw = localStorage.getItem(SETTINGS_STORAGE_KEY);
      if (!raw) {
        return;
      }

      const stored = JSON.parse(raw);
      vehicleCommandParsingEnabled = Boolean(stored.vehicleCommandParsingEnabled);
      excludeHistory = stored.excludeHistory !== false;
      selectedCharacterId = stored.selectedCharacterId ?? '';
      selectedPromptTemplateId = stored.selectedPromptTemplateId ?? '';
      selectedModel =
        typeof stored.selectedModel === 'string' ? stored.selectedModel : selectedModel;
    } catch (error) {
      console.warn('Failed to load autonomous settings', error);
    }
  }

  onMount(async () => {
    await carmakerStore.checkConnectionStatus();
    loadSettings();
  });

  async function connect() {
    const success = await carmakerStore.connect();
    if (success) {
      message = {
        type: 'success',
        text: `${carmakerStore.host}:${carmakerStore.port}에 연결되었습니다.`,
      };
      setTimeout(() => {
        message = null;
      }, 3000);
    } else {
      message = { type: 'error', text: '연결에 실패했습니다.' };
      setTimeout(() => {
        message = null;
      }, 3000);
    }
  }

  async function disconnect() {
    const success = await carmakerStore.disconnect();
    if (success) {
      message = { type: 'success', text: 'CarMaker와의 연결이 해제되었습니다.' };
      setTimeout(() => {
        message = null;
      }, 3000);
    }
  }

  async function saveSettings() {
    try {
      saving = true;
      message = null;

      carmakerStore.persistSettings();
      localStorage.setItem(
        SETTINGS_STORAGE_KEY,
        JSON.stringify({
          vehicleCommandParsingEnabled,
          excludeHistory,
          selectedCharacterId,
          selectedPromptTemplateId,
          selectedModel,
        })
      );

      message = { type: 'success', text: '설정이 저장되었습니다.' };
      setTimeout(() => {
        message = null;
      }, 3000);
    } catch (error) {
      message = {
        type: 'error',
        text: error instanceof Error ? error.message : '설정 저장에 실패했습니다.',
      };
    } finally {
      saving = false;
    }
  }
</script>

<div class="autonomous-settings">
  <div class="page-header">
    <div>
      <h1>자율주행 설정</h1>
      <p class="page-description">CarMaker 제어와 관련된 설정을 관리합니다.</p>
    </div>
  </div>

  <div class="settings-form">
    <div class="form-section">
      <h2 class="section-title">
        <Icon icon="solar:link-circle-bold-duotone" width="20" height="20" />
        <span>CarMaker Connection</span>
      </h2>

      <div class="connection-controls">
        <div class="input-group">
          <label for="host">Host:</label>
          <input
            id="host"
            type="text"
            bind:value={carmakerStore.host}
            disabled={carmakerStore.isConnected}
            class="input-field"
          />
        </div>
        <div class="input-group">
          <label for="port">Port:</label>
          <input
            id="port"
            type="text"
            bind:value={carmakerStore.port}
            disabled={carmakerStore.isConnected}
            class="input-field"
          />
        </div>
        <button class="btn-primary" disabled={carmakerStore.isConnected} onclick={connect}>
          Connect
        </button>
        <button class="btn-secondary" disabled={!carmakerStore.isConnected} onclick={disconnect}>
          Disconnect
        </button>
        <div class="status-indicator">
          <span class="status-dot" class:connected={carmakerStore.isConnected}></span>
          <span class="text-secondary">
            {carmakerStore.isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>
    </div>
  </div>

  <div class="settings-form">
    <div class="form-section">
      <h2 class="section-title">
        <Icon icon="solar:settings-minimalistic-bold-duotone" width="20" height="20" />
        <span>Control Settings</span>
      </h2>

      <div class="settings-controls">
        <div class="input-group">
          <label for="duration">Duration (ms):</label>
          <input
            id="duration"
            type="text"
            bind:value={carmakerStore.duration}
            class="input-field"
          />
        </div>
        <div class="input-group">
          <label for="mode">Control Mode:</label>
          <select id="mode" bind:value={carmakerStore.controlMode} class="select-field">
            {#each controlModes as mode}
              <option value={mode}>{mode}</option>
            {/each}
          </select>
        </div>
      </div>
    </div>
  </div>

  <div class="settings-form">
    <div class="form-section">
      <h2 class="section-title">
        <Icon icon="solar:code-square-bold-duotone" width="20" height="20" />
        <span>AI CarMaker Control</span>
      </h2>

      <div class="toggle-row">
        <div class="toggle-info">
          <div class="label-with-help">
            <label for="command-parsing">AI 자율주행 모니터링</label>
            <button class="btn-icon help-btn-inline" onclick={() => (showMonitoringHelpModal = true)}>
              <Icon icon="solar:question-circle-bold" width="18" height="18" />
            </button>
          </div>
        </div>
        <label class="toggle-switch">
          <input id="command-parsing" type="checkbox" bind:checked={vehicleCommandParsingEnabled} />
          <span class="toggle-switch-track">
            <span class="toggle-switch-thumb"></span>
          </span>
        </label>
      </div>

      <div class="toggle-row">
        <div class="toggle-info">
          <div class="label-with-help">
            <label for="exclude-history">일회용 메시지</label>
            <button class="btn-icon help-btn-inline" onclick={() => (showOneTimeHelpModal = true)}>
              <Icon icon="solar:question-circle-bold" width="18" height="18" />
            </button>
          </div>
        </div>
        <label class="toggle-switch">
          <input id="exclude-history" type="checkbox" bind:checked={excludeHistory} />
          <span class="toggle-switch-track">
            <span class="toggle-switch-thumb"></span>
          </span>
        </label>
      </div>

      <div class="subsection">
        <div class="subsection-header">
          <h3 class="subsection-title">
            <Icon icon="solar:chat-round-call-bold-duotone" width="18" height="18" />
            대화 설정
          </h3>
          <button class="btn-icon help-btn-inline" onclick={() => (showChatSettingsHelpModal = true)}>
            <Icon icon="solar:question-circle-bold" width="18" height="18" />
          </button>
        </div>

        <div class="ai-config-grid">
          <div class="form-group">
            <label for="trigger-template">시스템 템플릿</label>
            <select id="trigger-template" bind:value={selectedPromptTemplateId} class="select-field">
              <option value="">선택하세요</option>
              {#each promptTemplates as template}
                <option value={template.id}>{template.name}</option>
              {/each}
            </select>
          </div>

          <div class="form-group">
            <label for="trigger-character">캐릭터</label>
            <select id="trigger-character" bind:value={selectedCharacterId} class="select-field">
              <option value="">선택하세요</option>
              {#each characters as character}
                <option value={character.id}>{character.name}</option>
              {/each}
            </select>
          </div>

          <div class="form-group">
            <label for="trigger-model">모델</label>
            <select id="trigger-model" bind:value={selectedModel} class="select-field">
              {#each claudeModels as model}
                <option value={model}>{model}</option>
              {/each}
            </select>
          </div>
        </div>

        <p class="helper-text">
          캐릭터/템플릿 목록은 아직 Python API 연동 전입니다. 현재는 UX 보존을 위해 빈 목록 상태로
          유지됩니다.
        </p>
      </div>
    </div>
  </div>

  {#if message}
    <div class={message.type === 'success' ? 'alert-success' : 'alert-error'}>
      {message.text}
    </div>
  {/if}

  <div class="form-actions">
    <button type="button" class="btn-primary" onclick={saveSettings} disabled={saving}>
      <Icon icon="solar:diskette-bold-duotone" width="20" height="20" />
      <span>{saving ? '저장 중...' : '설정 저장'}</span>
    </button>
  </div>
</div>

<HelpModal
  bind:visible={showMonitoringHelpModal}
  title="AI 자율주행 모니터링"
  onClose={() => (showMonitoringHelpModal = false)}
>
  <section class="help-section">
    <h4>🤖 AI 자율주행 모니터링이란?</h4>
    <p class="help-desc">
      AI 응답에서 차량 제어 명령을 자동으로 파싱하여 CarMaker에 실행합니다.
    </p>
  </section>
</HelpModal>

<HelpModal
  bind:visible={showOneTimeHelpModal}
  title="일회용 메시지"
  onClose={() => (showOneTimeHelpModal = false)}
>
  <section class="help-section">
    <h4>💬 일회용 메시지란?</h4>
    <p class="help-desc">
      트리거 발동 시 이전 대화 기록 포함 여부를 설정합니다.
    </p>
  </section>
</HelpModal>

<HelpModal
  bind:visible={showChatSettingsHelpModal}
  title="대화 설정"
  onClose={() => (showChatSettingsHelpModal = false)}
>
  <section class="help-section">
    <h4>⚙️ 대화 설정이란?</h4>
    <p class="help-desc">
      트리거 발동 시 AI와 대화할 때 사용할 시스템 템플릿, 캐릭터, 모델을 설정합니다.
    </p>
  </section>
</HelpModal>

<style>
  .autonomous-settings {
    max-width: 800px;
    margin: 0 auto;
  }

  .settings-form {
    background: var(--color-surface);
    border-radius: 0.75rem;
    padding: 2rem;
    box-shadow: var(--shadow-dialog);
    margin-bottom: 1.5rem;
  }

  .form-section {
    margin-bottom: 2rem;
  }

  .form-section:last-child {
    margin-bottom: 0;
  }

  .connection-controls,
  .settings-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .settings-controls {
    gap: 1.5rem;
  }

  .input-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .input-group label {
    font-weight: 600;
    color: var(--color-text-secondary);
  }

  .status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
  }

  .status-dot {
    width: 0.625rem;
    height: 0.625rem;
    border-radius: 999px;
    background: rgba(255, 122, 122, 0.9);
  }

  .status-dot.connected {
    background: rgba(102, 214, 137, 0.95);
  }

  .toggle-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2rem;
    margin-bottom: 1rem;
  }

  .toggle-info {
    flex: 1;
  }

  .label-with-help {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .label-with-help label {
    font-weight: 600;
    font-size: 1rem;
    color: var(--color-text-primary);
    margin: 0;
  }

  .toggle-switch {
    position: relative;
    display: inline-flex;
    align-items: center;
  }

  .toggle-switch input {
    position: absolute;
    opacity: 0;
    pointer-events: none;
  }

  .toggle-switch-track {
    position: relative;
    width: 3.5rem;
    height: 2rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.12);
    transition: background 0.2s ease;
  }

  .toggle-switch-thumb {
    position: absolute;
    top: 0.25rem;
    left: 0.25rem;
    width: 1.5rem;
    height: 1.5rem;
    border-radius: 999px;
    background: white;
    transition: transform 0.2s ease;
  }

  .toggle-switch input:checked + .toggle-switch-track {
    background: rgba(94, 164, 255, 0.45);
  }

  .toggle-switch input:checked + .toggle-switch-track .toggle-switch-thumb {
    transform: translateX(1.5rem);
  }

  .subsection {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid var(--color-border);
  }

  .subsection-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .subsection-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0;
  }

  .ai-config-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-top: 1rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .form-group label {
    font-weight: 600;
    color: var(--color-text-secondary);
    font-size: 0.875rem;
  }

  .helper-text {
    margin: 1rem 0 0;
    color: var(--color-text-secondary);
    line-height: 1.6;
  }

  .alert-success,
  .alert-error {
    padding: 0.875rem 1rem;
    border-radius: 0.75rem;
    margin-bottom: 1rem;
  }

  .alert-success {
    background: rgba(102, 214, 137, 0.14);
    border: 1px solid rgba(102, 214, 137, 0.22);
    color: #bff3ce;
  }

  .alert-error {
    background: rgba(255, 122, 122, 0.14);
    border: 1px solid rgba(255, 122, 122, 0.22);
    color: #ffc0c0;
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
  }

  @media (max-width: 760px) {
    .toggle-row,
    .connection-controls,
    .settings-controls {
      align-items: stretch;
      flex-direction: column;
    }

    .input-group {
      width: 100%;
      flex-direction: column;
      align-items: stretch;
    }

    .ai-config-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
