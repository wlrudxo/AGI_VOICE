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

Installed research TestRun folder:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_MPC_BO
/mnt/e/CarMakerProject/AGI/Data/TestRun/LLM_MPC_BO
```

Installed base TestRun:

```text
LLM_MPC_BO/ICCAS_Slalom18m_Base
E:\CarMakerProject\AGI\Data\TestRun\LLM_MPC_BO\ICCAS_Slalom18m_Base
/mnt/e/CarMakerProject/AGI/Data/TestRun/LLM_MPC_BO/ICCAS_Slalom18m_Base
```

Installed friction variants:

```text
LLM_MPC_BO/ICCAS_Slalom18m_Nominal   Road.Link.0.Friction = 1.0, Driver.Knowl.0.Friction = 1.0
LLM_MPC_BO/ICCAS_Slalom18m_LowMu06   Road.Link.0.Friction = 0.6, Driver.Knowl.0.Friction = 0.6
LLM_MPC_BO/ICCAS_Slalom18m_HarshMu05 Road.Link.0.Friction = 0.5, Driver.Knowl.0.Friction = 0.5
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
- [x] Copied official `Examples/VehicleDynamics/Handling/Slalom18m` into the AGI CarMaker project as `LLM_MPC_BO/ICCAS_Slalom18m_Base`.
- [x] Updated only the copied TestRun `Description` header to mark the ICCAS research source/name.
- [x] Live-load `LLM_MPC_BO/ICCAS_Slalom18m_Base` in CarMaker.
- [x] Confirmed `LLM_MPC_BO/ICCAS_Slalom18m_Base` completes with `SIM_END` under the default IPG driver.
- [x] Created explicit-friction variants in the AGI CarMaker project:
  `ICCAS_Slalom18m_Nominal`, `ICCAS_Slalom18m_LowMu06`, and `ICCAS_Slalom18m_HarshMu05`.
- [x] Live-load `LLM_MPC_BO/ICCAS_Slalom18m_Nominal`.
- [x] Live-load `LLM_MPC_BO/ICCAS_Slalom18m_LowMu06`.
- [x] Live-load `LLM_MPC_BO/ICCAS_Slalom18m_HarshMu05`.
- [x] Added `llm_mpc_bo/scripts/erg_drive_summary.py` for `.erg` / `.erg.info` driving-log summaries.
- [x] Added `llm_mpc_bo/scripts/evaluate_slalom.py` for baseline metric and scalar objective evaluation.
- [x] Added `llm_mpc_bo/scripts/plot_slalom_baseline.py` for x-y trajectory and time-series plots.
- [x] Parsed Nominal, LowMu06, and HarshMu05 `.erg` outputs into JSON/CSV summaries.
- [x] Confirmed added output quantities in latest Base `.erg.info`: `Vhcl.tRoad`, `Vhcl.YawRate`, `Car.Road.Path.DevDist`, `Car.Road.Path.DevAng`, `Car.Road.Route.DevDist`, `Car.Road.Route.DevAng`, `Driver.Lat.dy`, `DM.Steer.AngVel`, and `DM.Steer.AngAcc`.
- [x] Recreated `ICCAS_Slalom18m_Nominal`, `ICCAS_Slalom18m_LowMu06`, and `ICCAS_Slalom18m_HarshMu05` from the updated Base after output-quantity changes.
- [x] Corrected Slalom18m pylon geometry interpretation: `DrvPylon.Param` gives gate center and width, so actual pylon coordinates are `x=s`, `y=latOffset +/- width/2`.
- [x] Added `llm_mpc_bo/docs/slalom18m_pylon_geometry.md` to record the pylon interpretation and examples from the TestRun file.
- [x] Added `llm_mpc_bo/scripts/extract_slalom_pylons.py` output for actual pylon points, not only gate centers.
- [x] Added `llm_mpc_bo/scripts/plot_slalom_pylon_map.py` for pylon-only map visualization.
- [x] Regenerated trajectory and pylon plots using actual pylon coordinates.
- [x] Searched local CarMaker 15.0.1 examples for Slalom, Simulink, steering-control, and MPC connection candidates.
- [x] Added `llm_mpc_bo/docs/carmaker_simulink_slalom_mpc_connection_scan.md` with the Simulink connection scan and recommended path.
- [x] Selected `UserSteer CM4SL` as the first implementation route for Simulink/MPC steering control on the existing Slalom18m scenario.
- [x] Confirmed the effective steering override point in `UserSteer.mdl`.
- [x] Built a successful `Base mu=1.0` trajectory reference table for Simulink lookup.
- [x] Confirmed `Read CM Dict` blocks can be used for real-time CarMaker quantities in Simulink.
- [x] Completed first Simulink closed-loop PD/feedforward smoke test on normal road without road departure.
- [x] Decided the final controller should be a standard slalom MPC; PD is only a signal/override/reference smoke test.

