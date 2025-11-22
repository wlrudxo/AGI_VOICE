#!/usr/bin/env python3
"""
Test script for LLM Integration Layer

Usage:
    1. Set ANTHROPIC_API_KEY environment variable
    2. Start CarMaker simulation
    3. Run this script:
       - With GUI: python test_llm_integration.py --gui
       - CLI only: python test_llm_integration.py
"""

import sys
import time
import tkinter as tk
from carmaker_control_server import CarMakerControlServer
from llm_integration import LLMIntegrationLayer


def main_with_gui():
    """Run LLM integration with GUI for visual monitoring"""
    print("=" * 60)
    print("LLM Integration Test - WITH GUI")
    print("=" * 60)

    # Import GUI here to avoid tkinter dependency in CLI mode
    from carmaker_gui import CarMakerGUI

    # Create GUI
    root = tk.Tk()
    gui = CarMakerGUI(root)

    print("\n[GUI] CarMaker GUI initialized")
    print("[GUI] Use GUI to connect to CarMaker and start monitoring")
    print("[GUI] LLM auto-intervention will work alongside GUI\n")

    # Use GUI's server for LLM integration
    server = gui.server

    # Initialize LLM Integration Layer (Manual Mode)
    print("[LLM] Initializing LLM Integration Layer (Manual Mode)...")
    llm_layer = LLMIntegrationLayer(server, manual_mode=True)

    # Load triggers
    print("[LLM] Loading triggers from llm_triggers.json...")
    success = llm_layer.load_triggers('llm_triggers.json')
    if not success:
        print("[LLM] WARNING: Failed to load triggers")
    else:
        print(f"[LLM] ✓ Loaded {len(llm_layer.trigger_manager.triggers)} triggers")
        print("\n[LLM] Loaded Triggers:")
        for trigger in llm_layer.trigger_manager.triggers:
            print(f"  - {trigger['name']}: {trigger['condition']}")

    # Instructions
    print("\n" + "=" * 60)
    print("INSTRUCTIONS")
    print("=" * 60)
    print("1. Use GUI to connect to CarMaker (localhost:16660)")
    print("2. Click 'Start Monitoring' in GUI to see real-time data")
    print("3. Click 'Start LLM Monitoring' button below to enable auto-intervention")
    print("4. When triggers fire, choose example responses in terminal")
    print("=" * 60)

    # Add LLM control button to GUI
    llm_frame = tk.LabelFrame(root, text="LLM Auto-Intervention")
    llm_frame.pack(fill="x", padx=10, pady=5)

    llm_status = tk.Label(llm_frame, text="LLM: Stopped", foreground="red")
    llm_status.pack(side="left", padx=10)

    def toggle_llm():
        if not llm_layer.enabled:
            # Check if connected
            if not server.client.connected:
                tk.messagebox.showwarning("LLM", "Please connect to CarMaker first!")
                return

            llm_layer.start_monitoring()
            llm_status.config(text="LLM: Active", foreground="green")
            llm_btn.config(text="Stop LLM Monitoring")
        else:
            llm_layer.stop_monitoring()
            llm_status.config(text="LLM: Stopped", foreground="red")
            llm_btn.config(text="Start LLM Monitoring")

    llm_btn = tk.Button(llm_frame, text="Start LLM Monitoring", command=toggle_llm)
    llm_btn.pack(side="left", padx=5)

    # Run GUI main loop
    print("\n[GUI] Starting GUI main loop...")
    root.mainloop()

    # Cleanup when GUI closes
    print("\n[LLM] Shutting down...")
    llm_layer.stop_monitoring()
    print("Goodbye!")


