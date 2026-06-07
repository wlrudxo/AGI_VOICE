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
+ CarMaker Slalom18m/UserSteer standard scenario
+ LHC/random vs BO vs LLM-only vs Hybrid BO tuning
```

Do not switch to CARLA, CasADi, or a custom MPC solver unless explicitly asked.
Do not make LQR/PD the main controller. PD/LQR are only smoke-test/fallback
controllers.

LowMu/icy-road variants are stress-test or future-work extensions, not the main
benchmark for the current formal tuning run.

Do not add reinforcement learning as a main comparison group for the first
paper. The current experiment is static 5D MPC-weight tuning, not state-action
policy learning, and a 100-run budget is too small for a fair RL baseline.

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
MPC mv output -> Gain block -> VhclCtrl Steering Ang
```

Latest verified state: the user changed this Gain block to `1`, and the
vehicle completed the run. Do not add a second sign flip in MATLAB/Python.
If the vehicle aborts early again, check this block and the sign diagnosis from
`analyze_results_mat.m` before changing MPC weights.

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

Initial/default `mpcobj` from `init_slalom_mpc.m`:

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

Current convention after steering command scale correction:

```text
MPC output delta_cmd = VhclCtrl.Steering.Ang [rad]
Simulink steering Gain = 1
MPC plant input gain is scaled in init_slalom_mpc.m
```

Current checked tuned set:

```text
Weights.OutputVariables = [30, 10, 0.5]
Weights.ManipulatedVariables = 0.05
Weights.ManipulatedVariablesRate = 0.5
MV.Min = -12
MV.Max = 12
MV.RateMin = -0.6
MV.RateMax = 0.6
```

## Preferred Native Run Procedure

For the current tuning workflow, prefer the shared MATLAB/CarMaker loop
documented in:

```text
llm_mpc_bo/docs/shared_matlab_carmaker_tuning_workflow.md
```

The important rule is: keep MATLAB, Simulink, and CarMaker GUI open; do not
relaunch for every trial. Load the TestRun only when the GUI is blank or on the
wrong run, then update `mpcobj` in the existing MATLAB base workspace and run
`sim('UserSteer')`.

### Fresh MATLAB Fallback

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

The current model logs the applied steering command as `signal1`;
`analyze_results_mat.m` maps this automatically. As of the latest verified
run, the Simulink steering Gain block is `1`.

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

Later correction after live shared-session testing:

```text
The user changed the Simulink Gain block from -1 to 1.
The MPC plant input gain was corrected so delta_cmd is steering wheel angle.
With Gain=1 and params [30, 10, 0.5, 0.05, 0.5]:
Status: SIM_END
J: 53.9036
Pylon hits: 5
RMSE e_t: 0.4972 m
MAX |e_t|: 2.2070 m
Applied sign issue: false
```

Latest automated BO smoke/formalization result:

```text
Experiment dir: llm_mpc_bo/results/experiments/standard_slalom_bo_seed7
Completed trials: 12
Best run: bo_0010
Status: SIM_END
J: 2.1349
Pylon hits: 0
RMSE e_t: 0.2603 m
MAX |e_t|: 0.9529 m
Best params:
  q_y = 42.7413
  q_psi = 79.8466
  q_r = 15.1523
  r_delta = 0.5276
  r_d_delta = 0.9608
```

Interpretation:

- The current verified steering sign is `Gain=1`, not an added software sign
  flip.
- The nominal/UserSteer CM4SL run completes in the shared-session workflow.
- Tracking quality remains poor because it still hits 5 pylons.
- Next work should tune only the five MPC weights around the current best set:
  `q_y, q_psi, q_r, r_delta, r_d_delta`.

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

1. Keep `Results.mat` logging active with the applied `delta_cmd`.
2. Use `analyze_results_mat.m` after each run and use `summary.objective.JFailClosed` as the BO objective.
3. Use the shared MATLAB workflow instead of launching a new MATLAB per trial.
4. Tune manually enough to reduce pylon hits on the nominal controller.
5. Expose BO variables:

```text
q_y, q_psi, q_r, r_delta, r_d_delta
```

6. Build the trial runner:

```text
theta -> update mpcobj -> run Simulink/CarMaker -> export -> evaluate J
```

7. For repeatable optimization runs, use:

```text
llm_mpc_bo/scripts/mpc_trial_cli.py       one evaluated trial
llm_mpc_bo/scripts/mpc_experiment_cli.py  resumable LHC/random/BO loop
```

The same `--experiment-dir` is the optimization state. It contains
`optimizer_config.json`, `trials.jsonl`, `candidates.jsonl`,
`best_summary.json`, deterministic LHC/random candidate plans, and per-trial
summaries. Reusing the directory continues from the next missing iteration. BO
rereads `trials.jsonl` after each trial before proposing the next candidate.

Main 5D experiment design:

```text
BO: 100 total trials = 30 LHC initialization + 70 BO/EI
LHC/random baselines: 100 trials each
Use one fixed seed per repeated experiment and a separate directory per method/seed.
```