## Current Generated Analysis Artifacts

Pylon geometry note:

```text
llm_mpc_bo/docs/slalom18m_pylon_geometry.md
```

CarMaker-Simulink connection scan:

```text
llm_mpc_bo/docs/carmaker_simulink_slalom_mpc_connection_scan.md
```

Core scripts:

```text
llm_mpc_bo/scripts/erg_drive_summary.py
llm_mpc_bo/scripts/evaluate_slalom.py
llm_mpc_bo/scripts/extract_slalom_pylons.py
llm_mpc_bo/scripts/build_slalom_reference.py
llm_mpc_bo/scripts/plot_slalom_baseline.py
llm_mpc_bo/scripts/plot_slalom_runs.py
llm_mpc_bo/scripts/plot_slalom_pylon_map.py
```

Processed latest baseline data:

```text
llm_mpc_bo/results/processed/base_latest_summary.json
llm_mpc_bo/results/processed/base_latest_drive_log.csv
llm_mpc_bo/results/processed/base_latest_evaluation.json
llm_mpc_bo/results/processed/lowmu06_latest_summary.json
llm_mpc_bo/results/processed/lowmu06_latest_drive_log.csv
llm_mpc_bo/results/processed/lowmu06_latest_evaluation.json
llm_mpc_bo/results/processed/slalom18m_pylons.csv
llm_mpc_bo/results/processed/slalom18m_pylons.json
```

Current figures:

```text
llm_mpc_bo/results/figures/slalom18m_pylon_map.png
llm_mpc_bo/results/figures/slalom18m_xy_baseline_vs_lowmu.png
llm_mpc_bo/results/figures/slalom18m_time_metrics_baseline_vs_lowmu.png
llm_mpc_bo/results/figures/slalom18m_xy_usersteer_mu_sweep.png
llm_mpc_bo/results/figures/slalom18m_time_usersteer_mu_sweep.png
llm_mpc_bo/results/figures/slalom18m_xy_pd_latest_vs_base.png
llm_mpc_bo/results/figures/slalom18m_time_pd_latest_vs_base.png
```

Current interpretation:

- Base `mu=1.0` follows the pylon corridor and completes the scenario.
- LowMu06 `mu=0.6` loses lateral tracking in the slalom section and aborts near the road edge.
- Earlier plots that showed the base trajectory passing through pylons were wrong because they plotted `latOffset` gate centers as pylon positions.
- No ready-made `Slalom + Simulink MPC` example was found locally; the shortest route is to combine the current Slalom18m TestRun with the official `Hockenheim_UserSteer` / `DemoCar_UserSteer_CM4SL` / `UserSteer.mdl` CM4SL example.
- The paper should not claim a novel vehicle-dynamics controller. The controller should be a standard slalom MPC; the research contribution is LLM-assisted BO for tuning under CarMaker-Simulink validation.

## Baseline Smoke Test Evidence

Date: 2026-06-06

CarMaker project:

```text
E:\CarMakerProject\AGI
```

TestRun:

```text
LLM_MPC_BO/ICCAS_Slalom18m_Base
```

SimOutput folder reported by user:

```text
E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260606
/mnt/e/CarMakerProject/AGI/SimOutput/DESKTOP-QHUIRV6/20260606
```

Generated result files:

```text
E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260606\LLM_MPC_BO_ICCAS_Slalom18m_Base_130239.erg
E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260606\LLM_MPC_BO_ICCAS_Slalom18m_Base_130239.erg.info
```

Session log:

```text
E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\Log\DESKTOP-QHUIRV6_20260606_123855.log
/mnt/e/CarMakerProject/AGI/SimOutput/DESKTOP-QHUIRV6/Log/DESKTOP-QHUIRV6_20260606_123855.log
```

Relevant session-log lines:

```text
SIM_START  LLM_MPC_BO/ICCAS_Slalom18m_Base  2026-06-06 13:02:39
Slalom time: 11.415 s
Average Speed: 56.77 km/h
SIM_END    LLM_MPC_BO/ICCAS_Slalom18m_Base  38.026s  517.399m
```

