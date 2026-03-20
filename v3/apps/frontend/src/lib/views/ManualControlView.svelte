<script>
  import Icon from '@iconify/svelte';
  import HelpModal from '../components/HelpModal.svelte';
  import { carmakerStore } from '../stores/carmakerStore.svelte.js';

  let gasValue = $state(0.0);
  let brakeValue = $state(0.0);
  let steerValue = $state(0.0);
  let laneOffsetValue = $state(0.0);
  let targetVelocityValue = $state(0.0);
  let commandInput = $state('');
  let showHelpModal = $state(false);
  let logMessages = $state([]);

  function addLog(message) {
    const timestamp = new Date().toLocaleTimeString();
    logMessages = [...logMessages, `[${timestamp}] ${message}`].slice(-100);
  }

  async function sendControl(controlType, value) {
    try {
      if (controlType === 'Gas') {
        await carmakerStore.setGas(value, 2000);
      } else if (controlType === 'Brake') {
        await carmakerStore.setBrake(value, 2000);
      } else if (controlType === 'Steer.Ang') {
        await carmakerStore.setSteer(value, 2000);
      } else if (controlType === 'LaneOffset') {
        await carmakerStore.setLaneOffset(value, 2000);
      } else if (controlType === 'v.Trgt') {
        await carmakerStore.setTargetVelocity(value, 2000);
      } else {
        throw new Error(`Unknown control type: ${controlType}`);
      }

      addLog(`✓ ${controlType} = ${value.toFixed(2)}`);
    } catch (error) {
      addLog(`✗ ${controlType} failed: ${error}`);
    }
  }

  async function executeCommand() {
    if (!commandInput.trim()) {
      return;
    }

    try {
      const result = await carmakerStore.executeCommand(commandInput);
      addLog(`✓ ${commandInput} → ${result}`);
      commandInput = '';
    } catch (error) {
      addLog(`✗ Command failed: ${error}`);
    }
  }
</script>

<div class="manual-control">
  <div class="page-header">
    <div class="title-row">
      <div>
        <h1>메뉴얼 제어</h1>
        <p class="page-description">차량을 수동으로 제어하고 명령을 실행합니다.</p>
      </div>
      <button class="btn-icon help-btn" onclick={() => (showHelpModal = true)} title="도움말">
        <Icon icon="solar:question-circle-bold" width="20" height="20" />
      </button>
    </div>
  </div>

  <section class="card section">
    <h2 class="section-title text-primary">
      <Icon icon="solar:steering-wheel-bold-duotone" width="24" height="24" />
      Driver Inputs
    </h2>

    <div class="control-row">
      <span class="control-label">Gas (0-1):</span>
      <input type="range" min="0" max="1" step="0.01" bind:value={gasValue} class="slider" />
      <span class="value-display">{gasValue.toFixed(2)}</span>
      <button class="btn-primary btn-set" onclick={() => sendControl('Gas', gasValue)}>Set</button>
    </div>

    <div class="control-row">
      <span class="control-label">Brake (0-1):</span>
      <input type="range" min="0" max="1" step="0.01" bind:value={brakeValue} class="slider" />
      <span class="value-display">{brakeValue.toFixed(2)}</span>
      <button class="btn-primary btn-set" onclick={() => sendControl('Brake', brakeValue)}>Set</button>
    </div>

    <div class="control-row">
      <span class="control-label">Steer (-1~1):</span>
      <input type="range" min="-1" max="1" step="0.01" bind:value={steerValue} class="slider" />
      <span class="value-display">{steerValue.toFixed(2)}</span>
      <button class="btn-primary btn-set" onclick={() => sendControl('Steer.Ang', steerValue)}>Set</button>
    </div>

    <div class="control-row">
      <span class="control-label">LaneOffset (-6.5~6.5):</span>
      <input type="range" min="-6.5" max="6.5" step="0.1" bind:value={laneOffsetValue} class="slider" />
      <span class="value-display">{laneOffsetValue.toFixed(1)}</span>
      <button class="btn-primary btn-set" onclick={() => sendControl('LaneOffset', laneOffsetValue)}>Set</button>
    </div>

    <div class="control-row">
      <span class="control-label">v.Trgt (0~50 m/s):</span>
      <input type="range" min="0" max="50" step="0.5" bind:value={targetVelocityValue} class="slider" />
      <span class="value-display">{targetVelocityValue.toFixed(1)}</span>
      <button class="btn-primary btn-set" onclick={() => sendControl('v.Trgt', targetVelocityValue)}>Set</button>
    </div>
  </section>

  <section class="card section">
    <h2 class="section-title text-primary">
      <Icon icon="solar:code-bold-duotone" width="24" height="24" />
      Text Command Input
    </h2>
    <div class="command-input-group">
      <input
        type="text"
        bind:value={commandInput}
        placeholder="Enter command..."
        class="input-field command-input"
        onkeydown={(e) => e.key === 'Enter' && executeCommand()}
      />
      <button class="btn-primary" onclick={executeCommand}>Execute</button>
    </div>
  </section>

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

<HelpModal bind:visible={showHelpModal} title="Text Command 도움말" onClose={() => (showHelpModal = false)}>
  <section class="help-section">
    <h4>📋 명령어 형식</h4>
    <p class="help-desc">CarMaker APO 프로토콜을 사용하여 차량을 직접 제어할 수 있습니다.</p>
  </section>

  <section class="help-section">
    <h4>🚗 차량 제어 명령어</h4>
    <div class="command-example"><code>DVAWrite DM.Gas 0.5 2000 Abs</code><p>Gas 페달을 0.5로 2초간 설정</p></div>
    <div class="command-example"><code>DVAWrite DM.Brake 0.3 1500 Abs</code><p>Brake 페달을 0.3으로 1.5초간 설정</p></div>
    <div class="command-example"><code>DVAWrite DM.Steer.Ang 0.2 3000 Abs</code><p>조향각을 0.2 라디안으로 3초간 설정</p></div>
    <div class="command-example"><code>DVAWrite DM.v.Trgt 50 -1 Abs</code><p>목표 속도를 50 m/s로 설정 (무한 지속: -1)</p></div>
    <div class="command-example"><code>DVAWrite DM.LaneOffset 0.5 5000 Abs</code><p>차선 오프셋을 0.5m로 5초간 설정</p></div>
  </section>

  <section class="help-section">
    <h4>⚙️ 시뮬레이션 제어</h4>
    <div class="command-example"><code>StartSim</code><p>시뮬레이션 시작</p></div>
    <div class="command-example"><code>StopSim</code><p>시뮬레이션 중지</p></div>
    <div class="command-example"><code>DVAWrite SC.TAccel 0.001 30000 Abs</code><p>시간 가속도를 0.001로 설정 (일시정지 효과)</p></div>
  </section>
</HelpModal>

<style>
  .manual-control {
    max-width: 800px;
    margin: 0 auto;
  }

  .title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
  }

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

  .slider {
    flex: 1;
  }

  .value-display {
    min-width: 50px;
    text-align: right;
    font-family: 'Courier New', monospace;
    font-weight: 600;
    color: var(--color-text-primary);
  }

  .btn-set {
    min-width: 60px;
  }

  .command-input-group {
    display: flex;
    gap: 0.5rem;
  }

  .command-input {
    flex: 1;
  }

  @media (max-width: 760px) {
    .control-row {
      flex-wrap: wrap;
    }

    .control-label,
    .value-display,
    .btn-set {
      min-width: auto;
      width: 100%;
      text-align: left;
    }

    .command-input-group {
      flex-direction: column;
    }
  }
</style>
