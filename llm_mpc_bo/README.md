# LLM MPC BO Slalom Workflow

This workspace runs CarMaker/Simulink MPC weight tuning experiments for the
Slalom18m scenario. The current workflow uses:

- Main CarMaker TestRun: `LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL`
- Simulink model: `E:\CarMakerProject\AGI\src_cm4sl\UserSteer.mdl`
- Shared MATLAB engine, for example `MATLAB_58352`
- Python 3.12 for MATLAB Engine execution
- Python 3 with matplotlib for plots

The current main target is the normal-friction slalom. LowMu07 is kept as a
harder reference condition in the experiment log, but the next formal tuning
pass uses a tighter 4D controller-weight search on the normal road.

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
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL `
  --allow-uncurated
```

Or let the trial CLI load it before a run:

```powershell
py -3.12 llm_mpc_bo\scripts\mpc_trial_cli.py `
  --engine MATLAB_58352 `
  --experiment-dir llm_mpc_bo\results\experiments\manual_standard_current `
  --method manual `
  --iter 1 `
  --run-id manual_standard_0001 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL `
  --load-testrun `
  --allow-uncurated `
  --params-json "{""q_y"":1,""q_psi"":1,""r_delta"":1,""r_d_delta"":1}"
```

The `--params-json` values are still required by the CLI, but for a manual/IPG
driver baseline they are just recorded metadata unless the Simulink model is
currently switched to MPC override.

## Manual Baseline

Run one manual/IPG-driver baseline whenever the TestRun or road-friction setup
changes. Detailed LowMu06/LowMu07 baseline observations are kept in
`docs/experiment_log_20260608.md`; this README keeps only the repeatable
workflow.

## BO/LHC Commands

Run BO with 15-point LHC initialization and 50 total trials:

```powershell
py -3.12 llm_mpc_bo\scripts\mpc_experiment_cli.py `
  --strategy bo `
  --count 50 `
  --budget 50 `
  --bo-init 15 `
  --seed 1 `
  --engine MATLAB_58352 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL `
  --load-testrun `
  --allow-uncurated `
  --experiment-dir llm_mpc_bo\results\experiments\standard_slalom_4d_bo_qr0_budget50_seed1 `
  --reset-mpc
```

`--count` is the target total completed trial count for the experiment
directory, not the number of new trials to append. If a directory already has
42 completed BO trials and the command uses `--count 50 --budget 50`, the CLI
runs only the missing trials 43-50. Use `--max-new-trials N` only when an
interactive session should intentionally pause after at most `N` new
simulations.

Run an LHC baseline with the same budget and seed:

```powershell
py -3.12 llm_mpc_bo\scripts\mpc_experiment_cli.py `
  --strategy lhc `
  --count 50 `
  --budget 50 `
  --seed 1 `
  --engine MATLAB_58352 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL `
  --load-testrun `
  --allow-uncurated `
  --experiment-dir llm_mpc_bo\results\experiments\standard_slalom_4d_lhc_qr0_budget50_seed1 `
  --reset-mpc
```

For repeated seeds, use a new `--experiment-dir` for each method/seed pair.
Never reuse one experiment directory after changing search ranges, objective
terms, steering constraints, TestRun, seed, or BO initialization count.

Run a Sobol landscape-audit batch when the goal is dense, low-discrepancy
coverage of the 4D log-scale search space rather than optimizer comparison:

```powershell
py -3.12 llm_mpc_bo\scripts\mpc_experiment_cli.py `
  --strategy sobol `
  --method sobol `
  --count 1024 `
  --budget 1024 `
  --seed 1 `
  --engine MATLAB_58352 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL_V61 `
  --load-testrun `
  --allow-uncurated `
  --experiment-dir llm_mpc_bo\results\experiments\standard_slalom_v61_4d_sobol_entryignored_budget1024_seed1 `
  --reset-mpc
```

For interactive Sobol smoke checks, keep the same `--count 1024 --budget
1024` target and add `--max-new-trials N`. This preserves the final 1024-point
candidate plan while running only the next `N` missing simulations.

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
  --budget 50 `
  --bo-init 15 `
  --seed 1 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL `
  --experiment-dir llm_mpc_bo\results\experiments\standard_slalom_4d_bo_qr0_budget50_seed1
```

Run only a short continuation toward a 50-trial target:

```powershell
py -3.12 llm_mpc_bo\scripts\mpc_experiment_cli.py `
  --strategy bo `
  --count 50 `
  --budget 50 `
  --max-new-trials 5 `
  --bo-init 15 `
  --seed 1 `
  --engine MATLAB_58352 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL `
  --load-testrun `
  --allow-uncurated `
  --experiment-dir llm_mpc_bo\results\experiments\standard_slalom_4d_bo_qr0_budget50_seed1 `
  --reset-mpc
```

## Current Fixed Constraints

The formal MPC tuning variables are:

```text
q_y, q_psi, r_delta, r_d_delta
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

Current search range:

```text
q_y, q_psi, r_delta, r_d_delta in [0.01, 100], log scale
q_r = 0 fixed
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