Interpretation:

- The copied TestRun loads and runs inside the AGI CarMaker project.
- The copied TestRun reproduces the official source behavior for the default driver.
- This clears the first scenario-baseline gate.
- Next practical step is to create nominal/low-mu/harsh variants and smoke-test low friction.

## Friction Variant Smoke Test Evidence

Date: 2026-06-06

Session log:

```text
E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\Log\DESKTOP-QHUIRV6_20260606_123855.log
```

Nominal result:

```text
TestRun: LLM_MPC_BO/ICCAS_Slalom18m_Nominal
Status: SIM_END
Slalom time: 11.415 s
Average speed: 56.77 km/h
Duration/distance: 38.026 s, 517.399 m
ERG: E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260606\LLM_MPC_BO_ICCAS_Slalom18m_Nominal_130706.erg
```

LowMu06 result:

```text
TestRun: LLM_MPC_BO/ICCAS_Slalom18m_LowMu06
Status: SIM_ABORT
Failure: Vehicle leaves road at about x=399.894, y=-6.00169 TireNo=1
Duration/distance: 30.627 s, 394.085 m
ERG: E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260606\LLM_MPC_BO_ICCAS_Slalom18m_LowMu06_130842.erg
```

HarshMu05 result:

```text
TestRun: LLM_MPC_BO/ICCAS_Slalom18m_HarshMu05
Status: SIM_ABORT
Failure: Vehicle leaves road at about x=431.265, y=6.00289 TireNo=0
Duration/distance: 33.762 s, 427.013 m
ERG: E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260606\LLM_MPC_BO_ICCAS_Slalom18m_HarshMu05_130814.erg
```

Processed summaries:

```text
llm_mpc_bo/results/processed/nominal_summary.json
llm_mpc_bo/results/processed/nominal_drive_log.csv
llm_mpc_bo/results/processed/lowmu06_summary.json
llm_mpc_bo/results/processed/lowmu06_drive_log.csv
llm_mpc_bo/results/processed/harshmu05_summary.json
llm_mpc_bo/results/processed/harshmu05_drive_log.csv
```

Initial interpretation:

- `mu = 1.0` completes and can serve as sanity baseline.
- `mu = 0.6` fails earlier at about `s = 394 m` with road departure and 5 pylon hits in `.erg.info`.
- `mu = 0.5` also fails, but later at about `s = 427 m` with road departure and 4 pylon hits in `.erg.info`.
- LowMu06 is a strong main optimization target because the default driver fails clearly under a still plausible low-friction condition.
- Pylon hits can be read from `Scratchpad.PylonHit.*` in `.erg.info` and should be included in the objective as a violation count.

Driving-log parser:

```text
llm_mpc_bo/scripts/erg_drive_summary.py
```

Example command:

```bash
python3 llm_mpc_bo/scripts/erg_drive_summary.py \
  /mnt/e/CarMakerProject/AGI/SimOutput/DESKTOP-QHUIRV6/20260606/LLM_MPC_BO_ICCAS_Slalom18m_LowMu06_130842.erg \
  --session-log /mnt/e/CarMakerProject/AGI/SimOutput/DESKTOP-QHUIRV6/Log/DESKTOP-QHUIRV6_20260606_123855.log \
  --json llm_mpc_bo/results/processed/lowmu06_summary.json \
  --csv llm_mpc_bo/results/processed/lowmu06_drive_log.csv \
  --downsample 20
```

## Added Quantity Check

Date: 2026-06-06

Latest checked run:

```text
E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260606\LLM_MPC_BO_ICCAS_Slalom18m_Base_133335.erg
E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260606\LLM_MPC_BO_ICCAS_Slalom18m_Base_133335.erg.info
```

Newly confirmed quantities:

```text
Vhcl.tRoad
Vhcl.YawRate
Car.Road.Path.DevAng
Car.Road.Path.DevDist
Car.Road.Route.DevAng
Car.Road.Route.DevDist
DM.Steer.AngAcc
DM.Steer.AngVel
Driver.Lat.dy
```

Processed output:

```text
llm_mpc_bo/results/processed/base_latest_summary.json
llm_mpc_bo/results/processed/base_latest_drive_log.csv
```

Initial value interpretation from the latest Base run:

