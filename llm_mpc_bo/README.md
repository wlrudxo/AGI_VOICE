# LLM MPC BO Slalom Workflow

This workspace runs CarMaker/Simulink MPC weight tuning experiments for the
Slalom18m scenario. The current workflow uses:

- Main CarMaker TestRun: `LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu07`
- Simulink model: `E:\CarMakerProject\AGI\src_cm4sl\UserSteer.mdl`
- Shared MATLAB engine, for example `MATLAB_58352`
- Python 3.12 for MATLAB Engine execution
- Python 3 with matplotlib for plots

`LowMu07` is the current main target because the manual/IPG-driver run finishes
without road departure but still hits pylons. This keeps the benchmark harder
than nominal slalom while avoiding the fully failed behavior seen at lower mu.

## Active Files

Core CLIs:

```text
scripts/mpc_experiment_cli.py      resumable LHC/random/BO batch runner
scripts/mpc_trial_cli.py           one CarMaker/Simulink MPC trial
scripts/analyze_results_mat.m      Results.mat + latest matching ERG analyzer
scripts/erg_drive_summary.py       ERG summary and pylon-hit extraction
scripts/plot_experiment_objective.py
scripts/plot_mpc_trial.py
```

Simulink setup:

```text
simulink/init_slalom_mpc.m
simulink/apply_slalom_mpc_params.m
simulink/init_slalom_reference.m
simulink/slalom18m_base_reference.csv
```

Primary docs:

```text
docs/shared_matlab_carmaker_tuning_workflow.md
docs/standard_slalom_mpc_bo_experiment_plan.md
docs/standard_slalom_experiment_results.md
docs/slalom18m_pylon_geometry.md
```

## Current Workflow

Use this order for a clean experiment session:

```text
1. Start CarMaker GUI and open the Simulink model if needed.
2. Share the active MATLAB session with matlab.engine.shareEngine.
3. Load the intended TestRun explicitly when changing scenarios.
4. Run one manual baseline trial and inspect pylon hits.
5. Run LHC/random/BO/Hybrid experiments in separate experiment directories.
6. Use the generated objective and trajectory plots for review.
```

Do not rely on `--testrun` alone when switching from one TestRun to another.
The trial CLI reuses the currently loaded CarMaker TestRun unless
`--load-testrun` is passed.

## TestRun Loading

Load the TestRun once:

```powershell
py -3 workspace\carmaker_llm_scenario_skill\agent\carmaker_research_runner.py load `
  --direct-carmaker `
  --host localhost `
  --port 16660 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu07 `
  --allow-uncurated
```

Or let the trial CLI load it before a run:

```powershell
py -3.12 llm_mpc_bo\scripts\mpc_trial_cli.py `
  --engine MATLAB_58352 `
  --experiment-dir llm_mpc_bo\results\experiments\manual_lowmu07_current `
  --method manual `
  --iter 1 `
  --run-id manual07_0001 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu07 `
  --load-testrun `
  --allow-uncurated `
  --params-json "{""q_y"":1,""q_psi"":1,""q_r"":1,""r_delta"":1,""r_d_delta"":1}"
```

The `--params-json` values are still required by the CLI, but for a manual/IPG
driver baseline they are just recorded metadata unless the Simulink model is
currently switched to MPC override.

## Manual Baseline

Current LowMu07 manual baseline:

```text
TestRun: LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu07
mu: 0.7
status: SIM_END
pylonHits: 4
J: 41.5306
rmseET: 0.2146 m
maxAbsET: 1.0084 m
```

Generated plots:

```text
results/experiments/manual_lowmu07_current/trials/manual07_0001/trajectory_pylons.png
results/experiments/manual_lowmu07_current/trials/manual07_0001/trial_time_signals.png
```

LowMu06 was checked as a harder reference:

```text
TestRun: LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu06
status: SIM_END
pylonHits: 6
J: 68.7739
rmseET: 1.3224 m
maxAbsET: 5.1704 m
```

## BO/LHC Commands

Run BO with 30-point LHC initialization and 100 total trials:

```powershell
py -3.12 llm_mpc_bo\scripts\mpc_experiment_cli.py `
  --strategy bo `
  --count 100 `
  --budget 100 `
  --bo-init 30 `
  --seed 1 `
  --engine MATLAB_58352 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu07 `
  --load-testrun `
  --allow-uncurated `
  --experiment-dir llm_mpc_bo\results\experiments\lowmu07_bo_scale20_rate10_range001_100_seed1 `
  --reset-mpc
```

`--count` is the target total completed trial count for the experiment
directory, not the number of new trials to append. If a directory already has
92 completed BO trials and the command uses `--count 100 --budget 100`, the CLI
runs only the missing trials 93-100. Use `--max-new-trials N` only when an
interactive session should intentionally pause after at most `N` new
simulations.

Run an LHC baseline with the same budget and seed:

```powershell
py -3.12 llm_mpc_bo\scripts\mpc_experiment_cli.py `
  --strategy lhc `
  --count 100 `
  --budget 100 `
  --seed 1 `
  --engine MATLAB_58352 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu07 `
  --load-testrun `
  --allow-uncurated `
  --experiment-dir llm_mpc_bo\results\experiments\lowmu07_lhc_scale20_rate10_range001_100_seed1 `
  --reset-mpc
```

For repeated seeds, use a new `--experiment-dir` for each method/seed pair.
Never reuse one experiment directory after changing search ranges, objective
terms, steering constraints, TestRun, seed, or BO initialization count.

## Outputs

Each experiment directory contains:

```text
optimizer_config.json
experiment_config.json
candidates.jsonl
trials.jsonl
best_summary.json
objective_by_episode.png
best_trajectory_pylons.png
best_trial_time_signals.png
trials/<run_id>/
```

Per-trial PNGs are off by default. Each trial keeps `aligned_signals.csv`,
`summary.json`, `summary.md`, `latest_erg_summary.json`, and
`trial_summary.json`, so plots can be regenerated later.

Refresh only experiment-level plots without running simulations:

```powershell
py -3.12 llm_mpc_bo\scripts\mpc_experiment_cli.py `
  --strategy bo `
  --count 0 `
  --budget 100 `
  --bo-init 30 `
  --seed 1 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu07 `
  --experiment-dir llm_mpc_bo\results\experiments\lowmu07_bo_scale20_rate10_range001_100_seed1
```

Run only a short continuation toward a 100-trial target:

```powershell
py -3.12 llm_mpc_bo\scripts\mpc_experiment_cli.py `
  --strategy bo `
  --count 100 `
  --budget 100 `
  --max-new-trials 5 `
  --bo-init 30 `
  --seed 1 `
  --engine MATLAB_58352 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu07 `
  --load-testrun `
  --allow-uncurated `
  --experiment-dir llm_mpc_bo\results\experiments\lowmu07_bo_scale20_rate10_range001_100_seed1 `
  --reset-mpc
```

## Current Fixed Constraints

The formal MPC tuning variables are:

```text
q_y, q_psi, q_r, r_delta, r_d_delta
```

Fixed steering-wheel command constraints:

```text
MV.Min/Max = [-12, 12] rad
MV.RateMin/RateMax = [-10, 10] rad/s
```

The MPC prediction model uses a fixed steering-wheel command input calibration:

```text
steeringCmdInputScale = 20
Simulink steering Gain = 1
```

This is model calibration, not an optimization variable. Removing this scale
made previous broad-search results invalid because the MPC under-commanded
steering.

Current broad search range:

```text
q_y, q_psi, q_r, r_delta, r_d_delta in [0.01, 100], log scale
```

Current objective:

```text
J =
  100.0 * simFail
  + 10.0 * pylonHits
  + 4.0 * rmseET
  + 0.5 * maxAbsET
  + 5.0 * rmseEPsi
```

Here `simFail` is treated as road departure, crash, or simulation abort.
Steering magnitude, steering rate, and yaw rate are reported separately rather
than being penalized again in the BO objective.

Current detailed experiment observations are kept in
`docs/experiment_log_20260608.md`; keep this README focused on setup, context,
and repeatable commands.
