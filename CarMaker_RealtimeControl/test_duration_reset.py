#!/usr/bin/env python3
"""
Test script for Duration -1 Command Reset Behavior

Purpose:
    Test whether sending a command with duration=1ms resets a previously
    sent command with duration=-1 (infinite duration).

Test Cases:
    1. DM.Brake: Apply 0.5 brake with -1ms, wait 1.5s, send 0.5 brake with 1ms, wait 5s
    2. DM.Steer.Ang: Apply -0.3 steer with -1ms, wait 1.5s, send -0.3 steer with 1ms, wait 5s
    3. SC.TAccel: Set time scale to 0.1 with -1ms, wait 1.5s, send 0.1 with 1ms, wait 5s

Expected Behavior:
    - If 1ms command resets the previous -1ms command:
      → The control should return to default/autonomous behavior after reset
    - If 1ms command does NOT reset:
      → The control should remain at the specified value (0.5 brake, -0.3 steer, 0.1 time scale)

Usage:
    1. Start CarMaker simulation
    2. Run: python test_duration_reset.py
    3. Observe vehicle behavior and terminal output
"""

import socket
import time
import sys


class DurationResetTester:
    def __init__(self, host='localhost', port=16660):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False

    def connect(self):
        """Connect to CarMaker APO server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"✓ Connected to CarMaker at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            print("Make sure CarMaker is running with APO server on port 16660")
            self.socket = None
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from CarMaker"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None
        self.connected = False

    def send_command(self, cmd, timeout=2.0):
        """Send command to CarMaker and get response"""
        if not self.connected or not self.socket:
            return None

        try:
            self.socket.settimeout(timeout)
            full_cmd = f"{cmd}\n"
            self.socket.send(full_cmd.encode())

            data = self.socket.recv(4096)
            response = data.decode().strip()
            return response
        except socket.timeout:
            print(f"✗ Timeout for command: {cmd}")
            return None
        except Exception as e:
            print(f"✗ Error: {e}")
            return None

    def read_value(self, variable):
        """Read current value of a variable"""
        resp = self.send_command(f"DVARead {variable}", timeout=1.0)
        if resp and resp.startswith("O"):
            try:
                val_str = resp[1:].strip()
                return float(val_str) if val_str else None
            except:
                return None
        return None

    def write_value(self, variable, value, duration, mode='Abs'):
        """Write value to CarMaker using DVAWrite"""
        cmd = f"DVAWrite {variable} {value} {duration} {mode}"
        resp = self.send_command(cmd)

        # Debug: Print raw response
        print(f"  → Command: {cmd}")
        print(f"  → Response: '{resp}' (length: {len(resp) if resp else 0})")

        # Accept both "O" prefix and empty success responses
        if resp is not None and (resp.startswith("O") or resp == ""):
            print(f"  ✓ DVAWrite {variable} {value} {duration} {mode}")
            return True
        else:
            print(f"  ✗ Failed: DVAWrite {variable} {value} {duration} {mode}")
            print(f"    Response: '{resp}'")
            return False

    def test_brake_reset(self):
        """Test Case 1: DM.Brake with -1 duration"""
        print("\n" + "=" * 70)
        print("TEST CASE 1: DM.Brake Reset Behavior")
        print("=" * 70)

        # Read initial brake value
        initial = self.read_value('DM.Brake')
        print(f"\n[STEP 1] Initial DM.Brake value: {initial}")

        input("\nPress Enter to apply DM.Brake = 0.5 with duration = -1ms...")

        # Apply brake with -1 duration (infinite)
        print(f"\n[STEP 2] Applying DM.Brake = 0.5 with duration = -1ms")
        success = self.write_value('DM.Brake', 0.5, -1)
        if not success:
            print("✗ Test aborted: Failed to write brake command")
            return False

        # Monitor continuously
        print(f"\n[STEP 3] Monitoring DM.Brake (Press Enter to continue)...")
        while True:
            current = self.read_value('DM.Brake')
            speed = self.read_value('Car.v')
            print(f"  DM.Brake = {current:.4f}, Car.v = {speed:.2f} m/s ({speed*3.6:.1f} km/h)")

            print("  [Options: Enter = next step, 'c' = continue monitoring]", end='')
            choice = input(" ")
            if choice.lower() != 'c':
                break
            time.sleep(0.1)

        input("\nPress Enter to send reset command: DM.Brake = 0.5 with duration = 1ms...")

        # Send reset command (same value with 1ms duration)
        print(f"\n[STEP 4] Sending reset command: DM.Brake = 0.5 with duration = 1ms")
        success = self.write_value('DM.Brake', 0.5, 1)
        if not success:
            print("✗ Test aborted: Failed to write reset command")
            return False

        # Monitor after reset
        print(f"\n[STEP 5] Monitoring after reset (Press Enter to continue)...")
        while True:
            current = self.read_value('DM.Brake')
            speed = self.read_value('Car.v')
            print(f"  DM.Brake = {current:.4f}, Car.v = {speed:.2f} m/s ({speed*3.6:.1f} km/h)")

            print("  [Options: Enter = finish test, 'c' = continue monitoring]", end='')
            choice = input(" ")
            if choice.lower() != 'c':
                break
            time.sleep(0.1)

        print("\n✓ Test Case 1 completed")
        return True

    def test_steer_reset(self):
        """Test Case 2: DM.Steer.Ang with -1 duration"""
        print("\n" + "=" * 70)
        print("TEST CASE 2: DM.Steer.Ang Reset Behavior")
        print("=" * 70)

        # Read initial steer value
        initial = self.read_value('DM.Steer.Ang')
        print(f"\n[STEP 1] Initial DM.Steer.Ang value: {initial}")

        input("\nPress Enter to apply DM.Steer.Ang = -0.3 with duration = -1ms...")

        # Apply steer with -1 duration (infinite)
        print(f"\n[STEP 2] Applying DM.Steer.Ang = -0.3 with duration = -1ms")
        success = self.write_value('DM.Steer.Ang', -0.3, -1)
        if not success:
            print("✗ Test aborted: Failed to write steer command")
            return False

        # Monitor continuously
        print(f"\n[STEP 3] Monitoring DM.Steer.Ang (Press Enter to continue)...")
        while True:
            current = self.read_value('DM.Steer.Ang')
            actual_steer = self.read_value('Vhcl.Steer.Ang')
            troad = self.read_value('Vhcl.tRoad')
            print(f"  DM.Steer.Ang = {current:.4f}, Vhcl.Steer.Ang = {actual_steer:.4f}, tRoad = {troad:.2f}m")

            print("  [Options: Enter = next step, 'c' = continue monitoring]", end='')
            choice = input(" ")
            if choice.lower() != 'c':
                break
            time.sleep(0.1)

        input("\nPress Enter to send reset command: DM.Steer.Ang = -0.3 with duration = 1ms...")

        # Send reset command (same value with 1ms duration)
        print(f"\n[STEP 4] Sending reset command: DM.Steer.Ang = -0.3 with duration = 1ms")
        success = self.write_value('DM.Steer.Ang', -0.3, 1)
        if not success:
            print("✗ Test aborted: Failed to write reset command")
            return False

        # Monitor after reset
        print(f"\n[STEP 5] Monitoring after reset (Press Enter to continue)...")
        while True:
            current = self.read_value('DM.Steer.Ang')
            actual_steer = self.read_value('Vhcl.Steer.Ang')
            troad = self.read_value('Vhcl.tRoad')
            print(f"  DM.Steer.Ang = {current:.4f}, Vhcl.Steer.Ang = {actual_steer:.4f}, tRoad = {troad:.2f}m")

            print("  [Options: Enter = finish test, 'c' = continue monitoring]", end='')
            choice = input(" ")
            if choice.lower() != 'c':
                break
            time.sleep(0.1)

        print("\n✓ Test Case 2 completed")
        return True

    def test_time_scale_reset(self):
        """Test Case 3: SC.TAccel with -1 duration"""
        print("\n" + "=" * 70)
        print("TEST CASE 3: SC.TAccel (Time Scale) Reset Behavior")
        print("=" * 70)

        # Read initial time scale value
        initial = self.read_value('SC.TAccel')
        sim_time_initial = self.read_value('Time')
        print(f"\n[STEP 1] Initial SC.TAccel value: {initial}")
        print(f"           Initial SimTime: {sim_time_initial}")

        input("\nPress Enter to apply SC.TAccel = 0.1 with duration = -1ms...")

        # Apply time scale with -1 duration (infinite)
        print(f"\n[STEP 2] Applying SC.TAccel = 0.1 with duration = -1ms")
        success = self.write_value('SC.TAccel', 0.1, -1)
        if not success:
            print("✗ Test aborted: Failed to write time scale command")
            return False

        # Monitor continuously
        print(f"\n[STEP 3] Monitoring SC.TAccel (Press Enter to continue)...")
        last_time = time.time()
        last_sim_time = self.read_value('Time')

        while True:
            time.sleep(0.5)
            current = self.read_value('SC.TAccel')
            sim_time = self.read_value('Time')

            # Calculate time rates
            real_elapsed = time.time() - last_time
            sim_elapsed = sim_time - last_sim_time if last_sim_time else 0
            time_ratio = sim_elapsed / real_elapsed if real_elapsed > 0 else 0

            print(f"  SC.TAccel = {current:.4f}, SimTime = {sim_time:.2f}s, Ratio = {time_ratio:.2f}x")

            last_time = time.time()
            last_sim_time = sim_time

            print("  [Options: Enter = next step, 'c' = continue monitoring]", end='')
            choice = input(" ")
            if choice.lower() != 'c':
                break

        input("\nPress Enter to send reset command: SC.TAccel = 0.1 with duration = 1ms...")

        # Send reset command (same value with 1ms duration)
        print(f"\n[STEP 4] Sending reset command: SC.TAccel = 0.1 with duration = 1ms")
        success = self.write_value('SC.TAccel', 0.1, 1)
        if not success:
            print("✗ Test aborted: Failed to write reset command")
            return False

        # Monitor after reset
        print(f"\n[STEP 5] Monitoring after reset (Press Enter to continue)...")
        last_time = time.time()
        last_sim_time = self.read_value('Time')

        while True:
            time.sleep(0.5)
            current = self.read_value('SC.TAccel')
            sim_time = self.read_value('Time')

            # Calculate time rates
            real_elapsed = time.time() - last_time
            sim_elapsed = sim_time - last_sim_time if last_sim_time else 0
            time_ratio = sim_elapsed / real_elapsed if real_elapsed > 0 else 0

            print(f"  SC.TAccel = {current:.4f}, SimTime = {sim_time:.2f}s, Ratio = {time_ratio:.2f}x")

            last_time = time.time()
            last_sim_time = sim_time

            print("  [Options: Enter = finish test, 'c' = continue monitoring]", end='')
            choice = input(" ")
            if choice.lower() != 'c':
                break

        print("\n✓ Test Case 3 completed")
        return True


def main():
    print("=" * 70)
    print("CarMaker Duration -1 Reset Test")
    print("=" * 70)
    print("\nThis test checks if sending a command with 1ms duration")
    print("resets a previous command with -1ms (infinite) duration.\n")

    tester = DurationResetTester()

    # Connect to CarMaker
    if not tester.connect():
        sys.exit(1)

    try:
        # Run all test cases
        print("\n💡 Watch the CarMaker simulation window to observe behavior!")
        print("Press Ctrl+C to abort at any time.\n")

        input("Press Enter to start Test Case 1 (DM.Brake)...")
        tester.test_brake_reset()

        input("\nPress Enter to start Test Case 2 (DM.Steer.Ang)...")
        tester.test_steer_reset()

        input("\nPress Enter to start Test Case 3 (SC.TAccel)...")
        tester.test_time_scale_reset()

        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print("\n✓ All test cases completed")
        print("\nAnalysis:")
        print("  1. Check if brake/steer/time scale returned to default after 1ms reset")
        print("  2. If values remained constant:")
        print("     → 1ms command does NOT reset -1ms command")
        print("     → Need alternative solution (e.g., send opposite value)")
        print("  3. If values returned to default:")
        print("     → 1ms command successfully resets -1ms command")
        print("     → Can use this approach for wait_until implementation")

    except KeyboardInterrupt:
        print("\n\n✗ Test interrupted by user")
    finally:
        tester.disconnect()
        print("\n✓ Disconnected from CarMaker")
        print("Goodbye!")


if __name__ == "__main__":
    main()