```text
Vhcl.tRoad min/max:                 -1.9387 / 1.7506 m
Car.Road.Path.DevDist min/max:      -1.9387 / 1.7506 m
Car.Road.Route.DevDist min/max:     -1.9387 / 1.7506 m
Driver.Lat.dy min/max:              -0.5441 / 0.6220 m
DM.Steer.AngVel min/max:            -13.4073 / 16.3014 rad/s
DM.Steer.AngAcc min/max:            -174.5329 / 174.5329 rad/s^2
```

Interpretation:

- `Vhcl.tRoad`, `Car.Road.Path.DevDist`, and `Car.Road.Route.DevDist` are numerically identical in this straight-route slalom run.
- `Driver.Lat.dy` is not the same as global lateral position; it is the IPG Driver's lateral deviation from desired static course and is likely the best built-in tracking-error candidate for the default Driver.
- For MPC objective work, use `Driver.Lat.dy` when comparing to the built-in driver target, and keep the pylon-derived reference as a transparent geometric alternative.
- `DM.Steer.AngVel` and `DM.Steer.AngAcc` are now available for steering smoothness terms.

After confirming the added output quantities, the three friction variants were recreated from the updated Base TestRun:

```text
LLM_MPC_BO/ICCAS_Slalom18m_Nominal
LLM_MPC_BO/ICCAS_Slalom18m_LowMu06
LLM_MPC_BO/ICCAS_Slalom18m_HarshMu05
```

The intended differences from Base are only:

```text
Description
Road.Link.0.Friction
Driver.Knowl.0.Friction
```

Latest LowMu06 rerun after output-quantity update:

```text
ERG: E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260606\LLM_MPC_BO_ICCAS_Slalom18m_LowMu06_135318.erg
ERG info: E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260606\LLM_MPC_BO_ICCAS_Slalom18m_LowMu06_135318.erg.info
Status: SIM_ABORT
Failure: Vehicle leaves road at about x=399.894, y=-6.00169 TireNo=1
Duration/distance: 30.627 s, 394.085 m
Pylon hits: 5
```

Confirmed latest LowMu06 now includes:

```text
Vhcl.tRoad
Vhcl.YawRate
Car.Road.Path.DevAng
Car.Road.Path.DevDist
Car.Road.Route.DevAng
Car.Road.Route.DevDist
DM.Steer.AngAcc
DM.Steer.AngVel
Driver.Lat.dy
```

Processed latest LowMu06 output:

```text
llm_mpc_bo/results/processed/lowmu06_latest_summary.json
llm_mpc_bo/results/processed/lowmu06_latest_drive_log.csv
```

Latest LowMu06 key values:

```text
abs(Vhcl.tRoad) max:             5.2239 m
abs(Car.Road.Path.DevDist) max:  5.2239 m
abs(Driver.Lat.dy) max:          5.6123 m
abs(DM.Steer.AngVel) max:        26.1799 rad/s
abs(Car.YawRate) max:            0.4831 rad/s
```

## Baseline Evaluation and Plots

Date: 2026-06-06

Evaluation script:

```text
llm_mpc_bo/scripts/evaluate_slalom.py
```

Plot script:

```text
llm_mpc_bo/scripts/plot_slalom_baseline.py
```

Evaluation outputs:

```text
llm_mpc_bo/results/processed/base_latest_evaluation.json
llm_mpc_bo/results/processed/lowmu06_latest_evaluation.json
```

Figure outputs:

```text
llm_mpc_bo/results/figures/slalom18m_xy_baseline_vs_lowmu.png
llm_mpc_bo/results/figures/slalom18m_time_metrics_baseline_vs_lowmu.png
```

Current baseline objective values:

```text
Base mu=1.0:
  status: SIM_END
  RMSE_y: 0.5980 m
  MAX_y: 1.9290 m
  pylon hits: 1
  J_failClosed: 9.3193

LowMu06 mu=0.6:
  status: SIM_ABORT
  RMSE_y: 1.1981 m
  MAX_y: 5.2239 m
  pylon hits: 5
  J_continuous: 55.3447
  J_failClosed: 100.0
```

Interpretation:

- `LowMu06` is a clear failing baseline under the default IPG Driver.
- The x-y plot shows the low-friction vehicle diverging from the successful base trajectory around the middle of the pylon sequence and leaving the road near `x ~= 400 m`.
- The time-series plot shows large path deviation and aggressive steering wheel angle/rate before abort.
- For the first MPC/BO objective, `Car.Road.Path.DevDist` is the preferred tracking-error signal because it is built into CarMaker and matches `Vhcl.tRoad`/`Route.DevDist` for this straight-route scenario.

