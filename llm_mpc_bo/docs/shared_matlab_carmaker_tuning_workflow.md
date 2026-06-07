# Shared MATLAB/CarMaker MPC Tuning Workflow

Updated: 2026-06-07

## Purpose

Use the already-open Windows MATLAB, Simulink, and CarMaker GUI sessions for
manual MPC tuning. Do not relaunch MATLAB for each trial.

The verified loop is:

```text
connect to shared MATLAB engine
-> keep CarMaker GUI open
-> load TestRun only when needed
-> update mpcobj in MATLAB base workspace
-> sim('UserSteer')
-> analyze Results.mat + latest ERG
-> choose next mpcobj parameters
```

## Current Verified State

CarMaker project:

```text
E:\CarMakerProject\AGI
```

Simulink model:

```text
E:\CarMakerProject\AGI\src_cm4sl\UserSteer.mdl
```

TestRun:

```text
LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL
```

MATLAB shared engine name from the working session:

```matlab
matlab.engine.shareEngine
matlab.engine.engineName
```

Observed engine name:

```text
MATLAB_58352
```

This name can change when MATLAB is restarted. Always query it from MATLAB or
with `matlab.engine.find_matlab()` before connecting.

## One-Time MATLAB Setup

In the existing MATLAB Desktop session:

```matlab
cd('E:\CarMakerProject\AGI\src_cm4sl')
cmenv
addpath('E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink')
addpath('E:\GitProject\AGI_VOICE\llm_mpc_bo\scripts')
run('E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink\init_slalom_mpc.m')
open_system('UserSteer')
matlab.engine.shareEngine
matlab.engine.engineName
```

The Python Engine package was installed for Python 3.12 and can attach to the
shared MATLAB session.

Sanity check from PowerShell:

```powershell
@'
import matlab.engine
print(matlab.engine.find_matlab())
eng = matlab.engine.connect_matlab('MATLAB_58352')
print(eng.eval("pwd"))
print(eng.eval("exist('mpcobj','var')"))
print(eng.eval("bdIsLoaded('UserSteer')"))
'@ | py -3.12 -
```

Expected:

```text
pwd = E:\CarMakerProject\AGI\src_cm4sl
exist('mpcobj','var') = 1
bdIsLoaded('UserSteer') = true
```

## TestRun Handling

Do not relaunch CarMaker for each trial.

If the CarMaker GUI is already open and the desired TestRun is already loaded,
skip loading and just run Simulink. If the GUI is blank or on the wrong TestRun,
load it once through the existing TCP command port:

```powershell
py -3 workspace\carmaker_llm_scenario_skill\agent\carmaker_research_runner.py load `
  --direct-carmaker `
  --host localhost `
  --port 16660 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL `
  --allow-uncurated
```

Expected response:

```text
LoadTestRun -> OK (no response)
Vehicle = Examples/DemoCar_UserSteer_CM4SL
Traffic.N = 0
```

This is safer than depending on Simulink to remember the CarMaker TestRun
selection.

## Simulink Steering Sign

As of the latest verified run, the user changed the steering Gain block from
`-1` to `1`, and the vehicle completed the run. With `Gain=1`, the sign
diagnosis reports no applied steering sign issue.

Do not add another sign flip in MATLAB or Python. The tuning scripts only update
`mpcobj`; they do not edit Simulink wiring.

If the vehicle aborts early again, first check the Simulink Gain block and the
`analyze_results_mat.m` sign diagnosis before changing MPC weights.

## Workspace-Only MPC Parameter Updates

Use `apply_slalom_mpc_params.m` to update only the existing MATLAB base
workspace `mpcobj`.

Current convention:

```text
MPC output delta_cmd = VhclCtrl.Steering.Ang [rad]
Simulink steering Gain = 1
constraints are fixed steering-wheel angle limits
```

The MPC plant input gain is scaled in `init_slalom_mpc.m`; do not add another
Simulink scaling Gain for the formal experiment.

Current checked parameter set:

```matlab
params = struct( ...
    'q_y', 30, ...
    'q_psi', 10, ...
    'q_r', 0.5, ...
    'r_delta', 0.05, ...
    'r_d_delta', 0.5 ...
);
mpcobj = apply_slalom_mpc_params(params);
```

This applies:

```text
Weights.OutputVariables = [30 10 0.5]
Weights.ManipulatedVariables = 0.05
Weights.ManipulatedVariablesRate = 0.5
MV.Min/Max = [-12, 12]
MV.RateMin/RateMax = [-0.6, 0.6]
```

Avoid rerunning `init_slalom_mpc.m` inside every trial unless the controller
object is missing or intentionally reset. Reinitializing can wipe manual tuning
state.

## Run One Trial From PowerShell

Preferred CLI form:

```powershell
py -3.12 llm_mpc_bo/scripts/mpc_trial_cli.py `
  --engine MATLAB_58352 `
  --experiment-dir llm_mpc_bo/results/experiments/standard_slalom_latest `
  --method manual `
  --iter 1 `
  --run-id manual_0001 `
  --params-json "{""q_y"":30,""q_psi"":10,""q_r"":0.5,""r_delta"":0.05,""r_d_delta"":0.5}"
```

This writes:

```text
experiment_config.json
trials.jsonl
best_summary.json
trials/<run_id>/trial_summary.json
trials/<run_id>/trajectory_pylons.png
trials/<run_id>/trial_time_signals.png
```

The trial CLI generates trajectory/time PNGs automatically after a successful
run. Plotting uses the `py -3` Python environment because that environment has
`matplotlib`; the MATLAB Engine trial runner itself still uses Python 3.12.
Use `--skip-trial-plots` only when plotting overhead is not wanted.

## Run/Resume an Optimization Batch

For grid/LHC/BO-style experiments, use the experiment CLI instead of manually
calling the single-trial CLI repeatedly:

```powershell
py -3.12 llm_mpc_bo/scripts/mpc_experiment_cli.py `
  --strategy lhc `
  --count 30 `
  --budget 30 `
  --seed 7 `
  --engine MATLAB_58352 `
  --experiment-dir llm_mpc_bo/results/experiments/standard_slalom_lhc_seed7
```

```powershell
py -3.12 llm_mpc_bo/scripts/mpc_experiment_cli.py `
  --strategy bo `
  --count 100 `
  --budget 100 `
  --bo-init 30 `
  --seed 1 `
  --engine MATLAB_58352 `
  --experiment-dir llm_mpc_bo/results/experiments/standard_slalom_bo_seed1
```

```powershell
py -3.12 llm_mpc_bo/scripts/mpc_experiment_cli.py `
  --strategy random `
  --count 100 `
  --budget 100 `
  --seed 1 `
  --engine MATLAB_58352 `
  --experiment-dir llm_mpc_bo/results/experiments/standard_slalom_random_seed1
```

The important rule is to reuse the same `--experiment-dir` for the same
optimization. The directory is the resumable state:

```text
optimizer_config.json  locked strategy/seed/budget/range config
trials.jsonl       evaluated trial ledger
candidates.jsonl   proposed candidate ledger
best_summary.json  best evaluated parameter set so far
candidate_plan_*   deterministic LHC/random candidate plan
trials/<run_id>/   per-trial summaries and analysis outputs
```

After the batch command exits, the CLI also regenerates:

```text
objective_by_episode.png
best_trajectory_pylons.png
best_trial_time_signals.png
```

This episode-vs-`J` plot is generated for LHC, random, and BO experiments from
the current `trials.jsonl`. The best-trial plots are regenerated from
`best_summary.json` and written directly under the experiment directory. A
zero-count rerun can refresh only the experiment summary and best-trial plots
without running new simulations. Use
`--skip-objective-plot` or `--skip-best-trial-plot` only when plotting overhead
is not wanted.

During batch experiments, per-trial PNG generation is off by default to reduce
runtime and disk churn. Each trial still keeps `aligned_signals.csv`,
`summary.json`, `summary.md`, `latest_erg_summary.json`, and
`trial_summary.json`, so trajectory/time plots can be regenerated later. Use
`--write-trial-plots` to write `trajectory_pylons.png` and
`trial_time_signals.png` for every trial during the batch. Use
`--write-analysis-plots` only when the analyzer's debug `time_signals.png` and
`sroad_tracking.png` are needed.

If 12 trials were completed and the command is run again with the same method
and directory, the next run starts at iteration 13. BO is executed sequentially:
after each trial it rereads `trials.jsonl`, updates the surrogate from all
successful observations, and proposes the next candidate.

For the main 5D tuning experiment, use `--budget 100 --bo-init 30`. That means
30 deterministic LHC initialization trials followed by 70 BO/EI trials. Use a
new directory for each seed, for example:

```text
standard_slalom_bo_seed1
standard_slalom_bo_seed2
standard_slalom_bo_seed3
standard_slalom_lhc_seed1
standard_slalom_lhc_seed2
standard_slalom_lhc_seed3
```

The optimizer config is locked on first use. If a later command uses a different
seed, budget, BO init count, candidate pool size, tuned-key list, or range in
the same directory, the CLI stops instead of mixing incompatible experiments.

Dry-run shows the next candidates without starting CarMaker/Simulink:

```powershell
py -3.12 llm_mpc_bo/scripts/mpc_experiment_cli.py `
  --strategy bo `
  --count 3 `
  --budget 100 `
  --bo-init 30 `
  --seed 1 `
  --experiment-dir llm_mpc_bo/results/experiments/standard_slalom_bo_seed1 `
  --dry-run
```

Manual Python Engine form for debugging:

This attaches to the existing MATLAB session, changes only `mpcobj`, runs
Simulink, and analyzes the result:

```powershell
@'
import matlab.engine
eng = matlab.engine.connect_matlab('MATLAB_58352')
cmd = r"""
cd('E:\CarMakerProject\AGI\src_cm4sl');
addpath('E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink');
addpath('E:\GitProject\AGI_VOICE\llm_mpc_bo\scripts');

params = struct('q_y',30,'q_psi',10,'q_r',0.5, ...
    'r_delta',0.05,'r_d_delta',0.5);
mpcobj = apply_slalom_mpc_params(params);

simOut = sim('UserSteer');
assignin('base','simOut',simOut);

summary = analyze_results_mat( ...
    'E:\CarMakerProject\AGI\src_cm4sl\Results.mat', ...
    'E:\GitProject\AGI_VOICE\llm_mpc_bo\results\trials\manual_trial_latest' ...
);
assignin('base','lastAnalysisSummary',summary);
fprintf('J=%g status=%s violations=%d\n', ...
    summary.objective.JFailClosed, ...
    summary.objective.ergStatus, ...
    summary.objective.NViolation);
"""
eng.eval(cmd, nargout=0)
print("J", eng.eval("lastAnalysisSummary.objective.JFailClosed"))
print("status", eng.eval("lastAnalysisSummary.objective.ergStatus"))
print("violations", eng.eval("lastAnalysisSummary.objective.NViolation"))
'@ | py -3.12 -
```

## Current Result Baseline

With `Gain=1`, direct steering-wheel-angle MPC output, and the current checked
parameter set:

```text
Status: SIM_END
J: 53.9036
Pylon hits: 5
RMSE e_t: 0.4972 m
MAX |e_t|: 2.2070 m
Max delta_cmd: 8.3915 rad
Max steer_manual: 10.5771 rad
Applied sign issue: false
```

Earlier trials before direct steering-wheel-angle MPC output:

```text
tune_001_aggressive_gain1:
  params = [80, 25, 1.0, 0.02, 0.2, 1.2], delta_rate_scale=3.0
  J = 58.3452, pylon hits = 11

tune_002_smoother_gain1:
  params = [45, 14, 0.8, 0.08, 1.2, 1.0], delta_rate_scale=1.5
  J = 53.1207, pylon hits = 10

tune_003_near_best_smoother_gain1:
  params = [30, 10, 0.5, 0.08, 0.8, 1.0], delta_rate_scale=1.5
  J = 53.1208, pylon hits = 10
```

These are useful only as historical debugging runs.

## Analysis Notes

Use `Results.mat` plus the latest matching ERG. `analyze_results_mat.m` writes:

```text
summary.json
summary.md
aligned_signals.csv
time_signals.png
sroad_tracking.png
latest_erg_summary.json
latest_erg_drive_log.csv
```

To regenerate one analyzed MPC trial as a trajectory/pylon PNG:

```powershell
py -3 llm_mpc_bo/scripts/plot_mpc_trial.py `
  --trial-dir llm_mpc_bo/results/experiments/standard_slalom_replay_lhc0063/trials/replay_lhc0063 `
  --label lhc_0063_replay
```

This reads `aligned_signals.csv` and `slalom18m_pylons.csv`, then writes:

```text
trajectory_pylons.png
trial_time_signals.png
```

The BO objective is:

```matlab
summary.objective.JFailClosed
```

Fail-closed behavior:

```text
SIM_ABORT -> 100-point simFail penalty plus any known pylon hits
SIM_END -> pylon-hit-dominant tracking/control objective
```

Current BO objective:

```text
J =
  100 * simFail
  + 50 * collisionDetected
  + 25 * collisionCount
  + 10 * pylonHits
  + 2.0 * (rmseET / 0.5)
  + 1.0 * (maxAbsET / 2.0)
  + 0.5 * (rmseEPsi / 0.1)
  + 0.3 * (maxYawRate / 0.7)
  + 0.1 * (rmseDelta / 3.0)
  + 0.05 * (rmseDeltaRate / 10.0)
```

Pylon contacts are counted by `pylonHitCount`; they are not currently surfaced
as generic collision events.

Be careful with stale ERG matching. A previous run appeared to complete because
the analyzer paired a one-sample `Results.mat` with a later `SIM_END` ERG. A
valid run should have both:

```text
Results.mat duration around 37.9 s
ERG status SIM_END with matching timestamp/run
```

## Practical Tuning Guidance

The current main limitation is pylon hits, not early simulation failure.

Observed effects:

```text
More aggressive tracking reduced max lateral error slightly but increased
steering activity and pylon hits.

Smoother settings reduced steering activity but did not improve pylon hits or
tracking objective.
```

Formal experiments should tune only MPC weights:

```text
q_y, q_psi, q_r, r_delta, r_d_delta
```

Keep steering constraints fixed. Prefer small changes and always restore the
best known parameter set after a bad trial.
