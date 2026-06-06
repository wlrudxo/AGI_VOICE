# LLM-MPC-BO ICCAS Research Progress Log

Created: 2026-06-06

## Purpose

This folder tracks the practical research work for an ICCAS 6-page paper on:

> LLM-assisted Bayesian optimization for MPC lateral-controller tuning in a CarMaker-Simulink low-friction slalom scenario.

The intended paper claim is conservative:

- MPC remains the controller.
- CarMaker-Simulink remains the simulator/validator.
- Bayesian optimization selects simulator-validated candidates.
- The LLM only provides warm-start candidates and bounded search-region guidance.

## Repository Location

Project root:

```text
E:\GitProject\AGI_VOICE
/mnt/e/GitProject/AGI_VOICE
```

Research workspace:

```text
E:\GitProject\AGI_VOICE\llm_mpc_bo
/mnt/e/GitProject/AGI_VOICE/llm_mpc_bo
```

Do not put this research work under `workspace/`. The existing scenario skill remains under `workspace/` and is used as a helper only.

## Reference Documents

Moved into this folder:

```text
llm_mpc_bo/docs/iccas_slalom_mpc_llm_bo_plan.md
llm_mpc_bo/docs/iccas_6p_carmaker_llm_research_ideas.md
```

Primary implementation plan:

```text
llm_mpc_bo/docs/iccas_slalom_mpc_llm_bo_plan.md
```

Broader topic alternatives and fallback claims:

```text
llm_mpc_bo/docs/iccas_6p_carmaker_llm_research_ideas.md
```

## Helper Skill / Existing Automation Asset

Existing CarMaker helper asset:

```text
E:\GitProject\AGI_VOICE\workspace\carmaker_llm_scenario_skill
/mnt/e/GitProject/AGI_VOICE/workspace/carmaker_llm_scenario_skill
```

Use this as a helper for:

- official CarMaker TestRun catalog scanning,
- `LoadTestRun`, `StartSim`, `StopSim`,
- `DVARead` / `DVAWrite`,
- telemetry snapshots,
- trigger/action smoke tests,
- CarMaker session-log triage.

Relevant files:

```text
workspace/carmaker_llm_scenario_skill/README.md
workspace/carmaker_llm_scenario_skill/research_automation_plan.md
workspace/carmaker_llm_scenario_skill/agent/carmaker_research_runner.py
```

Known CarMaker project for live automation:

```text
E:\CarMakerProject\AGI
/mnt/e/CarMakerProject/AGI
```

Known CarMaker TCP command port from that project:

```text
16660
```

Known session-log folder:

```text
E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\Log
/mnt/e/CarMakerProject/AGI/SimOutput/DESKTOP-QHUIRV6/Log
```

## Installed CarMaker Example Source

Official example TestRun root:

```text
C:\IPG\carmaker\win64-15.0.1\Data\TestRun\Examples
/mnt/c/IPG/carmaker/win64-15.0.1/Data/TestRun/Examples
```

Relevant scenario candidates found:

```text
Examples/VehicleDynamics/Handling/Slalom18m
Examples/VehicleDynamics/Handling/Slalom18m_AMS
Examples/VehicleDynamics/Handling/Slalom36m
Examples/BasicFunctions/Simulink/LaneChange_ISO_ESP
Examples/BasicFunctions/Simulink/Hockenheim_UserSteer
```

Current scenario choice:

```text
Main: Examples/VehicleDynamics/Handling/Slalom18m
Fallback/reference: Examples/VehicleDynamics/Handling/Slalom18m_AMS
Auxiliary harsh/high-speed candidate: Examples/VehicleDynamics/Handling/Slalom36m
Simulink reference candidate: Examples/BasicFunctions/Simulink/LaneChange_ISO_ESP
```

Why `Slalom18m` is the main candidate:

- It is an official CarMaker vehicle-dynamics slalom TestRun.
- Description says `Closed loop slalom driving with pylons gap of 18 m`.
- It uses `Examples/DemoCar`.
- Road length is `600 m`.
- Slalom section is around `s = 300 m` onward.
- End condition is `s > 485`.
- Default driver cruising speed is `58 km/h`.
- Current friction knowledge key is `Driver.Knowl.0.Friction = 1.0`.

Low-friction implementation hint found in official examples:

```text
Road.Link.0.Friction = 0.5
```

Example source where that pattern appears:

```text
Examples/BasicFunctions/Simulink/TractCtrl
```

Initial intended friction variants:

```text
Nominal: Road.Link.0.Friction = 1.0
LowMu main: Road.Link.0.Friction = 0.6
Harsh auxiliary: Road.Link.0.Friction = 0.5
```

