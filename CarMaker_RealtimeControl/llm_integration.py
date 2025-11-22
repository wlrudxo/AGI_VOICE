#!/usr/bin/env python3
"""
LLM Integration Layer for CarMaker Control
- Trigger-based auto intervention system
- LLM API integration (Claude)
- Script execution engine with guardrails
- Simulation pause/resume with safety guarantees
"""

import json
import time
import threading
import os
from typing import Dict, List, Any, Optional, Tuple


class TriggerManager:
    """Manages trigger conditions for LLM intervention"""

    def __init__(self, triggers: List[Dict[str, str]] = None):
        """
        Initialize TriggerManager

        Args:
            triggers: List of trigger definitions
                [{"name": "high_speed", "condition": "Car.v > 27.78", "description": "..."}]
        """
        self.triggers = triggers or []

    def load_from_file(self, filepath: str) -> bool:
        """Load triggers from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.triggers = data.get('triggers', [])
            return True
        except Exception as e:
            print(f"Failed to load triggers: {e}")
            return False

    def check_triggers(self, data: Dict[str, float]) -> Optional[Dict[str, str]]:
        """
        Check if any trigger condition is met

        Returns:
            Triggered rule dict if met, None otherwise
        """
        # Convert keys with dots to underscores for eval compatibility
        # 'Car.v' -> 'Car_v', 'Vhcl.tRoad' -> 'Vhcl_tRoad'
        # Also filter out None values (replace with 0.0)
        eval_data = {}
        for key, value in data.items():
            clean_key = key.replace('.', '_')
            eval_data[clean_key] = value if value is not None else 0.0

        for trigger in self.triggers:
            try:
                condition = trigger['condition']
                # Evaluate condition with AND/OR support
                result = eval(condition, {"__builtins__": {}}, {**eval_data, 'abs': abs, 'min': min, 'max': max})

                if result:
                    return trigger

            except Exception as e:
                # Only print error if it's not a periodic condition that's just checking time
                if 'Time' not in condition:
                    print(f"Trigger evaluation error: {trigger['name']} | {e}")
                continue

        return None


class ScriptExecutor:
    """Execute LLM-generated Python scripts with guardrails"""

    def __init__(self, server):
        """
        Initialize ScriptExecutor

        Args:
            server: CarMakerControlServer instance
        """
        self.server = server

    def execute_script(self, script: str, timeout: int = 30) -> Tuple[bool, str]:
        """
        Execute LLM-generated Python script with minimal guardrails

        Safety measures:
        1. Remove __builtins__ to block import/open/eval
        2. Timeout to prevent infinite loops
        3. Limit wait() duration

        Args:
            script: Python script to execute
            timeout: Maximum execution time in seconds

        Returns:
            (success, message) tuple
        """
        if not script:
            return False, "No script provided"

        # Helper functions context
        context = {
            'execute_cmd': lambda cmd: self.server.execute_command(cmd),
            'wait': lambda ms: time.sleep(min(ms, 10000) / 1000.0),  # Max 10 seconds
            'wait_until': lambda cond, t=30: self._wait_until(cond, min(t, 60)),  # Max 60 seconds
            'add_auto_rule': lambda cond, cmd, one_shot=True: self.server.add_auto_control_rule(cond, cmd, one_shot),
            'get_value': lambda var: self._get_value(var),
            'log': lambda msg: self.server.log(f"[LLM] {msg}"),
            # NEW: Failsafe control functions
            'maintain_and_wait_until': lambda cmd, cond, t=30000: self.maintain_and_wait_until(cmd, cond, t),
            'maintain_for': lambda cmd, dur: self.maintain_for(cmd, dur),
            # Safe built-in functions
            'abs': abs,
            'min': min,
            'max': max,
            'round': round,
            'len': len,
        }

        # Execute with timeout
        result = {"error": None, "success": False}

        def run_script():
            try:
                # Core guardrail: remove __builtins__
                # Blocks: import, open, eval, exec, __import__, etc.
                exec(script, {"__builtins__": {}}, context)
                result["success"] = True
            except Exception as e:
                result["error"] = e

        # Run in thread with timeout
        thread = threading.Thread(target=run_script, daemon=True)
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            self.server.log(f"Script timeout after {timeout}s")
            return False, f"Timeout after {timeout}s"

        if result["error"]:
            self.server.log(f"Script execution error: {result['error']}")
            return False, str(result["error"])

        if result["success"]:
            self.server.log("LLM script executed successfully")
            return True, "Script executed"

        return False, "Unknown error"

    def _wait_until(self, condition: str, timeout: int = 30) -> bool:
        """Wait until condition is met"""
        start_time = time.time()
        iteration = 0

        self.server.log(f"wait_until: waiting for '{condition}'")

        while True:
            if time.time() - start_time > timeout:
                self.server.log(f"wait_until timeout after {timeout}s: {condition}")
                return False

            # Read current values
            data = self.server.client.read_essential_quantities()

            # DEBUG: Print all data on first iteration
            if iteration == 0:
                self.server.log(f"wait_until: Raw data from CarMaker: {data}")

            # Convert keys with dots to underscores and handle None values
            eval_data = {}
            for key, value in data.items():
                clean_key = key.replace('.', '_')
                eval_data[clean_key] = value if value is not None else 0.0

            # DEBUG: Print converted data on first iteration
            if iteration == 0:
                self.server.log(f"wait_until: Converted eval_data keys: {list(eval_data.keys())}")
                self.server.log(f"wait_until: Car_v value: {eval_data.get('Car_v', 'NOT FOUND')}")

            # Log current speed every 2 seconds (20 iterations at 10Hz)
            if iteration % 20 == 0:
                speed_ms = eval_data.get('Car_v', 0.0)
                speed_kmh = speed_ms * 3.6
                self.server.log(f"wait_until: Current speed = {speed_kmh:.1f} km/h ({speed_ms:.2f} m/s), checking '{condition}'")

            # Evaluate condition with current data
            try:
                result = eval(condition, {"__builtins__": {}}, {**eval_data, 'abs': abs, 'min': min, 'max': max})
                if result:
                    speed_ms = eval_data.get('Car_v', 0.0)
                    speed_kmh = speed_ms * 3.6
                    self.server.log(f"wait_until: Condition met! Speed = {speed_kmh:.1f} km/h ({speed_ms:.2f} m/s)")
                    return True
            except Exception as e:
                self.server.log(f"wait_until: Condition evaluation error: {e}")
                self.server.log(f"wait_until: Available variables: {list(eval_data.keys())}")
                return False

            iteration += 1
            time.sleep(0.1)  # 10Hz check

    def _get_value(self, variable: str) -> Optional[float]:
        """Get current value of a variable"""
        resp = self.server.client.send_command(f"DVARead {variable}")
        if resp and resp.startswith("O"):
            return float(resp[1:].strip())
        return None

    def maintain_and_wait_until(self, command: str, condition: str, timeout: int = 30000) -> bool:
        """
        Maintain a command by repeatedly sending it while waiting for a condition
        Failsafe: command stops automatically if script fails

        Args:
            command: Command to maintain (e.g., 'DVAWrite DM.v.Trgt 19.44 200 Abs')
            condition: Condition to wait for (e.g., 'Car_v >= 19.44')
            timeout: Timeout in milliseconds (default 30000ms = 30s)

        Returns:
            True if condition met, False if timeout
        """
        start_time = time.time()
        iteration = 0

        self.server.log(f"maintain_and_wait_until: '{command}' until '{condition}' (timeout={timeout}ms)")

        while True:
            # Check timeout
            elapsed_ms = (time.time() - start_time) * 1000
            if elapsed_ms > timeout:
                self.server.log(f"maintain_and_wait_until: TIMEOUT after {timeout}ms")
                return False

            # Send command every iteration (0.2s) - Heartbeat
            self.server.execute_command(command)

            # Read current values
            data = self.server.client.read_essential_quantities()

            # Convert keys
            eval_data = {}
            for key, value in data.items():
                clean_key = key.replace('.', '_')
                eval_data[clean_key] = value if value is not None else 0.0

            # Log every 2 seconds (10 iterations at 0.2s)
            if iteration % 10 == 0:
                speed_ms = eval_data.get('Car_v', 0.0)
                self.server.log(f"maintain_and_wait_until[{iteration:03d}]: Speed={speed_ms:.2f} m/s, checking '{condition}'")

            # Check condition
            try:
                result = eval(condition, {"__builtins__": {}}, {**eval_data, 'abs': abs, 'min': min, 'max': max})
                if result:
                    speed_ms = eval_data.get('Car_v', 0.0)
                    self.server.log(f"maintain_and_wait_until: Condition met! Speed={speed_ms:.2f} m/s")
                    return True
            except Exception as e:
                self.server.log(f"maintain_and_wait_until: Condition error: {e}")
                return False

            iteration += 1
            time.sleep(0.2)  # 200ms interval

    def maintain_for(self, command: str, duration: int):
        """
        Maintain a command for a specific duration

        Args:
            command: Command to maintain (e.g., 'DVAWrite DM.v.Trgt 19.44 200 Abs')
            duration: Duration in milliseconds
        """
        self.server.log(f"maintain_for: '{command}' for {duration}ms")

        iterations = int(duration / 200)  # 200ms per iteration

        for i in range(iterations):
            self.server.execute_command(command)

            # Log every 2 seconds (10 iterations)
            if i % 10 == 0:
                data = self.server.client.read_essential_quantities()
                speed_ms = data.get('Car.v') or 0.0
                self.server.log(f"maintain_for[{i:03d}/{iterations:03d}]: Speed={speed_ms:.2f} m/s")

            time.sleep(0.2)

        self.server.log(f"maintain_for: Completed {duration}ms")


class PromptGenerator:
    """Generate prompts for LLM from trigger and vehicle state"""

    @staticmethod
    def generate_prompt(trigger: Dict[str, str], current_state: Dict[str, float],
                       recent_history: List[Dict] = None) -> str:
        """
        Generate LLM prompt from trigger and state

        Args:
            trigger: Trigger that fired
            current_state: Current vehicle state
            recent_history: Recent state history (optional)

        Returns:
            Formatted prompt string
        """
        # Helper values - safely handle None values
        speed_ms = current_state.get('Car.v') or 0.0
        speed_kmh = speed_ms * 3.6

        prompt = f"""You are an autonomous CarMaker simulation control system.

