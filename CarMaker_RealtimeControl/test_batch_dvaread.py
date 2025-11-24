"""
Test script for CarMaker DVARead batch command.

According to DVARead documentation:
- Syntax: DVARead name ?name2? ?name3? ...
- If more than one quantity is given, the return value is a list.

This script tests reading all essential quantities in a single DVARead command
instead of sequential requests.
"""

import socket
import time

class BatchDVAReadTester:
    def __init__(self, host='localhost', port=16660):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False

        # Ego vehicle quantities (from carmaker_client.py)
        self.ego_quantities = [
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
            'DM.v.Trgt',
            'DM.LaneOffset',
        ]

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"✓ Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            self.socket = None
            self.connected = False
            return False

    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None
        self.connected = False

    def send_command(self, cmd, timeout=5.0):
        if not self.connected or not self.socket:
            return None

        try:
            self.socket.settimeout(timeout)
            full_cmd = f"{cmd}\n"
            self.socket.send(full_cmd.encode())

            data = self.socket.recv(8192)  # Increased buffer size for batch response
            response = data.decode().strip()
            return response
        except socket.timeout:
            print(f"✗ Timeout for command: {cmd}")
            return None
        except Exception as e:
            print(f"✗ Error: {e}")
            self.disconnect()
            return None

    def test_sequential_read(self):
        """Test 1: Sequential DVARead (current implementation)"""
        print("\n" + "="*60)
        print("TEST 1: Sequential DVARead (Current Implementation)")
        print("="*60)

        results = {}
        start_time = time.time()

        for var in self.ego_quantities:
            resp = self.send_command(f"DVARead {var}", timeout=0.5)
            if resp and resp.startswith("O"):
                try:
                    val_str = resp[1:].strip()
                    results[var] = float(val_str) if val_str else 0.0
                except:
                    results[var] = None
            else:
                results[var] = None

        elapsed = time.time() - start_time

        print(f"\nResults ({len(results)} variables):")
        for var, val in results.items():
            print(f"  {var:20s} = {val}")

        print(f"\n⏱  Elapsed time: {elapsed*1000:.2f} ms")
        print(f"📊 Average per variable: {elapsed*1000/len(results):.2f} ms")

        return elapsed, results

    def test_batch_read(self):
        """Test 2: Batch DVARead (all variables in one command)"""
        print("\n" + "="*60)
        print("TEST 2: Batch DVARead (All Variables in One Command)")
        print("="*60)

        # Build command: DVARead var1 var2 var3 ...
        batch_cmd = "DVARead " + " ".join(self.ego_quantities)
        print(f"\nCommand: {batch_cmd[:80]}...")

        start_time = time.time()
        resp = self.send_command(batch_cmd, timeout=5.0)
        elapsed = time.time() - start_time

        if not resp:
            print("✗ No response received")
            return elapsed, {}

        print(f"\nRaw response ({len(resp)} chars):")
        print(f"  {resp[:200]}...")

        # Parse response
        results = {}
        if resp.startswith("O"):
            # Remove "O" prefix and split values
            val_str = resp[1:].strip()

            # Try different delimiters
            print("\nTrying to parse response...")

            # Option 1: Space-separated
            values = val_str.split()
            if len(values) == len(self.ego_quantities):
                print(f"✓ Parsed as space-separated values ({len(values)} values)")
                for var, val_str in zip(self.ego_quantities, values):
                    try:
                        results[var] = float(val_str)
                    except:
                        results[var] = None
            else:
                # Option 2: List format (Tcl list)
                print(f"Received {len(values)} values, expected {len(self.ego_quantities)}")
                print(f"Values: {values}")

                # Store raw values for inspection
                for i, (var, val_str) in enumerate(zip(self.ego_quantities, values)):
                    try:
                        results[var] = float(val_str) if i < len(values) else None
                    except:
                        results[var] = None
        else:
            print(f"✗ Error response: {resp}")
            return elapsed, {}

        print(f"\nResults ({len(results)} variables):")
        for var, val in results.items():
            print(f"  {var:20s} = {val}")

        print(f"\n⏱  Elapsed time: {elapsed*1000:.2f} ms")
        if len(results) > 0:
            print(f"📊 Average per variable: {elapsed*1000/len(results):.2f} ms")

        return elapsed, results

    def test_small_batch_read(self):
        """Test 3: Small Batch DVARead (3 variables)"""
        print("\n" + "="*60)
        print("TEST 3: Small Batch DVARead (3 Variables)")
        print("="*60)

        # Test with 3 variables
        small_batch = ['Time', 'Car.v', 'Vhcl.sRoad']
        batch_cmd = "DVARead " + " ".join(small_batch)
        print(f"\nCommand: {batch_cmd}")

        start_time = time.time()
        resp = self.send_command(batch_cmd, timeout=2.0)
        elapsed = time.time() - start_time

        print(f"\nRaw response: {resp}")

        results = {}
        if resp and resp.startswith("O"):
            val_str = resp[1:].strip()
            values = val_str.split()

            print(f"Parsed values: {values}")

            for var, val_str in zip(small_batch, values):
                try:
                    results[var] = float(val_str)
                except:
                    results[var] = None

        print(f"\nResults:")
        for var, val in results.items():
            print(f"  {var:20s} = {val}")

        print(f"\n⏱  Elapsed time: {elapsed*1000:.2f} ms")

        return elapsed, results


def main():
    print("="*60)
    print("CarMaker DVARead Batch Command Test")
    print("="*60)

    tester = BatchDVAReadTester()

    if not tester.connect():
        print("\n✗ Failed to connect to CarMaker")
        print("Make sure CarMaker is running with APO server on port 16660")
        return

    try:
        # Run tests
        seq_time, seq_results = tester.test_sequential_read()
        batch_time, batch_results = tester.test_batch_read()
        small_time, small_results = tester.test_small_batch_read()

        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"\nSequential read time: {seq_time*1000:.2f} ms")
        print(f"Batch read time:      {batch_time*1000:.2f} ms")
        print(f"Small batch time:     {small_time*1000:.2f} ms")

        if batch_time > 0 and seq_time > 0:
            speedup = seq_time / batch_time
            print(f"\n🚀 Speedup: {speedup:.2f}x faster")
            print(f"⏱  Time saved: {(seq_time - batch_time)*1000:.2f} ms")

        # Verify results match
        if seq_results and batch_results:
            mismatches = []
            for var in seq_results:
                if var in batch_results:
                    seq_val = seq_results[var]
                    batch_val = batch_results[var]
                    if seq_val != batch_val:
                        mismatches.append((var, seq_val, batch_val))

            if mismatches:
                print(f"\n⚠️  Found {len(mismatches)} mismatches:")
                for var, seq_val, batch_val in mismatches:
                    print(f"  {var}: {seq_val} (sequential) vs {batch_val} (batch)")
            else:
                print("\n✓ All values match between sequential and batch reads")

    finally:
        tester.disconnect()
        print("\n✓ Disconnected")


if __name__ == "__main__":
    main()
