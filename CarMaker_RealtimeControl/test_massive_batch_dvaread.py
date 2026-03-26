"""
Massive Batch DVARead Test - T00 ~ T31 Traffic Objects (All Quantities)

Tests sequential vs batch read for 100+ variables:
- 32 traffic objects (T00 ~ T31)
- 7 quantities per object (tx, ty, v_0.x, v_0.y, LongVel, sRoad, tRoad)
- Total: 224 variables

Plus 12 ego vehicle variables = 236 total variables
"""

import socket
import time

class MassiveBatchTester:
    def __init__(self, host='localhost', port=16660):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False

        # Ego vehicle quantities
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

        # Traffic object quantities (per object)
        self.traffic_obj_quantities = [
            'tx',       # Global position X (m)
            'ty',       # Global position Y (m)
            'v_0.x',    # Global velocity X (m/s)
            'v_0.y',    # Global velocity Y (m/s)
            'LongVel',  # Longitudinal velocity (m/s)
            'sRoad',    # Road coordinate (m)
            'tRoad',    # Lateral distance to route (m)
        ]

        # Build all traffic variable names (T00 ~ T31)
        self.all_traffic_vars = []
        for i in range(32):
            obj_name = f"T{i:02d}"
            for qty in self.traffic_obj_quantities:
                var = f"Traffic.{obj_name}.{qty}"
                self.all_traffic_vars.append(var)

        # All variables (ego + traffic)
        self.all_variables = self.ego_quantities + self.all_traffic_vars

        print(f"📊 Test configuration:")
        print(f"   Ego variables: {len(self.ego_quantities)}")
        print(f"   Traffic objects: 32 (T00 ~ T31)")
        print(f"   Quantities per object: {len(self.traffic_obj_quantities)}")
        print(f"   Traffic variables: {len(self.all_traffic_vars)}")
        print(f"   TOTAL VARIABLES: {len(self.all_variables)}")

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
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

    def send_command(self, cmd, timeout=10.0):
        if not self.connected or not self.socket:
            return None

        try:
            self.socket.settimeout(timeout)
            full_cmd = f"{cmd}\n"
            self.socket.send(full_cmd.encode())

            # Large buffer for massive response
            data = self.socket.recv(32768)
            response = data.decode().strip()
            return response
        except socket.timeout:
            print(f"✗ Timeout for command (first 80 chars): {cmd[:80]}...")
            return None
        except Exception as e:
            print(f"✗ Error: {e}")
            self.disconnect()
            return None

    def test_sequential_read(self):
        """Test 1: Sequential DVARead (236 individual requests)"""
        print("\n" + "="*70)
        print("TEST 1: Sequential DVARead (236 Individual Requests)")
        print("="*70)
        print(f"Reading {len(self.all_variables)} variables one by one...")

        results = {}
        start_time = time.time()
        success_count = 0
        error_count = 0

        for i, var in enumerate(self.all_variables):
            resp = self.send_command(f"DVARead {var}", timeout=1.0)
            if resp and resp.startswith("O"):
                try:
                    val_str = resp[1:].strip()
                    results[var] = float(val_str) if val_str else 0.0
                    success_count += 1
                except:
                    results[var] = None
                    error_count += 1
            else:
                results[var] = None
                error_count += 1

            # Progress indicator every 50 variables
            if (i + 1) % 50 == 0:
                print(f"  Progress: {i+1}/{len(self.all_variables)} variables read...")

        elapsed = time.time() - start_time

        print(f"\n✓ Sequential read completed")
        print(f"  Success: {success_count}/{len(self.all_variables)} variables")
        print(f"  Errors: {error_count}/{len(self.all_variables)} variables")
        print(f"\n⏱  Total time: {elapsed*1000:.2f} ms")
        print(f"📊 Average per variable: {elapsed*1000/len(self.all_variables):.2f} ms")

        # Show sample results
        print(f"\nSample results (first 5 variables):")
        for i, (var, val) in enumerate(results.items()):
            if i >= 5:
                break
            print(f"  {var:30s} = {val}")

        return elapsed, results

    def test_batch_read(self):
        """Test 2: Batch DVARead (1 single request with 236 variables)"""
        print("\n" + "="*70)
        print("TEST 2: Batch DVARead (1 Single Request with 236 Variables)")
        print("="*70)

        # Build massive command: DVARead var1 var2 var3 ... var236
        batch_cmd = "DVARead " + " ".join(self.all_variables)
        print(f"Command length: {len(batch_cmd)} characters")
        print(f"Command preview: {batch_cmd[:100]}...")

        start_time = time.time()
        resp = self.send_command(batch_cmd, timeout=10.0)
        elapsed = time.time() - start_time

        if not resp:
            print("✗ No response received")
            return elapsed, {}

        print(f"\n✓ Response received")
        print(f"  Response length: {len(resp)} characters")
        print(f"  Response preview: {resp[:150]}...")

        # Parse response
        results = {}
        success_count = 0
        error_count = 0

        if resp.startswith("O"):
            # Remove "O" prefix and split values
            val_str = resp[1:].strip()
            values = val_str.split()

            print(f"\nParsing response...")
            print(f"  Expected values: {len(self.all_variables)}")
            print(f"  Received values: {len(values)}")

            if len(values) == len(self.all_variables):
                print(f"✓ Value count matches!")

                for var, val_str in zip(self.all_variables, values):
                    try:
                        results[var] = float(val_str)
                        success_count += 1
                    except:
                        results[var] = None
                        error_count += 1
            else:
                print(f"⚠️  Value count mismatch!")
                # Parse what we can
                for i, (var, val_str) in enumerate(zip(self.all_variables, values)):
                    try:
                        results[var] = float(val_str) if i < len(values) else None
                        if i < len(values):
                            success_count += 1
                        else:
                            error_count += 1
                    except:
                        results[var] = None
                        error_count += 1
        else:
            print(f"✗ Error response: {resp[:200]}")
            return elapsed, {}

        print(f"\n✓ Batch read completed")
        print(f"  Success: {success_count}/{len(self.all_variables)} variables")
        print(f"  Errors: {error_count}/{len(self.all_variables)} variables")
        print(f"\n⏱  Total time: {elapsed*1000:.2f} ms")
        print(f"📊 Average per variable: {elapsed*1000/len(self.all_variables):.2f} ms")

        # Show sample results
        print(f"\nSample results (first 5 variables):")
        for i, (var, val) in enumerate(results.items()):
            if i >= 5:
                break
            print(f"  {var:30s} = {val}")

        return elapsed, results


