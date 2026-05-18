# CarMaker Research Automation Plan

Created: 2026-05-15

## Goal

Build an LLM-usable automation loop for CarMaker research using existing IPG
official roads and TestRuns. Map generation is out of scope for this phase.

The intended loop is:

```text
choose official TestRun/map
  -> choose quantities to monitor
  -> LoadTestRun
  -> StartSim
  -> sample telemetry
  -> evaluate trigger or ego-policy condition
  -> execute control command sequence
  -> continue sampling
  -> summarize result
  -> repeat with revised trigger/action/policy
```

## Current Skill Surface

- `workspace/carmaker_llm_scenario_skill/agent/carmaker_command.py`
  - Sends parsed `DVAWrite` commands through the V3 backend.
  - Supports `--resume-time` for trigger-time action after near-pausing with
    `SC.TAccel`.
- `workspace/carmaker_llm_scenario_skill/agent/carmaker_monitor.py`
  - Samples current backend telemetry and direct `SC.State` / `SC.TAccel`.
  - Uses a fixed config for front traffic object fields.
- `workspace/carmaker_llm_scenario_skill/agent/carmaker_trigger_monitor.py`
  - Monitors one condition, slows simulation with `SC.TAccel = 0.0001`, and
    prints a planning snapshot.
- `v3/services/python-api/app/services/carmaker.py`
  - Provides backend connection, fixed telemetry, raw command execution,
    `StartSim`, `StopSim`, and watched traffic objects.
- `v3/services/python-api/app/services/triggers.py`
  - Provides persistent trigger rules and backend-side trigger execution for
    the frontend workflow.

## Gap

The pieces can control a running scenario, but there is no single LLM-facing
workflow that can:

1. discover usable official IPG scenarios,
2. choose one by stable id/tag,
3. load it through CarMaker's official `LoadTestRun` command,
4. choose an arbitrary quantity set for one run,
5. collect a run log,
6. fire one or more trigger/action rules,
7. produce a compact result summary that the next LLM iteration can use.

## Implementation Direction

Add one agent-side research runner instead of widening the V3 UI first:

```text
workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py
```

Responsibilities:

- `catalog`
  - scan official IPG TestRuns under
    `C:\IPG\carmaker\win64-15.0.1\Data\TestRun\Examples`
  - parse TestRun InfoFiles for road, vehicle, traffic count, and short
    description
  - emit a JSON catalog and Markdown report under
    `workspace/carmaker_llm_scenario_skill/reports/research_automation/`
- `run`
  - accept `--testrun Examples/...`
  - accept `--quantities Time,Car.v,Vhcl.sRoad,...`
  - issue `LoadTestRun "<path>"`, `StartSim`, optional `StopSim`
  - sample requested quantities with raw `DVARead`
  - write JSONL samples and Markdown summary
- trigger/action support
  - accept simple trigger conditions such as `Car.v >= 13`
  - on trigger, slow time with `SC.TAccel = 0.0001`
  - execute a parsed command sequence such as
    `DM.Brake = 0.4 | 1200 | Abs`
  - resume normal time before action unless disabled
- fail-closed behavior
  - if connection, load, start, DVARead, trigger action, or state read is
    uncertain, record the failure and stop the run instead of claiming success.

## Initial Official Scenario Set

Use a small allow-list first so the runner is predictable:

- `Examples/BasicFunctions/Traffic/Man_AutonomousJunctions`
- `Examples/BasicFunctions/Traffic/Man_FollowTraj_PedestrianCrossing`
- `Examples/BasicFunctions/Road/Expressway/Cruising_3lanes`
- `Examples/BasicFunctions/Road/Networks/RuralRoad`
- `Examples/BasicFunctions/Road/Surface/Bumps`
- `Examples/VehicleDynamics/Handling/LaneChange_ISO`
- `Examples/VehicleDynamics/Braking/Braking`

The catalog command can scan more broadly, but `run` should warn when a chosen
TestRun is outside the curated set unless `--allow-uncurated` is passed.

## Verification Plan

1. Static compile all touched Python scripts.
2. Dry-run catalog generation from installed CarMaker 15.0.1 files.
3. Dry-run a run plan without contacting CarMaker.
4. Validate command parser behavior for trigger action sequences.
5. If CarMaker/backend is live, run a short smoke on one official TestRun.
   If not live, document that live runtime verification is pending.

