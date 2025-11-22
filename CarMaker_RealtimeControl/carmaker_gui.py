#!/usr/bin/env python3
"""
CarMaker GUI
- Pure GUI code
- Uses CarMakerControlServer internally (same process)
- No socket communication - direct method calls
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from carmaker_control_server import CarMakerControlServer


class CarMakerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CarMaker Control GUI")
        self.root.geometry("900x950")

        # Create control server (same process)
        self.server = CarMakerControlServer()

        # Register callbacks
        self.server.add_log_callback(self.log)
        self.server.add_monitor_callback(self.on_monitor_data)

        # Start socket server for CLI
        self.server.start_socket_server()

        # Monitoring flag
        self.monitoring = False

        self.create_widgets()

    def create_widgets(self):
        # --- Connection Section ---
        conn_frame = ttk.LabelFrame(self.root, text="CarMaker Connection")
        conn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(conn_frame, text="Host:").pack(side="left", padx=5)
        self.host_entry = ttk.Entry(conn_frame, width=15)
        self.host_entry.insert(0, "localhost")
        self.host_entry.pack(side="left", padx=5)

        ttk.Label(conn_frame, text="Port:").pack(side="left", padx=5)
        self.port_entry = ttk.Entry(conn_frame, width=10)
        self.port_entry.insert(0, "16660")
        self.port_entry.pack(side="left", padx=5)

        self.conn_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_carmaker)
        self.conn_btn.pack(side="left", padx=5)

        self.disconn_btn = ttk.Button(conn_frame, text="Disconnect", command=self.disconnect_carmaker, state='disabled')
        self.disconn_btn.pack(side="left", padx=5)

        self.status_lbl = ttk.Label(conn_frame, text="Disconnected", foreground="red")
        self.status_lbl.pack(side="left", padx=10)

        # --- Control Settings ---
        set_frame = ttk.LabelFrame(self.root, text="Control Settings")
        set_frame.pack(fill="x", padx=10, pady=5)

        dur_frame = ttk.Frame(set_frame)
        dur_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(dur_frame, text="Duration (ms):", width=15).pack(side="left")
        self.dur_entry = ttk.Entry(dur_frame, width=10)
        self.dur_entry.insert(0, "2000")
        self.dur_entry.pack(side="left", padx=5)

        mode_frame = ttk.Frame(set_frame)
        mode_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(mode_frame, text="Control Mode:", width=15).pack(side="left")
        self.mode_var = tk.StringVar(value="Abs")
        self.mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var, width=10, state="readonly")
        self.mode_combo['values'] = ('Abs', 'Off', 'Fac', 'AbsRamp', 'FacRamp')
        self.mode_combo.pack(side="left", padx=5)

        # --- Control Section ---
        ctrl_frame = ttk.LabelFrame(self.root, text="Driver Inputs")
        ctrl_frame.pack(fill="x", padx=10, pady=5)

        # Gas
        gas_frame = ttk.Frame(ctrl_frame)
        gas_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(gas_frame, text="Gas (0-1):", width=15).pack(side="left")
        self.gas_var = tk.DoubleVar(value=0.0)
        self.gas_scale = ttk.Scale(gas_frame, from_=0.0, to=1.0, variable=self.gas_var, orient="horizontal",
                                    command=lambda v: self.update_label(self.gas_val_lbl, v))
        self.gas_scale.pack(side="left", fill="x", expand=True, padx=5)
        self.gas_val_lbl = ttk.Label(gas_frame, text="0.00", width=5)
        self.gas_val_lbl.pack(side="left")
        ttk.Button(gas_frame, text="Set", command=lambda: self.send_control('Gas', self.gas_var.get())).pack(
            side="left", padx=5)

        # Brake
        brake_frame = ttk.Frame(ctrl_frame)
        brake_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(brake_frame, text="Brake (0-1):", width=15).pack(side="left")
        self.brake_var = tk.DoubleVar(value=0.0)
        self.brake_scale = ttk.Scale(brake_frame, from_=0.0, to=1.0, variable=self.brake_var, orient="horizontal",
                                      command=lambda v: self.update_label(self.brake_val_lbl, v))
        self.brake_scale.pack(side="left", fill="x", expand=True, padx=5)
        self.brake_val_lbl = ttk.Label(brake_frame, text="0.00", width=5)
        self.brake_val_lbl.pack(side="left")
        ttk.Button(brake_frame, text="Set", command=lambda: self.send_control('Brake', self.brake_var.get())).pack(
            side="left", padx=5)

        # Steering
        steer_frame = ttk.Frame(ctrl_frame)
        steer_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(steer_frame, text="Steer (-1~1):", width=15).pack(side="left")
        self.steer_var = tk.DoubleVar(value=0.0)
        self.steer_scale = ttk.Scale(steer_frame, from_=-1.0, to=1.0, variable=self.steer_var, orient="horizontal",
                                      command=lambda v: self.update_label(self.steer_val_lbl, v))
        self.steer_scale.pack(side="left", fill="x", expand=True, padx=5)
        self.steer_val_lbl = ttk.Label(steer_frame, text="0.00", width=5)
        self.steer_val_lbl.pack(side="left")
        ttk.Button(steer_frame, text="Set", command=lambda: self.send_control('Steer.Ang', self.steer_var.get())).pack(
            side="left", padx=5)

        # --- Text Command Section ---
        cmd_frame = ttk.LabelFrame(self.root, text="Text Command Input")
        cmd_frame.pack(fill="x", padx=10, pady=5)

        cmd_input_frame = ttk.Frame(cmd_frame)
        cmd_input_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(cmd_input_frame, text="Command:").pack(anchor="w")
        self.cmd_entry = ttk.Entry(cmd_input_frame)
        self.cmd_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(cmd_input_frame, text="Execute", command=self.execute_command).pack(side="right")

        # --- Monitor Section ---
        mon_frame = ttk.LabelFrame(self.root, text="Vehicle Data Monitor")
        mon_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.monitor_btn = ttk.Button(mon_frame, text="Start Monitoring", command=self.toggle_monitoring)
        self.monitor_btn.pack(anchor="ne", padx=5, pady=5)

        # Treeview for data
        columns = ('Variable', 'Value', 'Unit/Desc')
        self.tree = ttk.Treeview(mon_frame, columns=columns, show='headings', height=12)
        self.tree.heading('Variable', text='Variable')
        self.tree.heading('Value', text='Value')
        self.tree.heading('Unit/Desc', text='Description')

        self.tree.column('Variable', width=200)
        self.tree.column('Value', width=150)
        self.tree.column('Unit/Desc', width=300)

        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        self.update_tree_items({})

        # --- Log Section ---
        log_frame = ttk.LabelFrame(self.root, text="Log")
        log_frame.pack(fill="x", padx=10, pady=5)

        self.log_area = scrolledtext.ScrolledText(log_frame, height=6, state='disabled')
        self.log_area.pack(fill="both", expand=True, padx=5, pady=5)

    def update_label(self, label, value):
        label.config(text=f"{float(value):.2f}")

    def log(self, message):
        """Log message (called from GUI and server callback)"""
        def _log():
            self.log_area.config(state='normal')
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END)
            self.log_area.config(state='disabled')

        # Ensure thread-safe
        if threading.current_thread() != threading.main_thread():
            self.root.after(0, _log)
        else:
            _log()

    def on_monitor_data(self, data):
        """Callback when monitor data is updated"""
        self.root.after(0, lambda: self.update_tree_items(data))

    # ========== CarMaker Connection ==========

    def connect_carmaker(self):
        """Connect to CarMaker"""
        host = self.host_entry.get()
        try:
            port = int(self.port_entry.get())
            self.server.client.host = host
            self.server.client.port = port

            success, msg = self.server.connect_carmaker()
            if success:
                self.status_lbl.config(text="Connected", foreground="green")
                self.conn_btn.config(state='disabled')
                self.disconn_btn.config(state='normal')
            else:
                messagebox.showerror("Connection Error", msg)
        except ValueError:
            messagebox.showerror("Error", "Invalid Port")

    def disconnect_carmaker(self):
        """Disconnect from CarMaker"""
        self.server.disconnect_carmaker()
        self.status_lbl.config(text="Disconnected", foreground="red")
        self.conn_btn.config(state='normal')
        self.disconn_btn.config(state='disabled')
        self.monitoring = False
        self.monitor_btn.config(text="Start Monitoring")

    # ========== Control Commands ==========

    def send_control(self, ctrl_type, value):
        """Send control command"""
        dur = int(self.dur_entry.get())
        mode = self.mode_var.get()
        command = f"DVAWrite DM.{ctrl_type} {value} {dur} {mode}"
        self.server.execute_command(command)

    def execute_command(self):
        """Execute custom command"""
        command = self.cmd_entry.get().strip()
        if not command:
            return
        self.server.execute_command(command)

    # ========== Monitoring ==========

    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        if not self.monitoring:
            success, msg = self.server.start_monitoring()
            if success:
                self.monitoring = True
                self.monitor_btn.config(text="Stop Monitoring")
            else:
                messagebox.showwarning("Monitoring", msg)
        else:
            self.server.stop_monitoring()
            self.monitoring = False
            self.monitor_btn.config(text="Start Monitoring")

    def update_tree_items(self, data):
        """Update treeview with data (supports dynamic traffic objects)"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Base descriptions for ego vehicle
        base_desc_map = {
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
        }

        # Traffic quantity descriptions (template)
        traffic_desc_map = {
            'tx': 'Position X (m)',
            'ty': 'Position Y (m)',
            'tz': 'Position Z (m)',
            'v_0.x': 'Velocity X (m/s)',
            'v_0.y': 'Velocity Y (m/s)',
            'v_0.z': 'Velocity Z (m/s)',
            'LongVel': 'Long Velocity (m/s)',
            'sRoad': 'Road Pos S (m)',
            'tRoad': 'Lateral Pos T (m)',
            'State': 'State (0=hidden,1=visible)'
        }

        def get_description(key):
            """Get description for any key (ego or traffic)"""
            if key in base_desc_map:
                return base_desc_map[key]
            # Check if it's a traffic object variable
            if key.startswith('Traffic.T'):
                # Extract: Traffic.T00.v_0.x -> T00, v_0.x
                # Remove "Traffic." prefix
                without_prefix = key[8:]  # Remove "Traffic."
                # Split once to get obj_name and qty
                parts = without_prefix.split('.', 1)
                if len(parts) == 2:
                    obj_name = parts[0]  # T00, T01, ...
                    qty = parts[1]       # tx, ty, v_0.x, ...
                    if qty in traffic_desc_map:
                        return f"Traffic {obj_name} {traffic_desc_map[qty]}"
            return ""

        if not data:
            for key, desc in base_desc_map.items():
                self.tree.insert('', tk.END, values=(key, "N/A", desc))
        else:
            for key, val in data.items():
                desc = get_description(key)
                val_str = f"{val:.4f}" if val is not None else "Err"
                self.tree.insert('', tk.END, values=(key, val_str, desc))


if __name__ == "__main__":
    root = tk.Tk()
    app = CarMakerGUI(root)
    root.mainloop()
