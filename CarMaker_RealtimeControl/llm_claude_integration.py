#!/usr/bin/env python3
"""
Claude AI Integration for CarMaker Control

This script uses Claude API to generate CarMaker control commands
from natural language prompts.

Requirements:
    pip install anthropic

Setup:
    export ANTHROPIC_API_KEY=your_api_key_here
    # or on Windows:
    set ANTHROPIC_API_KEY=your_api_key_here

Usage:
    python llm_claude_integration.py --prompt "Drive smoothly around the curve"
    python llm_claude_integration.py --interactive
"""

import argparse
import json
import os
import sys
import subprocess


def call_carmaker_control(args_list):
    """Call carmaker_llm_control.py and return JSON result"""
    cmd = [sys.executable, "carmaker_llm_control.py"] + args_list
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def get_vehicle_status():
    """Get current vehicle status"""
    return call_carmaker_control(["--status"])


def execute_command(command):
    """Execute a command in CarMaker"""
    return call_carmaker_control(["--cmd", command])


def ask_claude(prompt, vehicle_status):
    """
    Ask Claude to generate CarMaker control commands

    Returns list of DVAWrite commands
    """
    try:
        import anthropic
    except ImportError:
        print("Error: anthropic package not installed")
        print("Install with: pip install anthropic")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Prepare context with vehicle status and UAQ reference
    system_prompt = """You are an expert CarMaker vehicle control system. You generate precise DVAWrite commands to control a simulated vehicle.

Available Commands:
1. DVAWrite DM.Gas <value> <duration> <mode>
   - value: 0.0 to 1.0 (throttle percentage)
   - duration: milliseconds (-1 for unlimited)
   - mode: Abs, AbsRamp, Fac, etc.

2. DVAWrite DM.Brake <value> <duration> <mode>
   - value: 0.0 to 1.0 (brake percentage)

3. DVAWrite DM.Steer.Ang <value> <duration> <mode>
   - value: steering angle in radians (-1.0 to 1.0)

4. DVAWrite DM.v.Trgt <value> <duration> <mode>
   - value: target speed in m/s

5. DVAWrite DM.LaneOffset <value> <duration> <mode>
   - value: lateral offset in meters

6. DVAWrite SC.TAccel <value>
   - value: time acceleration (0.001 = pause, 1.0 = normal)

7. StartSim, StopSim, GetSimStatus

Important:
- Speed conversion: km/h to m/s: divide by 3.6
- Always use smooth transitions (AbsRamp) for steering and speed changes
- Use appropriate durations (2000-5000 ms for smooth changes)
- Consider current vehicle state before generating commands

Output Format:
Return ONLY a JSON object with this structure:
{
  "analysis": "brief analysis of the situation",
  "commands": ["command1", "command2", ...],
  "explanation": "why these commands were chosen"
}
"""

    # Format vehicle status for Claude
    status_text = json.dumps(vehicle_status, indent=2)

    user_message = f"""Current Vehicle Status:
{status_text}

User Request: {prompt}

Generate appropriate CarMaker control commands to fulfill this request. Consider the current vehicle state and generate safe, smooth commands."""

    # Call Claude API
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    # Parse Claude's response
    response_text = message.content[0].text

    # Extract JSON from response
    try:
        # Try to find JSON in the response
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

    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse Claude's JSON response: {e}")
        print(f"Raw response: {response_text}")
        return {
            "analysis": "Failed to parse response",
            "commands": [],
            "explanation": response_text
        }


def main():
    parser = argparse.ArgumentParser(
        description='Claude AI Integration for CarMaker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single prompt
  python llm_claude_integration.py --prompt "Accelerate smoothly to 100 km/h"

  # Interactive mode
  python llm_claude_integration.py --interactive

Setup:
  1. Install: pip install anthropic
  2. Set API key: export ANTHROPIC_API_KEY=your_key
  3. Run the script
        """
    )

    parser.add_argument('--prompt', type=str,
                        help='Natural language command')
    parser.add_argument('--interactive', action='store_true',
                        help='Interactive conversation mode')
    parser.add_argument('--dry-run', action='store_true',
                        help='Generate commands but do not execute')

    args = parser.parse_args()

    if args.interactive:
        print("Claude AI CarMaker Control - Interactive Mode")
        print("=" * 60)
        print("Type your commands, or 'quit' to exit\n")

        while True:
            try:
                prompt = input("You: ").strip()

                if not prompt:
                    continue

                if prompt.lower() in ['quit', 'exit', 'q']:
                    break

                # Get vehicle status
                print("\nFetching vehicle status...")
                status = get_vehicle_status()

                if not status:
                    print("Failed to get status")
                    continue

                # Ask Claude
                print("Asking Claude...")
                claude_response = ask_claude(prompt, status)

                print(f"\nClaude's Analysis: {claude_response.get('analysis')}")
                print(f"\nGenerated Commands:")
                for cmd in claude_response.get('commands', []):
                    print(f"  → {cmd}")
                print(f"\nExplanation: {claude_response.get('explanation')}")

                if args.dry_run:
                    print("\n[DRY RUN - Commands not executed]")
                    continue

                # Execute commands
                print("\nExecuting commands...")
                for cmd in claude_response.get('commands', []):
                    result = execute_command(cmd)
                    if result:
                        status_symbol = "✓" if result.get('success') else "✗"
                        print(f"  {status_symbol} {cmd}")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

    elif args.prompt:
        # Get status
        print("Fetching vehicle status...")
        status = get_vehicle_status()

        if not status:
            print("Failed to get vehicle status")
            sys.exit(1)

        # Ask Claude
        print("Asking Claude AI...")
        claude_response = ask_claude(args.prompt, status)

        print("\n" + "=" * 60)
        print("CLAUDE'S RESPONSE")
        print("=" * 60)
        print(f"\nAnalysis: {claude_response.get('analysis')}")
        print(f"\nCommands:")
        for cmd in claude_response.get('commands', []):
            print(f"  {cmd}")
        print(f"\nExplanation: {claude_response.get('explanation')}")

        if args.dry_run:
            print("\n[DRY RUN - Commands not executed]")
            sys.exit(0)

        # Execute
        print("\n" + "=" * 60)
        print("EXECUTING COMMANDS")
        print("=" * 60)

        for cmd in claude_response.get('commands', []):
            result = execute_command(cmd)
            if result:
                print(f"\nCommand: {cmd}")
                print(f"Success: {result.get('success')}")
                print(f"Response: {result.get('response')}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
