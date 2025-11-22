# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CarMaker Real-Time Control System with LLM Integration - A Python-based control interface for IPG CarMaker simulation software. This system provides:

- **Socket-based real-time control** via APO (Application Programming Option) interface
- **GUI application** for manual control and monitoring
- **CLI tool** for command-line control
- **LLM integration layer** for autonomous trigger-based interventions
- **Failsafe control mechanisms** for safe autonomous operation

## Common Commands

### Running the System

```bash
# Start GUI application (includes control server)
python carmaker_gui.py

# Run CLI commands (auto-detects GUI server or direct connection)
python cm_cli.py status                                    # Get vehicle status
python cm_cli.py cmd "DVAWrite DM.Gas 0.5 2000 Abs"       # Execute command
python cm_cli.py wait_until "Car_v >= 27.78" "DVAWrite DM.Brake 0.3 2000 Abs" 30

# LLM-specific control interface (JSON output)
python carmaker_llm_control.py --status                    # Get status as JSON
python carmaker_llm_control.py --cmd "StartSim"           # Execute command
python carmaker_llm_control.py --batch commands.txt       # Batch execution
```

### Testing

```bash
# Test LLM integration layer
python llm_integration.py                                  # Runs test_script_executor()

# Test integration
python test_llm_integration.py
```

## Architecture

### Core Components

1. **carmaker_client.py** - Low-level socket client for CarMaker APO
   - Manages TCP socket connection to CarMaker (default: localhost:16660)
   - Sequential DVARead commands with thread locks
   - Execute arbitrary CarMaker commands (DVAWrite, StartSim, etc.)
   - Essential quantities: Gas, Brake, Steering, Speed, Position, etc.

2. **carmaker_control_server.py** - Headless control server
   - Manages CarMaker connection lifecycle
   - Socket server for CLI/GUI communication (port 7777)
   - Real-time monitoring loop (10Hz)
   - Auto-control rules with condition evaluation (AND/OR support)
   - Condition syntax: Uses underscores in variable names (Car_v not Car.v)

3. **carmaker_gui.py** - Tkinter GUI application
   - Direct method calls to control server (same process)
   - Manual control sliders (Gas, Brake, Steering)
   - Real-time data monitoring display
   - Text command input
   - Starts socket server for CLI access

4. **cm_cli.py** - Command-line interface
   - Auto-detects GUI server or falls back to direct connection
   - JSON output for easy parsing
   - Supports direct commands and conditional execution
   - wait_until support for condition-based automation

5. **carmaker_llm_control.py** - LLM-specific terminal interface
   - JSON-only output (no GUI dependencies)
   - Designed for LLM consumption
   - --status flag returns all essential quantities
   - --cmd for single commands, --batch for files

6. **llm_integration.py** - LLM integration layer
   - Trigger-based intervention system
   - Script executor with safety guardrails
   - Simulation pause/resume for LLM decision-making
   - Failsafe control functions (maintain_and_wait_until, maintain_for)
   - Manual mode for testing without API key

### Key Design Patterns

**Three-Layer Architecture:**
```
CarMaker <-> Client <-> Control Server <-> GUI/CLI/LLM
                                       |
                                       +-> Socket Server (port 7777)
```

**Condition Evaluation:**
- Variable naming: Dots replaced with underscores (Car.v → Car_v)
- Supports: >, <, >=, <=, ==, and, or, abs(), min(), max()
- Example: "Car_v > 27.78 and abs(Vhcl_tRoad) > 1.0"

**LLM Script Execution:**
- Python scripts with restricted __builtins__ (no import/open/eval)
- Helper functions: execute_cmd(), wait(), wait_until(), get_value(), log()
- Failsafe functions: maintain_and_wait_until(), maintain_for()
- Timeout protection (default 30s)

## CarMaker UAQ (User Accessible Quantities) Reference

The `/docs` directory contains complete UAQ documentation extracted from CarMaker Reference Manual Chapter 26:

- **UAQ_01_General_Control.md** - Simulation control, time, environment, driver inputs
- **UAQ_02_Car.md** - Vehicle body dynamics and aerodynamics
- **UAQ_03_Suspension.md** - Suspension system quantities
- **UAQ_04_Suspension_Tire_Brake.md** - Tire forces and brake system
- **UAQ_05_Powertrain.md** - Engine, gearbox, electric motor
- **UAQ_06_Sensor_Part1.md** - Object sensors, radar, camera, lidar
- **UAQ_06_Sensor_Part2.md** - GNSS, IMU, road sensors, collision
- **UAQ_07_Trailer.md** - Trailer quantities
- **UAQ_08_Traffic.md** - Traffic objects
- **UAQ_Complete_Reference.md** - Full combined reference

**Important**: When working with CarMaker quantities, use the Bash tool to reference the complete UAQ documentation:

```bash
cat docs/UAQ_Complete_Reference.md | grep -A 5 "quantity_name"
```

## CarMaker APO Command Reference

### DVAWrite Command Format
```
DVAWrite <Name> <Value> [Duration] [Mode]
```
- **Name**: UAQ variable name (e.g., DM.Gas, DM.Brake)
- **Value**: Numeric value to set
- **Duration**: Time in milliseconds (-1 for unlimited, default 2000ms)
- **Mode**: Abs, Off, Fac, AbsRamp, FacRamp (default: Abs)

