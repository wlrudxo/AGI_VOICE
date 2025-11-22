#!/usr/bin/env python3
"""
CarMaker LLM Control Interface
Terminal-based interface for LLM to control CarMaker

Usage:
    python carmaker_llm_control.py --status              # Get all vehicle info
    python carmaker_llm_control.py --cmd "DVAWrite DM.Gas 0.5 2000 Abs"
    python carmaker_llm_control.py --cmd "StartSim"
    python carmaker_llm_control.py --batch commands.txt  # Execute multiple commands from file
"""

import argparse
import sys
import json
from carmaker_client import CarMakerClient
import time


class CarMakerLLMInterface:
    def __init__(self, host='localhost', port=16660):
        self.client = CarMakerClient(host=host, port=port)
        self.connected = False

        # Essential quantities to read for status
        self.status_quantities = [
            'Time',
            'DM.Gas',
            'DM.Brake',
            'DM.Steer.Ang',
            'DM.GearNo',
            'Car.v',
            'Vhcl.YawRate',
            'Vhcl.Steer.Ang',
            'Vhcl.sRoad',
            'Vhcl.tRoad',
            'Env.Time',
            'DM.v.Trgt',
            'DM.LaneOffset',
            'SC.State',
            'SC.TAccel',
        ]

    def connect(self):
        """Connect to CarMaker"""
        success, msg = self.client.connect()
        if success:
            self.connected = True
            return {"success": True, "message": msg}
        else:
            return {"success": False, "message": msg}

    def disconnect(self):
        """Disconnect from CarMaker"""
        if self.connected:
            self.client.disconnect()
            self.connected = False

    def get_status(self):
        """
        Get comprehensive vehicle status
        Returns all essential quantities in JSON format
        """
        if not self.connected:
            conn_result = self.connect()
            if not conn_result["success"]:
                return {"error": "Not connected to CarMaker", "details": conn_result["message"]}

        status_data = {}

        # Read all essential quantities
        for var in self.status_quantities:
            resp = self.client.send_command(f"DVARead {var}")
            if resp and resp.startswith("O"):
                try:
                    val_str = resp[1:].strip()
                    if val_str:
                        status_data[var] = float(val_str)
                    else:
                        status_data[var] = None
                except ValueError:
                    status_data[var] = val_str  # Keep as string if not a number
            else:
                status_data[var] = None

        # Get simulation status
        sim_status = self.client.send_command("GetSimStatus")
        status_data["SimStatus"] = sim_status if sim_status else "Unknown"

        # Add human-readable interpretations
        status_data["_interpretation"] = self._interpret_status(status_data)

        return status_data

    def _interpret_status(self, data):
        """Add human-readable interpretation of status"""
        interpretation = {}

        # Simulation state
        sc_state = data.get("SC.State")
        if sc_state is not None:
            if sc_state < 0:
                state_map = {
                    -1: "Preprocessing",
                    -2: "Idle/Ready",
                    -3: "Postprocessing",
                    -4: "Model Check",
                    -5: "Driver Adaptation",
                    -6: "FATAL ERROR",
                    -7: "Waiting for License",
                    -8: "Simulation paused",
                    -10: "Starting application",
                    -11: "Simulink Initialization"
                }
                interpretation["simulation_state"] = state_map.get(int(sc_state), "Unknown")
            else:
                interpretation["simulation_state"] = f"Running (cycle {int(sc_state)})"

        # Vehicle speed in km/h
        if data.get("Car.v") is not None:
            interpretation["speed_kmh"] = round(data["Car.v"] * 3.6, 2)

        # Time acceleration
        if data.get("SC.TAccel") is not None:
            taccel = data["SC.TAccel"]
            if taccel < 0.01:
                interpretation["time_mode"] = "Paused (near zero speed)"
            elif taccel < 0.9:
                interpretation["time_mode"] = f"Slow motion ({taccel}x)"
            elif taccel > 1.1:
                interpretation["time_mode"] = f"Fast forward ({taccel}x)"
            else:
                interpretation["time_mode"] = "Normal speed"

        # Driver inputs
        interpretation["driver_inputs"] = {
            "gas": data.get("DM.Gas"),
            "brake": data.get("DM.Brake"),
            "steering_rad": data.get("DM.Steer.Ang"),
            "gear": int(data.get("DM.GearNo")) if data.get("DM.GearNo") is not None else None
        }

        return interpretation

    def execute_command(self, command):
        """
        Execute a DVA command or simulation control command
        Returns result in JSON format
        """
        if not self.connected:
            conn_result = self.connect()
            if not conn_result["success"]:
                return {"error": "Not connected to CarMaker", "details": conn_result["message"]}

        success, response = self.client.execute_command(command)

        return {
            "command": command,
            "success": success,
            "response": response,
            "timestamp": time.time()
        }

    def execute_batch(self, commands_text):
        """
        Execute multiple commands
        Returns list of results
        """
        if not self.connected:
            conn_result = self.connect()
            if not conn_result["success"]:
                return {"error": "Not connected to CarMaker", "details": conn_result["message"]}

        results = self.client.execute_batch_commands(commands_text)

        output = []
        for cmd, success, response in results:
            output.append({
                "command": cmd,
                "success": success,
                "response": response
            })

        return output


def main():
    parser = argparse.ArgumentParser(
        description='CarMaker LLM Control Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get vehicle status (all sensor data)
  python carmaker_llm_control.py --status

  # Execute single command
  python carmaker_llm_control.py --cmd "DVAWrite DM.Gas 0.5 2000 Abs"

  # Start simulation
  python carmaker_llm_control.py --cmd "StartSim"

  # Execute multiple commands from file
  python carmaker_llm_control.py --batch commands.txt

  # Specify CarMaker host/port
  python carmaker_llm_control.py --host 192.168.1.100 --port 16660 --status

For LLM Integration:
  The output is always in JSON format for easy parsing.
  Use --status to get current vehicle state before sending commands.
        """
    )

    parser.add_argument('--status', action='store_true',
                        help='Get comprehensive vehicle status')
    parser.add_argument('--cmd', type=str,
                        help='Execute a single command')
    parser.add_argument('--batch', type=str,
                        help='Execute commands from file (one per line)')
    parser.add_argument('--host', type=str, default='localhost',
                        help='CarMaker host (default: localhost)')
    parser.add_argument('--port', type=int, default=16660,
                        help='CarMaker port (default: 16660)')
    parser.add_argument('--pretty', action='store_true',
                        help='Pretty print JSON output')

    args = parser.parse_args()

    # Create interface
    interface = CarMakerLLMInterface(host=args.host, port=args.port)

    try:
        result = None

        if args.status:
            # Get status
            result = interface.get_status()

        elif args.cmd:
            # Execute single command
            result = interface.execute_command(args.cmd)

        elif args.batch:
            # Execute batch commands
            try:
                with open(args.batch, 'r') as f:
                    commands_text = f.read()
                result = interface.execute_batch(commands_text)
            except FileNotFoundError:
                result = {"error": f"File not found: {args.batch}"}
            except Exception as e:
                result = {"error": f"Failed to read file: {str(e)}"}

        else:
            parser.print_help()
            sys.exit(1)

        # Output result as JSON
        if args.pretty:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(result, ensure_ascii=False))

    finally:
        interface.disconnect()


if __name__ == "__main__":
    main()
