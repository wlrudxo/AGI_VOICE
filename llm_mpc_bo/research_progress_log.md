# LLM-MPC-BO Research Progress Log

Updated: 2026-06-07

## Research Direction

Paper target:

```text
LLM-assisted Bayesian optimization for standard MPC lateral-controller tuning
in a CarMaker-Simulink low-friction Slalom18m scenario.
```

Current decision:

- Use **MPC Controller block** as the final controller implementation route.
- Use PD/LQR only as prior smoke tests or fallback baselines, not as the main controller.
- Do not claim novelty in vehicle dynamics or MPC formulation.
- Main claim should be BO/LLM-assisted BO tuning efficiency and safer simulator trial selection.

Detailed old debug log was archived to:

```text
llm_mpc_bo/docs/research_progress_log_detailed_archive_20260607.md
```

## Key Paths

Repository:

```text
E:\GitProject\AGI_VOICE
/mnt/e/GitProject/AGI_VOICE
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

Current Simulink model:

```text
E:\CarMakerProject\AGI\src_cm4sl\UserSteer.mdl
```

## Current TestRuns

Base and non-Simulink variants:

```text
LLM_MPC_BO/ICCAS_Slalom18m_Base
LLM_MPC_BO/ICCAS_Slalom18m_Nominal
LLM_MPC_BO/ICCAS_Slalom18m_LowMu06
LLM_MPC_BO/ICCAS_Slalom18m_HarshMu05
```

CM4SL/UserSteer variants:

```text
LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL
LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_Nominal
LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu06
LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_HarshMu05
```

## Implemented Artifacts

Reference and MPC setup:

```text
llm_mpc_bo/simulink/slalom18m_base_reference.csv
llm_mpc_bo/simulink/init_slalom_reference.m
llm_mpc_bo/simulink/init_slalom_mpc.m
llm_mpc_bo/simulink/run_slalom_mpc_and_export.m
llm_mpc_bo/simulink/run_slalom_mpc_batch.m
```

Analysis scripts:

```text
llm_mpc_bo/scripts/erg_drive_summary.py
llm_mpc_bo/scripts/evaluate_slalom.py
llm_mpc_bo/scripts/plot_slalom_baseline.py
llm_mpc_bo/scripts/plot_slalom_runs.py
llm_mpc_bo/scripts/extract_slalom_pylons.py
llm_mpc_bo/scripts/plot_slalom_pylon_map.py
llm_mpc_bo/scripts/build_slalom_reference.py
llm_mpc_bo/scripts/analyze_sigsout_mpc.py
llm_mpc_bo/scripts/analyze_results_mat.m
```

Important notes:

```text
llm_mpc_bo/docs/slalom18m_pylon_geometry.md
llm_mpc_bo/docs/carmaker_simulink_slalom_mpc_connection_scan.md
llm_mpc_bo/docs/matlab_lane_following_example_notes.md
llm_mpc_bo/docs/native_windows_agent_handoff.md
```

## Execution Environment Decision

Use Windows-native MATLAB for all CarMaker/Simulink execution.

Recommended split:

```text
Windows MATLAB:
  run CarMaker/Simulink
  load cmenv
  create mpcobj/reference workspace variables
  save Simulink `Results.mat`

WSL/Codex:
  inspect files
  analyze exported `Results.mat` and ERG
  generate plots
  maintain docs/scripts/git
```

Reason: WSL-to-Windows GUI/MATLAB/CarMaker automation caused quoting,
workspace, GUI-dialog, and TCP-session issues. Native MATLAB avoids most of
that friction.

## Confirmed Technical Facts

### Slalom Geometry

- Slalom18m is the selected official CarMaker scenario.
- Slalom section starts around `s = 300 m`.
- Pylon coordinates must be interpreted from `DrvPylon.Param` as:

```text
x = s
y = latOffset +/- width/2
```

### Signals

Use these CarMaker quantities in Simulink:

```text
Vhcl.sRoad
Car.Road.Path.DevDist
Car.Road.Path.DevAng
Car.YawRate
Car.v
```

Reference lookup:

```text
t_ref   = lookup(Vhcl.sRoad, slalom_s_ref, slalom_t_ref)
psi_ref = lookup(Vhcl.sRoad, slalom_s_ref, slalom_psi_ref)
```

### Steering Override

Effective steering override point:

```text
VehicleControlUpd output
  -> CreateBus VhclCtrl.Steering
  -> VhclCtrl Steering Ang
```

Changing only `VhclCtrl Steering Ang` is sufficient; setting it to zero made the vehicle drive straight.

### Current MPC Block Wiring

MPC Controller block object:

```text
mpcobj
```

Inputs:

```text
mo  = [Car.Road.Path.DevDist; Car.Road.Path.DevAng; Car.YawRate]
ref = [t_ref; psi_ref; 0]
```

Output:

```text
mv = steering angle command
```

Actual working sign path:

```text
MPC mv output -> Gain(-1) -> VhclCtrl Steering Ang
```

The `Gain(-1)` is currently required. Without it, `e_t` and `delta_cmd` had the same sign and the vehicle diverged before the slalom section.

### Results.mat Analysis Path

Current preferred analysis path:

```text
E:\CarMakerProject\AGI\src_cm4sl\Results.mat
  + latest CarMaker ERG
  -> llm_mpc_bo/scripts/analyze_results_mat.m
  -> aligned_signals.csv / summary.json / summary.md / plots / BO objective
