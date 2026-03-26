<script lang="ts">
  import { onMount } from 'svelte';
  import { requestJson } from '$lib/backend';
  import Icon from '@iconify/svelte';
  import HelpModal from '$lib/components/HelpModal.svelte';
  import { disableAutocomplete } from '$lib/actions/disableAutocomplete';
  import { triggerMonitor } from '$lib/stores/triggerMonitor.svelte';

  interface TriggerCondition {
    id: number;
    name: string;
    isActive: boolean;
    expression: string; // Expression string (e.g., "Traffic.T01.sRoad - Traffic.T00.sRoad < 100")
    message: string;
    conversationId?: number;
    useRuleControl: boolean;
    debugAction: string;
    cooldown: number; // Cooldown time in milliseconds (default: 5000)
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
  });

  async function loadTriggers() {
    try {
      triggers = await requestJson('/api/triggers');
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
    expression: '',
    message: '',
    debugAction: '',
    cooldown: 5000 // Default 5 seconds
  });

  function startCreate() {
    editingTrigger = null;
    formData = {
      name: '',
      expression: '',
      message: '',
      debugAction: '',
      cooldown: 5000
    };
    showForm = true;
  }

  function startEdit(trigger: TriggerCondition) {
    editingTrigger = trigger;
    formData = {
      name: trigger.name,
      expression: trigger.expression,
      message: trigger.message,
      debugAction: trigger.debugAction,
      cooldown: trigger.cooldown
    };
    showForm = true;
  }

  function cancelForm() {
    showForm = false;
    editingTrigger = null;
  }

  async function saveTrigger() {
    if (!formData.name.trim() || !formData.message.trim()) {
      alert('트리거 이름과 메시지를 입력해주세요.');
      return;
    }

    if (!formData.expression.trim()) {
      alert('트리거 조건식을 입력해주세요.');
      return;
    }

    try {
      if (editingTrigger) {
        // Update existing (preserve useRuleControl)
        await requestJson(`/api/triggers/${editingTrigger.id}`, {
          method: 'PUT',
          body: {
            name: formData.name,
            expression: formData.expression,
            message: formData.message,
            debugAction: formData.debugAction,
            cooldown: formData.cooldown,
            useRuleControl: editingTrigger.useRuleControl,
            conversationId: null
          }
        });
      } else {
        // Create new (default useRuleControl to false)
        await requestJson('/api/triggers', {
          method: 'POST',
          body: {
            name: formData.name,
            expression: formData.expression,
            message: formData.message,
            debugAction: formData.debugAction,
            cooldown: formData.cooldown,
            conversationId: null,
            useRuleControl: false
          }
        });
      }

      await loadTriggers();
      // IMPORTANT: Reload triggerMonitor's trigger list if monitoring is active
      if (triggerMonitor.isMonitoring) {
        await triggerMonitor.loadTriggers();
      }
      cancelForm();
    } catch (error: any) {
      alert(`트리거 저장 실패: ${error}`);
    }
  }

  async function toggleActive(id: number) {
    try {
      await requestJson(`/api/triggers/${id}/toggle`, { method: 'POST' });
      await loadTriggers();
      // IMPORTANT: Reload triggerMonitor's trigger list if monitoring is active
      if (triggerMonitor.isMonitoring) {
        await triggerMonitor.loadTriggers();
      }
    } catch (error: any) {
      alert(`트리거 토글 실패: ${error}`);
    }
  }

  async function toggleRuleControl(id: number) {
    try {
      await requestJson(`/api/triggers/${id}/toggle-rule-control`, { method: 'POST' });
      await loadTriggers();
      // IMPORTANT: Reload triggerMonitor's trigger list if monitoring is active
      if (triggerMonitor.isMonitoring) {
        await triggerMonitor.loadTriggers();
      }
    } catch (error: any) {
      alert(`규칙 제어 토글 실패: ${error}`);
    }
  }

  async function deleteTrigger(id: number) {
    if (confirm('이 트리거를 삭제하시겠습니까?')) {
      try {
        await requestJson(`/api/triggers/${id}`, { method: 'DELETE' });
        await loadTriggers();
        // IMPORTANT: Reload triggerMonitor's trigger list if monitoring is active
        if (triggerMonitor.isMonitoring) {
          await triggerMonitor.loadTriggers();
        }
      } catch (error: any) {
        alert(`트리거 삭제 실패: ${error}`);
      }
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
          <label for="trigger-name" class="form-label">트리거 이름</label>
          <input
            type="text"
            id="trigger-name"
            bind:value={formData.name}
            placeholder="예: 속도 초과 경고"
            class="input-field"
          />
        </div>

        <!-- Expression -->
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
              <strong>지원되는 연산자:</strong><br/>
              • 비교: &gt;, &lt;, &gt;=, &lt;=, ==, !=<br/>
              • 논리: &amp;&amp; (AND), || (OR)<br/>
              • 산술: +, -, *, /, %<br/>
              • 함수: abs(), sqrt(), pow(), min(), max()<br/>
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

                <p style="margin-top: 1rem;"><strong>3. 복합 조건 (AND)</strong></p>
                <code>Car.v &gt; 27.78 &amp;&amp; abs(Vhcl.tRoad) &gt; 2.0</code>
                <p class="text-muted">속도 초과 AND 차선 이탈(2m 이상)</p>

                <p style="margin-top: 1rem;"><strong>4. 복합 조건 (OR)</strong></p>
                <code>(Car.v &gt; 30 &amp;&amp; DM.Brake &lt; 0.1) || abs(Vhcl.tRoad) &gt; 3.0</code>
                <p class="text-muted">고속에서 브레이크 미작동 OR 심각한 차선 이탈</p>

                <p style="margin-top: 1rem;"><strong>5. 수학 함수 사용</strong></p>
                <code>sqrt(pow(Vhcl.tRoad, 2) + pow(Vhcl.YawRate, 2)) &gt; 2.5</code>
                <p class="text-muted">횡방향 가속도 벡터 크기가 2.5 초과</p>
              </div>
            </details>
          </div>
        </div>

        <!-- LLM Message -->
        <div class="form-group">
          <label for="llm-message" class="form-label">LLM 전송 메시지</label>
          <textarea
            id="llm-message"
            bind:value={formData.message}
            rows="4"
            placeholder="조건 충족 시 LLM에 전송할 메시지를 입력하세요. Vehicle Data는 자동으로 포함됩니다."
            class="textarea-field"
          ></textarea>
          <p class="form-hint">
            트리거 발동 시 이 메시지와 함께 현재 Vehicle Data가 LLM에 전송됩니다.
          </p>
        </div>

        <!-- Debug Action -->
        <div class="form-group">
          <label for="debug-action" class="form-label">Action 예시 (LLM 응답 형식)</label>
          <textarea
            id="debug-action"
            bind:value={formData.debugAction}
            rows="6"
            placeholder="예시: DM.Gas = 0.5&#10;DM.Brake = 0.0&#10;DM.Steer.Ang = 0.1"
            class="textarea-field code-input"
          ></textarea>
          <p class="form-hint">
            LLM 응답 형식으로 작성. 규칙 제어 ON 시 이 액션을 바로 실행합니다.
          </p>
        </div>

        <!-- Cooldown -->
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
            <span class="cooldown-hint">{(formData.cooldown / 1000).toFixed(1)}초</span>
          </div>
          <p class="form-hint">
            트리거 발동 후 다시 발동할 수 있을 때까지 대기 시간. 조건이 계속 충족되어도 쿨다운 중에는 재발동되지 않습니다.
          </p>
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
                <span class="trigger-status cooldown">
                  쿨다운: {(trigger.cooldown / 1000).toFixed(1)}s
                </span>
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
      <li><strong>쿨다운</strong>: 발동 후 재발동까지 대기 시간 (기본 5000ms)</li>
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

    <div class="example-card">
      <h5>추월 트리거 (전방 차량 접근)</h5>
      <ul class="help-list">
        <li><strong>이름</strong>: 추월</li>
        <li><strong>조건</strong>: (Traffic.T00.sRoad - Vhcl.sRoad) &lt; 40 && (Traffic.T00.sRoad - Vhcl.sRoad) > 0</li>
        <li><strong>메시지</strong>: "전방 차량과의 거리가 가까워졌습니다. 추월하세요."</li>
      </ul>
      <p class="help-warning">⚠️ <strong>> 0 조건 필수!</strong> 없으면 추월 후에도 트리거가 재발동됩니다. (음수도 &lt; 40 만족)</p>
    </div>
  </section>

  <section class="help-section">
    <h4>⚠️ 조건 작성 시 주의사항</h4>
    <ul class="help-list">
      <li><strong>범위 조건</strong>: 단순 비교만으로는 부족한 경우가 있습니다. 예: 거리 &lt; 40 → 음수도 포함됨</li>
      <li><strong>방향 고려</strong>: 전방/후방 판별이 필요하면 > 0 또는 &lt; 0 조건을 추가하세요</li>
      <li><strong>쿨다운</strong>: 트리거별로 설정 가능 (기본 5초). 트리거 발동 후 쿨다운 시간 동안 재발동 방지. 조건이 계속 만족되어도 쿨다운 중에는 무시됨</li>
      <li><strong>괄호 사용</strong>: 복잡한 조건은 괄호로 우선순위를 명확히 하세요</li>
    </ul>
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
    max-width: 800px;
    margin: 0 auto;
  }

  /* Title Row with Help Button */
  .title-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  /* help-btn 스타일은 app.css에 정의됨 */
  /* Help Modal Styles는 HelpModal.svelte에 정의됨 */

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

  .textarea-field {
    width: 100%;
    resize: vertical;
  }

  .code-input {
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    background: var(--color-background);
  }

  /* Action preview (reusing log-container base) */
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

  /* Expression preview (reusing log-container + primary accent) */
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

  /* Example details - use existing card + form-hint styles */
  .example-details {
    margin-top: 0.75rem;
  }

  .example-details summary {
    cursor: pointer;
    font-weight: 600;
    margin-top: 0.5rem;
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

  /* Help warning message */
  .help-warning {
    margin-top: 0.5rem;
    padding: 0.5rem 0.75rem;
    background: var(--color-warning-bg-light, rgba(245, 158, 11, 0.1));
    border-left: 3px solid var(--color-warning, #f59e0b);
    border-radius: 0.25rem;
    font-size: 0.85rem;
    color: var(--color-warning, #f59e0b);
  }

  /* Cooldown input group */
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
</style>