def main():
    print("=" * 60)
    print("LLM Integration Test - CarMaker Control")
    print("=" * 60)

    # Initialize server
    print("\n[1/5] Initializing Control Server...")
    server = CarMakerControlServer(
        host='localhost',
        carmaker_port=16660,
        socket_port=7777
    )

    # Connect to CarMaker
    print("[2/5] Connecting to CarMaker...")
    success, msg = server.connect_carmaker()
    if not success:
        print(f"ERROR: {msg}")
        print("\nMake sure CarMaker is running and APO is enabled.")
        sys.exit(1)

    print(f"✓ Connected to CarMaker")

    # Start monitoring
    print("[3/5] Starting monitoring...")
    success, msg = server.start_monitoring()
    if not success:
        print(f"ERROR: {msg}")
        sys.exit(1)

    print(f"✓ Monitoring started")

    # Initialize LLM Integration Layer (Manual Mode - No API calls)
    print("[4/5] Initializing LLM Integration Layer (Manual Mode)...")
    llm_layer = LLMIntegrationLayer(server, manual_mode=True)

    # Load triggers
    print("[5/5] Loading triggers from llm_triggers.json...")
    success = llm_layer.load_triggers('llm_triggers.json')
    if not success:
        print("WARNING: Failed to load triggers")
        print("Continuing without triggers...")
    else:
        print(f"✓ Loaded {len(llm_layer.trigger_manager.triggers)} triggers")

        # Display triggers
        print("\nLoaded Triggers:")
        for trigger in llm_layer.trigger_manager.triggers:
            print(f"  - {trigger['name']}: {trigger['condition']}")

    # Start LLM monitoring
    print("\n" + "=" * 60)
    print("Starting LLM Auto-Intervention System (MANUAL MODE)")
    print("=" * 60)
    print("\n💡 Manual Mode: When a trigger fires, you'll be asked to:")
    print("   1. Choose from example responses (1, 2, 3)")
    print("   2. Paste your own JSON")
    print("   3. Type 'skip' to skip intervention")
    print("\nThe system will monitor and pause when triggers fire.")
    print("Press Ctrl+C to stop.\n")

    llm_layer.start_monitoring()

    # Keep running
    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        llm_layer.stop_monitoring()
        server.stop_monitoring()
        server.disconnect_carmaker()
        print("Goodbye!")


def test_trigger_detection():
    """Test trigger detection without LLM API call"""
    print("=" * 60)
    print("Testing Trigger Detection (No LLM)")
    print("=" * 60)

    # Initialize server
    print("\n[1/3] Initializing Control Server...")
    server = CarMakerControlServer()

    # Connect
    print("[2/3] Connecting to CarMaker...")
    success, msg = server.connect_carmaker()
    if not success:
        print(f"ERROR: {msg}")
        sys.exit(1)

    print(f"✓ Connected")

    # Test trigger manager
    print("[3/3] Testing trigger detection...")
    from llm_integration import TriggerManager

    trigger_mgr = TriggerManager()
    trigger_mgr.load_from_file('llm_triggers.json')

    print(f"✓ Loaded {len(trigger_mgr.triggers)} triggers\n")

    # Monitor and check triggers
    print("Monitoring for 30 seconds...\n")

    try:
        for i in range(300):  # 30 seconds at 10Hz
            data = server.client.read_essential_quantities()

            # Check triggers
            triggered = trigger_mgr.check_triggers(data)

            if triggered:
                print(f"\n[TRIGGER] {triggered['name']}: {triggered['description']}")
                print(f"  Condition: {triggered['condition']}")
                print(f"  Current state: Speed={data.get('Car.v', 0)*3.6:.1f} km/h, "
                      f"Lateral={data.get('Vhcl.tRoad', 0):.2f}m, "
                      f"YawRate={data.get('Vhcl.YawRate', 0):.3f}\n")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nStopped by user")

    server.disconnect_carmaker()
    print("Test completed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='LLM Integration Test')
    parser.add_argument('--gui', action='store_true',
                       help='Run with GUI for visual monitoring')
    parser.add_argument('--test-triggers', action='store_true',
                       help='Test trigger detection only (no LLM API calls)')

    args = parser.parse_args()

    if args.test_triggers:
        test_trigger_detection()
    elif args.gui:
        main_with_gui()
    else:
        main()
