#!/usr/bin/env python3
"""
CarMaker Control Server
- Headless server that manages CarMaker connection
- Socket server for CLI/GUI communication
- Monitoring and auto control rules
- Condition-based automation
"""

import threading
import time
import socket
import json
from carmaker_client import CarMakerClient


class CarMakerControlServer:
    def __init__(self, host='localhost', carmaker_port=16660, socket_port=7777):
        self.host = host
        self.carmaker_port = carmaker_port
        self.socket_port = socket_port

        # CarMaker client
        self.client = CarMakerClient()
        self.client.host = host
        self.client.port = carmaker_port

        # Monitoring
        self.monitoring = False
        self.monitor_thread = None
        self.monitor_callbacks = []  # List of callbacks for data updates

        # Auto control rules
        self.auto_control_rules = []

        # Socket server
        self.socket_server_running = False
        self.server_socket = None

        # Event logging callbacks
        self.log_callbacks = []

    def log(self, message):
        """Log message to all registered callbacks"""
        print(f"[SERVER] {message}")
        for callback in self.log_callbacks:
            try:
                callback(message)
            except:
                pass

    def add_log_callback(self, callback):
        """Add a callback for log messages"""
        self.log_callbacks.append(callback)

    def add_monitor_callback(self, callback):
        """Add a callback for monitor data updates"""
        self.monitor_callbacks.append(callback)

    # ========== CarMaker Connection ==========

    def connect_carmaker(self):
        """Connect to CarMaker"""
        success, msg = self.client.connect()
        if success:
            self.log(f"Connected to CarMaker at {self.host}:{self.carmaker_port}")
        else:
            self.log(f"Failed to connect to CarMaker: {msg}")
        return success, msg

    def disconnect_carmaker(self):
        """Disconnect from CarMaker"""
        self.stop_monitoring()
        self.client.disconnect()
        self.log("Disconnected from CarMaker")

    # ========== Monitoring ==========

    def start_monitoring(self):
        """Start monitoring loop"""
        if self.monitoring:
            return True, "Already monitoring"

        if not self.client.connected:
            return False, "Not connected to CarMaker"

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.log("Monitoring started")
        return True, "Monitoring started"

    def stop_monitoring(self):
        """Stop monitoring loop"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self.log("Monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring and self.client.connected:
            try:
                # Measure read time
                start_time = time.time()
                data = self.client.read_essential_quantities()
                read_time = time.time() - start_time

                # Log read time and traffic object count
                nObjs = data.get('Traffic.nObjs', 0)
                total_vars = len(data)
                self.log(f"Read {total_vars} vars (Traffic.nObjs={nObjs}) in {read_time:.3f}s")

                # Notify callbacks
                for callback in self.monitor_callbacks:
                    try:
                        callback(data)
                    except:
                        pass

                # Check auto control rules
                self._check_auto_control_rules(data)

                time.sleep(0.1)  # 10Hz update rate

            except Exception as e:
                self.log(f"Monitor error: {e}")
                self.monitoring = False
                break

    # ========== Auto Control Rules ==========

    def add_auto_control_rule(self, condition, command, one_shot=True):
        """Add an auto control rule"""
        rule = {
            "condition": condition,
            "command": command,
            "one_shot": one_shot
        }
        self.auto_control_rules.append(rule)
        self.log(f"AUTO RULE ADDED: {condition} → {command}")
        return True, f"Rule added. Total: {len(self.auto_control_rules)}"

    def clear_auto_control_rules(self):
        """Clear all auto control rules"""
        count = len(self.auto_control_rules)
        self.auto_control_rules.clear()
        self.log(f"Cleared {count} auto control rules")
        return True, f"Cleared {count} rules"

    def _check_auto_control_rules(self, data):
        """Check and execute auto control rules with AND/OR support"""
        if not self.auto_control_rules:
            return

        rules_to_remove = []

        for i, rule in enumerate(self.auto_control_rules):
            try:
                condition = rule['condition']
                command = rule['command']
                one_shot = rule.get('one_shot', True)

                # Evaluate condition with AND/OR support using eval
                condition_met = self._evaluate_condition_expr(condition, data)

                if condition_met:
                    # Execute command
                    success, result = self.client.execute_command(command)
                    self.log(f"AUTO: {condition} → {command} | {result}")

                    if one_shot:
                        rules_to_remove.append(i)

            except Exception as e:
                self.log(f"Auto control rule error: {e}")

        # Remove one-shot rules that fired
        for i in reversed(rules_to_remove):
            del self.auto_control_rules[i]

    def _evaluate_condition_expr(self, condition, data):
        """
        Evaluate condition expression with AND/OR support
        Supports: >, <, >=, <=, ==, and, or, abs(), etc.
        Example: "Car_v > 27.78 and abs(Vhcl_tRoad) > 1.0"
        Note: Variable names use underscores (Car_v not Car.v)
        """
        try:
            # Convert keys with dots to underscores and handle None values
            eval_data = {}
            for key, value in data.items():
                clean_key = key.replace('.', '_')
                eval_data[clean_key] = value if value is not None else 0.0

            # Safe evaluation with __builtins__ removed
            result = eval(condition, {"__builtins__": {}}, {**eval_data, 'abs': abs, 'min': min, 'max': max})
            return bool(result)
        except Exception as e:
            self.log(f"Condition evaluation error: {condition} | {e}")
            return False

    # ========== Command Execution ==========

    def execute_command(self, command):
        """Execute a CarMaker command"""
        if not self.client.connected:
            return False, "Not connected to CarMaker"

        success, result = self.client.execute_command(command)
        self.log(f"CMD: {command} → {result}")
        return success, result

    def get_status(self):
        """Get current vehicle status"""
        if not self.client.connected:
            return False, {}, "Not connected to CarMaker"

        data = self.client.read_essential_quantities()
        return True, data, "OK"

    def evaluate_condition(self, condition, command):
        """Evaluate condition and execute command if met (supports AND/OR)"""
        try:
            # Read current data
            data = self.client.read_essential_quantities()

            # Evaluate condition
            condition_met = self._evaluate_condition_expr(condition, data)

            if condition_met:
                success, result = self.client.execute_command(command)
                return success, f"Condition met: {condition}. Executed: {result}"
            else:
                return True, f"Condition not met: {condition}. Skipped."

        except Exception as e:
            return False, f"Error: {str(e)}"

    def wait_until_condition(self, condition, command, timeout=30):
        """Wait until condition is met, then execute command (supports AND/OR)"""
        try:
            start_time = time.time()
            check_count = 0

            while True:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    return False, f"Timeout after {timeout}s"

                # Read current data
                data = self.client.read_essential_quantities()
                check_count += 1

                # Evaluate condition
                condition_met = self._evaluate_condition_expr(condition, data)

                if condition_met:
                    success, result = self.client.execute_command(command)
                    return success, f"Condition met after {elapsed:.1f}s ({check_count} checks). Condition: {condition}. Executed: {result}"

                time.sleep(0.1)

        except Exception as e:
            return False, f"Error: {str(e)}"

    # ========== Socket Server ==========

    def start_socket_server(self):
        """Start socket server for CLI/GUI communication"""
        if self.socket_server_running:
            return

        self.socket_server_running = True
        threading.Thread(target=self._socket_server_loop, daemon=True).start()
        self.log(f"Socket server started on port {self.socket_port}")

    def stop_socket_server(self):
        """Stop socket server"""
        self.socket_server_running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.log("Socket server stopped")

    def _socket_server_loop(self):
        """Main socket server loop"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', self.socket_port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)

            self.log(f"Listening on localhost:{self.socket_port}")

            while self.socket_server_running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    threading.Thread(target=self._handle_client, args=(client_socket,), daemon=True).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.socket_server_running:
                        self.log(f"Socket accept error: {e}")

        except Exception as e:
            self.log(f"Socket server error: {e}")
        finally:
            if self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass

    def _handle_client(self, client_socket):
        """Handle individual client connection"""
        try:
            data = client_socket.recv(8192).decode('utf-8')
            if not data:
                return

            request = json.loads(data)
            action = request.get("action")

            response = self._process_request(action, request)

            client_socket.sendall(json.dumps(response).encode('utf-8'))

        except Exception as e:
            error_response = {
                "success": False,
                "error": str(e)
            }
            try:
                client_socket.sendall(json.dumps(error_response).encode('utf-8'))
            except:
                pass
        finally:
            client_socket.close()

    def _process_request(self, action, request):
        """Process client request and return response"""
        if action == "cmd":
            command = request.get("command", "")
            success, result = self.execute_command(command)
            return {
                "success": success,
                "result": result,
                "command": command
            }

        elif action == "status":
            success, data, msg = self.get_status()
            return {
                "success": success,
                "data": data,
                "message": msg
            }

        elif action == "conditional":
            condition = request.get("condition", "")
            command = request.get("command", "")
            success, result = self.evaluate_condition(condition, command)
            return {
                "success": success,
                "result": result
            }

        elif action == "wait_until":
            condition = request.get("condition", "")
            command = request.get("command", "")
            timeout = request.get("timeout", 30)
            success, result = self.wait_until_condition(condition, command, timeout)
            return {
                "success": success,
                "result": result
            }

        elif action == "auto_control":
            condition = request.get("condition", "")
            command = request.get("command", "")
            one_shot = request.get("one_shot", True)

            if not self.monitoring:
                return {
                    "success": False,
                    "error": "Monitoring must be active for auto_control"
                }

            success, result = self.add_auto_control_rule(condition, command, one_shot)
            return {
                "success": success,
                "result": result
            }

        elif action == "connect":
            success, msg = self.connect_carmaker()
            return {
                "success": success,
                "message": msg
            }

        elif action == "disconnect":
            self.disconnect_carmaker()
            return {
                "success": True,
                "message": "Disconnected"
            }

        elif action == "start_monitoring":
            success, msg = self.start_monitoring()
            return {
                "success": success,
                "message": msg
            }

        elif action == "stop_monitoring":
            self.stop_monitoring()
            return {
                "success": True,
                "message": "Monitoring stopped"
            }

        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }

    def run(self):
        """Run the server (blocking)"""
        self.log("CarMaker Control Server starting...")

        # Start socket server
        self.start_socket_server()

        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.log("Shutting down...")
            self.stop_socket_server()
            self.disconnect_carmaker()


if __name__ == "__main__":
    server = CarMakerControlServer()
    server.run()
