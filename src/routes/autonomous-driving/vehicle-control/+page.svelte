<script lang="ts">
  import Icon from '@iconify/svelte';

  // Connection state
  let host = $state('localhost');
  let port = $state('16660');
  let isConnected = $state(false);

  // Driver inputs
  let gasValue = $state(0.0);
  let brakeValue = $state(0.0);
  let steerValue = $state(0.0);

  // Text command
  let commandInput = $state('');

  // Monitor
  let isMonitoring = $state(false);
  let monitorData: Record<string, number | null> = $state({});

  // Log
  let logMessages: string[] = $state([]);

  // Functions
  function connect() {
    // TODO: Implement connection logic
    isConnected = true;
    addLog(`Connecting to ${host}:${port}...`);
  }

  function disconnect() {
    // TODO: Implement disconnection logic
    isConnected = false;
    isMonitoring = false;
    addLog('Disconnected from CarMaker');
  }

  function sendControl(controlType: string, value: number) {
    // TODO: Implement control command
    // Settings will be fetched from autonomous-driving/settings page
    const duration = '2000'; // TODO: Get from settings
    const controlMode = 'Abs'; // TODO: Get from settings
    const command = `DVAWrite DM.${controlType} ${value} ${duration} ${controlMode}`;
    addLog(`Execute: ${command}`);
  }

  function executeCommand() {
    if (!commandInput.trim()) return;
    // TODO: Implement command execution
    addLog(`Execute: ${commandInput}`);
    commandInput = '';
  }

  function toggleMonitoring() {
    isMonitoring = !isMonitoring;
    if (isMonitoring) {
      addLog('Started monitoring');
      // TODO: Start monitoring
    } else {
      addLog('Stopped monitoring');
      // TODO: Stop monitoring
    }
  }

  function addLog(message: string) {
    const timestamp = new Date().toLocaleTimeString();
    logMessages = [...logMessages, `[${timestamp}] ${message}`];
  }

  // Base descriptions for monitor data
  const baseDescMap: Record<string, string> = {
    'Time': 'Simulation Time (s)',
    'DM.Gas': 'Gas Pedal (0-1)',
    'DM.Brake': 'Brake Pedal (0-1)',
    'DM.Steer.Ang': 'Steering Angle (rad)',
    'DM.GearNo': 'Gear Number',
    'Car.v': 'Vehicle Speed (m/s)',
    'Vhcl.YawRate': 'Yaw Rate (rad/s)',
    'Vhcl.Steer.Ang': 'Wheel Steering Angle (rad)',
    'Vhcl.sRoad': 'Road Position S (m)',
    'Vhcl.tRoad': 'Lateral Position T (m)',
    'DM.v.Trgt': 'Target Speed (m/s)',
    'DM.LaneOffset': 'Lane Offset (m)',
    'Traffic.nObjs': 'Active Traffic Objects Count',
  };
</script>

<div class="vehicle-control">
  <div class="page-header">
    <h1>🚗 차량 제어</h1>
    <p class="page-description">CarMaker 차량을 실시간으로 제어합니다.</p>
  </div>

  <!-- Vehicle Data Monitor -->
  <section class="card section">
    <div class="section-header">
      <h2 class="section-title text-primary">
        <Icon icon="solar:chart-bold-duotone" width="24" height="24" />
        Vehicle Data Monitor
      </h2>
      <button class="btn-primary" onclick={toggleMonitoring}>
        {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
      </button>
    </div>
    <div class="table-wrapper" style="max-height: 500px; overflow-y: auto;">
      <table class="table">
        <thead>
          <tr>
            <th>Variable</th>
            <th>Value</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          {#if Object.keys(monitorData).length === 0}
            {#each Object.entries(baseDescMap) as [key, desc]}
              <tr>
                <td class="text-primary">{key}</td>
                <td class="text-muted">N/A</td>
                <td class="text-secondary">{desc}</td>
              </tr>
            {/each}
          {:else}
            {#each Object.entries(monitorData) as [key, value]}
              <tr>
                <td class="text-primary">{key}</td>
                <td class="text-accent">{value !== null ? value.toFixed(4) : 'Err'}</td>
                <td class="text-secondary">{baseDescMap[key] || ''}</td>
              </tr>
            {/each}
          {/if}
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

<style>
  .vehicle-control {
    max-width: 800px;
    margin: 0 auto;
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
