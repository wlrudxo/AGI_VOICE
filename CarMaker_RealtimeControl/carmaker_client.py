import socket
import time
import threading
import logging

class CarMakerClient:
    def __init__(self, host='localhost', port=16660):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.lock = threading.Lock()

        # Ego vehicle quantities (always requested)
        # Using UAQ Names (First column in documentation)
        # 'Vehicle.xxx' are C-Codes, 'Vhcl.xxx' or 'Car.xxx' are UAQ Names.
        self.ego_quantities = [
            'Time',
            'DM.Gas',
            'DM.Brake',
            'DM.Steer.Ang',
            'DM.GearNo',
            'Car.v',            # Absolute velocity of vehicle connected body (UAQ_02 section 26.7.1)
            'Vhcl.YawRate',     # UAQ Name for Yaw Rate
            'Vhcl.Steer.Ang',   # UAQ Name for Steering Angle
            'Vhcl.sRoad',       # UAQ Name for Road Position S
            'Vhcl.tRoad',       # UAQ Name for Lateral Position T
            'DM.v.Trgt',        # Target Speed
            'DM.LaneOffset',    # Lane Offset
        ]

        # Traffic object quantities template (UAQ_08)
        # Object names: T00, T01, T02, ... (auto-generated, type-independent)
        # For each traffic object, these quantities will be requested
        self.traffic_obj_quantities = [
            'tx',       # Global position X (m)
            'ty',       # Global position Y (m)
            # 'tz',       # Global position Z (m)
            'v_0.x',    # Global velocity X (m/s)
            'v_0.y',    # Global velocity Y (m/s)
            # 'v_0.z',    # Global velocity Z (m/s)
            'LongVel',  # Longitudinal velocity (m/s)
            'sRoad',    # Road coordinate (m)
            'tRoad',    # Lateral distance to route (m)
            # 'State',    # State (0=hidden, 1=visible)
        ]

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(2.0)
            self.socket.connect((self.host, self.port))
            self.connected = True
            return True, "Connected successfully"
        except Exception as e:
            self.socket = None
            self.connected = False
            return False, str(e)

    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None
        self.connected = False

    def send_command(self, cmd, timeout=2.0):
        if not self.connected or not self.socket:
            return None

        with self.lock:
            try:
                self.socket.settimeout(timeout)

                full_cmd = f"{cmd}\n"
                self.socket.send(full_cmd.encode())

                # Wait for response (larger buffer for batch reads)
                try:
                    data = self.socket.recv(32768)
                    response = data.decode().strip()
                    return response
                except socket.timeout:
                    # print(f"CMD: {cmd} -> TIMEOUT")
                    return None
            except Exception as e:
                print(f"Send error: {e}")
                self.disconnect()
                return None

    def read_essential_quantities(self):
        """
        Read essential quantities using batch DVARead for maximum performance.

        Strategy (simplified with batch DVARead):
        1. Batch read: Ego quantities + Traffic.nObjs (1 request, ~20ms)
        2. If traffic exists: Batch read all traffic data (1 request, ~26ms for 32 objects)

        Total: ~50ms for all data (vs 4800ms sequential)
        Performance: 183x faster with consistent data snapshot
        """
        results = {}

        # Step 1: Batch read ego quantities + Traffic.nObjs
        batch_vars = self.ego_quantities + ['Traffic.nObjs']
        batch_cmd = "DVARead " + " ".join(batch_vars)

        resp = self.send_command(batch_cmd, timeout=1.0)
        if resp and resp.startswith("O"):
            val_str = resp[1:].strip()
            values = val_str.split()

            if len(values) == len(batch_vars):
                for var, val_str in zip(batch_vars, values):
                    try:
                        results[var] = float(val_str)
                    except:
                        results[var] = None
            else:
                # Fallback: set None for all
                for var in batch_vars:
                    results[var] = None
        else:
            # No response or error
            for var in batch_vars:
                results[var] = None

        # Step 2: If traffic exists, batch read all traffic data
        nObjs = results.get('Traffic.nObjs', 0)
        if nObjs and nObjs > 0:
            try:
                nObjs = int(nObjs)
            except:
                nObjs = 0

        if nObjs > 0:
            # Build all traffic variable names (T00 ~ T{nObjs-1})
            traffic_vars = []
            for i in range(nObjs):
                obj_name = f"T{i:02d}"
                for qty in self.traffic_obj_quantities:
                    var = f"Traffic.{obj_name}.{qty}"
                    traffic_vars.append(var)

            # Batch read all traffic data in one request
            if traffic_vars:
                batch_cmd = "DVARead " + " ".join(traffic_vars)
                resp = self.send_command(batch_cmd, timeout=2.0)

                if resp and resp.startswith("O"):
                    val_str = resp[1:].strip()
                    values = val_str.split()

                    if len(values) == len(traffic_vars):
                        for var, val_str in zip(traffic_vars, values):
                            try:
                                results[var] = float(val_str)
                            except:
                                results[var] = None
                    else:
                        # Partial data or mismatch
                        for i, var in enumerate(traffic_vars):
                            if i < len(values):
                                try:
                                    results[var] = float(values[i])
                                except:
                                    results[var] = None
                            else:
                                results[var] = None
                else:
                    # No response for traffic data
                    for var in traffic_vars:
                        results[var] = None

        return results

    def set_control(self, control_type, value, duration=2000, mode='Abs'):
        """
        Set control value with optional duration (ms) and mode.
        duration: Time in ms to apply the value. Default 2000ms (2s) to make it noticeable.
        mode: 'Abs', 'AbsRamp', 'Fac', etc.
        """
        cmd = ""
        # Map control_type to UAQ name
        uaq_name = ""
        if control_type == 'gas':
            uaq_name = "DM.Gas"
        elif control_type == 'brake':
            uaq_name = "DM.Brake"
        elif control_type == 'steer':
            uaq_name = "DM.Steer.Ang"
        elif control_type == 'speed_target':
            uaq_name = "DM.v.Trgt"
        elif control_type == 'lane_offset':
            uaq_name = "DM.LaneOffset"

        if uaq_name:
            # Format: DVAWrite <Name> <Value> <Duration> <Mode>
            cmd = f"DVAWrite {uaq_name} {value:.4f} {duration} {mode}"
            return self.send_command(cmd)
        return None

    def execute_command(self, command):
        """
        Execute raw CarMaker commands directly.
        Useful for text-based control and LLM integration.

        Supported commands:
        - DVAWrite <Name> <Value> [Duration] [Mode]
        - DVARead <Name>
        - StartSim
        - StopSim
        - GetSimStatus
        - QuantSubscribe
        - LoadTestRun

        Returns: (success, response_or_error_msg)
        """
        if not command or not command.strip():
            return False, "Empty command"

        # Clean up command
        cmd = command.strip()

        # Basic validation for DVAWrite commands
        if cmd.startswith("DVAWrite"):
            # Validate DVAWrite format: DVAWrite <Name> <Value> [Duration] [Mode]
            parts = cmd.split()
            if len(parts) < 3:
                return False, "DVAWrite requires at least Name and Value"

            # Check if it's a DM (Driver Model) command
            if len(parts) >= 2 and parts[1].startswith("DM."):
                # Log for debugging
                print(f"Executing DM command: {cmd}")

        # Send command and get response
        response = self.send_command(cmd)

        if response is None:
            return False, "No response from CarMaker (timeout or connection lost)"
        elif response and response.startswith("E"):
            return False, f"Error: {response}"
        else:
            return True, response if response else "OK (no response)"

    def execute_batch_commands(self, commands_text):
        """
        Execute multiple commands from text input (separated by newlines).
        Returns list of (command, success, response) tuples.
        """
        results = []
        lines = commands_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith('//'):
                continue

            success, response = self.execute_command(line)
            results.append((line, success, response))

            # Small delay between commands to avoid overwhelming CarMaker
            time.sleep(0.01)

        return results
