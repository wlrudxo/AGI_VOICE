#!/usr/bin/env python3
"""
LLM Agent Example for CarMaker Control

This script demonstrates how an LLM can control CarMaker:
1. Get current vehicle status
2. Analyze the situation
3. Generate control commands
4. Execute commands

Usage:
    python llm_agent_example.py --prompt "Accelerate to 80 km/h"
    python llm_agent_example.py --prompt "Apply gentle braking"
    python llm_agent_example.py --interactive
"""

import argparse
import json
import subprocess
import sys


def call_carmaker_control(args_list):
    """
    Call carmaker_llm_control.py and return JSON result
    """
    cmd = [sys.executable, "carmaker_llm_control.py"] + args_list
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error executing command: {result.stderr}", file=sys.stderr)
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}", file=sys.stderr)
        print(f"Output was: {result.stdout}", file=sys.stderr)
        return None


def get_vehicle_status():
    """Get current vehicle status from CarMaker"""
    return call_carmaker_control(["--status", "--pretty"])


def execute_command(command):
    """Execute a command in CarMaker"""
    return call_carmaker_control(["--cmd", command])


def llm_generate_commands(prompt, status):
    """
    This is where you would call an actual LLM (Claude, GPT, etc.)
    For now, this is a simple rule-based example showing the pattern

    In production, you would:
    1. Format status as context
    2. Send to LLM API (Anthropic, OpenAI, etc.)
    3. Parse LLM response for commands
    """

    print("\n" + "="*60)
    print("LLM DECISION MAKING PROCESS (Simulated)")
    print("="*60)

    # Format context for LLM
    context = f"""
Current Vehicle Status:
- Speed: {status.get('_interpretation', {}).get('speed_kmh', 'N/A')} km/h
- Simulation State: {status.get('_interpretation', {}).get('simulation_state', 'N/A')}
- Gas Pedal: {status.get('DM.Gas', 'N/A')}
- Brake Pedal: {status.get('DM.Brake', 'N/A')}
- Steering: {status.get('DM.Steer.Ang', 'N/A')} rad
- Time Acceleration: {status.get('SC.TAccel', 'N/A')}x

User Request: {prompt}
"""

    print(context)
    print("\nGenerating commands based on request...")

    # Simple rule-based example (replace with actual LLM call)
    commands = []

    prompt_lower = prompt.lower()

    if "accelerate" in prompt_lower or "speed up" in prompt_lower:
        # Extract target speed if mentioned
        if "80" in prompt:
            commands.append("DVAWrite DM.Gas 0.6 3000 Abs")
            commands.append("DVAWrite DM.v.Trgt 22.22 5000 Abs")  # 80 km/h = 22.22 m/s
        else:
            commands.append("DVAWrite DM.Gas 0.5 2000 Abs")

    elif "brake" in prompt_lower or "slow" in prompt_lower:
        if "gentle" in prompt_lower or "light" in prompt_lower:
            commands.append("DVAWrite DM.Brake 0.3 2000 Abs")
        elif "hard" in prompt_lower or "emergency" in prompt_lower:
            commands.append("DVAWrite DM.Brake 1.0 1000 Abs")
        else:
            commands.append("DVAWrite DM.Brake 0.5 2000 Abs")

    elif "steer" in prompt_lower or "turn" in prompt_lower:
        if "left" in prompt_lower:
            commands.append("DVAWrite DM.Steer.Ang 0.2 2000 AbsRamp")
        elif "right" in prompt_lower:
            commands.append("DVAWrite DM.Steer.Ang -0.2 2000 AbsRamp")

    elif "start" in prompt_lower:
        commands.append("StartSim")

    elif "stop" in prompt_lower:
        commands.append("StopSim")

    elif "pause" in prompt_lower:
        commands.append("DVAWrite SC.TAccel 0.001")

    elif "resume" in prompt_lower or "continue" in prompt_lower:
        commands.append("DVAWrite SC.TAccel 1.0")

    else:
        commands.append("# No matching action found for this prompt")

    print(f"\nGenerated Commands:")
    for cmd in commands:
        print(f"  → {cmd}")

    return commands


def main():
    parser = argparse.ArgumentParser(
        description='LLM Agent for CarMaker Control',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single prompt
  python llm_agent_example.py --prompt "Accelerate to 80 km/h"

  # Interactive mode
  python llm_agent_example.py --interactive

  # With actual LLM (requires API key)
  export ANTHROPIC_API_KEY=your_key
  python llm_agent_example.py --prompt "Navigate the curve smoothly" --use-llm
        """
    )

    parser.add_argument('--prompt', type=str,
                        help='Natural language command for the vehicle')
    parser.add_argument('--interactive', action='store_true',
                        help='Interactive mode (continuous conversation)')
    parser.add_argument('--use-llm', action='store_true',
                        help='Use actual LLM API (requires configuration)')

    args = parser.parse_args()

    if args.interactive:
        # Interactive mode
        print("CarMaker LLM Agent - Interactive Mode")
        print("Type your commands in natural language, or 'quit' to exit")
        print("="*60)

        while True:
            try:
                prompt = input("\nYou: ").strip()

                if not prompt:
                    continue

                if prompt.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break

                # Get current status
                print("\nFetching vehicle status...")
                status = get_vehicle_status()

                if status is None:
                    print("Failed to get vehicle status")
                    continue

                # Generate commands
                commands = llm_generate_commands(prompt, status)

                if not commands or commands[0].startswith("#"):
                    print("Could not generate valid commands from this prompt.")
                    continue

                # Execute commands
                print("\nExecuting commands...")
                for cmd in commands:
                    result = execute_command(cmd)
                    if result:
                        if result.get("success"):
                            print(f"  ✓ {cmd}")
                        else:
                            print(f"  ✗ {cmd}: {result.get('response')}")

            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break
            except Exception as e:
                print(f"Error: {e}")

    elif args.prompt:
        # Single prompt mode
        print(f"Processing prompt: {args.prompt}")

        # Get current status
        print("\n1. Fetching vehicle status...")
        status = get_vehicle_status()

        if status is None:
            print("Failed to get vehicle status")
            sys.exit(1)

        print(f"\nCurrent speed: {status.get('_interpretation', {}).get('speed_kmh', 'N/A')} km/h")

        # Generate commands
        print("\n2. Generating control commands...")
        commands = llm_generate_commands(args.prompt, status)

        if not commands or commands[0].startswith("#"):
            print("Could not generate valid commands from this prompt.")
            sys.exit(1)

        # Execute commands
        print("\n3. Executing commands...")
        for cmd in commands:
            result = execute_command(cmd)
            if result:
                print(f"  Command: {cmd}")
                print(f"  Success: {result.get('success')}")
                print(f"  Response: {result.get('response')}")
                print()

        print("Done!")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