## Current Status

- [x] Read the broad ICCAS research-ideas document.
- [x] Read the slalom MPC LLM-BO implementation-plan document.
- [x] Decided that the practical implementation should follow `iccas_slalom_mpc_llm_bo_plan.md`.
- [x] Inspected official CarMaker example TestRuns under CarMaker 15.0.1.
- [x] Found direct slalom candidates.
- [x] Selected `Examples/VehicleDynamics/Handling/Slalom18m` as the main scenario candidate.
- [x] Identified `Road.Link.0.Friction` as the simplest likely low-friction TestRun edit.
- [x] Created the `llm_mpc_bo/` research folder at the AGI_VOICE repo root.
- [x] Moved both ICCAS planning documents from `docs/` into `llm_mpc_bo/docs/`.
- [x] Created this progress log.

## Work Plan

### Phase 1: Research Workspace Setup

- [x] Create `llm_mpc_bo/`.
- [x] Move ICCAS planning documents into `llm_mpc_bo/docs/`.
- [x] Create this durable research progress log.
- [ ] Create subfolders for practical work:

```text
llm_mpc_bo/carmaker/
llm_mpc_bo/carmaker/testruns/
llm_mpc_bo/simulink/
llm_mpc_bo/scripts/
llm_mpc_bo/scripts/bo/
llm_mpc_bo/scripts/llm/
llm_mpc_bo/results/
llm_mpc_bo/results/raw/
llm_mpc_bo/results/processed/
llm_mpc_bo/results/figures/
llm_mpc_bo/paper/
```

### Phase 2: CarMaker Scenario Baseline

- [ ] Copy or package the official `Slalom18m` TestRun into a research-controlled location.
- [ ] Preserve an unmodified source copy.
- [ ] Create a nominal variant with friction `1.0`.
- [ ] Create a low-friction variant with friction `0.6`.
- [ ] Optionally create a harsh variant with friction `0.5`.
- [ ] Load the nominal variant in CarMaker.
- [ ] Confirm the default IPG driver can complete the scenario.
- [ ] Load the low-friction variant in CarMaker.
- [ ] Confirm whether the default IPG driver can complete the low-friction scenario.
- [ ] Record session-log outcomes for each baseline run.

Key checks:

- Does the TestRun load without missing road/vehicle resources?
- Does the scenario finish with `SIM_END`?
- Does low friction make the task meaningfully harder without making every run fail?
- Are pylon hit, road departure, or lateral instability visible in logs or telemetry?

### Phase 3: Telemetry and Metric Definition

- [ ] Determine available UAQ / DVA quantities for the slalom TestRun.
- [ ] Confirm exact signal names for:

```text
Time
Car.v
Vhcl.sRoad
Vhcl.tRoad
Car.YawRate
DM.Steer.Ang or steering command equivalent
Car.SideSlipAngle if available
```

- [ ] Decide how to compute lateral tracking error.
- [ ] Decide how to detect cone hit / pylon hit / violation.
- [ ] Decide how to detect simulation failure.
- [ ] Create a first metric extractor.
- [ ] Create the scalar objective `J`.

Initial objective from the plan:

```text
J =
  1.00 * RMSE_y / 0.50
+ 0.60 * MAX_y / 1.50
+ 0.20 * RMSE_delta / 0.20
+ 0.30 * RMSE_d_delta / 0.80
+ 0.30 * MAX_yaw_rate / 0.80
+ 5.00 * N_violation
+ 20.0 * I_crash_or_sim_fail
```

Hard-fail fallback:

```text
J = 50 + 10 * N_violation
```

### Phase 4: CarMaker-Simulink MPC Connection

- [ ] Identify the best Simulink steering/control reference model.
- [ ] Confirm MATLAB R2025a + CarMaker 15.0.1 + CM4SL startup path.
- [ ] Confirm active Simulink model can run with CarMaker.
- [ ] Decide whether to adapt an existing CM4SL model or create a new slalom MPC model.
- [ ] Connect CarMaker vehicle/path states to Simulink MPC.
- [ ] Send steering command back from Simulink to CarMaker.
- [ ] Confirm one closed-loop slalom run with a fixed MPC parameter set.

Known CM4SL setup reference from the helper skill:

```matlab
addpath('C:\IPG\carmaker\win64-15.0.1\Matlab')
addpath('C:\IPG\carmaker\win64-15.0.1\Matlab\R2025a')
addpath('C:\IPG\carmaker\win64-15.0.1\CM4SL\R2025a')

cd('E:\CarMakerProject\AGI\src_cm4sl')
cmenv
```

