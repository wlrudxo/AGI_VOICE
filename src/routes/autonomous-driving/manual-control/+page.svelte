<script lang="ts">
  import { invoke } from '@tauri-apps/api/core';
  import Icon from '@iconify/svelte';
  import HelpModal from '$lib/components/HelpModal.svelte';

  // Driver inputs
  let gasValue = $state(0.0);
  let brakeValue = $state(0.0);
  let steerValue = $state(0.0);

  // Text command
  let commandInput = $state('');

  // Help modal
  let showHelpModal = $state(false);

  // Log
  let logMessages: string[] = $state([]);

  async function sendControl(controlType: string, value: number) {
    try {
      const duration = 2000; // Default 2 seconds
      let result: string;

      if (controlType === 'Gas') {
        result = await invoke('set_gas', { value, duration });
      } else if (controlType === 'Brake') {
        result = await invoke('set_brake', { value, duration });
      } else if (controlType === 'Steer.Ang') {
        result = await invoke('set_steer', { value, duration });
      } else {
        throw new Error(`Unknown control type: ${controlType}`);
      }

      addLog(`✓ ${controlType} = ${value.toFixed(2)}`);
    } catch (error: any) {
      addLog(`✗ ${controlType} failed: ${error}`);
    }
  }

  async function executeCommand() {
    if (!commandInput.trim()) return;

    try {
      const result = await invoke('execute_vehicle_command', { command: commandInput });
      addLog(`✓ ${commandInput} → ${result}`);
      commandInput = '';
    } catch (error: any) {
      addLog(`✗ Command failed: ${error}`);
    }
  }

  function addLog(message: string) {
    const timestamp = new Date().toLocaleTimeString();
    logMessages = [...logMessages, `[${timestamp}] ${message}`];

    // Keep last 100 messages
    if (logMessages.length > 100) {
      logMessages = logMessages.slice(-100);
    }
  }
</script>

