#!/usr/bin/env python3
"""
CarMaker CLI - Simple command-line interface for CarMaker control

Usage:
    # Get vehicle status (all current data)
    python cm_cli.py status

    # Execute DVA command
    python cm_cli.py cmd "DVAWrite DM.Gas 0.5 2000 Abs"

    # Execute conditional command (requires GUI server running)
    python cm_cli.py conditional "Car.v > 20" "DVAWrite DM.Brake 0.3 2000 Abs"

    # Multiple commands
    python cm_cli.py cmd "StartSim"
    python cm_cli.py cmd "DVAWrite DM.v.Trgt 20.0 5000 Abs"
    python cm_cli.py cmd "StopSim"

Mode:
    --direct: Connect directly to CarMaker (default if GUI not available)
    --gui: Use GUI server (default if GUI is running on port 7777)
"""

import sys
import json
import socket
from carmaker_client import CarMakerClient


class CarMakerCLI:
    def __init__(self, use_gui_server=None):
        self.client = CarMakerClient()
        self.connected = False
        self.gui_server_host = 'localhost'
        self.gui_server_port = 7777

        # Auto-detect GUI server if not specified
        if use_gui_server is None:
            self.use_gui_server = self.check_gui_server_available()
        else:
            self.use_gui_server = use_gui_server

    def check_gui_server_available(self):
        """Check if GUI server is running"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((self.gui_server_host, self.gui_server_port))
            sock.close()
            return result == 0
        except:
            return False

    def send_to_gui_server(self, request_data):
        """Send request to GUI server and get response"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((self.gui_server_host, self.gui_server_port))

            # Send request
            sock.sendall(json.dumps(request_data).encode('utf-8'))

            # Receive response
            response_data = sock.recv(4096).decode('utf-8')
            sock.close()

            return json.loads(response_data)
        except Exception as e:
            return {
                "success": False,
                "error": f"GUI server communication error: {str(e)}"
            }

    def connect(self):
        """Connect to CarMaker (only for direct mode)"""
        if self.use_gui_server:
            return True  # GUI server handles connection

        if self.connected:
            return True

        success, msg = self.client.connect()
        if success:
            self.connected = True
            return True
        else:
            print(json.dumps({"error": "Connection failed", "message": msg}))
            return False

    def get_status(self):
        """Get all vehicle information"""
        if self.use_gui_server:
            # Use GUI server
            request = {"action": "status"}
            response = self.send_to_gui_server(request)
            if response.get("success"):
                data = response.get("data", {})
                # Add speed in km/h
                if "Car.v" in data and data["Car.v"] is not None:
                    data["speed_kmh"] = round(data["Car.v"] * 3.6, 2)
                data["_mode"] = "GUI Server"
                print(json.dumps(data, indent=2))
            else:
                print(json.dumps(response, indent=2))
            return

        # Direct mode
        if not self.connect():
            return

        # Essential quantities
        quantities = [
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

        data = {}
        for var in quantities:
            resp = self.client.send_command(f"DVARead {var}")
            if resp and resp.startswith("O"):
                try:
                    val_str = resp[1:].strip()
                    data[var] = float(val_str) if val_str else None
                except:
                    data[var] = val_str
            else:
                data[var] = None

        # Simulation status
        sim_status = self.client.send_command("GetSimStatus")
        data["SimStatus"] = sim_status

        # Add interpretations
        data["speed_kmh"] = round(data["Car.v"] * 3.6, 2) if data.get("Car.v") else None
        data["_mode"] = "Direct Connection"

        print(json.dumps(data, indent=2))

    def execute_command(self, command):
        """Execute a DVA or simulation command"""
        if self.use_gui_server:
            # Use GUI server
            request = {"action": "cmd", "command": command}
            response = self.send_to_gui_server(request)
            response["_mode"] = "GUI Server"
            print(json.dumps(response, indent=2))
            return

        # Direct mode
        if not self.connect():
            return

        success, response = self.client.execute_command(command)

        result = {
            "command": command,
            "success": success,
            "response": response,
            "_mode": "Direct Connection"
        }

        print(json.dumps(result, indent=2))

    def execute_conditional(self, condition, command):
        """Execute conditional command (requires GUI server)"""
        if not self.use_gui_server:
            print(json.dumps({
                "error": "Conditional commands require GUI server to be running",
                "hint": "Start the GUI application first: python simple_carmaker_test_gui.py"
            }, indent=2))
            return

        request = {
            "action": "conditional",
            "condition": condition,
            "command": command
        }

        response = self.send_to_gui_server(request)
        response["_mode"] = "GUI Server"
        response["condition"] = condition
        print(json.dumps(response, indent=2))

    def wait_until(self, condition, command, timeout=30):
        """Wait until condition is met, then execute command (requires GUI server)"""
        if not self.use_gui_server:
            print(json.dumps({
                "error": "wait_until requires GUI server to be running",
                "hint": "Start the GUI application first: python simple_carmaker_test_gui.py"
            }, indent=2))
            return

        request = {
            "action": "wait_until",
            "condition": condition,
            "command": command,
            "timeout": timeout
        }

        response = self.send_to_gui_server(request)
        response["_mode"] = "GUI Server"
        response["condition"] = condition
        print(json.dumps(response, indent=2))

    def auto_control(self, condition, command):
        """Add auto control rule (GUI monitors and executes automatically)"""
        if not self.use_gui_server:
            print(json.dumps({
                "error": "auto_control requires GUI server to be running",
                "hint": "Start the GUI application first: python simple_carmaker_test_gui.py"
            }, indent=2))
            return

        request = {
            "action": "auto_control",
            "condition": condition,
            "command": command,
            "one_shot": True
        }

        response = self.send_to_gui_server(request)
        response["_mode"] = "GUI Server"
        print(json.dumps(response, indent=2))

    def cleanup(self):
        """Disconnect"""
        if self.connected:
            self.client.disconnect()


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python cm_cli.py status")
        print("  python cm_cli.py cmd \"DVAWrite DM.Gas 0.5 2000 Abs\"")
        print("  python cm_cli.py conditional \"Car.v > 20\" \"DVAWrite DM.Brake 0.3 2000 Abs\"")
        print("  python cm_cli.py wait_until \"Car.v >= 100\" \"DVAWrite DM.Gas 0.0 500 Abs\" [timeout]")
        print("\nOptions:")
        print("  --direct: Force direct connection to CarMaker")
        print("  --gui: Force using GUI server (must be running)")
        sys.exit(1)

    # Parse options
    use_gui_server = None
    args = sys.argv[1:]

    if "--direct" in args:
        use_gui_server = False
        args.remove("--direct")
    elif "--gui" in args:
        use_gui_server = True
        args.remove("--gui")

    cli = CarMakerCLI(use_gui_server=use_gui_server)

    # Show mode
    mode_msg = "GUI Server" if cli.use_gui_server else "Direct Connection"
    print(f"# Mode: {mode_msg}\n", file=sys.stderr)

    try:
        if len(args) < 1:
            print(json.dumps({"error": "No action specified"}))
            sys.exit(1)

        action = args[0]

        if action == "status":
            cli.get_status()

        elif action == "cmd":
            if len(args) < 2:
                print(json.dumps({"error": "Command argument required"}))
                sys.exit(1)
            command = args[1]
            cli.execute_command(command)

        elif action == "conditional":
            if len(args) < 3:
                print(json.dumps({"error": "Conditional requires condition and command"}))
                print("Example: python cm_cli.py conditional \"Car.v > 20\" \"DVAWrite DM.Brake 0.3\"")
                sys.exit(1)
            condition = args[1]
            command = args[2]
            cli.execute_conditional(condition, command)

        elif action == "wait_until":
            if len(args) < 3:
                print(json.dumps({"error": "wait_until requires condition and command"}))
                print("Example: python cm_cli.py wait_until \"Car.v >= 100\" \"DVAWrite DM.Gas 0.0\" 30")
                sys.exit(1)
            condition = args[1]
            command = args[2]
            timeout = int(args[3]) if len(args) > 3 else 30
            cli.wait_until(condition, command, timeout)

        elif action == "auto":
            if len(args) < 3:
                print(json.dumps({"error": "auto requires condition and command"}))
                print("Example: python cm_cli.py auto \"Car.v >= 27.78\" \"DVAWrite DM.Gas 0.0 500 Abs\"")
                sys.exit(1)
            condition = args[1]
            command = args[2]
            cli.auto_control(condition, command)

        else:
            print(json.dumps({"error": f"Unknown action: {action}"}))
            sys.exit(1)

    finally:
        cli.cleanup()


if __name__ == "__main__":
    main()
