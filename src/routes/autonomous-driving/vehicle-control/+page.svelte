<script lang="ts">
  import { onMount } from 'svelte';
  import Icon from '@iconify/svelte';
  import { carmakerStore } from '$lib/stores/carmakerStore.svelte';
  import { triggerMonitor } from '$lib/stores/triggerMonitor.svelte';

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
      <h1>차량 제어</h1>
      <p class="page-description">CarMaker 차량을 실시간으로 제어합니다.</p>
    </div>
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
        class="btn-compact"
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
        {triggerMonitor.isMonitoring ? 'Stop Trigger' : 'Start Trigger'}
      </button>

      {#if triggerMonitor.isMonitoring}
        <div class="trigger-status">
          <Icon icon="solar:power-bold-duotone" width="16" height="16" class="text-accent" />
          <span class="text-accent">{triggerMonitor.triggers.filter(t => t.isActive).length} active</span>
        </div>
      {:else}
        <div></div>
      {/if}
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
    <h2 class="section-title text-primary">
      Vehicle Data Monitor
    </h2>
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

<style>
  .vehicle-control {
    max-width: 800px;
    margin: 0 auto;
  }

  /* Control Buttons Grid */
  .control-buttons {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
    margin-bottom: 0.75rem;
  }

  .control-buttons:last-child {
    margin-bottom: 0;
  }

  .trigger-status {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.375rem;
    font-size: 0.75rem;
    font-weight: 600;
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
