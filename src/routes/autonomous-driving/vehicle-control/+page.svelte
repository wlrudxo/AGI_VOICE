<script lang="ts">
  import { onMount } from 'svelte';
  import Icon from '@iconify/svelte';
  import { carmakerStore } from '$lib/stores/carmakerStore.svelte';
  import { triggerMonitor } from '$lib/stores/triggerMonitor.svelte';
  import { dialogStore } from '$lib/stores/dialogStore.svelte';
  import HelpModal from '$lib/components/HelpModal.svelte';

  // Check connection status on mount (for page reload)
  onMount(async () => {
    await carmakerStore.checkConnectionStatus();
    await triggerMonitor.loadTriggers();
  });

  // Note: No cleanup on unmount - carmakerStore and triggerMonitor are global stores
  // shared across all autonomous-driving tabs

  // Fixed order signal definitions (matches Python implementation order)
  // Array of [signal, description] tuples to maintain display order
  const signalDefinitions: [string, string][] = [
    ['Time', 'Simulation Time (s)'],
    ['DM.Gas', 'Gas Pedal (0-1)'],
    ['DM.Brake', 'Brake Pedal (0-1)'],
    ['DM.Steer.Ang', 'Steering Angle (rad)'],
    ['DM.GearNo', 'Gear Number'],
    ['Car.v', 'Vehicle Speed (m/s)'],
    ['Vhcl.YawRate', 'Yaw Rate (rad/s)'],
    ['Vhcl.Steer.Ang', 'Wheel Steering Angle (rad)'],
    ['Vhcl.sRoad', 'Road Position S (m)'],
    ['Vhcl.tRoad', 'Lateral Position T (m)'],
    ['DM.v.Trgt', 'Target Speed (m/s)'],
    ['DM.LaneOffset', 'Lane Offset (m)'],
    ['Car.tx', 'Ego Position X (m)'],
    ['Car.ty', 'Ego Position Y (m)'],
    ['LongCtrl.AEB.IsActive', 'AEB Active (Braking)'],
    ['Traffic.nObjs', 'Active Traffic Objects Count'],
  ];

  // Traffic quantity descriptions (same as Python implementation)
  const trafficDescMap: Record<string, string> = {
    'tx': 'Position X (m)',
    'ty': 'Position Y (m)',
    'v_0.x': 'Velocity X (m/s)',
    'v_0.y': 'Velocity Y (m/s)',
    'LongVel': 'Long Velocity (m/s)',
    'sRoad': 'Road Pos S (m)',
    'tRoad': 'Lateral Pos T (m)',
  };

  // Get description for any key (ego or traffic)
  function getDescription(key: string): string {
    // Check if it's a base signal
    const baseSignal = signalDefinitions.find(([signal]) => signal === key);
    if (baseSignal) {
      return baseSignal[1];
    }

    // Check if it's a traffic object variable
    if (key.startsWith('Traffic.T')) {
      // Extract: Traffic.T00.v_0.x -> T00, v_0.x
      const withoutPrefix = key.substring(8); // Remove "Traffic."
      const parts = withoutPrefix.split('.', 2);
      if (parts.length === 2) {
        const objName = parts[0]; // T00, T01, ...
        const qty = parts[1]; // tx, ty, v_0.x, ...
        const desc = trafficDescMap[qty];
        if (desc) {
          return `Traffic ${objName} ${desc}`;
        }
      }
    }

    return '';
  }

  // Get all display signals (base signals + dynamic traffic signals)
  const allSignals = $derived(() => {
    const signals: [string, string][] = [...signalDefinitions];

    // Add traffic object signals dynamically
    const trafficKeys = Object.keys(carmakerStore.monitorData)
      .filter(key => key.startsWith('Traffic.T'))
      .sort();

    for (const key of trafficKeys) {
      const desc = getDescription(key);
      if (desc) {
        signals.push([key, desc]);
      }
    }

    return signals;
  });

  // Track monitoring state before pause
  let wasMonitoringBeforePause = $state(false);

  // Help modal
  let showHelpModal = $state(false);

  // Traffic object input
  let trafficObjectInput = $state('');

  // Log container auto-scroll
  let logContainer: HTMLDivElement;

  // Auto-scroll to bottom when logs update
  $effect(() => {
    // Track log changes
    const _carmakerLogs = carmakerStore.logMessages.length;
    const _triggerLogs = triggerMonitor.logMessages.length;

    // Scroll to bottom
    if (logContainer) {
      logContainer.scrollTop = logContainer.scrollHeight;
    }
  });

  // Simulation control functions
  async function startSimulation() {
    try {
      await carmakerStore.executeCommand('StartSim');
      carmakerStore.addLog('✓ Simulation started');
    } catch (error: any) {
      carmakerStore.addLog(`✗ Failed to start simulation: ${error}`);
    }
  }

  async function stopSimulation() {
    try {
      // Reset all controls first, then stop simulation
      await carmakerStore.resetAllControls();
      await carmakerStore.executeCommand('StopSim');
      carmakerStore.addLog('✓ Simulation stopped');
    } catch (error: any) {
      carmakerStore.addLog(`✗ Failed to stop simulation: ${error}`);
    }
  }

  async function pauseSimulation() {
    try {
      wasMonitoringBeforePause = await carmakerStore.pauseSimulation();
    } catch (error: any) {
      // Error already logged in store
    }
  }

  async function resumeSimulation() {
    try {
      await carmakerStore.resumeSimulation(wasMonitoringBeforePause);
      wasMonitoringBeforePause = false;
    } catch (error: any) {
      // Error already logged in store
    }
  }

  /**
   * Reset all vehicle control commands
   * Sends all DM.* commands with 1ms duration to reset state
   */
  async function resetControl() {
    const confirmed = await dialogStore.confirm(
      '모든 차량 제어 명령을 초기화하시겠습니까?\n\n실행 중인 wait_until 및 AI 스크립트가 전부 중단됩니다.',
      'Reset Control'
    );

    if (!confirmed) {
      return;
    }

    try {
      await carmakerStore.resetAllControls();
    } catch (error: any) {
      carmakerStore.addLog(`✗ Reset failed: ${error}`);
    }
  }

  /**
   * Add traffic object to watch list
   */
  async function addTrafficObject() {
    const input = trafficObjectInput.trim();
    if (!input) return;

    // Parse input: accept "T00", "T01", "0", "1", etc.
    let index: number;
    if (input.toUpperCase().startsWith('T')) {
      index = parseInt(input.substring(1), 10);
    } else {
      index = parseInt(input, 10);
    }

    if (isNaN(index) || index < 0) {
      carmakerStore.addLog(`✗ Invalid traffic object: ${input}`);
      return;
    }

    await carmakerStore.addWatchedTrafficObject(index);
    trafficObjectInput = '';
  }
