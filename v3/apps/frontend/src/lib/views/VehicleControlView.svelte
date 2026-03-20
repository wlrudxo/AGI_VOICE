<script>
  import { onMount } from 'svelte';
  import Icon from '@iconify/svelte';
  import HelpModal from '../components/HelpModal.svelte';
  import { carmakerStore } from '../stores/carmakerStore.svelte.js';
  import { triggerMonitor } from '../stores/triggerMonitor.svelte.js';
  import { dialogStore } from '../stores/dialogStore.svelte.js';

  onMount(async () => {
    await carmakerStore.checkConnectionStatus();
    await triggerMonitor.loadTriggers();
  });

  const signalDefinitions = [
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

  const trafficDescMap = {
    tx: 'Position X (m)',
    ty: 'Position Y (m)',
    'v_0.x': 'Velocity X (m/s)',
    'v_0.y': 'Velocity Y (m/s)',
    LongVel: 'Long Velocity (m/s)',
    sRoad: 'Road Pos S (m)',
    tRoad: 'Lateral Pos T (m)',
  };

  function getDescription(key) {
    const baseSignal = signalDefinitions.find(([signal]) => signal === key);
    if (baseSignal) {
      return baseSignal[1];
    }

    if (key.startsWith('Traffic.T')) {
      const withoutPrefix = key.substring(8);
      const parts = withoutPrefix.split('.', 2);
      if (parts.length === 2) {
        const objName = parts[0];
        const qty = parts[1];
        const desc = trafficDescMap[qty];
        if (desc) {
          return `Traffic ${objName} ${desc}`;
        }
      }
    }

    return '';
  }

  const allSignals = $derived(() => {
    const signals = [...signalDefinitions];
    const trafficKeys = Object.keys(carmakerStore.monitorData)
      .filter((key) => key.startsWith('Traffic.T'))
      .sort();

    for (const key of trafficKeys) {
      const desc = getDescription(key);
      if (desc) {
        signals.push([key, desc]);
      }
    }

    return signals;
  });

  let wasMonitoringBeforePause = $state(false);
  let showHelpModal = $state(false);
  let trafficObjectInput = $state('');
  let logContainer = $state();

  $effect(() => {
    const _carmakerLogs = carmakerStore.logMessages.length;
    const _triggerLogs = triggerMonitor.logMessages.length;

    if (logContainer) {
      logContainer.scrollTop = logContainer.scrollHeight;
    }
  });

  async function startSimulation() {
    try {
      await carmakerStore.executeCommand('StartSim');
      carmakerStore.addLog('✓ Simulation started');
    } catch (error) {
      carmakerStore.addLog(`✗ Failed to start simulation: ${error}`);
    }
  }

  async function stopSimulation() {
    try {
      await carmakerStore.resetAllControls();
      await carmakerStore.executeCommand('StopSim');
      carmakerStore.addLog('✓ Simulation stopped');
    } catch (error) {
      carmakerStore.addLog(`✗ Failed to stop simulation: ${error}`);
    }
  }

  async function pauseSimulation() {
    try {
      wasMonitoringBeforePause = await carmakerStore.pauseSimulation();
    } catch {
      // Store already logged the error.
    }
  }

  async function resumeSimulation() {
    try {
      await carmakerStore.resumeSimulation(wasMonitoringBeforePause);
      wasMonitoringBeforePause = false;
    } catch {
      // Store already logged the error.
    }
  }

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
    } catch (error) {
      carmakerStore.addLog(`✗ Reset failed: ${error}`);
    }
  }

  async function addTrafficObject() {
    const input = trafficObjectInput.trim();
    if (!input) {
      return;
    }

    let index;
    if (input.toUpperCase().startsWith('T')) {
      index = Number.parseInt(input.substring(1), 10);
    } else {
      index = Number.parseInt(input, 10);
    }

    if (Number.isNaN(index) || index < 0) {
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

  <section class="card section">
    <h2 class="section-title text-primary">Simulation Control</h2>

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
        onclick={() =>
          triggerMonitor.isMonitoring ? triggerMonitor.stopMonitoring() : triggerMonitor.startMonitoring()}
        disabled={!carmakerStore.isConnected || !carmakerStore.isMonitoring}
      >
        <Icon
          icon={triggerMonitor.isMonitoring ? 'solar:stop-bold' : 'solar:bolt-bold'}
          width="16"
          height="16"
        />
        {#if triggerMonitor.isMonitoring}
          {triggerMonitor.triggers.filter((t) => t.isActive).length} triggered
        {:else}
          Start Trigger
        {/if}
      </button>

      <button class="btn-compact btn-secondary" onclick={resetControl} disabled={!carmakerStore.isConnected}>
        <Icon icon="solar:restart-bold" width="16" height="16" />
        Reset Control
      </button>
    </div>

    <div class="control-buttons">
      <button class="btn-primary btn-compact" onclick={startSimulation} disabled={!carmakerStore.isConnected}>
        <Icon icon="solar:play-bold" width="16" height="16" />
        Start
      </button>
      <button class="btn-danger btn-compact" onclick={stopSimulation} disabled={!carmakerStore.isConnected}>
        <Icon icon="solar:stop-bold" width="16" height="16" />
        Stop
      </button>
      <button class="btn-secondary btn-compact" onclick={pauseSimulation} disabled={!carmakerStore.isConnected}>
        <Icon icon="solar:pause-bold" width="16" height="16" />
        Pause (0.001x)
      </button>
      <button class="btn-secondary btn-compact" onclick={resumeSimulation} disabled={!carmakerStore.isConnected}>
        <Icon icon="solar:restart-bold" width="16" height="16" />
        Resume (1.0x)
      </button>
    </div>
  </section>

  <section class="card section">
    <div class="section-header">
      <h2 class="section-title text-primary">Vehicle Data Monitor</h2>
    </div>

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

  <section class="card section">
    <div class="section-header">
      <h2 class="section-title text-primary">System Log</h2>
      <button class="btn-text" onclick={() => { carmakerStore.clearLogs(); triggerMonitor.clearLogs(); }}>
        <Icon icon="solar:trash-bin-trash-bold" width="16" height="16" />
        Clear All
      </button>
    </div>
    <div class="log-container" bind:this={logContainer}>
      {#if carmakerStore.logMessages.length === 0 && triggerMonitor.logMessages.length === 0}
        <p class="text-muted">No logs yet...</p>
      {:else}
        {#each carmakerStore.logMessages as message}
          <div class="log-message text-secondary">{message}</div>
        {/each}
        {#each triggerMonitor.logMessages as message}
          <div class="log-message text-secondary">{message}</div>
        {/each}
      {/if}
    </div>
  </section>
</div>

<HelpModal bind:visible={showHelpModal} title="차량 제어 도움말" onClose={() => (showHelpModal = false)}>
  <section class="help-section">
    <h4>🚗 차량 제어란?</h4>
    <p class="help-desc">
      CarMaker 시뮬레이션 환경에서 차량을 실시간으로 제어하고 모니터링하는 시스템입니다. TCP 연결을 통해 차량 데이터를 수신하고 제어 명령을 전송합니다.
    </p>
  </section>

  <section class="help-section">
    <h4>💡 사용 순서</h4>
    <ol class="help-list">
      <li><strong>Connect</strong>: CarMaker TCP 연결</li>
      <li><strong>Start</strong>: 시뮬레이션 시작</li>
      <li><strong>Start Monitor</strong>: 차량 데이터 모니터링 활성화</li>
      <li><strong>Start Trigger</strong>: 트리거 자동 감지 시작</li>
      <li><strong>Reset Control</strong>: 필요 시 제어 명령 초기화</li>
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

  .title-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .control-buttons {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
    margin-bottom: 0.75rem;
  }

  .control-buttons:last-child {
    margin-bottom: 0;
  }

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

  @media (max-width: 900px) {
    .control-buttons {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (max-width: 640px) {
    .control-buttons {
      grid-template-columns: 1fr;
    }

    .traffic-input-row {
      flex-wrap: wrap;
    }
  }
</style>
