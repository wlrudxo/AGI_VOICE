<script lang="ts">
  import { onMount } from 'svelte';
  import { invoke } from '@tauri-apps/api/core';
  import Icon from '@iconify/svelte';
  import { carmakerStore } from '$lib/stores/carmakerStore.svelte';

  interface Character {
    id: number;
    name: string;
  }

  interface PromptTemplate {
    id: number;
    name: string;
  }

  const controlModes = ['Abs', 'Off', 'Fac', 'AbsRamp', 'FacRamp'];
  const claudeModels = ['sonnet', 'haiku', 'opus'];

  let saving = $state(false);
  let message = $state<{ type: 'success' | 'error'; text: string } | null>(null);
  let vehicleCommandParsingEnabled = $state(false);

  // Trigger AI settings
  let characters = $state<Character[]>([]);
  let promptTemplates = $state<PromptTemplate[]>([]);
  let excludeHistory = $state(true); // 일회용 메시지 (기본값: true)
  let selectedCharacterId = $state<number | null>(null);
  let selectedPromptTemplateId = $state<number | null>(null);
  let selectedModel = $state('sonnet');

  // Load AI data (characters, templates)
  async function loadAIData() {
    try {
      characters = await invoke<Character[]>('get_characters');
      promptTemplates = await invoke<PromptTemplate[]>('get_prompt_templates');

      // Load default chat settings as fallback
      try {
        const chatSettings: any = await invoke('get_chat_settings');
        if (!selectedCharacterId && chatSettings.defaultCharacterId) {
          selectedCharacterId = chatSettings.defaultCharacterId;
        }
        if (!selectedPromptTemplateId && chatSettings.defaultPromptTemplateId) {
          selectedPromptTemplateId = chatSettings.defaultPromptTemplateId;
        }
        if (!selectedModel && chatSettings.defaultClaudeModel) {
          selectedModel = chatSettings.defaultClaudeModel;
        }
      } catch (err) {
        console.log('No default chat settings found, using first items');
      }
    } catch (error) {
      console.error('Failed to load AI data:', error);
    }
  }

  // Load settings from localStorage
  function loadSettings() {
    try {
      const stored = localStorage.getItem('carmaker_command_parsing_enabled');
      vehicleCommandParsingEnabled = stored === 'true';

      // Load trigger AI settings
      const storedExcludeHistory = localStorage.getItem('trigger_exclude_history');
      excludeHistory = storedExcludeHistory !== 'false'; // Default: true

      const storedCharacterId = localStorage.getItem('trigger_character_id');
      if (storedCharacterId) {
        selectedCharacterId = parseInt(storedCharacterId);
      }

      const storedTemplateId = localStorage.getItem('trigger_prompt_template_id');
      if (storedTemplateId) {
        selectedPromptTemplateId = parseInt(storedTemplateId);
      }

      const storedModel = localStorage.getItem('trigger_model');
      if (storedModel) {
        selectedModel = storedModel;
      }
    } catch (error) {
      console.error('Failed to load parsing settings:', error);
    }
  }

  // Check connection status on mount (for page reload)
  onMount(async () => {
    await carmakerStore.checkConnectionStatus();
    await loadAIData();
    loadSettings();
  });

  async function connect() {
    const success = await carmakerStore.connect();
    if (success) {
      message = { type: 'success', text: `${carmakerStore.host}:${carmakerStore.port}에 연결되었습니다.` };
      setTimeout(() => { message = null; }, 3000);
    } else {
      message = { type: 'error', text: '연결에 실패했습니다.' };
      setTimeout(() => { message = null; }, 3000);
    }
  }

  async function disconnect() {
    const success = await carmakerStore.disconnect();
    if (success) {
      message = { type: 'success', text: 'CarMaker와의 연결이 해제되었습니다.' };
      setTimeout(() => { message = null; }, 3000);
    }
  }

  async function saveSettings() {
    try {
      saving = true;
      message = null;

      // Save vehicle command parsing setting to localStorage
      localStorage.setItem('carmaker_command_parsing_enabled', vehicleCommandParsingEnabled.toString());

      // Save trigger AI settings
      localStorage.setItem('trigger_exclude_history', excludeHistory.toString());
      if (selectedCharacterId) {
        localStorage.setItem('trigger_character_id', selectedCharacterId.toString());
      }
      if (selectedPromptTemplateId) {
        localStorage.setItem('trigger_prompt_template_id', selectedPromptTemplateId.toString());
      }
      localStorage.setItem('trigger_model', selectedModel);

      console.log('Settings saved:', {
        host: carmakerStore.host,
        port: carmakerStore.port,
        duration: carmakerStore.duration,
        controlMode: carmakerStore.controlMode,
        vehicleCommandParsingEnabled,
        triggerAI: {
          excludeHistory,
          characterId: selectedCharacterId,
          promptTemplateId: selectedPromptTemplateId,
          model: selectedModel
        }
      });

      message = { type: 'success', text: '설정이 저장되었습니다.' };

      // 3초 후 메시지 제거
      setTimeout(() => {
        message = null;
      }, 3000);
    } catch (err: any) {
      console.error('Failed to save settings:', err);
      message = { type: 'error', text: err.message || '설정 저장에 실패했습니다.' };
    } finally {
      saving = false;
    }
  }
</script>