<div class="manual-control">
  <div class="page-header">
    <div>
      <h1>메뉴얼 제어</h1>
      <p class="page-description">차량을 수동으로 제어하고 명령을 실행합니다.</p>
    </div>
  </div>

  <!-- Driver Inputs -->
  <section class="card section">
    <h2 class="section-title text-primary">
      <Icon icon="solar:steering-wheel-bold-duotone" width="24" height="24" />
      Driver Inputs
    </h2>

    <!-- Gas -->
    <div class="control-row">
      <label class="control-label">Gas (0-1):</label>
      <input
        type="range"
        min="0"
        max="1"
        step="0.01"
        bind:value={gasValue}
        class="slider"
      />
      <span class="value-display">{gasValue.toFixed(2)}</span>
      <button class="btn-primary btn-set" onclick={() => sendControl('Gas', gasValue)}>
        Set
      </button>
    </div>

    <!-- Brake -->
    <div class="control-row">
      <label class="control-label">Brake (0-1):</label>
      <input
        type="range"
        min="0"
        max="1"
        step="0.01"
        bind:value={brakeValue}
        class="slider"
      />
      <span class="value-display">{brakeValue.toFixed(2)}</span>
      <button class="btn-primary btn-set" onclick={() => sendControl('Brake', brakeValue)}>
        Set
      </button>
    </div>

    <!-- Steering -->
    <div class="control-row">
      <label class="control-label">Steer (-1~1):</label>
      <input
        type="range"
        min="-1"
        max="1"
        step="0.01"
        bind:value={steerValue}
        class="slider"
      />
      <span class="value-display">{steerValue.toFixed(2)}</span>
      <button class="btn-primary btn-set" onclick={() => sendControl('Steer.Ang', steerValue)}>
        Set
      </button>
    </div>
  </section>

  <!-- Text Command Input -->
  <section class="card section">
    <h2 class="section-title text-primary">
      <Icon icon="solar:code-bold-duotone" width="24" height="24" />
      Text Command Input
      <button class="btn-icon help-btn" onclick={() => (showHelpModal = true)} title="도움말">
        <Icon icon="solar:question-circle-bold" width="20" height="20" />
      </button>
    </h2>
    <div class="command-input-group">
      <input
        type="text"
        bind:value={commandInput}
        placeholder="Enter command..."
        class="input-field command-input"
        onkeydown={(e) => e.key === 'Enter' && executeCommand()}
      />
      <button class="btn-primary" onclick={executeCommand}>
        Execute
      </button>
    </div>
  </section>

  <!-- Log Section -->
  <section class="card section">
    <h2 class="section-title text-primary">
      <Icon icon="solar:document-text-bold-duotone" width="24" height="24" />
      Log
    </h2>
    <div class="log-container">
      {#if logMessages.length === 0}
        <p class="text-muted">No logs yet...</p>
      {:else}
        {#each logMessages as message}
          <div class="log-message text-secondary">{message}</div>
        {/each}
      {/if}
    </div>
  </section>
</div>

<!-- Help Modal -->
<HelpModal
  bind:visible={showHelpModal}
  title="Text Command 도움말"
  onClose={() => (showHelpModal = false)}
>
  <section class="help-section">
    <h4>📋 명령어 형식</h4>
    <p class="help-desc">
      CarMaker APO 프로토콜을 사용하여 차량을 직접 제어할 수 있습니다.
    </p>
  </section>

  <section class="help-section">
    <h4>🚗 차량 제어 명령어</h4>

    <div class="command-example">
      <code>DVAWrite DM.Gas 0.5 2000 Abs</code>
      <p>Gas 페달을 0.5로 2초간 설정</p>
    </div>

    <div class="command-example">
      <code>DVAWrite DM.Brake 0.3 1500 Abs</code>
      <p>Brake 페달을 0.3으로 1.5초간 설정</p>
    </div>

    <div class="command-example">
      <code>DVAWrite DM.Steer.Ang 0.2 3000 Abs</code>
      <p>조향각을 0.2 라디안으로 3초간 설정</p>
    </div>

    <div class="command-example">
      <code>DVAWrite DM.v.Trgt 50 -1 Abs</code>
      <p>목표 속도를 50 m/s로 설정 (무한 지속: -1)</p>
    </div>

    <div class="command-example">
      <code>DVAWrite DM.LaneOffset 0.5 5000 Abs</code>
      <p>차선 오프셋을 0.5m로 5초간 설정</p>
    </div>
  </section>

  <section class="help-section">
    <h4>⚙️ 시뮬레이션 제어</h4>

    <div class="command-example">
      <code>StartSim</code>
      <p>시뮬레이션 시작</p>
    </div>

    <div class="command-example">
      <code>StopSim</code>
      <p>시뮬레이션 중지</p>
    </div>

    <div class="command-example">
      <code>DVAWrite SC.TAccel 0.001 30000 Abs</code>
      <p>시간 가속도를 0.001로 설정 (일시정지 효과)</p>
    </div>
  </section>

  <section class="help-section">
    <h4>📊 변수 읽기</h4>

    <div class="command-example">
      <code>DVARead Car.v</code>
      <p>차량 속도 읽기 (m/s)</p>
    </div>

    <div class="command-example">
      <code>DVARead Vhcl.sRoad</code>
      <p>도로 위치 S 좌표 읽기 (m)</p>
    </div>

    <div class="command-example">
      <code>DVARead Traffic.nObjs</code>
      <p>주변 차량 수 읽기</p>
    </div>
  </section>

  <section class="help-section">
    <h4>📖 DVAWrite 파라미터</h4>
    <div class="param-table">
      <div class="param-row">
        <span class="param-name">Name</span>
        <span class="param-desc">변수명 (예: DM.Gas, DM.Brake)</span>
      </div>
      <div class="param-row">
        <span class="param-name">Value</span>
        <span class="param-desc">설정할 값 (float)</span>
      </div>
      <div class="param-row">
        <span class="param-name">Duration</span>
        <span class="param-desc">지속 시간 (ms), -1은 무한</span>
      </div>
      <div class="param-row">
        <span class="param-name">Mode</span>
        <span class="param-desc">
          <strong>Abs</strong>: 절대값 (즉시 적용)<br />
          <strong>AbsRamp</strong>: 부드러운 전환<br />
          <strong>Fac</strong>: 배율
        </span>
      </div>
    </div>
  </section>

  <section class="help-section">
    <h4>💡 초보자 권장 명령어</h4>

    <div class="command-example highlight">
      <code>DVAWrite DM.Gas 0.3 2000 Abs</code>
      <p>부드러운 가속 테스트</p>
    </div>

    <div class="command-example highlight">
      <code>DVARead Car.v</code>
      <p>현재 속도 확인</p>
    </div>

    <div class="command-example highlight">
      <code>DVAWrite DM.Brake 0.5 1000 Abs</code>
      <p>감속 테스트</p>
    </div>
  </section>
</HelpModal>

<style>
  .manual-control {
    max-width: 800px;
    margin: 0 auto;
  }

  /* Control Row (Sliders) */
  .control-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .control-label {
    min-width: 120px;
    font-weight: 500;
    color: var(--color-text-secondary);
  }

  .value-display {
    min-width: 50px;
    text-align: right;
    font-family: 'Courier New', monospace;
    font-weight: 600;
    color: var(--color-text-primary);
  }

  /* Additional button styles */
  .btn-set {
    min-width: 60px;
  }

  /* Command Input */
  .command-input-group {
    display: flex;
    gap: 0.5rem;
  }

  .command-input {
    flex: 1;
  }

  /* help-btn 스타일은 app.css에 정의됨 */
</style>