## Development Log

- 2026-05-15: Plan created after reading current V3 backend, agent scripts, and
  IPG official ScriptControl examples. Confirmed official commands:
  `LoadTestRun`, `StartSim`, `StopSim`.
- 2026-05-15: Implemented `workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py`.
  - `catalog` scans official CarMaker 15.0.1 TestRun InfoFiles and writes
    `reports/research_automation/official_testrun_catalog.md`.
  - `select` lets an LLM narrow candidates by curated status, tags, and text
    search before choosing a TestRun path.
  - `run --dry-run` prints the exact `LoadTestRun`, `StartSim`, quantity, trigger,
    action, and `StopSim` plan without touching CarMaker.
  - `run` is prepared to call the V3 backend, sample arbitrary `DVARead`
    quantities, fire one trigger, execute one command sequence, and write
    `samples.jsonl` plus `summary.md`.
  - `self-test` validates parser, trigger expression, curated guard, and summary
    generation without requiring CarMaker.
  - Curated TestRuns are enforced by default. Use `--allow-uncurated` only after
    inspecting a candidate.

## LLM Usage Contract

Catalog official scenarios:

```bash
python3 workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py catalog --curated-only
```

Select official scenarios by tags or text:

```bash
python3 workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py select --curated-only --tags traffic,junction
python3 workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py select --curated-only --search pedestrian
```

Dry-run an experiment plan:

```bash
python3 workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py run \
  --testrun Examples/BasicFunctions/Traffic/Man_AutonomousJunctions \
  --quantities Time,Car.v,Vhcl.sRoad,Vhcl.tRoad,DM.Brake,Traffic.nObjs \
  --duration 15 \
  --interval 0.5 \
  --trigger "Car.v >= 10 and Vhcl.sRoad > 50" \
  --action "DM.Brake = 0.3 | 1000 | Abs" \
  --dry-run
```

Run against a live V3 backend and CarMaker APO listener:

```bash
python3 workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py run \
  --backend-url http://127.0.0.1:8010 \
  --connect \
  --testrun Examples/BasicFunctions/Traffic/Man_AutonomousJunctions \
  --quantities Time,Car.v,Vhcl.sRoad,Vhcl.tRoad,DM.Brake,Traffic.nObjs \
  --duration 15 \
  --interval 0.5 \
  --trigger "Car.v >= 10 and Vhcl.sRoad > 50" \
  --action "DM.Brake = 0.3 | 1000 | Abs"
```

Run directly against the CarMaker 15 TcpCmdPort when the V3 backend is not
running:

```bash
python3 workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py run \
  --direct-carmaker \
  --host localhost \
  --port 16660 \
  --testrun Examples/BasicFunctions/Traffic/Man_AutonomousJunctions \
  --quantities Time,Car.v,Vhcl.sRoad,Vhcl.tRoad,DM.Brake,Traffic.nObjs \
  --duration 15 \
  --interval 0.5 \
  --trigger "Car.v >= 10 and Vhcl.sRoad > 50" \
  --action "DM.Brake = 0.3 | 1000 | Abs"
```

Expected output files:

```text
workspace/carmaker_llm_scenario_skill/reports/research_automation/runs/<run_id>/samples.jsonl
workspace/carmaker_llm_scenario_skill/reports/research_automation/runs/<run_id>/summary.md
```

Offline runner self-test:

```bash
python3 workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py self-test
```

## Verification Log

- `python3 -m py_compile workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py workspace/carmaker_llm_scenario_skill/agent/carmaker_command.py workspace/carmaker_llm_scenario_skill/agent/carmaker_state.py`
  passed.
- `python3 workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py catalog --curated-only` produced 7
  curated official TestRun entries.
- `python3 workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py select --curated-only --tags traffic,junction`
  selected `Examples/BasicFunctions/Traffic/Man_AutonomousJunctions`.
- `python3 workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py select --curated-only --search pedestrian`
  selected `Examples/BasicFunctions/Traffic/Man_FollowTraj_PedestrianCrossing`.