Current Situation:
- Trigger: {trigger['name']} - {trigger['description']}
- Condition: {trigger['condition']}
- Current Speed: {speed_kmh:.1f} km/h ({speed_ms:.2f} m/s)
- Gas Pedal: {current_state.get('DM.Gas') or 0:.2f}
- Brake: {current_state.get('DM.Brake') or 0:.2f}
- Steering Angle: {current_state.get('DM.Steer.Ang') or 0:.3f} rad
- Road Position: {current_state.get('Vhcl.sRoad') or 0:.1f} m
- Lateral Offset: {current_state.get('Vhcl.tRoad') or 0:.2f} m
- Yaw Rate: {current_state.get('Vhcl.YawRate') or 0:.3f} rad/s
- Simulation Time: {current_state.get('Time') or 0:.2f} s

Available Helper Functions:
- execute_cmd(command: str) -> bool
  Example: execute_cmd('DVAWrite DM.Gas 0.5 2000 Abs')

- wait(milliseconds: int)
  Example: wait(1000)  # Wait 1 second

- wait_until(condition: str, timeout: int = 30) -> bool
  Example: wait_until('Car_v >= 27.78')
  Example: wait_until('Car_v >= 27.78 and Vhcl_tRoad < 0.5')

- add_auto_rule(condition: str, command: str, one_shot: bool = True)
  Example: add_auto_rule('Car_v <= 25.0', 'DVAWrite DM.Brake 0.0 500 Abs')
  Note: Use underscores in variable names (Car_v not Car.v)