def main():
    print("="*70)
    print("CarMaker Massive Batch DVARead Test")
    print("Testing 236 variables: 12 ego + 224 traffic (T00~T31)")
    print("="*70)

    tester = MassiveBatchTester()

    if not tester.connect():
        print("\n✗ Failed to connect to CarMaker")
        print("Make sure CarMaker is running with APO server on port 16660")
        return

    try:
        # Wait before first test
        print("\n⏳ Waiting 3 seconds before sequential test...")
        time.sleep(3)

        # Test 1: Sequential
        seq_time, seq_results = tester.test_sequential_read()

        # Wait between tests
        print("\n⏳ Waiting 5 seconds before batch test...")
        time.sleep(5)

        # Test 2: Batch
        batch_time, batch_results = tester.test_batch_read()

        # Summary
        print("\n" + "="*70)
        print("FINAL SUMMARY")
        print("="*70)
        print(f"\n📊 Test Configuration:")
        print(f"   Total variables: {len(tester.all_variables)}")
        print(f"   - Ego: {len(tester.ego_quantities)}")
        print(f"   - Traffic: {len(tester.all_traffic_vars)} (32 objects × 7 quantities)")

        print(f"\n⏱  Performance Results:")
        print(f"   Sequential read: {seq_time*1000:.2f} ms ({len(tester.all_variables)} requests)")
        print(f"   Batch read:      {batch_time*1000:.2f} ms (1 request)")

        if batch_time > 0 and seq_time > 0:
            speedup = seq_time / batch_time
            time_saved = seq_time - batch_time
            print(f"\n🚀 Performance Gain:")
            print(f"   Speedup: {speedup:.2f}x faster")
            print(f"   Time saved: {time_saved*1000:.2f} ms ({time_saved:.3f} seconds)")
            print(f"   Efficiency: {(1 - batch_time/seq_time)*100:.1f}% reduction")

        # Data integrity check
        if seq_results and batch_results:
            print(f"\n🔍 Data Integrity Check:")
            print(f"   Sequential results: {len(seq_results)} variables")
            print(f"   Batch results: {len(batch_results)} variables")

            # Note: Values will differ due to time difference (vehicle is moving)
            print(f"\n⚠️  Note: Values will differ due to time difference between tests")
            print(f"   Sequential test took {seq_time:.3f}s (vehicle moved during read)")
            print(f"   Batch test took {batch_time:.3f}s (snapshot at single moment)")
            print(f"   → Batch provides more consistent data (all at same timestamp)")

    finally:
        tester.disconnect()
        print("\n✓ Disconnected")


if __name__ == "__main__":
    main()
