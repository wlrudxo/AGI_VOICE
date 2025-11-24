<script lang="ts">
  import { onMount } from 'svelte';
  import { invoke } from '@tauri-apps/api/core';
  import Icon from '@iconify/svelte';
  import { carmakerStore } from '$lib/stores/carmakerStore.svelte';
  import HelpModal from '$lib/components/HelpModal.svelte';

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

  // Help modals
  let showMonitoringHelpModal = $state(false);
  let showOneTimeHelpModal = $state(false);
  let showChatSettingsHelpModal = $state(false);

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
      <h1>자율주행 설정</h1>
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

  <!-- AI CarMaker Control Section (Combined) -->
  <div class="settings-form">
    <div class="form-section">
      <h2 class="section-title">
        <Icon icon="solar:code-square-bold-duotone" width="20" height="20" />
        <span>AI CarMaker Control</span>
      </h2>

      <!-- AI 자율주행 모니터링 Toggle -->
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

      <!-- 일회용 메시지 Toggle -->
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

      <!-- 대화 설정 -->
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
      </div>
    </div>
  </div>

  <!-- 메시지 & 저장 버튼 -->
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

<!-- Help Modal: AI 자율주행 모니터링 -->
<HelpModal
  bind:visible={showMonitoringHelpModal}
  title="AI 자율주행 모니터링"
  onClose={() => (showMonitoringHelpModal = false)}
>
  <section class="help-section">
    <h4>🤖 AI 자율주행 모니터링이란?</h4>
    <p class="help-desc">
      AI 응답에서 차량 제어 명령을 자동으로 파싱하여 CarMaker에 실행합니다.
      트리거 발동 시 AI의 응답에 포함된 제어 명령을 자동으로 인식하고 실행합니다.
    </p>
  </section>

  <section class="help-section">
    <h4>📋 명령 형식</h4>
    <p class="help-desc">
      AI 응답에 다음과 같은 형식의 명령을 포함하면 자동으로 파싱되어 실행됩니다.
    </p>

    <div class="command-example">
      <code>DM.Gas = 0.5</code>
      <p>가스 페달을 0.5로 설정 (범위: 0-1)</p>
    </div>

    <div class="command-example">
      <code>DM.Brake = 0.3</code>
      <p>브레이크 페달을 0.3으로 설정 (범위: 0-1)</p>
    </div>

    <div class="command-example">
      <code>DM.Steer.Ang = 0.1</code>
      <p>조향각을 0.1 라디안으로 설정</p>
    </div>
  </section>

  <section class="help-section">
    <h4>🔄 동작 방식</h4>
    <ol class="help-list">
      <li>트리거가 발동되면 AI에게 상황을 전달합니다.</li>
      <li>AI가 응답을 생성하며, 차량 제어 명령을 포함합니다.</li>
      <li>시스템이 응답에서 명령을 자동으로 추출합니다.</li>
      <li>추출된 명령을 CarMaker로 전송하여 실행합니다.</li>
    </ol>
  </section>

  <section class="help-section">
    <h4>⚠️ 사용 전 확인사항</h4>
    <ul class="help-list">
      <li><strong>CarMaker 연결</strong>이 필요합니다 (Connection 섹션에서 연결).</li>
      <li><strong>Vehicle Monitoring</strong>이 활성화되어야 합니다 (차량 제어 탭).</li>
      <li><strong>Trigger Monitoring</strong>은 별도로 제어됩니다 (트리거 설정 탭).</li>
      <li>이 토글은 AI 응답 파싱만 활성화/비활성화합니다.</li>
    </ul>
  </section>
</HelpModal>

<!-- Help Modal: 일회용 메시지 -->
<HelpModal
  bind:visible={showOneTimeHelpModal}
  title="일회용 메시지"
  onClose={() => (showOneTimeHelpModal = false)}
