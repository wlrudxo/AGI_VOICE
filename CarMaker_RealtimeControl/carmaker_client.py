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

        # Cached traffic object count (read once)
        self.cached_nObjs = None

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
        # Reset cached values on disconnect
        self.cached_nObjs = None

    def send_command(self, cmd, timeout=2.0):
        if not self.connected or not self.socket:
            return None

        with self.lock:
            try:
                self.socket.settimeout(timeout)

                full_cmd = f"{cmd}\n"
                self.socket.send(full_cmd.encode())

                # Wait for response
                try:
                    data = self.socket.recv(4096)
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
        Read essential quantities with smart traffic filtering.

        Strategy:
        1. Read ego vehicle quantities + Traffic.nObjs
        2. Read sRoad for all traffic objects (lightweight)
        3. Find nearest front and rear vehicles based on sRoad
        4. Read detailed info only for nearest front/rear vehicles

        This reduces reads from 334 to ~50 variables (major speedup!)
        """
        results = {}

        # Step 1: Read ego quantities
        for var in self.ego_quantities:
            resp = self.send_command(f"DVARead {var}", timeout=0.3)
            if resp and resp.startswith("O"):
                try:
                    val_str = resp[1:].strip()
                    results[var] = float(val_str) if val_str else 0.0
                except:
                    results[var] = None
            else:
                results[var] = None

        # Step 2: Read Traffic.nObjs (only first time)
        if self.cached_nObjs is None:
            resp = self.send_command(f"DVARead Traffic.nObjs", timeout=0.3)
            nObjs = 0
            if resp and resp.startswith("O"):
                try:
                    val_str = resp[1:].strip()
                    nObjs = int(float(val_str)) if val_str else 0
                    self.cached_nObjs = nObjs
                    results['Traffic.nObjs'] = nObjs
                except:
                    results['Traffic.nObjs'] = None
            else:
                results['Traffic.nObjs'] = None
        else:
            # Use cached value
            nObjs = self.cached_nObjs
            results['Traffic.nObjs'] = nObjs

        # Step 3: If traffic exists, find nearest front/rear vehicles
        if nObjs > 0:
            ego_sRoad = results.get('Vhcl.sRoad', 0.0)

            # Read sRoad for all traffic objects
            traffic_positions = {}
            for i in range(nObjs):
                obj_name = f"T{i:02d}"
                var = f"Traffic.{obj_name}.sRoad"
                resp = self.send_command(f"DVARead {var}", timeout=0.3)
                if resp and resp.startswith("O"):
                    try:
                        val_str = resp[1:].strip()
                        sRoad = float(val_str) if val_str else 0.0
                        traffic_positions[obj_name] = sRoad
                    except:
                        pass

            # Find nearest front and rear vehicles
            front_vehicle = None
            rear_vehicle = None
            min_front_dist = float('inf')
            min_rear_dist = float('inf')

            for obj_name, sRoad in traffic_positions.items():
                if sRoad > ego_sRoad:  # Front vehicle
                    dist = sRoad - ego_sRoad
                    if dist < min_front_dist:
                        min_front_dist = dist
                        front_vehicle = obj_name
                elif sRoad < ego_sRoad:  # Rear vehicle
                    dist = ego_sRoad - sRoad
                    if dist < min_rear_dist:
                        min_rear_dist = dist
                        rear_vehicle = obj_name

            # Step 4: Read detailed info for nearest vehicles
            target_vehicles = []
            if front_vehicle:
                target_vehicles.append(front_vehicle)
            if rear_vehicle:
                target_vehicles.append(rear_vehicle)

            for obj_name in target_vehicles:
                # Already have sRoad from previous read
                results[f"Traffic.{obj_name}.sRoad"] = traffic_positions[obj_name]

                # Read remaining quantities
                for qty in self.traffic_obj_quantities:
                    if qty == 'sRoad':  # Skip, already read
                        continue
                    var = f"Traffic.{obj_name}.{qty}"
                    resp = self.send_command(f"DVARead {var}", timeout=0.3)
                    if resp and resp.startswith("O"):
                        try:
                            val_str = resp[1:].strip()
                            results[var] = float(val_str) if val_str else 0.0
                        except:
                            results[var] = None
                    else:
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