## UserSteer Mu Sweep Plots

Date: 2026-06-06

Plot script:

```text
llm_mpc_bo/scripts/plot_slalom_runs.py
```

Input runs:

```text
UserSteer mu=1.0:
  E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260606\LLM_MPC_BO_ICCAS_Slalom18m_UserSteer_CM4SL_144759.erg
UserSteer LowMu06:
  E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260606\LLM_MPC_BO_ICCAS_Slalom18m_UserSteer_LowMu06_144832.erg
UserSteer HarshMu05:
  E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260606\LLM_MPC_BO_ICCAS_Slalom18m_UserSteer_HarshMu05_145559.erg
```

Evaluation outputs:

```text
llm_mpc_bo/results/processed/usersteer_cm4sl_latest_evaluation.json
llm_mpc_bo/results/processed/usersteer_lowmu06_latest_evaluation.json
llm_mpc_bo/results/processed/usersteer_harshmu05_latest_evaluation.json
```

Figure outputs:

```text
llm_mpc_bo/results/figures/slalom18m_xy_usersteer_mu_sweep.png
llm_mpc_bo/results/figures/slalom18m_time_usersteer_mu_sweep.png
```

Current UserSteer objective values:

```text
UserSteer mu=1.0:
  status: SIM_END
  pylon hits: 1
  J_failClosed: 9.286

UserSteer LowMu06:
  status: SIM_END
  pylon hits: 6
  J_failClosed: 40.727

UserSteer HarshMu05:
  status: SIM_ABORT
  abort: x=432.92 m, y=6.00208 m
  pylon hits: 6
  J_continuous: 61.703
  J_failClosed: 110.0
```

Interpretation:

- `UserSteer LowMu06` does not leave the road, but it is not a good controller result because it still hits many pylons and slows/deviates heavily.
- `UserSteer HarshMu05` gives a useful hard-failure condition for stress testing MPC/BO because it reaches the positive road edge near the end of the slalom section.

## Simulink Steering Override Point

Date: 2026-06-06

Confirmed in `E:\CarMakerProject\AGI\src_cm4sl\UserSteer.mdl`.

Initial assumption:

```text
CreateBus VhclCtrl output
  -> custom controller
  -> VehicleControlUpd input 2
```

This did not affect final steering, even with `-disablevehiclecontrol`.

Effective override point:

```text
VehicleControlUpd output 3
  -> CreateBus VhclCtrl.Steering
  -> VhclCtrl Steering Ang
  -> VhclCtrl.Steering outport
  -> IPG Vehicle steering input
```

Smoke-test evidence:

```text
Inside CreateBus VhclCtrl.Steering:
  VhclCtrl Steering Ang = 0 * original steering angle
Result:
  vehicle drives straight
```

Decision:

- The first Simulink controller and MPC implementation should override only `VhclCtrl Steering Ang` downstream of `VehicleControlUpd`.
- `VhclCtrl Steering AngVel`, `VhclCtrl Steering AngAcc`, `VhclCtrl Steering Trq`, and `VhclCtrl Steering SteerByTrq` can initially remain pass-through.
- If the MPC angle command causes discontinuity or solver/vehicle issues, set `AngVel` to the discrete derivative of the command and `AngAcc` to zero or a bounded derivative.
- The first controller should be validated with simple gain tests before replacing it with MPC:

```text
Ang_cmd = gain * Ang_original
gain candidates: 0.0, 0.5, 1.0, 1.5, -1.0
```

## Slalom Reference Path for Simulink

Date: 2026-06-06

Decision:

- Use the successful `Base mu=1.0` trajectory as the first MPC reference path.
- Do not directly synthesize the first reference from pylon positions, because the base trajectory is already a feasible pylon-avoiding path and avoids gate-geometry interpretation errors.

Generated by:

```text
llm_mpc_bo/scripts/build_slalom_reference.py
```

Reference files:

```text
llm_mpc_bo/simulink/slalom18m_base_reference.csv
llm_mpc_bo/simulink/init_slalom_reference.m
```

Reference range:

```text
Initial version: s = 280.0 to 505.0 m, 0.5 m step
Current version: s = 0.0 to 525.0 m, 0.5 m step
```

The full-run reference avoids a special controller enable window before the slalom section. The path tracking controller can be applied consistently over the full maneuver, with only low-speed or out-of-range fallback if needed.

