<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import Icon from '@iconify/svelte';
  import { carmakerStore } from '$lib/stores/carmakerStore.svelte';

  // Check connection status on mount (for page reload)
  onMount(async () => {
    await carmakerStore.checkConnectionStatus();
  });

  // Cleanup on unmount
  onDestroy(() => {
    carmakerStore.cleanup();
  });

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
    ['Traffic.nObjs', 'Active Traffic Objects Count'],
  ];

  // Track monitoring state before pause
  let wasMonitoringBeforePause = $state(false);

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
</script>

<div class="vehicle-control">
  <div class="page-header">
    <div>
      <h1>🚗 차량 제어</h1>
      <p class="page-description">CarMaker 차량을 실시간으로 제어합니다.</p>
    </div>
    <div class="header-actions">
      <!-- 설정 탭의 connect와 동일 -->
      {#if carmakerStore.isConnected}
        <button class="btn-danger" onclick={() => carmakerStore.disconnect()}>
          <Icon icon="solar:link-broken-bold" width="20" height="20" />
          Disconnect
        </button>
      {:else}
        <button class="btn-primary" onclick={() => carmakerStore.connect()}>
          <Icon icon="solar:link-circle-bold" width="20" height="20" />
          Connect
        </button>
      {/if}
    </div>
  </div>

  <!-- Simulation Control -->
  <section class="card section">
    <h2 class="section-title text-primary">
      <Icon icon="solar:play-circle-bold-duotone" width="24" height="24" />
      Simulation Control
    </h2>
    <div class="control-buttons">
      <button
        class="btn-primary control-btn"
        onclick={startSimulation}
        disabled={!carmakerStore.isConnected}
      >
        <Icon icon="solar:play-bold" width="16" height="16" />
        Start
      </button>
      <button
        class="btn-danger control-btn"
        onclick={stopSimulation}
        disabled={!carmakerStore.isConnected}
      >
        <Icon icon="solar:stop-bold" width="16" height="16" />
        Stop
      </button>
      <button
        class="btn-secondary control-btn"
        onclick={pauseSimulation}
        disabled={!carmakerStore.isConnected}
      >
        <Icon icon="solar:pause-bold" width="16" height="16" />
        Pause (0.001x)
      </button>
      <button
        class="btn-secondary control-btn"
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
        <Icon icon="solar:chart-bold-duotone" width="24" height="24" />
        Vehicle Data Monitor
      </h2>
      <button class="btn-primary" onclick={() => carmakerStore.toggleMonitoring()}>
        {carmakerStore.isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
      </button>
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
          {#each signalDefinitions as [signal, desc]}
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
    <h2 class="section-title text-primary">
      <Icon icon="solar:document-text-bold-duotone" width="24" height="24" />
      Log
    </h2>
    <div class="log-container">
      {#if carmakerStore.logMessages.length === 0}
        <p class="text-muted">No logs yet...</p>
      {:else}
        {#each carmakerStore.logMessages as message}
          <div class="log-message text-secondary">{message}</div>
        {/each}
      {/if}
    </div>
  </section>
</div>

<style>
  .vehicle-control {
    max-width: 640px;
    margin: 0 auto;
  }

  .control-buttons {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
    margin-top: 1.25rem;
  }

  /* Override app.css button styles with more specific selector */
  .control-buttons .control-btn {
    padding: 0.375rem 0.75rem !important;
    font-size: 0.875rem !important;
  }

  /* Monitor table with fixed column widths */
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

  .connection-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .input-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .input-group label {
    font-weight: 500;
    color: var(--color-text-secondary);
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
</style>
