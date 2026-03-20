<script>
  import { onMount } from 'svelte';
  import Icon from '@iconify/svelte';
  import HelpModal from '../components/HelpModal.svelte';
  import { disableAutocomplete } from '../disableAutocomplete.js';
  import { dialogStore } from '../stores/dialogStore.svelte.js';
  import { triggerMonitor } from '../stores/triggerMonitor.svelte.js';

  let triggers = $state([]);
  let showHelpModal = $state(false);

  onMount(async () => {
    await loadTriggers();
  });

  async function loadTriggers() {
    triggers = await triggerMonitor.loadTriggers();
  }

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
    { key: 'Traffic.nObjs', desc: 'Active Traffic Objects Count' },
  ];

  const operators = ['>', '<', '>=', '<=', '==', '!='];

  let showForm = $state(false);
  let editingTrigger = $state(null);
  let formData = $state({
    name: '',
    expression: '',
    message: '',
    debugAction: '',
    cooldown: 5000,
  });

  function startCreate() {
    editingTrigger = null;
    formData = {
      name: '',
      expression: '',
      message: '',
      debugAction: '',
      cooldown: 5000,
    };
    showForm = true;
  }

  function startEdit(trigger) {
    editingTrigger = trigger;
    formData = {
      name: trigger.name,
      expression: trigger.expression,
      message: trigger.message,
      debugAction: trigger.debugAction,
      cooldown: trigger.cooldown,
    };
    showForm = true;
  }

  function cancelForm() {
    showForm = false;
    editingTrigger = null;
  }

  async function saveTrigger() {
    if (!formData.name.trim() || !formData.message.trim()) {
      dialogStore.alert('트리거 이름과 메시지를 입력해주세요.', '알림');
      return;
    }

    if (!formData.expression.trim()) {
      dialogStore.alert('트리거 조건식을 입력해주세요.', '알림');
      return;
    }

    try {
      if (editingTrigger) {
        await triggerMonitor.updateTrigger(editingTrigger.id, {
          name: formData.name,
          expression: formData.expression,
          message: formData.message,
          debugAction: formData.debugAction,
          cooldown: Number(formData.cooldown),
          useRuleControl: editingTrigger.useRuleControl,
          conversationId: null,
        });
      } else {
        await triggerMonitor.createTrigger({
          name: formData.name,
          expression: formData.expression,
          message: formData.message,
          debugAction: formData.debugAction,
          cooldown: Number(formData.cooldown),
          conversationId: null,
          useRuleControl: false,
        });
      }

      await loadTriggers();
      if (triggerMonitor.isMonitoring) {
        await triggerMonitor.loadTriggers();
      }
      cancelForm();
    } catch (error) {
      dialogStore.alert(`트리거 저장 실패: ${error}`, '오류');
    }
  }

  async function toggleActive(id) {
    try {
      await triggerMonitor.toggleActive(id);
      await loadTriggers();
      if (triggerMonitor.isMonitoring) {
        await triggerMonitor.loadTriggers();
      }
    } catch (error) {
      dialogStore.alert(`트리거 토글 실패: ${error}`, '오류');
    }
  }

  async function toggleRuleControl(id) {
    try {
      await triggerMonitor.toggleRuleControl(id);
      await loadTriggers();
      if (triggerMonitor.isMonitoring) {
        await triggerMonitor.loadTriggers();
      }
    } catch (error) {
      dialogStore.alert(`규칙 제어 토글 실패: ${error}`, '오류');
    }
  }

  async function deleteTrigger(id) {
    const confirmed = await dialogStore.confirm('이 트리거를 삭제하시겠습니까?', 'Delete Trigger');
    if (!confirmed) {
      return;
    }

    try {
      await triggerMonitor.deleteTrigger(id);
      await loadTriggers();
      if (triggerMonitor.isMonitoring) {
        await triggerMonitor.loadTriggers();
      }
    } catch (error) {
      dialogStore.alert(`트리거 삭제 실패: ${error}`, '오류');
    }
  }
</script>