MATLAB workspace variables loaded by `init_slalom_reference.m`:

```text
slalom_s_ref      breakpoint vector, Vhcl.sRoad [m]
slalom_t_ref      reference lateral path, Car.Road.Path.DevDist [m]
slalom_psi_ref    reference path heading error profile, Car.Road.Path.DevAng [rad]
slalom_delta_ff   reference steering feedforward, DM.Steer.Ang [rad]
```

Simulink insertion plan:

```text
Read CM Dict: Vhcl.sRoad
Read CM Dict: Car.Road.Path.DevDist
Read CM Dict: Car.Road.Path.DevAng
Read CM Dict: Car.YawRate
Read CM Dict: Car.v

1-D Lookup Table:
  Breakpoints 1 = slalom_s_ref
  Table data    = slalom_t_ref
  Input         = Vhcl.sRoad
  Output        = t_ref

e_t = Car.Road.Path.DevDist - t_ref
```

Optional feedforward:

```text
1-D Lookup Table:
  Breakpoints 1 = slalom_s_ref
  Table data    = slalom_delta_ff
  Input         = Vhcl.sRoad
  Output        = delta_ff
```

First PD smoke-test controller:

```text
delta_cmd = delta_ff - Kt*e_t - Kpsi*Car.Road.Path.DevAng - Kr*Car.YawRate
```

## Standard Controller Scope Decision

Date: 2026-06-06

Decision:

- Use a conventional slalom MPC controller.
- Do not implement or claim 4WS/4WID, game-theoretic coordination, DYC, rear steering, or torque allocation.
- Use external vehicle-dynamics/stability papers only as background support for including yaw-rate, sideslip, steering effort, and low-friction safety metrics in the objective.
- The core paper contribution remains:

```text
CarMaker-Simulink validated MPC tuning
Pure BO vs LLM-assisted BO
Sample efficiency and unsafe-trial reduction under low-friction slalom
```

Initial MPC structure:

```text
Reference:
  Base mu=1.0 successful trajectory

State/error signals:
  e_t   = Car.Road.Path.DevDist - t_ref(s)
  e_psi = Car.Road.Path.DevAng - psi_ref(s)
  r     = Car.YawRate
  v     = Car.v

Input:
  u_mpc = steering-angle correction

Command:
  delta_cmd = delta_ff(s) + u_mpc
```

First MPC should be validated on normal road before low-friction runs:

```text
1. mu=1.0 UserSteer CM4SL: implementation sanity and pylon-hit check.
2. mu=0.6 UserSteer LowMu06: main optimization target.
3. mu=0.5 UserSteer HarshMu05: stress/robustness case.
```

## PD / Feedforward Smoke Test Evidence

Date: 2026-06-06

Latest checked run:

```text
E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260606\LLM_MPC_BO_ICCAS_Slalom18m_UserSteer_CM4SL_163635.erg
```

Processed outputs:

```text
llm_mpc_bo/results/processed/usersteer_pd_latest_summary.json
llm_mpc_bo/results/processed/usersteer_pd_latest_drive_log.csv
llm_mpc_bo/results/processed/usersteer_pd_latest_evaluation.json
llm_mpc_bo/results/figures/slalom18m_xy_pd_latest_vs_base.png
llm_mpc_bo/results/figures/slalom18m_time_pd_latest_vs_base.png
```

Result:

```text
status: completed run, no road departure
duration: 37.98 s
distance: 522.59 m
pylon hits: 4
MAX_y / DevDist: 2.613 m
J_failClosed: 28.502
```

Interpretation:

- The Simulink steering override, `Read CM Dict` inputs, reference lookup, and feedforward/feedback signal flow are functional enough for closed-loop execution.
- The PD/feedforward controller is not intended as the final controller and is not yet competitive with the base driver.
- The latest run follows the same broad slalom trend but has larger late-section deviation and pylon hits.
- Next implementation step is to replace PD with a standard MPC correction controller and validate it first at `mu=1.0`.

## Work Plan

### Phase 1: Research Workspace Setup

- [x] Create `llm_mpc_bo/`.
- [x] Move ICCAS planning documents into `llm_mpc_bo/docs/`.
- [x] Create this durable research progress log.
- [x] Create subfolders for practical work:

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