<div class="autonomous-settings">
  <div class="page-header">
    <div>
      <h1>⚙️ 자율주행 설정</h1>
      <p class="page-description">CarMaker 제어와 관련된 설정을 관리합니다.</p>
    </div>
  </div>

  <!-- CarMaker Connection Section -->
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
        <button
          class="btn-primary"
          disabled={carmakerStore.isConnected}
          onclick={connect}
        >
          Connect
        </button>
        <button
          class="btn-secondary"
          disabled={!carmakerStore.isConnected}
          onclick={disconnect}
        >
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

  <!-- Control Settings Section -->
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

  <!-- AI Command Parsing Section -->
  <div class="settings-form">
    <div class="form-section">
      <h2 class="section-title">
        <Icon icon="solar:code-square-bold-duotone" width="20" height="20" />
        <span>AI CarMaker Control</span>
      </h2>

      <div class="toggle-row">
        <div class="toggle-info">
          <label for="command-parsing">AI 자율주행 모니터링</label>
          <p class="helper-text">
            AI 응답에서 차량 제어 명령을 자동으로 파싱하여 실행합니다. 트리거 모니터링도 함께 활성화됩니다.
            <br />
            형식: <code>DM.Gas = 0.5</code>, <code>DM.Brake = 0.3</code> 등
          </p>
        </div>
        <label class="toggle-switch">
          <input
            id="command-parsing"
            type="checkbox"
            bind:checked={vehicleCommandParsingEnabled}
          />
          <span class="toggle-switch-track">
            <span class="toggle-switch-thumb"></span>
          </span>
        </label>
      </div>
    </div>
  </div>

  <!-- Trigger AI Settings Section -->
  <div class="settings-form">
    <div class="form-section">
      <h2 class="section-title">
        <Icon icon="solar:chat-round-call-bold-duotone" width="20" height="20" />
        <span>트리거 AI 설정</span>
      </h2>

      <!-- Exclude History Toggle -->
      <div class="toggle-row">
        <div class="toggle-info">
          <label for="exclude-history">일회용 메시지</label>
          <p class="helper-text">
            활성화 시 트리거 발동마다 이전 대화 기록 없이 새로운 요청을 보냅니다.
            <br />
            비활성화 시 동일 대화방에 메시지가 누적됩니다.
          </p>
        </div>
        <label class="toggle-switch">
          <input
            id="exclude-history"
            type="checkbox"
            bind:checked={excludeHistory}
          />
          <span class="toggle-switch-track">
            <span class="toggle-switch-thumb"></span>
          </span>
        </label>
      </div>

      <!-- AI Configuration -->
      <div class="ai-config-grid">
        <div class="form-group">
          <label for="trigger-template">시스템 템플릿</label>
          <select
            id="trigger-template"
            bind:value={selectedPromptTemplateId}
            class="select-field"
          >
            <option value={null}>선택하세요</option>
            {#each promptTemplates as template}
              <option value={template.id}>{template.name}</option>
            {/each}
          </select>
        </div>

        <div class="form-group">
          <label for="trigger-character">캐릭터</label>
          <select
            id="trigger-character"
            bind:value={selectedCharacterId}
            class="select-field"
          >
            <option value={null}>선택하세요</option>
            {#each characters as character}
              <option value={character.id}>{character.name}</option>
            {/each}
          </select>
        </div>

        <div class="form-group">
          <label for="trigger-model">모델</label>
          <select
            id="trigger-model"
            bind:value={selectedModel}
            class="select-field"
          >
            {#each claudeModels as model}
              <option value={model}>{model}</option>
            {/each}
          </select>
        </div>
      </div>

      <p class="helper-text">
        트리거 발동 시 위에서 선택한 AI 설정을 사용합니다. 미선택 시 AI 설정의 기본값을 사용합니다.
      </p>
    </div>
  </div>

  <!-- 메시지 & 저장 버튼 -->
  {#if message}
    <div class="message" class:success={message.type === 'success'} class:error={message.type === 'error'}>
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

<style>
  .autonomous-settings {
    max-width: 800px;
    margin: 0 auto;
  }

  .settings-form {
    background: var(--color-surface);
    border-radius: 0.75rem;
    padding: 2rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1.5rem;
  }

  .form-section {
    margin-bottom: 2rem;
  }

  .form-section:last-child {
    margin-bottom: 0;
  }

  /* Settings Controls */
  .connection-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .settings-controls {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    flex-wrap: wrap;
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

  /* Toggle Row */
  .toggle-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2rem;
  }

  .toggle-info {
    flex: 1;
  }

  .toggle-info label {
    font-weight: 600;
    font-size: 1rem;
    color: var(--color-text-primary);
    display: block;
    margin-bottom: 0.5rem;
  }

  .helper-text {
    font-size: 0.875rem;
    color: var(--color-text-secondary);
    line-height: 1.5;
    margin: 0;
  }

  .helper-text code {
    background: var(--color-background);
    padding: 0.125rem 0.375rem;
    border-radius: 0.25rem;
    font-family: 'Courier New', monospace;
    font-size: 0.8125rem;
    color: var(--color-primary);
  }

  .message {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1.5rem;
    font-weight: 500;
  }

  .message.success {
    background: #d1fae5;
    color: #065f46;
  }

  .message.error {
    background: #fee2e2;
    color: #991b1b;
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
  }

  /* AI Config Grid */
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
</style>