>
  <section class="help-section">
    <h4>💬 일회용 메시지란?</h4>
    <p class="help-desc">
      트리거가 발동될 때마다 AI에게 전송하는 메시지의 대화 기록 포함 여부를 설정합니다.
    </p>
  </section>

  <section class="help-section">
    <h4>✅ 활성화 (일회용)</h4>
    <p class="help-desc">
      트리거 발동마다 <strong>이전 대화 기록 없이</strong> 새로운 요청을 보냅니다.
    </p>

    <div class="example-card">
      <h5>장점</h5>
      <ul class="help-list">
        <li>매번 독립적인 판단을 받을 수 있습니다.</li>
        <li>이전 응답의 영향을 받지 않습니다.</li>
        <li>토큰 사용량이 적습니다.</li>
      </ul>
    </div>

    <div class="example-card">
      <h5>사용 사례</h5>
      <p>단순 규칙 기반 제어, 독립적인 판단이 필요한 경우</p>
    </div>
  </section>

  <section class="help-section">
    <h4>❌ 비활성화 (대화 누적)</h4>
    <p class="help-desc">
      트리거 발동마다 <strong>동일 대화방에 메시지가 누적</strong>됩니다.
    </p>

    <div class="example-card">
      <h5>장점</h5>
      <ul class="help-list">
        <li>AI가 이전 상황을 기억합니다.</li>
        <li>연속적인 의사결정이 가능합니다.</li>
        <li>상황 변화를 추적할 수 있습니다.</li>
      </ul>
    </div>

    <div class="example-card">
      <h5>사용 사례</h5>
      <p>복잡한 시나리오, 상황 인식이 필요한 경우, 학습 기반 제어</p>
    </div>
  </section>

  <section class="help-section">
    <h4>💡 권장 설정</h4>
    <ul class="help-list">
      <li><strong>규칙 모드</strong> (규칙 제어 ON): 일회용 메시지 활성화 권장</li>
      <li><strong>LLM 모드</strong> (트리거만 ON): 대화 누적 권장 (상황 인식)</li>
    </ul>
  </section>
</HelpModal>

<!-- Help Modal: 대화 설정 -->
<HelpModal
  bind:visible={showChatSettingsHelpModal}
  title="대화 설정"
  onClose={() => (showChatSettingsHelpModal = false)}
>
  <section class="help-section">
    <h4>⚙️ 대화 설정이란?</h4>
    <p class="help-desc">
      트리거 발동 시 AI와 대화할 때 사용할 시스템 템플릿, 캐릭터, 모델을 설정합니다.
      여기서 설정한 값은 트리거 전용으로 사용되며, 일반 채팅 위젯과는 별도로 동작합니다.
    </p>
  </section>

  <section class="help-section">
    <h4>📋 설정 항목</h4>

    <div class="command-example">
      <code>시스템 템플릿</code>
      <p>
        AI의 역할과 행동 방식을 정의합니다.
        예: "자율주행 연구 전문가", "차량 제어 전문가"
      </p>
    </div>

    <div class="command-example">
      <code>캐릭터</code>
      <p>
        AI의 말투, 성격, 톤을 정의합니다.
        예: "Research Assistant" - 전문적이고 친절한 톤
      </p>
    </div>

    <div class="command-example">
      <code>모델</code>
      <p>
        사용할 Claude 모델을 선택합니다.
        - sonnet: 균형잡힌 성능 (권장)
        - haiku: 빠른 응답
        - opus: 고성능 (느림)
      </p>
    </div>
  </section>

  <section class="help-section">
    <h4>🔄 기본값 사용</h4>
    <p class="help-desc">
      시스템 템플릿 또는 캐릭터를 "선택하세요"로 두면,
      <strong>AI 설정</strong> 메뉴의 <strong>채팅 설정</strong>에서 지정한 기본값을 사용합니다.
    </p>
    <ul class="help-list">
      <li>트리거 전용 설정을 사용하려면 여기서 직접 선택</li>
      <li>일반 채팅과 동일한 설정을 사용하려면 "선택하세요" 유지</li>
    </ul>
  </section>

  <section class="help-section">
    <h4>💡 Tip</h4>
    <ul class="help-list">
      <li>시스템 템플릿과 캐릭터는 <strong>AI 설정</strong> 메뉴에서 추가/수정할 수 있습니다.</li>
      <li>트리거 전용 시스템 템플릿을 만들어두면 자율주행에 특화된 응답을 받을 수 있습니다.</li>
      <li>모델은 빠른 응답이 필요하면 haiku, 정확도가 중요하면 sonnet을 권장합니다.</li>
    </ul>
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
    display: block;
  }

  /* Label with Help Button */
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

  /* help-btn-inline 스타일은 app.css에 정의됨 */

  /* Subsection Styles */
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

  .example-card {
    background: var(--color-background);
    padding: 1rem;
    border-radius: 0.5rem;
    margin-top: 0.75rem;
  }

  .example-card h5 {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--color-primary);
  }

  .example-card p {
    margin: 0;
    color: var(--color-text-secondary);
    line-height: 1.8;
  }
</style>
