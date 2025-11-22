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
    <div class="monitor-table-wrapper">
      <table class="monitor-table">
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
    max-width: 1400px;
    margin: 0 auto;
  }

  .page-header {
    margin-bottom: 2rem;
  }

  .page-header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-text-primary);
    margin: 0 0 0.5rem 0;
  }

  .page-description {
    color: var(--color-text-secondary);
    margin: 0;
  }

  /* Section Styles */
  .section {
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-sm);
  }

  .section-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.125rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--color-text-primary);
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  /* Connection Controls */
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

  /* Status Indicator */
  .status-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-left: auto;
  }

  .status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: var(--color-error);
  }

  .status-dot.connected {
    background-color: var(--color-success);
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

  .slider {
    flex: 1;
    height: 6px;
    border-radius: 3px;
    background: var(--color-border);
    outline: none;
    -webkit-appearance: none;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--color-primary);
    cursor: pointer;
  }

  .slider::-moz-range-thumb {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--color-primary);
    cursor: pointer;
    border: none;
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

  /* Monitor Table */
  .monitor-table-wrapper {
    overflow-x: auto;
    max-height: 500px;
    overflow-y: auto;
    border: 1px solid var(--color-border);
    border-radius: 6px;
  }

  .monitor-table {
    width: 100%;
    border-collapse: collapse;
  }

  .monitor-table th {
    position: sticky;
    top: 0;
    background-color: var(--color-surface);
    padding: 0.75rem;
    text-align: left;
    font-weight: 600;
    color: var(--color-text-primary);
    border-bottom: 2px solid var(--color-border);
  }

  .monitor-table td {
    padding: 0.75rem;
    border-bottom: 1px solid var(--color-border);
  }

  .monitor-table tbody tr:hover {
    background-color: var(--color-surface-hover);
  }

  /* Log Container */
  .log-container {
    max-height: 200px;
    overflow-y: auto;
    padding: 1rem;
    background-color: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: 6px;
    font-family: 'Courier New', monospace;
    font-size: 0.875rem;
  }

  .log-message {
    padding: 0.25rem 0;
  }
</style>