<div class="trigger-settings">
  <div class="page-header">
    <div class="title-row">
      <h1>트리거 설정</h1>
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

  {#if showForm}
    <div class="form-card card section">
      <div class="form-header">
        <h2 class="section-title text-primary">
          <Icon icon="solar:settings-bold-duotone" width="24" height="24" />
          {editingTrigger ? '트리거 수정' : '새 트리거 생성'}
        </h2>
      </div>

      <div class="form-body">
        <div class="form-group">
          <label for="trigger-name" class="form-label">트리거 이름</label>
          <input
            type="text"
            id="trigger-name"
            bind:value={formData.name}
            placeholder="예: 속도 초과 경고"
            class="input-field"
          />
        </div>

        <div class="form-group">
          <label for="expression" class="form-label">트리거 조건식</label>
          <textarea
            id="expression"
            bind:value={formData.expression}
            rows="3"
            placeholder="예시: Car.v > 27.78 && abs(Vhcl.tRoad) > 2.0"
            class="textarea-field code-input"
            use:disableAutocomplete
          ></textarea>
          <div class="form-hint-box">
            <p class="form-hint">
              <strong>지원되는 연산자:</strong><br />
              • 비교: {operators.join(', ')}<br />
              • 논리: &amp;&amp; (AND), || (OR)<br />
              • 산술: +, -, *, /, %<br />
              • 함수: abs(), sqrt(), pow(), min(), max()<br />
              • 괄호: () 로 우선순위 지정
            </p>
            <details class="example-details">
              <summary class="text-primary" style="cursor: pointer; font-weight: 600; margin-top: 0.5rem;">
                예시 보기
              </summary>
              <div class="example-box">
                <p><strong>1. 속도 초과 감지</strong></p>
                <code>Car.v &gt; 27.78</code>
                <p class="text-muted">차량 속도가 100km/h(27.78m/s) 초과</p>

                <p style="margin-top: 1rem;"><strong>2. 추월 조건 (전방 차량 접근)</strong></p>
                <code>(Traffic.T00.sRoad - Vhcl.sRoad) &lt; 40 &amp;&amp; (Traffic.T00.sRoad - Vhcl.sRoad) &gt; 0</code>
                <p class="text-muted">전방 차량이 <strong>앞에 있고</strong> 거리 40m 미만</p>
                <p class="text-muted" style="color: var(--color-warning); font-size: 0.8rem;">⚠️ &gt; 0 조건 필수! 없으면 추월 후에도 재발동됨</p>
              </div>
            </details>
          </div>
        </div>

        <div class="form-group">
          <label for="llm-message" class="form-label">LLM 전송 메시지</label>
          <textarea
            id="llm-message"
            bind:value={formData.message}
            rows="4"
            placeholder="조건 충족 시 LLM에 전송할 메시지를 입력하세요. Vehicle Data는 자동으로 포함됩니다."
            class="textarea-field"
          ></textarea>
          <p class="form-hint">트리거 발동 시 이 메시지와 함께 현재 Vehicle Data가 LLM에 전송됩니다.</p>
        </div>

        <div class="form-group">
          <label for="debug-action" class="form-label">Action 예시 (LLM 응답 형식)</label>
          <textarea
            id="debug-action"
            bind:value={formData.debugAction}
            rows="6"
            placeholder="예시: DM.Gas = 0.5&#10;DM.Brake = 0.0&#10;DM.Steer.Ang = 0.1"
            class="textarea-field code-input"
          ></textarea>
          <p class="form-hint">LLM 응답 형식으로 작성. 규칙 제어 ON 시 이 액션을 바로 실행합니다.</p>
        </div>

        <div class="form-group">
          <label for="cooldown" class="form-label">쿨다운 (ms)</label>
          <div class="cooldown-input-group">
            <input
              type="number"
              id="cooldown"
              bind:value={formData.cooldown}
              min="0"
              step="100"
              class="input-field cooldown-input"
            />
            <span class="cooldown-hint">{(Number(formData.cooldown) / 1000).toFixed(1)}초</span>
          </div>
          <p class="form-hint">트리거 발동 후 다시 발동할 수 있을 때까지 대기 시간입니다.</p>
        </div>

        <div class="form-group">
          <div class="form-label">사용 가능한 변수</div>
          <div class="param-table">
            {#each availableVariables as variable}
              <div class="param-row">
                <div class="param-name">{variable.key}</div>
                <div class="param-desc">{variable.desc}</div>
              </div>
            {/each}
          </div>
        </div>

        <div class="form-actions">
          <button class="btn-secondary" onclick={cancelForm}>취소</button>
          <button class="btn-primary" onclick={saveTrigger}>저장</button>
        </div>
      </div>
    </div>
  {:else}
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
                      <input type="checkbox" checked={trigger.isActive} onchange={() => toggleActive(trigger.id)} />
                      <span class="toggle-switch-track">
                        <span class="toggle-switch-thumb"></span>
                      </span>
                    </label>
                  </div>
                  <div class="toggle-group">
                    <span class="toggle-label">규칙</span>
                    <label class="toggle-switch">
                      <input type="checkbox" checked={trigger.useRuleControl} onchange={() => toggleRuleControl(trigger.id)} />
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
                <span class="trigger-status cooldown">쿨다운: {(trigger.cooldown / 1000).toFixed(1)}s</span>
              </div>
            </div>

            <div class="trigger-body">
              <div class="trigger-section">
                <h4>발동 조건식</h4>
                <pre class="expression-preview">{trigger.expression}</pre>
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

<HelpModal bind:visible={showHelpModal} title="트리거 설정 도움말" onClose={() => (showHelpModal = false)}>
  <section class="help-section">
    <h4>⚡ 트리거란?</h4>
    <p class="help-desc">차량 데이터가 특정 조건을 만족할 때 자동으로 LLM 메시지 또는 규칙 제어를 실행하는 시스템입니다.</p>
  </section>

  <section class="help-section">
    <h4>🎯 트리거 구성 요소</h4>
    <ul class="help-list">
      <li><strong>이름</strong>: 트리거를 식별할 수 있는 이름</li>
      <li><strong>발동 조건</strong>: 차량 데이터 변수와 비교 연산자, 값으로 구성</li>
      <li><strong>LLM 메시지</strong>: 조건 충족 시 LLM에 전송할 메시지</li>
      <li><strong>Action 예시</strong>: 규칙 제어 모드에서 실행할 명령</li>
      <li><strong>쿨다운</strong>: 발동 후 재발동까지 대기 시간</li>
    </ul>
  </section>

  <section class="help-section">
    <h4>📌 사용 예시</h4>
    <div class="example-card">
      <h5>속도 초과 감지 트리거</h5>
      <ul class="help-list">
        <li><strong>이름</strong>: 속도 초과 경고</li>
        <li><strong>조건</strong>: Car.v &gt; 27.78</li>
        <li><strong>메시지</strong>: "차량 속도가 100km/h를 초과했습니다. 감속이 필요합니다."</li>
      </ul>
    </div>
  </section>
</HelpModal>

<style>
  .trigger-settings {
    max-width: 800px;
    margin: 0 auto;
  }

  .title-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

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

  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--color-border);
  }

  .triggers-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

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

  .trigger-status.cooldown {
    background: var(--color-background);
    color: var(--color-text-secondary);
    border: 1px solid var(--color-border);
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

  .expression-preview {
    margin: 0;
    padding: 0.75rem;
    background: var(--color-primary-bg-light);
    border: 1px solid var(--color-primary);
    border-radius: 0.375rem;
    color: var(--color-primary);
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    line-height: 1.6;
    overflow-x: auto;
    font-weight: 600;
  }

  .example-details {
    margin-top: 0.75rem;
  }

  .example-box {
    margin-top: 0.5rem;
    padding: 1rem;
    background: var(--color-background);
    border-radius: 0.375rem;
    border: 1px solid var(--color-border);
  }

  .example-box code {
    display: block;
    padding: 0.5rem;
    background: var(--color-primary-bg-light);
    color: var(--color-primary);
    border-radius: 0.25rem;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    margin-bottom: 0.25rem;
  }

  .example-box p {
    margin: 0;
    font-size: 0.875rem;
  }

  .cooldown-input-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .cooldown-input {
    width: 150px;
  }

  .cooldown-hint {
    color: var(--color-text-secondary);
    font-size: 0.9rem;
    font-weight: 500;
  }

  .empty-state :global(.empty-icon) {
    color: var(--color-primary);
    opacity: 0.3;
  }
</style>
