# Native Windows Agent Handoff

Updated: 2026-06-07

## Role

This document is for a Windows-native AI/agent continuing the CarMaker-Simulink
MPC work from the current state.

Run CarMaker, MATLAB, and Simulink from Windows-native MATLAB. Use WSL/Codex
only for file inspection, Python analysis, plotting, git, and documentation.

## Research Direction

Keep the current direction:

```text
standard Simulink MPC Controller block
+ CarMaker Slalom18m low-friction scenario
+ BO vs LLM-assisted BO tuning
```

Do not switch to CARLA, CasADi, or a custom MPC solver unless explicitly asked.
Do not make LQR/PD the main controller. PD/LQR are only smoke-test/fallback
controllers.

## Key Paths

Repository:

```text
E:\GitProject\AGI_VOICE
```

Research workspace:

```text
E:\GitProject\AGI_VOICE\llm_mpc_bo
```

CarMaker project:

```text
E:\CarMakerProject\AGI
E:\CarMakerProject\AGI\src_cm4sl
```

CarMaker install:

```text
C:\IPG\carmaker\win64-15.0.1
```

Simulink model:

```text
E:\CarMakerProject\AGI\src_cm4sl\UserSteer.mdl
```

Current TestRun:

```text
LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL
```

## Current Simulink Wiring

MPC Controller block:

```text
Controller object: mpcobj
```

Inputs:

```text
mo  = [Car.Road.Path.DevDist; Car.Road.Path.DevAng; Car.YawRate]
ref = [t_ref; psi_ref; 0]
```

Reference lookup:

```text
t_ref   = 1-D Lookup Table(s=Vhcl.sRoad, breakpoints=slalom_s_ref, table=slalom_t_ref)
psi_ref = 1-D Lookup Table(s=Vhcl.sRoad, breakpoints=slalom_s_ref, table=slalom_psi_ref)
```

Output:

```text
MPC mv output -> Gain(-1) -> VhclCtrl Steering Ang
```

The `Gain(-1)` is important. Without it, the vehicle diverged before the
slalom section because `e_t` and `delta_cmd` had the same sign.

Effective steering override location:

```text
VehicleControlUpd output
  -> CreateBus VhclCtrl.Steering
  -> VhclCtrl Steering Ang
```

## Required Workspace Variables

`init_slalom_mpc.m` creates:

```text
slalom_s_ref
slalom_t_ref
slalom_psi_ref
slalom_delta_ff
mpcobj
```

Current `mpcobj`:

```text
Ts = 0.02
PredictionHorizon = 40
ControlHorizon = 8
MV.Min = -2
MV.Max = 2
MV.RateMin = -0.03
MV.RateMax = 0.03
Weights.OutputVariables = [5, 2, 0.2]
Weights.ManipulatedVariables = 0.2
Weights.ManipulatedVariablesRate = 2
```

## Preferred Native Run Procedure

In Windows MATLAB Desktop:

```matlab
cd('E:\CarMakerProject\AGI\src_cm4sl')
cmenv
run('E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink\init_slalom_mpc.m')
open_system('UserSteer')
run('E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink\run_slalom_mpc_batch.m')
```

`run_slalom_mpc_batch.m` is intended to work from a fresh MATLAB workspace. It
does:

```text
cd E:\CarMakerProject\AGI\src_cm4sl
cmenv
run init_slalom_mpc.m
open UserSteer
run/export
```

The `.bat` launcher is optional:

```text
E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink\run_slalom_mpc_batch.bat
```

It launches MATLAB Desktop with `-r`, not `-batch`, because CarMaker/Simulink
can create GUI dialogs that break non-interactive `-batch` runs.

## Expected Output Files

Current preferred Simulink diagnostic file:

```text
E:\CarMakerProject\AGI\src_cm4sl\Results.mat
```

`Results.mat` should contain timeseries under variable `data`, with:

```text
s
t
t_ref
devang
psi_ref
yawrate
v
steer_manual
delta_cmd or applied_delta_cmd or signal1
```

The current model logs the applied Gain(-1)-corrected steering command as
`signal1`; `analyze_results_mat.m` maps this automatically.

Processed analysis outputs:

```text
E:\GitProject\AGI_VOICE\llm_mpc_bo\results\processed\results_mat_latest\summary.json
E:\GitProject\AGI_VOICE\llm_mpc_bo\results\processed\results_mat_latest\summary.md
E:\GitProject\AGI_VOICE\llm_mpc_bo\results\processed\results_mat_latest\aligned_signals.csv
E:\GitProject\AGI_VOICE\llm_mpc_bo\results\processed\results_mat_latest\time_signals.png
E:\GitProject\AGI_VOICE\llm_mpc_bo\results\processed\results_mat_latest\sroad_tracking.png
E:\GitProject\AGI_VOICE\llm_mpc_bo\results\processed\results_mat_latest\latest_erg_summary.json
E:\GitProject\AGI_VOICE\llm_mpc_bo\results\processed\results_mat_latest\latest_erg_drive_log.csv
```

CarMaker ERG outputs:

```text
E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6\20260607
```

Session summary log:

```text
E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6.log
```

## Known Recent Results

Before `Gain(-1)`:

```text
2026-06-07 14:10
TestRun: LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL
Result: fail before slalom, 8.355 s / 44.917 m
diagnosis: sign issue
```

After a subsequent run attempt from a new MATLAB session, the CarMaker log
showed:

```text
2026-06-07 14:11
SIM ... LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL 0 37.916 517.263
```

However, that run did not produce a fresh `sigsOut_latest` export because the
batch workspace/logging setup was incomplete at that time. The batch script has
now been updated to load all required workspace variables and to avoid deleting
old CSV files before a valid new `sigsOut` dataset exists.

Latest `Results.mat` + latest ERG analysis showed:

```text
Generated: 2026-06-07 15:03
Status: SIM_END
Duration: 37.918 s
Final s: 525.456 m
Signal mapping: signal1 -> applied delta_cmd
Applied sign issue: false
RMSE e_t: 0.7536 m
MAX |e_t|: 2.6615 m
Pylon hits: 10
BO J_failClosed: 52.9702
```

Interpretation:

- The applied Gain(-1) sign path is correct.
- The nominal/UserSteer CM4SL run completes.
- Tracking quality remains poor for slalom because it hits 10 pylons.
- Next work should tune MPC weights/rate limits and reference behavior, not
  flip steering sign again.

## If `sigsOut` Is Missing

Check these in the open Simulink model:

1. Required signals are marked for logging:

```text
delta_cmd
s
t
t_ref
devang
psi_ref
yawrate
v
steer_manual
```

2. Model parameters:

```matlab
set_param('UserSteer', 'SignalLogging', 'on')
set_param('UserSteer', 'SignalLoggingName', 'sigsOut')
set_param('UserSteer', 'ReturnWorkspaceOutputs', 'on')
```

3. After `sim`, verify:

```matlab
whos
sigsOut
simOut
```

If `logsout` exists instead of `sigsOut`, `run_slalom_mpc_and_export.m` should
also accept it.

## Analysis Commands

Preferred MATLAB analysis after a run:

```matlab
addpath('E:\GitProject\AGI_VOICE\llm_mpc_bo\scripts')
summary = analyze_results_mat( ...
    'E:\CarMakerProject\AGI\src_cm4sl\Results.mat', ...
    'E:\GitProject\AGI_VOICE\llm_mpc_bo\results\processed\results_mat_latest' ...
);
J = summary.objective.JFailClosed;
```

The script automatically finds the latest matching ERG under:

```text
E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6
```

and runs:

```text
llm_mpc_bo/scripts/erg_drive_summary.py
```

## Next Work

1. Keep `Results.mat` logging active with applied `delta_cmd` after Gain(-1).
2. Use `analyze_results_mat.m` after each run and use `summary.objective.JFailClosed` as the BO objective.
3. Run the same fixed MPC on `UserSteer_LowMu06`.
4. Tune manually enough to get a reasonable nominal controller.
5. Expose BO variables:

```text
q_y, q_psi, q_r, r_delta, r_d_delta, delta_max_scale
```

6. Build the trial runner:

```text
theta -> update mpcobj -> run Simulink/CarMaker -> export -> evaluate J
```