### Common Commands
```
StartSim                                    # Start simulation
StopSim                                     # Stop simulation
DVARead <Name>                              # Read single value
DVAWrite DM.Gas 0.5 2000 Abs               # Set gas pedal
DVAWrite DM.v.Trgt 27.78 -1 Abs            # Set target speed (100 km/h)
DVAWrite SC.TAccel 0.001 30000 Abs         # Pause simulation
GetSimStatus                                # Get simulation state
```

### Speed Conversions
- 50 km/h = 13.89 m/s
- 60 km/h = 16.67 m/s
- 70 km/h = 19.44 m/s
- 80 km/h = 22.22 m/s
- 100 km/h = 27.78 m/s

## LLM Integration Details

### Trigger Configuration (llm_triggers.json)
```json
{
  "triggers": [
    {
      "name": "speed_over_60kph",
      "condition": "Car_v > 16.67",
      "description": "Speed exceeds 60 km/h"
    }
  ]
}
```

### LLM Response Format
```json
{
  "analysis": "Situation analysis",
  "strategy": "Control strategy explanation",
  "script": "execute_cmd('DVAWrite DM.Gas 0.5 2000 Abs')\nlog('Action taken')"
}
```

### Failsafe Control Functions

These functions maintain commands by repeatedly sending them (heartbeat pattern), ensuring control stops automatically if script fails:

```python
# Maintain command until condition is met (max 30s)
maintain_and_wait_until('DVAWrite DM.v.Trgt 19.44 200 Abs', 'Car_v >= 19.44', 30000)

# Maintain command for specific duration
maintain_for('DVAWrite DM.v.Trgt 13.89 200 Abs', 3000)
```

### Safety Guarantees

1. **Simulation Pause/Resume**: LLM intervention automatically pauses (SC.TAccel=0.001) and resumes (SC.TAccel=1.0) simulation
2. **Finally Block**: try/finally ensures SC.TAccel is restored even on errors
3. **Timeout Protection**: All scripts timeout after 30s
4. **Heartbeat Pattern**: Failsafe functions send commands every 200ms; stops automatically if script fails
5. **Restricted Execution**: __builtins__ removed to prevent import/open/eval

## Known Issues and Solutions

### Data Synchronization (solution_proposal.md)

**Problem**: Sequential DVARead commands can desynchronize when CarMaker responses are delayed (e.g., slow-motion mode), causing "variable shift" where responses arrive out of order.

**Current Mitigation**: Increased timeout from 0.2s to 0.3s in read_essential_quantities() (carmaker_client.py:85)

**Proposed Solution**: Use Tcl Eval batch read for atomic request-response:
```python
# Instead of 13 sequential DVARead commands
# Use: Eval {list $Qu(Time) $Qu(DM.Gas) $Qu(DM.Brake) ...}
# Returns: "10.5 0.0 0.0 ..." (space-separated values)
```

## Development Guidelines

### When Adding New Features

1. **Always use UAQ documentation**: Check `/docs/UAQ_Complete_Reference.md` before adding new quantities
2. **Maintain failsafe principle**: Any autonomous control must have automatic termination
3. **Use condition evaluation syntax**: Remember to use underscores (Car_v) not dots (Car.v)
4. **Test in slow-motion mode**: Use `DVAWrite SC.TAccel 0.001` to verify timing robustness
5. **Log extensively**: Use server.log() for debugging; logs are written to llm_control.log

### Variable Naming Convention

- **CarMaker UAQ names**: Use dots (e.g., Car.v, DM.Gas) for DVARead/DVAWrite commands
- **Condition expressions**: Use underscores (e.g., Car_v, DM_Gas) for eval() conditions
- **Conversion happens automatically** in _evaluate_condition_expr()

### Threading Model

- **GUI thread**: Main tkinter thread (carmaker_gui.py)
- **Monitor thread**: 10Hz polling loop (carmaker_control_server.py:_monitor_loop)
- **LLM monitor thread**: Trigger detection loop (llm_integration.py:_monitor_loop)
- **Socket server thread**: Handles CLI connections (carmaker_control_server.py:_socket_server_loop)

All threads use daemon=True for clean shutdown.

## External Dependencies

- **CarMaker APO**: Requires CarMaker software running with APO interface enabled (port 16660)
- **docs/pycarmaker-master/**: Third-party CarMaker Python library documentation (reference only, not used in codebase)

## File Organization

```
/
├── carmaker_client.py              # Low-level APO client
├── carmaker_control_server.py      # Control server with monitoring
├── carmaker_gui.py                 # Tkinter GUI application
├── cm_cli.py                       # CLI tool
├── carmaker_llm_control.py         # LLM-specific interface
├── llm_integration.py              # LLM layer with trigger system
├── test_llm_integration.py         # Integration tests
├── llm_triggers.json               # Trigger configuration
├── example_commands.txt            # Example batch commands
├── solution_proposal.md            # Data sync issue analysis (Korean)
└── docs/
    ├── Guide.md                    # Usage guide
    ├── UAQ_*.md                    # CarMaker quantity reference
    └── pycarmaker-master/          # Third-party reference (not used in codebase)
        └── examples/               # Example scripts (reference only)
