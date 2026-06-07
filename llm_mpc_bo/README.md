# LLM MPC BO Slalom Workflow

This workspace runs CarMaker/Simulink MPC weight tuning experiments for the
Slalom18m scenario. The current workflow uses:

- CarMaker TestRun: `LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu06`
- Simulink model: `E:\CarMakerProject\AGI\src_cm4sl\UserSteer.mdl`
- Shared MATLAB engine, for example `MATLAB_58352`
- Python 3.12 for MATLAB Engine execution
- Python 3 with matplotlib for plots

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

## Current Experiment Command

Load the TestRun once:

```powershell
py -3 workspace\carmaker_llm_scenario_skill\agent\carmaker_research_runner.py load `
  --direct-carmaker `
  --host localhost `
  --port 16660 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu06 `
  --allow-uncurated
```

Run BO with 50-point LHC initialization and 150 total trials:

```powershell
py -3.12 llm_mpc_bo\scripts\mpc_experiment_cli.py `
  --strategy bo `
  --count 150 `
  --budget 150 `
  --bo-init 50 `
  --seed 1 `
  --engine MATLAB_58352 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu06 `
  --experiment-dir llm_mpc_bo\results\experiments\lowmu06_bo_rate10_seed1 `
  --reset-mpc
```

The batch runner does not reload the TestRun unless `--load-testrun` is passed.

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
  --budget 150 `
  --bo-init 50 `
  --seed 1 `
  --testrun LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu06 `
  --experiment-dir llm_mpc_bo\results\experiments\lowmu06_bo_rate10_seed1
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

The earlier LowMu06 BO run with `±0.6 rad/s` steering-rate limits is kept as a
constrained-baseline result under `results/experiments/lowmu06_bo_seed1`.
