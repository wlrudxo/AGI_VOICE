<script lang="ts">
  import { onMount } from 'svelte';
  import { invoke } from '@tauri-apps/api/core';
  import Icon from '@iconify/svelte';
  import { carmakerStore } from '$lib/stores/carmakerStore.svelte';
  import { triggerMonitor } from '$lib/stores/triggerMonitor.svelte';
  import HelpModal from '$lib/components/HelpModal.svelte';

  interface TriggerCondition {
    id: number;
    name: string;
    isActive: boolean;
    conditions: {
      variable: string;
      operator: string;
      value: string;
    }[];
    logicOperator: 'AND' | 'OR';
    message: string;
    conversationId?: number;
    useRuleControl: boolean;
    debugAction: string;
    createdAt: string;
    updatedAt: string;
  }

  // Triggers from backend
  let triggers: TriggerCondition[] = $state([]);

  // Help modal
  let showHelpModal = $state(false);

  // Load triggers on mount
  onMount(async () => {
    await loadTriggers();
    await carmakerStore.checkConnectionStatus();
  });

  // Note: No cleanup on unmount - triggerMonitor is a global store
  // shared across all autonomous-driving tabs

  async function loadTriggers() {
    try {
      triggers = await invoke('get_triggers');
      // Update trigger monitor with latest triggers
      await triggerMonitor.loadTriggers();
    } catch (error: any) {
      console.error('Failed to load triggers:', error);
    }
  }

  // Available variables (from vehicle-control page)
  const availableVariables = [
    { key: 'Time', desc: 'Simulation Time (s)' },
    { key: 'DM.Gas', desc: 'Gas Pedal (0-1)' },
    { key: 'DM.Brake', desc: 'Brake Pedal (0-1)' },
    { key: 'DM.Steer.Ang', desc: 'Steering Angle (rad)' },
    { key: 'DM.GearNo', desc: 'Gear Number' },
    { key: 'Car.v', desc: 'Vehicle Speed (m/s)' },
    { key: 'Vhcl.YawRate', desc: 'Yaw Rate (rad/s)' },
    { key: 'Vhcl.Steer.Ang', desc: 'Wheel Steering Angle (rad)' },
    { key: 'Vhcl.sRoad', desc: 'Road Position S (m)' },
    { key: 'Vhcl.tRoad', desc: 'Lateral Position T (m)' },
    { key: 'DM.v.Trgt', desc: 'Target Speed (m/s)' },
    { key: 'DM.LaneOffset', desc: 'Lane Offset (m)' },
    { key: 'Traffic.nObjs', desc: 'Active Traffic Objects Count' }
  ];

  const operators = ['>', '<', '>=', '<=', '==', '!='];

  // Form state
  let showForm = $state(false);
  let editingTrigger: TriggerCondition | null = $state(null);
  let formData = $state({
    name: '',
    conditions: [{ variable: 'Car.v', operator: '>', value: '' }],
    logicOperator: 'AND' as 'AND' | 'OR',
    message: '',
    debugAction: ''
  });

  function startCreate() {
    editingTrigger = null;
    formData = {
      name: '',
      conditions: [{ variable: 'Car.v', operator: '>', value: '' }],
      logicOperator: 'AND',
      message: '',
      debugAction: ''
    };
    showForm = true;
  }

  function startEdit(trigger: TriggerCondition) {
    editingTrigger = trigger;
    formData = {
      name: trigger.name,
      conditions: [...trigger.conditions],
      logicOperator: trigger.logicOperator,
      message: trigger.message,
      debugAction: trigger.debugAction
    };
    showForm = true;
  }

  function cancelForm() {
    showForm = false;
    editingTrigger = null;
  }

  function addCondition() {
    formData.conditions = [...formData.conditions, { variable: 'Car.v', operator: '>', value: '' }];
  }

  function removeCondition(index: number) {
    formData.conditions = formData.conditions.filter((_, i) => i !== index);
  }

  async function saveTrigger() {
    if (!formData.name.trim() || !formData.message.trim()) {
      alert('트리거 이름과 메시지를 입력해주세요.');
      return;
    }

    if (formData.conditions.some(c => !c.value.trim())) {
      alert('모든 조건의 값을 입력해주세요.');
      return;
    }

    try {
      if (editingTrigger) {
        // Update existing (preserve useRuleControl)
        await invoke('update_trigger', {
          id: editingTrigger.id,
          request: {
            ...formData,
            useRuleControl: editingTrigger.useRuleControl
          }
        });
      } else {
        // Create new (default useRuleControl to false)
        await invoke('create_trigger', {
          request: {
            ...formData,
            conversationId: null,
            useRuleControl: false
          }
        });
      }

      await loadTriggers();
      cancelForm();
    } catch (error: any) {
      alert(`트리거 저장 실패: ${error}`);
    }
  }

  async function toggleActive(id: number) {
    try {
      await invoke('toggle_trigger', { id });
      await loadTriggers();
    } catch (error: any) {
      alert(`트리거 토글 실패: ${error}`);
    }
  }

  async function toggleRuleControl(id: number) {
    try {
      await invoke('toggle_rule_control', { id });
      await loadTriggers();
    } catch (error: any) {
      alert(`규칙 제어 토글 실패: ${error}`);
    }
  }

  async function deleteTrigger(id: number) {
    if (confirm('이 트리거를 삭제하시겠습니까?')) {
      try {
        await invoke('delete_trigger', { id });
        await loadTriggers();
      } catch (error: any) {
        alert(`트리거 삭제 실패: ${error}`);
      }
    }
  }