- [x] Copy or package the official `Slalom18m` TestRun into a research-controlled location.
- [ ] Preserve an unmodified source copy.
- [x] Create a nominal variant with friction `1.0`.
- [x] Create a low-friction variant with friction `0.6`.
- [x] Optionally create a harsh variant with friction `0.5`.
- [x] Load the base copied variant in CarMaker.
- [x] Confirm the default IPG driver can complete the base copied scenario.
- [x] Load the nominal variant in CarMaker.
- [x] Confirm the default IPG driver can complete the nominal variant.
- [x] Load the low-friction variant in CarMaker.
- [x] Confirm whether the default IPG driver can complete the low-friction scenario.
- [x] Confirm LowMu06 fails with road departure, making it usable as the main optimization target.
- [x] Record session-log outcomes for each baseline run.

Key checks:

- Does the TestRun load without missing road/vehicle resources?
- Does the scenario finish with `SIM_END`?
- Does low friction make the task meaningfully harder without making every run fail?
- Are pylon hit, road departure, or lateral instability visible in logs or telemetry?

### Phase 3: Telemetry and Metric Definition

- [x] Determine available UAQ / DVA quantities for the slalom TestRun.
- [x] Confirm exact signal names available in current `.erg.info` for:

```text
Time
Car.v
Vhcl.sRoad
Vhcl.tRoad
Vhcl.YawRate
Car.YawRate
DM.Steer.Ang or steering command equivalent
DM.Steer.AngVel
DM.Steer.AngAcc
Car.SideSlipAngle if available
Car.tx
Car.ty
Car.ax
Car.ay
Steer.WhlAng
Car.muRoadFL/FR/RL/RR
Car.Road.Path.DevDist/DevAng
Car.Road.Route.DevDist/DevAng
Driver.Lat.dy
```

- [x] Decide how to compute lateral tracking error.
- [x] Decide how to detect cone hit / pylon hit / violation.
- [x] Decide how to detect simulation failure.
- [x] Create a first metric extractor.
- [x] Create the scalar objective `J`.

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

- [x] Identify the best Simulink steering/control reference model.
- [x] Confirm MATLAB R2025a + CarMaker 15.0.1 + CM4SL startup path.
- [x] Confirm active Simulink model can run with CarMaker.
- [x] Decide whether to adapt an existing CM4SL model or create a new slalom MPC model.
- [x] Connect CarMaker vehicle/path states to Simulink via `Read CM Dict`.
- [x] Send steering command back from Simulink to CarMaker at the effective `VhclCtrl Steering Ang` override point.
- [x] Confirm one closed-loop slalom run with a fixed non-MPC smoke-test controller.
- [ ] Implement the first standard MPC correction controller.
- [ ] Confirm one closed-loop slalom run with a fixed MPC parameter set on `mu=1.0`.
- [ ] Confirm the same fixed MPC parameter set can run on `mu=0.6`.

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

1. Implement the first standard MPC Controller block in Simulink.
2. Initialize MATLAB workspace with:

```matlab
cd('E:\CarMakerProject\AGI\src_cm4sl')
cmenv
run('E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink\init_slalom_mpc.m')
open_system('UserSteer')
```

3. Connect the MPC block as:

```text
mo  = [Car.Road.Path.DevDist; Car.Road.Path.DevAng; Car.YawRate]
ref = [t_ref(Vhcl.sRoad); psi_ref(Vhcl.sRoad); 0]
mv  = VehicleControlUpd -> CreateBus VhclCtrl.Steering -> VhclCtrl Steering Ang
```

Reference lookup remains:

```text
e_t       = Car.Road.Path.DevDist - t_ref(s)
e_psi     = Car.Road.Path.DevAng - psi_ref(s)
```

The current `mpcobj` initialization uses a linear bicycle lateral model derived
from the local MathWorks lane-following NMPC example:

```text
C:\Users\user\OneDrive\문서\MATLAB\Examples\R2025a\mpc\LaneFollowingUsingNMPCExample
```

Project note:

```text
llm_mpc_bo/docs/matlab_lane_following_example_notes.md
```

Latest MPC block sign check:

```text
2026-06-07 14:10 run
TestRun: LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL
Result: SIM fail at 8.355 s / 44.917 m before slalom
Diagnosis:
  corr(e_t, delta_cmd) = +0.9747
  same-sign fraction e_t * delta_cmd = 1.0
  corr(e_t, steer_manual) = -0.9034
Action:
  flip init_slalom_mpc.m steerSign from -1.0 to +1.0
Evidence:
  llm_mpc_bo/results/processed/sigsOut_latest_analysis/diagnosis.md
```