### Phase 5: Tunable Parameter Interface

- [ ] Expose the first 6 MPC tuning variables:

```text
q_y
q_psi
q_r
r_delta
r_d_delta
delta_max_scale
```

- [ ] Keep horizon variables out of the first implementation.
- [ ] Implement normalized `[0, 1]` to physical-parameter decoding.
- [ ] Support log-scale decoding for weight variables.
- [ ] Confirm `theta` can be injected before each simulation run.
- [ ] Confirm repeated runs use the newly injected parameters.

Initial parameter ranges:

```text
q_y:              0.1 - 100    log
q_psi:            0.1 - 100    log
q_r:              0.01 - 30    log
r_delta:          0.01 - 10    log
r_d_delta:        0.01 - 10    log
delta_max_scale:  0.6 - 1.2    linear
```

### Phase 6: Trial Runner

- [ ] Implement `theta -> run -> log -> metrics -> J`.
- [ ] Store every trial result as machine-readable JSON/CSV.
- [ ] Store raw run metadata and failure reason.
- [ ] Ensure fail-closed behavior for uncertain runs.
- [ ] Run a small manual sweep to verify repeatability.

Minimum trial output fields:

```text
run_id
method
seed
trial_index
normalized_x
decoded_theta
raw_metrics
objective_J
fail_reason
testrun
friction
timestamp
```

### Phase 7: Manual Baseline and Pure BO

- [ ] Record manual/default MPC baseline.
- [ ] Implement Latin Hypercube Sampling.
- [ ] Implement GP surrogate.
- [ ] Implement Expected Improvement acquisition.
- [ ] Run pure BO:

```text
10 LHS initial evaluations
30 BO/EI evaluations
40 total evaluations
```

- [ ] Save best-so-far objective curve.
- [ ] Save best pure-BO parameter set and metrics.

### Phase 8: LLM-Assisted BO

- [ ] Implement LLM warm-start prompt.
- [ ] Validate LLM JSON output against schema and bounds.
- [ ] Use 4 LLM warm-start candidates + 6 LHS candidates.
- [ ] Run 30 BO/EI evaluations after the initial 10.
- [ ] Optionally implement LLM intervention after iterations 10, 20, and 30.
- [ ] Use LLM intervention only as bounded search-region guidance.
- [ ] Keep EI/BO responsible for final candidate choice.

Initial LLM intervention output shape:

```json
{
  "diagnosis": "short failure analysis",
  "promisingRegion": {
    "q_y": [0.2, 0.8],
    "q_psi": [0.2, 0.9],
    "q_r": [0.1, 0.7],
    "r_delta": [0.2, 0.8],
    "r_d_delta": [0.3, 1.0],
    "delta_max_scale": [0.6, 1.0]
  },
  "avoidRegionReason": "short text",
  "confidence": 0.7
}
```

### Phase 9: Paper Artifacts

- [ ] Generate convergence plot.
- [ ] Generate method comparison table.
- [ ] Generate trajectory comparison plot.
- [ ] Generate lateral error time-series plot.
- [ ] Generate steering command time-series plot.
- [ ] Generate yaw-rate time-series plot.
- [ ] Save best parameter table.
- [ ] Draft architecture figure.
- [ ] Draft optimization flow figure.

Minimum comparison:

```text
Manual baseline
Pure BO
LLM-assisted BO
```

Preferred result claims if data supports them:

- LLM-assisted BO improves early-stage sample efficiency.
- LLM-assisted BO reduces unsafe/aggressive repeated trials.
- Final best performance may be similar to pure BO; sample efficiency is the safer claim.

## Immediate Next Actions

1. Create the practical subfolder skeleton under `llm_mpc_bo/`.
2. Copy `Slalom18m` into `llm_mpc_bo/carmaker/testruns/` as a preserved source reference.
3. Create nominal/low-mu/harsh edited variants.
4. Use the helper skill or CarMaker GUI to load and smoke-test the nominal and low-mu TestRuns.
5. Record session-log evidence in this document after each smoke test.

## Open Questions

- Should the copied TestRun live only inside this repo, or should it also be installed into `E:\CarMakerProject\AGI\Data\TestRun\...` for live execution?
- Which Simulink model is the best starting point for steering/MPC control?
- Which signal should be the authoritative lateral error for `J`: `Vhcl.tRoad`, a reference path error from Simulink, or a postprocessed pylon/path reference?
- Can cone/pylon hits be detected from session log, scratchpad notes, collision sensors, or a dedicated UAQ quantity?
- Should the first paper experiment use only `Slalom18m` at `mu = 0.6`, or include nominal/harsh as auxiliary results?