</script>

<div class="vehicle-control">
  <div class="page-header">
    <div class="title-row">
      <h1>차량 제어</h1>
      <button class="btn-icon help-btn" onclick={() => (showHelpModal = true)}>
        <Icon icon="solar:question-circle-bold" width="20" height="20" />
      </button>
    </div>
    <p class="page-description">CarMaker 차량을 실시간으로 제어합니다.</p>
  </div>

  <!-- Simulation Control -->
  <section class="card section">
    <h2 class="section-title text-primary">
      Simulation Control
    </h2>

    <!-- Primary Controls -->
    <div class="control-buttons">
      {#if carmakerStore.isConnected}
        <button class="btn-danger btn-compact" onclick={() => carmakerStore.disconnect()}>
          <Icon icon="solar:link-broken-bold" width="16" height="16" />
          Disconnect
        </button>
      {:else}
        <button class="btn-primary btn-compact" onclick={() => carmakerStore.connect()}>
          <Icon icon="solar:link-circle-bold" width="16" height="16" />
          Connect
        </button>
      {/if}

      <button
        class="btn-compact"
        class:btn-danger={carmakerStore.isMonitoring}
        class:btn-primary={!carmakerStore.isMonitoring}
        onclick={() => carmakerStore.toggleMonitoring()}
        disabled={!carmakerStore.isConnected}
      >
        <Icon
          icon={carmakerStore.isMonitoring ? 'solar:stop-bold' : 'solar:monitoring-bold'}
          width="16"
          height="16"
        />
        {carmakerStore.isMonitoring ? 'Stop Monitor' : 'Start Monitor'}
      </button>

      <button
        class="btn-compact trigger-btn"
        class:btn-danger={triggerMonitor.isMonitoring}
        class:btn-primary={!triggerMonitor.isMonitoring}
        onclick={() => triggerMonitor.isMonitoring ? triggerMonitor.stopMonitoring() : triggerMonitor.startMonitoring()}
        disabled={!carmakerStore.isConnected || !carmakerStore.isMonitoring}
      >
        <Icon
          icon={triggerMonitor.isMonitoring ? 'solar:stop-bold' : 'solar:bolt-bold'}
          width="16"
          height="16"
        />
        {#if triggerMonitor.isMonitoring}
          {triggerMonitor.triggers.filter(t => t.isActive).length} triggered
        {:else}
          Start Trigger
        {/if}
      </button>

      <button
        class="btn-compact btn-secondary"
        onclick={resetControl}
        disabled={!carmakerStore.isConnected}
      >
        <Icon icon="solar:restart-bold" width="16" height="16" />
        Reset Control
      </button>
    </div>

    <!-- Simulation Controls -->
    <div class="control-buttons">
      <button
        class="btn-primary btn-compact"
        onclick={startSimulation}
        disabled={!carmakerStore.isConnected}
      >
        <Icon icon="solar:play-bold" width="16" height="16" />
        Start
      </button>
      <button
        class="btn-danger btn-compact"
        onclick={stopSimulation}
        disabled={!carmakerStore.isConnected}
      >
        <Icon icon="solar:stop-bold" width="16" height="16" />
        Stop
      </button>
      <button
        class="btn-secondary btn-compact"
        onclick={pauseSimulation}
        disabled={!carmakerStore.isConnected}
      >
        <Icon icon="solar:pause-bold" width="16" height="16" />
        Pause (0.001x)
      </button>
      <button
        class="btn-secondary btn-compact"
        onclick={resumeSimulation}
        disabled={!carmakerStore.isConnected}
      >
        <Icon icon="solar:restart-bold" width="16" height="16" />
        Resume (1.0x)
      </button>
    </div>
  </section>

  <!-- Vehicle Data Monitor -->
  <section class="card section">
    <div class="section-header">
      <h2 class="section-title text-primary">
        Vehicle Data Monitor
      </h2>
    </div>

    <!-- Traffic Object Watch List -->
    <div class="traffic-watch-section">
      <div class="traffic-input-row">
        <input
          type="text"
          class="input-field traffic-input"
          placeholder="T00 or 0"
          bind:value={trafficObjectInput}
          onkeydown={(e) => e.key === 'Enter' && addTrafficObject()}
        />
        <button class="btn-primary btn-compact" onclick={addTrafficObject}>
          <Icon icon="solar:add-circle-bold" width="16" height="16" />
          Add
        </button>
        {#if carmakerStore.watchedTrafficObjects.length > 0}
          <button class="btn-secondary btn-compact" onclick={() => carmakerStore.clearWatchedTrafficObjects()}>
            <Icon icon="solar:trash-bin-trash-bold" width="16" height="16" />
            Clear All
          </button>
        {/if}
      </div>
      {#if carmakerStore.watchedTrafficObjects.length > 0}
        <div class="traffic-chips">
          {#each carmakerStore.watchedTrafficObjects as index}
            <span class="traffic-chip">
              T{index.toString().padStart(2, '0')}
              <button class="chip-remove" onclick={() => carmakerStore.removeWatchedTrafficObject(index)}>
                <Icon icon="solar:close-circle-bold" width="14" height="14" />
              </button>
            </span>
          {/each}
        </div>
      {/if}
    </div>

    <div class="table-wrapper" style="max-height: 600px; overflow-y: auto;">
      <table class="table monitor-table">
        <thead>
          <tr>
            <th>Variable</th>
            <th>Value</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          {#each allSignals() as [signal, desc]}
            {@const value = carmakerStore.monitorData[signal]}
            <tr>
              <td class="text-primary">{signal}</td>
              <td class={value !== undefined ? 'text-accent' : 'text-muted'}>
                {value !== undefined && typeof value === 'number' ? value.toFixed(4) : 'N/A'}
              </td>
              <td class="text-secondary">{desc}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </section>

  <!-- Log Section -->
  <section class="card section">
    <div class="section-header">
      <h2 class="section-title text-primary">
        System Log
      </h2>
      <button class="btn-text" onclick={() => { carmakerStore.logMessages = []; triggerMonitor.clearLogs(); }}>
        <Icon icon="solar:trash-bin-trash-bold" width="16" height="16" />
        Clear All
      </button>
    </div>
    <div class="log-container" bind:this={logContainer}>
      {#if carmakerStore.logMessages.length === 0 && triggerMonitor.logMessages.length === 0}
        <p class="text-muted">No logs yet...</p>
      {:else}
        <!-- CarMaker logs -->
        {#each carmakerStore.logMessages as message}
          <div class="log-message text-secondary">{message}</div>
        {/each}
        <!-- Trigger logs -->
        {#each triggerMonitor.logMessages as message}
          <div class="log-message text-secondary">{message}</div>
        {/each}
      {/if}
    </div>
  </section>
</div>

<!-- Help Modal -->
<HelpModal
  bind:visible={showHelpModal}
  title="차량 제어 도움말"
  onClose={() => (showHelpModal = false)}
>
  <section class="help-section">
    <h4>🚗 차량 제어란?</h4>
    <p class="help-desc">
      CarMaker 시뮬레이션 환경에서 차량을 실시간으로 제어하고 모니터링하는 시스템입니다. TCP 연결을 통해 차량 데이터를 수신하고 제어 명령을 전송합니다.
    </p>
  </section>

  <section class="help-section">
    <h4>🔌 연결 및 모니터링 버튼</h4>

    <div class="button-card">
      <h5>Connect / Disconnect</h5>
      <p>
        CarMaker TCP 서버에 연결하거나 연결을 해제합니다.<br/>
        • <strong>Connect</strong>: TCP 연결 시작 (기본 포트: 16660)<br/>
        • <strong>Disconnect</strong>: 연결 해제 및 모든 모니터링 중지
      </p>
    </div>

    <div class="button-card">
      <h5>Start Monitor / Stop Monitor</h5>
      <p>
        차량 데이터 모니터링을 시작하거나 중지합니다.<br/>
        • <strong>Start Monitor</strong>: Vehicle Data Monitor 활성화 (10Hz 폴링)<br/>
        • <strong>Stop Monitor</strong>: 데이터 수신 중지<br/>
        • 트리거 모니터링을 사용하려면 반드시 먼저 활성화해야 합니다.
      </p>
    </div>

    <div class="button-card">
      <h5>Start Trigger / {'{'}n{'}'} triggered</h5>
      <p>
        트리거 모니터링을 시작하거나 중지합니다.<br/>
        • <strong>Start Trigger</strong>: 트리거 조건 감지 시작<br/>
        • <strong>{'{'}n{'}'} triggered</strong>: 활성화된 트리거 개수 표시 (클릭 시 중지)<br/>
        • Start Monitor가 활성화되어 있어야 사용 가능합니다.
      </p>
    </div>

    <div class="button-card">
      <h5>Reset Control</h5>
      <p>
        모든 차량 제어 명령을 초기화합니다.<br/>
        • DM.Gas, DM.Brake, DM.Steer.Ang를 0으로 리셋<br/>
        • 실행 중인 wait_until 및 AI 스크립트 중단<br/>
        • DM.v.Trgt (목표 속도), DM.LaneOffset (차선 오프셋) 리셋
      </p>
    </div>
  </section>

  <section class="help-section">
    <h4>⚙️ 시뮬레이션 제어 버튼</h4>

    <div class="button-card">
      <h5>Start</h5>
      <p>
        CarMaker 시뮬레이션을 시작합니다.<br/>
        • TestRun 실행 시작<br/>
        • 차량 및 환경 초기화
      </p>
    </div>

    <div class="button-card">
      <h5>Stop</h5>
      <p>
        실행 중인 시뮬레이션을 중지합니다.<br/>
        • TestRun 종료<br/>
        • 모든 차량 데이터 초기화
      </p>
    </div>

    <div class="button-card">
      <h5>Pause (0.001x)</h5>
      <p>
        시뮬레이션을 초감속합니다.<br/>
        • 시간 스케일을 0.001x로 설정 (사실상 일시정지)<br/>
        • 차량 모니터링이 활성화된 경우 자동으로 중지됩니다.
      </p>
    </div>

    <div class="button-card">
      <h5>Resume (1.0x)</h5>
      <p>
        시뮬레이션을 정상 속도로 복원합니다.<br/>
        • 시간 스케일을 1.0x로 설정<br/>
        • Pause 전에 모니터링이 활성화되어 있었다면 자동으로 재시작됩니다.
      </p>
    </div>
  </section>

  <section class="help-section">
    <h4>📊 Vehicle Data Monitor</h4>
    <p class="help-desc">
      실시간으로 차량의 상태를 모니터링합니다. Start Monitor 버튼을 클릭하면 10Hz(100ms) 주기로 데이터가 업데이트됩니다.
    </p>

    <div class="monitor-categories">
      <h5>주요 모니터링 데이터:</h5>
      <ul class="help-list">
        <li><strong>Time</strong>: 시뮬레이션 시간 (초)</li>
        <li><strong>DM.Gas, DM.Brake, DM.Steer.Ang</strong>: 가스/브레이크/조향 제어 입력</li>
        <li><strong>Car.v</strong>: 차량 속도 (m/s)</li>
        <li><strong>Vhcl.sRoad, Vhcl.tRoad</strong>: 도로 상의 위치 (종방향/횡방향)</li>
        <li><strong>DM.v.Trgt, DM.LaneOffset</strong>: 목표 속도 및 차선 오프셋</li>
        <li><strong>Traffic.nObjs</strong>: 활성 교통 객체 수</li>
        <li><strong>Traffic.T00.*, Traffic.T01.*</strong>: 교통 객체별 위치, 속도 등</li>
      </ul>
    </div>
  </section>

  <section class="help-section">
    <h4>📋 System Log</h4>
    <p class="help-desc">
      모든 시스템 동작과 명령 실행 결과를 시간순으로 표시합니다.<br/>
      • CarMaker 명령 실행 로그<br/>
      • 트리거 발동 로그<br/>
      • AI 응답 및 차량 제어 명령 실행 로그<br/>
      • Clear All 버튼으로 로그 삭제 가능
    </p>
  </section>

  <section class="help-section">
    <h4>💡 사용 순서</h4>
    <ol class="help-list">
      <li><strong>Connect</strong>: CarMaker TCP 연결</li>
      <li><strong>Start</strong>: 시뮬레이션 시작</li>
      <li><strong>Start Monitor</strong>: 차량 데이터 모니터링 활성화</li>
      <li><strong>Start Trigger</strong>: (선택) 트리거 자동 감지 시작</li>
      <li>트리거 발동 시 자동으로 Pause → AI 응답 → Resume → 명령 실행</li>
      <li>필요 시 <strong>Reset Control</strong>로 제어 초기화</li>
      <li><strong>Stop</strong>: 시뮬레이션 종료</li>
      <li><strong>Disconnect</strong>: 연결 해제</li>
    </ol>
  </section>
</HelpModal>

<style>
  .vehicle-control {
    max-width: 800px;
    margin: 0 auto;
  }

  /* Title Row with Help Button - component specific */
  .title-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  /* Control Buttons Grid - component specific */
  .control-buttons {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
    margin-bottom: 0.75rem;
  }

  .control-buttons:last-child {
    margin-bottom: 0;
  }

  /* Monitor table with fixed column widths - component specific */
  .monitor-table {
    table-layout: fixed;
  }

  .monitor-table th:nth-child(1),
  .monitor-table td:nth-child(1) {
    width: 180px;
  }

  .monitor-table th:nth-child(2),
  .monitor-table td:nth-child(2) {
    width: 120px;
  }

  .monitor-table th:nth-child(3),
  .monitor-table td:nth-child(3) {
    width: auto;
  }

  /* Traffic Watch Section */
  .traffic-watch-section {
    margin-bottom: 1rem;
    padding: 0.75rem;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
  }

  .traffic-input-row {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .traffic-input {
    width: 100px;
    padding: 0.375rem 0.5rem;
    font-size: 0.875rem;
  }

  .traffic-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.375rem;
    margin-top: 0.5rem;
  }

  .traffic-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    background: var(--color-primary-bg-light);
    color: var(--color-primary);
    border-radius: 1rem;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .chip-remove {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    background: none;
    border: none;
    color: var(--color-primary);
    cursor: pointer;
    opacity: 0.7;
    transition: opacity 0.15s;
  }

  .chip-remove:hover {
    opacity: 1;
  }
</style>