- `python3 workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py self-test` passed.
- `run --dry-run` produced the intended Load/Start/Monitor/Trigger/Action/Stop
  plan.
- Missing trigger action fails closed with
  `--trigger requires --action or --action-file`.
- Uncurated TestRun selection fails closed unless `--allow-uncurated` is passed.
- Live backend smoke is pending because `http://127.0.0.1:8010` was not running
  in this session, and the repo-local Python API venv is Windows-only from WSL.
- Follow-up check confirmed the Windows venv can run `uvicorn --version`, but a
  Windows-launched backend was not reachable from this WSL/sandbox session. Live
  CarMaker execution remains an environment-dependent smoke, not a code-path
  blocker.
- Added `--direct-carmaker` so the same runner can execute against CarMaker 15's
  TcpCmdPort directly when the V3 backend is unavailable.
- Live direct smoke passed with CarMaker 15 listening on `localhost:16660`.
  - Run id: `live_direct_smoke_trigger_action`
  - TestRun: `Examples/BasicFunctions/Traffic/Man_AutonomousJunctions`
  - Samples: 9
  - Trigger: `Vhcl.sRoad>=11`
  - Fired sample: 4
  - Action: `DM.Brake = 0.3 | 1000 | Abs`
  - Evidence: `reports/research_automation/runs/live_direct_smoke_trigger_action/summary.md`
    and `samples.jsonl`
  - Observed effect: `DM.Brake` became `0.3` at samples 5-6 and `Car.v`
    dropped from about `13.81 m/s` at trigger sample 4 to about `9.45 m/s`
    by sample 7.
- 2026-05-18: Cleaned up the runner after live verification.
  - Added explicit validation for duration, interval, trigger time-scale, trigger
    duration, and invalid `--direct-carmaker --connect` combinations.
  - Made `--action` and `--action-file` mutually exclusive and fail clearly when
    the action file is missing.
  - Tightened state snapshot handling so uncertain `SC.State` / `SC.TAccel`
    reads stop the run instead of being silently treated as unknown telemetry.
  - Added command path and endpoint to each run summary for direct/backend
    provenance.
- 2026-05-18: Consolidated CarMaker LLM research assets into this workspace.
  - Moved the current agent tools from top-level `agent/` to `agent/` inside
    this workspace.
  - Moved the IPG skill/document source library under
    `references/ipg_skill_library/`.
  - Removed the old top-level `CarMaker_RealtimeControl/` prototype stack from
    the tracked tree; a legacy integration note remains under `references/`.

## Completion Audit

| Requirement | Artifact / evidence | Status |
| --- | --- | --- |
| Use existing IPG official maps, not map generation | Catalog reads `C:\IPG\carmaker\win64-15.0.1\Data\TestRun\Examples`; curated catalog lists official roads such as `UrbanRoad_RuralRoad_Expressway.rd5`, `Expressway_3Lanes.rd5`, and `RuralRoad_Junctions.rd5` | Implemented |
| Scenario/map selection | `catalog` and `select` commands; `official_testrun_catalog.md` | Implemented |
| Desired data selection for monitoring | `run --quantities Time,Car.v,...`; raw `DVARead` quantity list | Implemented |
| Simulation start/result checks | `run` issues `LoadTestRun`, `StartSim`, samples, optional `StopSim`, and writes `summary.md`; live direct smoke `live_direct_smoke_trigger_action` completed | Verified live |
| Trigger setup | `run --trigger "<expr>"` with safe expression evaluation | Implemented |
| Trigger-time control command | `--action` / `--action-file`, `SC.TAccel` near-pause, resume, then `DVAWrite` command sequence; live smoke applied `DM.Brake = 0.3` | Verified live |
| Result confirmation | `samples.jsonl` and `summary.md` per run; `self-test` verifies summary generation; live smoke summary and samples are saved | Verified live |
| Iterative review loop | Run summaries are stable input for the next LLM iteration; rerun with revised TestRun, quantities, trigger, or action | Implemented |
| Development docs | This plan, usage contract, verification log, and catalog Markdown | Implemented |
| Fail-closed behavior | Missing action, uncurated TestRun, missing backend, invalid DVARead, and command/read failures stop with errors | Implemented |