- get_value(variable: str) -> float
  Example: speed = get_value('Car.v')
  Note: Use original CarMaker names with dots for get_value()

- log(message: str)
  Example: log('Starting deceleration sequence')

Task: Generate appropriate control commands to safely handle this situation.

Response Format (JSON):
{{
  "analysis": "Brief situation analysis",
  "strategy": "Control strategy explanation",
  "script": \"\"\"
# Python script using helper functions
execute_cmd('DVAWrite DM.Gas 0.0 500 Abs')
wait(500)
log('Deceleration started')
\"\"\"
}}

Important:
- Use Python syntax (if/else, loops, variables allowed)
- Conditions support: >, <, >=, <=, ==, and, or, abs()
- Focus on safety and smooth control
- Return ONLY the JSON response"""

        return prompt


class LLMIntegrationLayer:
    """Main LLM integration layer with trigger-based intervention"""

    def __init__(self, server, api_key: str = None, manual_mode: bool = True):
        """
        Initialize LLM Integration Layer

        Args:
            server: CarMakerControlServer instance
            api_key: Anthropic API key (default: from ANTHROPIC_API_KEY env var)
            manual_mode: If True, prompt user for manual input instead of API call
        """
        self.server = server
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        self.manual_mode = manual_mode

        self.trigger_manager = TriggerManager()
        self.script_executor = ScriptExecutor(server)
        self.prompt_generator = PromptGenerator()

        self.enabled = False
        self.monitor_thread = None
        self.is_controlling = False  # Flag to prevent re-triggering during LLM control

        # LLM client (lazy init)
        self._llm_client = None

        # Setup log file (overwrite mode)
        self.log_file = open('llm_control.log', 'w', encoding='utf-8', buffering=1)  # Line buffered

        # Wrap server.log to also write to file
        self._original_server_log = server.log
        def wrapped_log(msg):
            self.log_file.write(f"{msg}\n")
            self._original_server_log(msg)
        server.log = wrapped_log

        server.log("=" * 70)
        server.log("LLM Integration Layer - Detailed Log")
        server.log("=" * 70)

    @property
    def llm_client(self):
        """Lazy initialization of Anthropic client"""
        if self._llm_client is None:
            try:
                import anthropic
                if not self.api_key:
                    raise ValueError("ANTHROPIC_API_KEY not set")
                self._llm_client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        return self._llm_client

    def load_triggers(self, filepath: str) -> bool:
        """Load triggers from JSON file"""
        return self.trigger_manager.load_from_file(filepath)

    def start_monitoring(self):
        """Start LLM intervention monitoring"""
        if self.enabled:
            self.server.log("LLM monitoring already active")
            return

        # Initialize simulation speed to normal (1.0) - 30 second timeout
        self.server.log("Initializing simulation speed to 1.0...")
        result = self.server.execute_command("DVAWrite SC.TAccel 1.0 30000 Abs")
        self.server.log(f"  SC.TAccel = 1.0 (30s timeout) result: {result}")

        self.enabled = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.server.log("LLM monitoring started")

    def stop_monitoring(self):
        """Stop LLM intervention monitoring"""
        self.enabled = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self.server.log("LLM monitoring stopped")

        # Close log file
        if self.log_file:
            self.log_file.close()
            # Restore original log
            self.server.log = self._original_server_log

    def _monitor_loop(self):
        """Main monitoring loop for trigger detection"""
        iteration = 0
        self.server.log("Monitor loop started")

        while self.enabled and self.server.client.connected:
            try:
                # Skip trigger check if already controlling
                if self.is_controlling:
                    if iteration % 10 == 0:
                        self.server.log(f"Monitor: LLM is controlling, skipping trigger check (iteration {iteration})")
                    iteration += 1
                    time.sleep(0.1)
                    continue

                # Read current state
                data = self.server.client.read_essential_quantities()

                # DEBUG: Log raw data every 1 second
                if iteration % 10 == 0:
                    self.server.log(f"Monitor[{iteration:04d}]: RAW DATA = {data}")
                    speed_ms = data.get('Car.v') or 0.0
                    gas = data.get('DM.Gas') or 0.0
                    brake = data.get('DM.Brake') or 0.0
                    self.server.log(f"Monitor[{iteration:04d}]: Speed={speed_ms:.2f} m/s ({speed_ms*3.6:.1f} km/h), Gas={gas:.2f}, Brake={brake:.2f}")

                # Check triggers
                triggered = self.trigger_manager.check_triggers(data)

                if triggered:
                    self.server.log(f"Monitor[{iteration:04d}]: *** TRIGGER DETECTED: {triggered['name']} ***")

                    # Perform LLM intervention with safety
                    self._llm_intervention_with_safety(triggered, data)

                iteration += 1
                time.sleep(0.1)  # 10Hz check rate

            except Exception as e:
                self.server.log(f"Monitor[{iteration:04d}]: ERROR: {e}")
                import traceback
                self.server.log(traceback.format_exc())
                time.sleep(1)

    def _llm_intervention_with_safety(self, trigger: Dict[str, str], data: Dict[str, float]):
        """
        LLM intervention with simulation pause/resume guarantee
        SC.TAccel recovery ensured via try/finally
        """
        self.server.log("=" * 70)
        self.server.log("LLM INTERVENTION START")
        self.server.log("=" * 70)

        try:
            # Set controlling flag to prevent re-triggering
            self.server.log("Step 1: Setting is_controlling flag")
            self.is_controlling = True
            self.server.log(f"  is_controlling = {self.is_controlling}")

            # Log current speed when trigger fires
            self.server.log(f"Step 2: Trigger info")
            self.server.log(f"  Trigger: {trigger['name']}")
            self.server.log(f"  RAW DATA at trigger: {data}")
            speed_ms = data.get('Car.v') or 0.0
            speed_kmh = speed_ms * 3.6
            self.server.log(f"  Car.v extracted: {data.get('Car.v')}")
            self.server.log(f"  Speed calculated: {speed_ms:.2f} m/s ({speed_kmh:.1f} km/h)")

            # Pause simulation - 30 second timeout
            self.server.log("Step 3: Pausing simulation (SC.TAccel = 0.001, 30s timeout)")
            result = self.server.execute_command("DVAWrite SC.TAccel 0.001 30000 Abs")
            self.server.log(f"  Command result: {result}")
            self.server.log(f"  Simulation paused for LLM intervention")

            # Generate prompt
            self.server.log("Step 4: Generating LLM prompt")
            prompt = self.prompt_generator.generate_prompt(trigger, data)

            # Call LLM
            self.server.log("Step 5: Calling LLM API (or manual input)...")
            llm_response = self._call_llm(prompt)

            if not llm_response:
                self.server.log("  ERROR: Failed to get LLM response")
                return

            # Log LLM response
            self.server.log("Step 6: LLM response received")
            self.server.log(f"  Analysis: {llm_response.get('analysis', 'N/A')}")
            self.server.log(f"  Strategy: {llm_response.get('strategy', 'N/A')}")

            # IMPORTANT: Resume simulation BEFORE executing script
            # Script needs simulation to run for wait_until(), etc.
            self.server.log("Step 7: Resuming simulation (SC.TAccel = 1.0, 30s timeout)")
            result = self.server.execute_command("DVAWrite SC.TAccel 1.0 30000 Abs")
            self.server.log(f"  Command result: {result}")
            self.server.log(f"  Simulation resumed - ready to execute script")

            # Execute script
            self.server.log("Step 8: Executing LLM script")
            script = llm_response.get('script', '')
            if script:
                self.server.log(f"  Script length: {len(script)} chars")
                success, msg = self.script_executor.execute_script(script, timeout=30)
                self.server.log(f"  Script execution result: success={success}, msg={msg}")
                if not success:
                    self.server.log(f"  ERROR: LLM script failed: {msg}")
            else:
                self.server.log("  WARNING: No script in LLM response")

        finally:
            # ALWAYS ensure simulation speed is restored and clear controlling flag
            self.server.log("Step 9 (FINALLY): Cleanup")
            result = self.server.execute_command("DVAWrite SC.TAccel 1.0 30000 Abs")
            self.server.log(f"  SC.TAccel restore (30s timeout) result: {result}")
            self.is_controlling = False
            self.server.log(f"  is_controlling = {self.is_controlling}")
            self.server.log("=" * 70)
            self.server.log("LLM INTERVENTION END")
            self.server.log("=" * 70)

    def _call_llm(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Call LLM API and parse response (or manual input if manual_mode=True)

        Returns:
            Parsed JSON response dict, or None on failure
        """
        if self.manual_mode:
            return self._manual_input_mode(prompt)

        try:
            message = self.llm_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # Parse JSON response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text

            result = json.loads(json_text)
            return result

        except Exception as e:
            self.server.log(f"LLM API error: {e}")
            return None

    def _manual_input_mode(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Manual input mode - show examples and let user input response

        Returns:
            Parsed JSON response dict, or None on failure
        """
        print("\n" + "=" * 70)
        print("🤖 LLM MANUAL INPUT MODE")
        print("=" * 70)
        print("\n[Simulation Context]")
        # Extract key info from prompt
        lines = prompt.split('\n')
        for line in lines:
            if 'Trigger:' in line or 'Speed:' in line or 'Gas' in line or 'Brake' in line or 'Lateral' in line:
                print(line)

        print("\n" + "=" * 70)
        print("📝 EXAMPLE RESPONSES (Copy and modify as needed)")
        print("=" * 70)

        print("\n[Example 1: Simple Brake Control - 1000ms]")
        example1 = {
            "analysis": "속도 80kph 초과 감지",
            "strategy": "브레이크를 약하게 1000ms 적용",
            "script": """execute_cmd('DVAWrite DM.Brake 0.2 1000 Abs')
log('Brake applied for 1000ms')"""
        }
        print(json.dumps(example1, indent=2, ensure_ascii=False))

        print("\n[Example 2: Accelerate to 100kph then Stop]")
        example2 = {
            "analysis": "100kph까지 가속 후 종료 테스트",
            "strategy": "가속 페달을 밟아 100kph 도달 대기, 도달 후 가속 중단",
            "script": """execute_cmd('DVAWrite DM.Gas 0.8 -1 Abs')
log('Accelerating to 100kph...')
wait_until('Car_v >= 27.78')
execute_cmd('DVAWrite DM.Gas 0.0 500 Abs')
log('Reached 100kph, acceleration stopped')"""
        }
        print(json.dumps(example2, indent=2, ensure_ascii=False))

        print("\n[Example 3: Speed Control with Failsafe (70 → 50 kph)]")
        example3 = {
            "analysis": "속도 변화 시퀀스: 70kph → 3초 유지 → 50kph → 3초 유지 (NEW: Failsafe)",
            "strategy": "목표 속도 직접 설정 + 0.2초마다 재전송 (에러 시 자동 중단)",
            "script": """# Step 1: Accelerate to 70kph (19.44 m/s)
log('Accelerating to 19.44 m/s (70kph)...')
maintain_and_wait_until('DVAWrite DM.v.Trgt 19.44 200 Abs', 'Car_v >= 19.44', 30000)
log('Reached 70kph')

# Step 2: Maintain 70kph for 3 seconds
log('Maintaining 70kph for 3 seconds...')
maintain_for('DVAWrite DM.v.Trgt 19.44 200 Abs', 3000)

# Step 3: Decelerate to 50kph (13.89 m/s)
log('Decelerating to 13.89 m/s (50kph)...')
maintain_and_wait_until('DVAWrite DM.v.Trgt 13.89 200 Abs', 'Car_v <= 13.89', 30000)
log('Reached 50kph')

# Step 4: Maintain 50kph for 3 seconds
log('Maintaining 50kph for 3 seconds...')
maintain_for('DVAWrite DM.v.Trgt 13.89 200 Abs', 3000)
log('Sequence completed')"""
        }
        print(json.dumps(example3, indent=2, ensure_ascii=False))

        print("\n" + "=" * 70)
        print("⌨️  Enter your response as JSON")
        print("=" * 70)
        print("Options:")
        print("  1 - Use Example 1 (Simple Deceleration)")
        print("  2 - Use Example 2 (Conditional Control)")
        print("  3 - Use Example 3 (Lane Correction)")
        print("  JSON - Paste your own JSON")
        print("  skip - Skip this intervention")
        print()

        try:
            user_input = input("Your choice: ").strip()

            if user_input == '1':
                return example1
            elif user_input == '2':
                return example2
            elif user_input == '3':
                return example3
            elif user_input.lower() == 'skip':
                print("⏭️  Skipping intervention")
                return None
            elif user_input.startswith('{'):
                # Try to parse as JSON
                result = json.loads(user_input)
                return result
            else:
                print("❌ Invalid input. Skipping intervention.")
                return None

        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


def test_script_executor():
    """Test script executor with dummy server"""
    class DummyServer:
        def log(self, msg):
            print(f"[LOG] {msg}")

        def execute_command(self, cmd):
            print(f"[CMD] {cmd}")
            return True, "OK"

        def add_auto_control_rule(self, cond, cmd, one_shot):
            print(f"[RULE] {cond} -> {cmd}")
            return True, "Rule added"

        class DummyClient:
            def send_command(self, cmd):
                return "O25.0"

            def read_essential_quantities(self):
                return {'Car.v': 25.0, 'Time': 10.0}

        client = DummyClient()

    server = DummyServer()
    executor = ScriptExecutor(server)

    # Test script
    test_script = """
log('Test script started')
execute_cmd('DVAWrite DM.Gas 0.5 1000 Abs')
wait(100)
speed = get_value('Car.v')
log(f'Current speed: {speed}')
add_auto_rule('Car.v > 30.0', 'DVAWrite DM.Brake 0.3 1000 Abs')
log('Test script completed')
"""

    print("=" * 60)
    print("Testing ScriptExecutor")
    print("=" * 60)

    success, msg = executor.execute_script(test_script)

    print(f"\nResult: {success}")
    print(f"Message: {msg}")


if __name__ == "__main__":
    test_script_executor()