4. Validate fixed MPC on `LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL` at `mu=1.0`.
5. Save and evaluate the fixed-MPC run with:

```text
llm_mpc_bo/scripts/erg_drive_summary.py
llm_mpc_bo/scripts/evaluate_slalom.py
llm_mpc_bo/scripts/plot_slalom_runs.py
llm_mpc_bo/scripts/analyze_sigsout_mpc.py
```

For quick Simulink signal diagnosis after exporting `sigsOut` CSV files to
`llm_mpc_bo/results/processed/sigsOut_latest`, run:

```bash
python3 llm_mpc_bo/scripts/analyze_sigsout_mpc.py
```

From MATLAB, the current open `UserSteer` model can be simulated and exported
with:

```matlab
run('E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink\run_slalom_mpc_and_export.m')
```

It writes:

```text
llm_mpc_bo/results/processed/sigsOut_latest_analysis/diagnosis.json
llm_mpc_bo/results/processed/sigsOut_latest_analysis/diagnosis.md
```

6. If fixed MPC completes nominal slalom, run the same fixed parameter set on `UserSteer_LowMu06`.
7. Define the final tunable MPC workspace parameters and expose them for BO:

```text
q_y, q_psi, q_r, r_delta, r_d_delta, delta_max_scale
```

8. Build the first manual trial runner for `theta -> CarMaker run -> metrics -> J`.

## Open Questions

- Should fixed MPC directly output full steering, or output only correction around `delta_ff`? Current first implementation: full steering angle from MPC Controller block.
- Which MPC implementation is fastest and most robust in the current MATLAB/Simulink setup: MPC Toolbox block, MATLAB Function with explicit QP, or a simpler constrained LQR-like predictive controller? Current choice: MPC Toolbox block.
- Should BO tune only weights, or include correction saturation/rate limits as part of `delta_max_scale` and `r_d_delta`?
- Should the main paper table use only `mu=0.6`, with `mu=1.0` and `mu=0.5` as sanity/stress auxiliary results? Current recommendation: yes.
- How should unsafe trials be counted: pylon hits only, road departure only, or combined pylon/road/saturation failure score? Current recommendation: combined objective with hard-fail road departure.

## Addendum: Results.mat + ERG Objective Path

Date: 2026-06-07

The preferred run-analysis path changed from `sigsOut_latest` to Simulink
`To File` output:

```text
E:\CarMakerProject\AGI\src_cm4sl\Results.mat
```

Reason:

- `sigsOut_latest` can become a 1-sample/0-second export when MATLAB/Simulink
  is driven from a non-interactive path.
- `Results.mat` contains full-run timeseries and matches the CarMaker ERG.

Implemented script:

```text
llm_mpc_bo/scripts/analyze_results_mat.m
```

Behavior:

- Loads `data` from `Results.mat`.
- Accepts `delta_cmd`, `applied_delta_cmd`, or `signal1` as the logged steering command.
- Defaults to treating the logged command as the applied Gain(-1)-corrected steering command.
- Supports old pre-Gain files with `deltaCmdMode = 'pre_gain'`.
- Aligns signals to the `s` timeseries time base.
- Computes tracking, heading, yaw-rate, steering, steering-rate metrics.
- Automatically finds the latest matching CarMaker ERG for
  `LLM_MPC_BO_ICCAS_Slalom18m_UserSteer_CM4SL`.
- Runs `erg_drive_summary.py` to get pylon hits and SIM_END/SIM_ABORT status.
- Computes the BO objective as `summary.objective.JFailClosed`.

Current latest analysis:

```text
Status: SIM_END
Duration: 37.918 s
Final s: 525.456 m
Signal mapping: signal1 -> applied delta_cmd
Applied sign issue: false
RMSE e_t: 0.7536 m
MAX |e_t|: 2.6615 m
RMSE delta: 0.1748 rad
RMSE delta rate: 0.4586 rad/s
MAX |yawrate|: 0.1378 rad/s
Pylon hits: 10
BO J_failClosed: 52.9702
```

Interpretation:

- The Gain(-1) sign correction is correct when evaluating the applied command.
- The nominal/UserSteer CM4SL MPC completes the scenario.
- Performance is not yet acceptable because it hits 10 pylons.
- Next work is MPC tuning and reference/weight/rate-limit adjustment, not
  another steering-sign change.