```

`Results.mat` is now preferred over `sigsOut_latest` because Simulink signal
logging produced a 1-sample export when run from a non-interactive/batch path.
The `Results.mat` To File output contains full-run timeseries and matches the
CarMaker ERG timing.

Expected fields:

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

The current Simulink file stores the applied steering command as `signal1`.
`analyze_results_mat.m` automatically maps `signal1` to `delta_cmd`. The
default assumes `delta_cmd` is already after the Gain(-1) sign correction. For
older files where `delta_cmd` was logged before Gain(-1), call:

```matlab
analyze_results_mat(inputPath, outputDir, 'pre_gain')
```

The script also finds the latest matching ERG under:

```text
E:\CarMakerProject\AGI\SimOutput\DESKTOP-QHUIRV6
```

and automatically runs `erg_drive_summary.py` to produce:

```text
llm_mpc_bo/results/processed/results_mat_latest/latest_erg_summary.json
llm_mpc_bo/results/processed/results_mat_latest/latest_erg_drive_log.csv
```

The BO objective is available as:

```matlab
summary.objective.JFailClosed
```

### MPC Plant Model

`init_slalom_mpc.m` uses a linear bicycle lateral model derived from the local MathWorks lane-following example:

```text
C:\Users\user\OneDrive\문서\MATLAB\Examples\R2025a\mpc\LaneFollowingUsingNMPCExample
```

Reduced model:

```text
x = [Vy; yaw_rate; lateral_deviation; heading_error]
y = [lateral_deviation; heading_error; yaw_rate]
u = steering angle
```

Current `mpcobj` settings:

```text
Ts = 0.02 s
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

## Latest Evidence

MPC block run before the `Gain(-1)` fix:

```text
Date: 2026-06-07 14:10
TestRun: LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL
Result: failed before slalom, 8.355 s / 44.917 m
Diagnosis:
  corr(e_t, delta_cmd) = +0.9747
  same-sign fraction e_t * delta_cmd = 1.0
  corr(e_t, steer_manual) = -0.9034
Action:
  add Gain(-1) between MPC mv output and VhclCtrl Steering Ang
```

Diagnosis files:

```text
llm_mpc_bo/results/processed/sigsOut_latest_analysis/diagnosis.md
llm_mpc_bo/results/processed/sigsOut_latest_analysis/diagnosis.json
```

User confirmed:

```text
Gain(-1) after MPC output makes the direction work.
```

Additional CarMaker log evidence from a later new-MATLAB run:

```text
2026-06-07 14:11
SIM ... LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL 0 37.916 517.263
```

This indicates the fixed sign path can complete the nominal/UserSteer CM4SL
run. A fresh `sigsOut` diagnosis still needs to be exported and checked because
the batch workspace/logging setup was incomplete during that run.

Latest `Results.mat` + ERG analysis:

```text
Date: 2026-06-07 15:03
Input: E:\CarMakerProject\AGI\src_cm4sl\Results.mat
ERG: latest LLM_MPC_BO_ICCAS_Slalom18m_UserSteer_CM4SL under 20260607
Status: SIM_END
Duration: 37.918 s
Final s: 525.456 m
Signal mapping: signal1 -> applied delta_cmd
Sign diagnosis: no applied sign issue

RMSE e_t: 0.7536 m
MAX |e_t|: 2.6615 m
RMSE delta: 0.1748 rad
RMSE delta rate: 0.4586 rad/s
MAX |yawrate|: 0.1378 rad/s
Pylon hits: 10
BO J_failClosed: 52.9702
```

Interpretation:

- The fixed sign path completes the nominal/UserSteer CM4SL run.
- The applied steering sign is correct.
- Tracking is still weak for slalom quality because the run hits 10 pylons.
- Next tuning should focus on tracking strength, smoothness, and reference
  suitability, not another sign flip.

## MATLAB Run Commands

When MATLAB/CarMaker/Simulink is already open and configured:

```matlab
run('E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink\init_slalom_mpc.m')
run('E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink\run_slalom_mpc_batch.m')
```

`run_slalom_mpc_batch.m` is now intended to work from a fresh Windows MATLAB
workspace. It performs:

```text
cd E:\CarMakerProject\AGI\src_cm4sl
cmenv
run init_slalom_mpc.m
open_system UserSteer
run/export
```

Outputs:

```text
llm_mpc_bo/results/processed/sigsOut_latest/*.csv
llm_mpc_bo/results/processed/sigsOut_latest/sigsOut_latest.mat
llm_mpc_bo/results/processed/sigsOut_latest_analysis/diagnosis.md
llm_mpc_bo/results/processed/sigsOut_latest_analysis/diagnosis.json
```

Preferred current analysis command:

```matlab
addpath('E:\GitProject\AGI_VOICE\llm_mpc_bo\scripts')
summary = analyze_results_mat( ...
    'E:\CarMakerProject\AGI\src_cm4sl\Results.mat', ...
    'E:\GitProject\AGI_VOICE\llm_mpc_bo\results\processed\results_mat_latest' ...
);
J = summary.objective.JFailClosed;
```

## Next Actions

1. Keep logging `Results.mat` with applied `delta_cmd` after the Gain(-1) sign correction.
2. Use `analyze_results_mat.m` after each run to compute `J_failClosed` from `Results.mat` plus the latest ERG.
3. Tune the nominal/UserSteer CM4SL MPC manually until pylon hits and `e_t` improve:

```text
Weights.OutputVariables
Weights.ManipulatedVariables
Weights.ManipulatedVariablesRate
MV.RateMin / MV.RateMax
MV.Min / MV.Max
```

4. Then evaluate:

```text
LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL
LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu06
```

5. Expose BO variables:

```text
q_y, q_psi, q_r, r_delta, r_d_delta, delta_max_scale
```

6. Build the first trial runner:

```text
theta -> init/update mpcobj -> run CarMaker/Simulink -> export sigsOut/ERG -> compute J
```

7. Compare:

```text
Manual tuned MPC
Pure BO tuned MPC
LLM-assisted BO tuned MPC
```