</script>

<div class="trigger-settings">
  <div class="page-header">
    <div class="title-row">
      <h1>⚡ 트리거 설정</h1>
      <button class="btn-icon help-btn" onclick={() => (showHelpModal = true)}>
        <Icon icon="solar:question-circle-bold" width="20" height="20" />
      </button>
    </div>
    <div class="header-actions">
      <button class="btn-primary" onclick={startCreate}>
        <Icon icon="solar:add-circle-bold" width="20" height="20" />
        새 트리거
      </button>
    </div>
  </div>

  <!-- Trigger Monitoring Control -->
  <section class="card section monitoring-control">
    <div class="section-header">
      <h2 class="section-title text-primary">
        <Icon icon="solar:monitoring-bold-duotone" width="24" height="24" />
        Trigger Monitoring
      </h2>
      <div class="monitoring-actions">
        {#if !carmakerStore.isConnected}
          <span class="status-badge disconnected">CarMaker Disconnected</span>
        {:else if !carmakerStore.isMonitoring}
          <span class="status-badge warning">Vehicle Monitoring Off</span>
        {:else}
          <button
            class="btn-primary"
            onclick={() => triggerMonitor.isMonitoring ? triggerMonitor.stopMonitoring() : triggerMonitor.startMonitoring()}
          >
            {triggerMonitor.isMonitoring ? 'Stop Trigger Monitoring' : 'Start Trigger Monitoring'}
          </button>
        {/if}
      </div>
    </div>
    {#if triggerMonitor.isMonitoring}
      <div class="monitoring-status">
        <Icon icon="solar:power-bold-duotone" width="20" height="20" class="status-icon active" />
        <span class="text-accent">Monitoring active - {triggers.filter(t => t.isActive).length} triggers enabled</span>
      </div>
    {/if}

    <!-- Trigger Monitor Log -->
    {#if triggerMonitor.logMessages.length > 0}
      <div class="log-section">
        <div class="log-header">
          <h3>Trigger Log</h3>
          <button class="btn-text" onclick={() => triggerMonitor.clearLogs()}>Clear</button>
        </div>
        <div class="log-container">
          {#each triggerMonitor.logMessages as message}
            <div class="log-message text-secondary">{message}</div>
          {/each}
        </div>
      </div>
    {/if}
  </section>

  {#if showForm}
    <!-- Trigger Form -->
    <div class="form-card card section">
      <div class="form-header">
        <h2 class="section-title text-primary">
          <Icon icon="solar:settings-bold-duotone" width="24" height="24" />
          {editingTrigger ? '트리거 수정' : '새 트리거 생성'}
        </h2>
      </div>

      <div class="form-body">
        <!-- Trigger Name -->
        <div class="form-group">
          <label for="trigger-name">트리거 이름</label>
          <input
            type="text"
            id="trigger-name"
            bind:value={formData.name}
            placeholder="예: 속도 초과 경고"
            class="input-field"
          />
        </div>

        <!-- Conditions -->
        <div class="form-group">
          <div class="condition-header">
            <label>발동 조건</label>
            <div class="logic-toggle">
              <button
                class="logic-btn"
                class:active={formData.logicOperator === 'AND'}
                onclick={() => formData.logicOperator = 'AND'}
              >
                AND (모두 충족)
              </button>
              <button
                class="logic-btn"
                class:active={formData.logicOperator === 'OR'}
                onclick={() => formData.logicOperator = 'OR'}
              >
                OR (하나 이상 충족)
              </button>
            </div>
          </div>

          {#each formData.conditions as condition, index}
            <div class="condition-row">
              <select bind:value={condition.variable} class="select-field">
                {#each availableVariables as variable}
                  <option value={variable.key}>{variable.key} - {variable.desc}</option>
                {/each}
              </select>
              <select bind:value={condition.operator} class="select-field operator-select">
                {#each operators as op}
                  <option value={op}>{op}</option>
                {/each}
              </select>
              <input
                type="text"
                bind:value={condition.value}
                placeholder="값"
                class="input-field value-input"
              />
              {#if formData.conditions.length > 1}
                <button class="btn-icon danger" onclick={() => removeCondition(index)}>
                  <Icon icon="solar:trash-bin-trash-bold" width="20" height="20" />
                </button>
              {/if}
            </div>
          {/each}

          <button class="btn-secondary btn-sm" onclick={addCondition}>
            <Icon icon="solar:add-circle-bold" width="16" height="16" />
            조건 추가
          </button>
        </div>

        <!-- LLM Message -->
        <div class="form-group">
          <label for="llm-message">LLM 전송 메시지</label>
          <textarea
            id="llm-message"
            bind:value={formData.message}
            rows="4"
            placeholder="조건 충족 시 LLM에 전송할 메시지를 입력하세요. Vehicle Data는 자동으로 포함됩니다."
            class="textarea-field"
          ></textarea>
          <small class="helper-text">
            트리거 발동 시 이 메시지와 함께 현재 Vehicle Data가 LLM에 전송됩니다.
          </small>
        </div>

        <!-- Debug Action -->
        <div class="form-group">
          <label for="debug-action">Action 예시 (LLM 응답 형식)</label>
          <textarea
            id="debug-action"
            bind:value={formData.debugAction}
            rows="6"
            placeholder="예시: DM.Gas = 0.5&#10;DM.Brake = 0.0&#10;DM.Steer.Ang = 0.1"
            class="textarea-field code-input"
          ></textarea>
          <small class="helper-text">
            LLM 응답 형식으로 작성. 규칙 제어 ON 시 이 액션을 바로 실행합니다.
          </small>
        </div>

        <!-- Form Actions -->
        <div class="form-actions">
          <button class="btn-secondary" onclick={cancelForm}>취소</button>
          <button class="btn-primary" onclick={saveTrigger}>저장</button>
        </div>
      </div>
    </div>
  {:else}
    <!-- Trigger List -->
    <div class="triggers-list">
      {#if triggers.length === 0}
        <div class="empty-state card">
          <Icon icon="solar:atom-bold-duotone" width="64" height="64" class="empty-icon" />
          <p class="text-secondary">등록된 트리거가 없습니다.</p>
          <button class="btn-primary" onclick={startCreate}>
            <Icon icon="solar:add-circle-bold" width="20" height="20" />
            첫 트리거 만들기
          </button>
        </div>
      {:else}
        {#each triggers as trigger}
          <div class="trigger-card card">
            <div class="trigger-header">
              <div class="trigger-title-row">
                <h3 class="trigger-name">{trigger.name}</h3>
                <div class="trigger-actions">
                  <div class="toggle-group">
                    <span class="toggle-label">트리거</span>
                    <label class="toggle-switch">
                      <input
                        type="checkbox"
                        checked={trigger.isActive}
                        onchange={() => toggleActive(trigger.id)}
                      />
                      <span class="toggle-switch-track">
                        <span class="toggle-switch-thumb"></span>
                      </span>
                    </label>
                  </div>
                  <div class="toggle-group">
                    <span class="toggle-label">규칙</span>
                    <label class="toggle-switch">
                      <input
                        type="checkbox"
                        checked={trigger.useRuleControl}
                        onchange={() => toggleRuleControl(trigger.id)}
                      />
                      <span class="toggle-switch-track">
                        <span class="toggle-switch-thumb"></span>
                      </span>
                    </label>
                  </div>
                  <button class="btn-icon" onclick={() => startEdit(trigger)}>
                    <Icon icon="solar:pen-bold" width="20" height="20" />
                  </button>
                  <button class="btn-icon danger" onclick={() => deleteTrigger(trigger.id)}>
                    <Icon icon="solar:trash-bin-trash-bold" width="20" height="20" />
                  </button>
                </div>
              </div>
              <div class="status-badges">
                <span class="trigger-status {trigger.isActive ? 'active' : 'inactive'}">
                  {trigger.isActive ? '활성' : '비활성'}
                </span>
                {#if trigger.useRuleControl}
                  <span class="trigger-status rule-control">규칙 제어</span>
                {/if}
              </div>
            </div>

            <div class="trigger-body">
              <div class="trigger-section">
                <h4>발동 조건 ({trigger.logicOperator})</h4>
                <div class="conditions-list">
                  {#each trigger.conditions as condition, index}
                    <div class="condition-badge">
                      <code>{condition.variable}</code>
                      <span class="operator">{condition.operator}</span>
                      <code>{condition.value}</code>
                      {#if index < trigger.conditions.length - 1}
                        <span class="logic-separator">{trigger.logicOperator}</span>
                      {/if}
                    </div>
                  {/each}
                </div>
              </div>

              <div class="trigger-section">
                <h4>LLM 메시지</h4>
                <p class="message-preview">{trigger.message}</p>
              </div>

              {#if trigger.debugAction}
                <div class="trigger-section">
                  <h4>Action 예시</h4>
                  <pre class="action-preview">{trigger.debugAction}</pre>
                </div>
              {/if}
            </div>
          </div>
        {/each}
      {/if}
    </div>
  {/if}
</div>

<!-- Help Modal -->
<HelpModal
  bind:visible={showHelpModal}
  title="트리거 설정 도움말"
  onClose={() => (showHelpModal = false)}
>
  <section class="help-section">
    <h4>⚡ 트리거란?</h4>
    <p class="help-desc">
      트리거는 차량 데이터(속도, 조향각 등)가 특정 조건을 만족할 때 자동으로 LLM에 메시지를 전송하거나 규칙 기반 제어를 실행하는 시스템입니다.
    </p>
  </section>

  <section class="help-section">
    <h4>🎯 트리거 구성 요소</h4>
    <ul class="help-list">
      <li><strong>이름</strong>: 트리거를 식별할 수 있는 이름</li>
      <li><strong>발동 조건</strong>: 차량 데이터 변수와 비교 연산자, 값으로 구성</li>
      <li><strong>논리 연산자</strong>: AND (모두 충족) 또는 OR (하나 이상 충족)</li>
      <li><strong>LLM 메시지</strong>: 조건 충족 시 LLM에 전송할 메시지</li>
      <li><strong>Action 예시</strong>: 규칙 제어 모드에서 실행할 명령</li>
    </ul>
  </section>

  <section class="help-section">
    <h4>🔧 동작 모드</h4>

    <div class="mode-card">
      <h5>📊 LLM 모드 (트리거 토글 ON, 규칙 토글 OFF)</h5>
      <p>
        1. 트리거 감지<br/>
        2. 시뮬레이션 초감속 (0.001x)<br/>
        3. LLM에 상황 전달 및 응답 대기<br/>
        4. 시뮬레이션 정상 속도 (1.0x)<br/>
        5. LLM 응답 파싱 및 명령 실행
      </p>
    </div>

    <div class="mode-card">
      <h5>📝 규칙 모드 (규칙 토글 ON)</h5>
      <p>
        1. 트리거 감지<br/>
        2. 시뮬레이션 초감속 (0.001x)<br/>
        3. 1초 대기<br/>
        4. 시뮬레이션 정상 속도 (1.0x)<br/>
        5. Action 예시의 명령 실행
      </p>
    </div>
  </section>

  <section class="help-section">
    <h4>📋 Action 예시 형식</h4>
    <p class="help-desc">규칙 모드에서 실행할 차량 제어 명령을 작성합니다.</p>

    <div class="command-example">
      <code>DM.Gas = 0.5</code>
      <p>가스 페달을 0.5로 설정</p>
    </div>

    <div class="command-example">
      <code>DM.Brake = 0.3</code>
      <p>브레이크 페달을 0.3으로 설정</p>
    </div>

    <div class="command-example">
      <code>DM.Steer.Ang = 0.1</code>
      <p>조향각을 0.1 라디안으로 설정</p>
    </div>
  </section>

  <section class="help-section">
    <h4>📌 사용 예시</h4>

    <div class="example-card">
      <h5>속도 초과 감지 트리거</h5>
      <ul class="help-list">
        <li><strong>이름</strong>: 속도 초과 경고</li>
        <li><strong>조건</strong>: Car.v > 27.78 (100km/h 초과)</li>
        <li><strong>메시지</strong>: "차량 속도가 100km/h를 초과했습니다. 감속이 필요합니다."</li>
        <li><strong>Action</strong>:<br/>
          <code>DM.Gas = 0.0<br/>DM.Brake = 0.5</code>
        </li>
      </ul>
    </div>
  </section>

  <section class="help-section">
    <h4>⚙️ 모니터링 활성화</h4>
    <p class="help-desc">
      트리거를 사용하려면:
    </p>
    <ol class="help-list">
      <li>차량 제어 탭에서 CarMaker 연결</li>
      <li>차량 제어 탭에서 Vehicle Monitoring 시작</li>
      <li>트리거 설정 탭에서 "Start Trigger Monitoring" 클릭</li>
      <li>트리거 활성화 (트리거 토글 ON)</li>
    </ol>
  </section>
</HelpModal>

<style>
  .trigger-settings {
    max-width: 1200px;
    margin: 0 auto;
  }

  /* Title Row with Help Button */
  .title-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .help-btn {
    color: var(--color-primary);
  }

  .help-btn:hover {
    background: var(--color-primary-bg-light);
  }

  /* Help Modal Styles */
  :global(.help-section) {
    margin-bottom: 1.5rem;
  }

  :global(.help-section h4) {
    margin: 0 0 0.75rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-text-primary);
  }

  :global(.help-section h5) {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--color-primary);
  }

  :global(.help-desc) {
    margin: 0;
    color: var(--color-text-secondary);
    line-height: 1.6;
  }

  :global(.help-list) {
    margin: 0.5rem 0 0 1.25rem;
    padding: 0;
    color: var(--color-text-secondary);
    line-height: 1.8;
  }

  :global(.help-list li) {
    margin-bottom: 0.375rem;
  }

  :global(.mode-card),
  :global(.example-card) {
    background: var(--color-background);
    padding: 1rem;
    border-radius: 0.5rem;
    margin-top: 0.75rem;
  }

  :global(.mode-card p),
  :global(.example-card p) {
    margin: 0;
    color: var(--color-text-secondary);
    line-height: 1.8;
  }

  :global(.command-example) {
    background: var(--color-background);
    padding: 0.75rem;
    border-radius: 0.375rem;
    margin: 0.5rem 0;
  }

  :global(.command-example code) {
    display: block;
    color: var(--color-primary);
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
  }

  :global(.command-example p) {
    margin: 0;
    font-size: 0.875rem;
    color: var(--color-text-secondary);
  }

  /* Monitoring Control - use existing section styles from app.css */
  .monitoring-actions {
    display: flex;
    gap: 0.75rem;
    align-items: center;
  }

  /* Status badges - custom styles (not in app.css) */
  .status-badge {
    padding: 0.375rem 0.75rem;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    font-weight: 600;
  }

  .status-badge.disconnected {
    background: var(--color-error-bg-light);
    color: var(--color-error);
  }

  .status-badge.warning {
    background: var(--color-warning-bg-light);
    color: var(--color-warning);
  }

  .monitoring-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 1rem;
    padding: 0.75rem;
    background: var(--color-primary-bg-light);
    border-radius: 0.375rem;
  }

  .monitoring-status :global(.status-icon.active) {
    color: var(--color-success);
  }

  /* Log Section - reuse log-container from app.css */
  .log-section {
    margin-top: 1.5rem;
  }

  .log-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .log-header h3 {
    margin: 0;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--color-text-secondary);
  }

  /* Form Card */
  .form-card {
    margin-bottom: 2rem;
  }

  .form-header {
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--color-border);
    margin-bottom: 1.5rem;
  }

  .form-body {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }


  .helper-text {
    color: var(--color-text-secondary);
    font-size: 0.8rem;
  }

  /* Condition Header */
  .condition-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .logic-toggle {
    display: flex;
    gap: 0.5rem;
  }

  .logic-btn {
    padding: 0.25rem 0.75rem;
    border: 1px solid var(--color-border);
    border-radius: 0.375rem;
    background: var(--color-surface);
    color: var(--color-text-secondary);
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .logic-btn:hover {
    border-color: var(--color-primary);
  }

  .logic-btn.active {
    background: var(--color-primary);
    color: white;
    border-color: var(--color-primary);
  }

  /* Condition Row */
  .condition-row {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .operator-select {
    width: 80px;
  }

  .value-input {
    width: 150px;
  }

  /* Form Actions */
  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--color-border);
  }

  /* Empty State Icon */
  .empty-state :global(.empty-icon) {
    color: var(--color-primary);
    opacity: 0.3;
  }

  /* Triggers List */
  .triggers-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  /* Trigger Card */
  .trigger-card {
    padding: 1.5rem;
  }

  .trigger-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--color-border);
  }

  .trigger-title-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex: 1;
  }

  .trigger-name {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-text-primary);
  }

  .trigger-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .trigger-status {
    padding: 0.25rem 0.75rem;
    border-radius: 0.375rem;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .trigger-status.active {
    background: var(--color-success-bg-light);
    color: var(--color-success);
  }

  .trigger-status.inactive {
    background: var(--color-background);
    border: 1px solid var(--color-border);
    color: var(--color-text-muted);
  }

  .trigger-status.rule-control {
    background: var(--color-primary-bg-light);
    color: var(--color-primary);
  }

  .status-badges {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .toggle-group {
    display: flex;
    align-items: center;
    gap: 0.375rem;
  }

  .toggle-label {
    font-size: 0.75rem;
    color: var(--color-text-secondary);
    font-weight: 500;
  }

  .trigger-body {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .trigger-section h4 {
    margin: 0 0 0.5rem 0;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--color-text-secondary);
  }

  .conditions-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .condition-badge {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: 0.375rem;
    font-size: 0.85rem;
  }

  .condition-badge code {
    color: var(--color-primary);
    font-weight: 600;
  }

  .condition-badge .operator {
    color: var(--color-text-secondary);
    font-weight: 600;
  }

  .logic-separator {
    margin-left: 0.5rem;
    padding: 0.125rem 0.5rem;
    background: var(--color-primary);
    color: white;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .message-preview {
    margin: 0;
    padding: 0.75rem;
    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: 0.375rem;
    color: var(--color-text-secondary);
    font-size: 0.9rem;
    line-height: 1.6;
  }

  .code-input {
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    background: var(--color-background);
  }

  /* Action preview */
  .action-preview {
    margin: 0;
    padding: 0.75rem;
    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: 0.375rem;
    color: var(--color-text-secondary);
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    line-height: 1.6;
    overflow-x: auto;
  }
</style>
