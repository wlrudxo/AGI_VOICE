# LLM-MPC-BO ICCAS Research Progress Log - 2026-06-07 Archive

This archive tracks the current MPC/Results.mat/CLI/BO automation work. Earlier CarMaker scenario setup, pylon geometry, Simulink wiring, and PD/feedforward smoke-test details were moved to:

```text
llm_mpc_bo/docs/research_progress_log_detailed_archive_20260606.md
```

For current continuation context, use:

```text
llm_mpc_bo/docs/native_windows_agent_handoff.md
llm_mpc_bo/docs/shared_matlab_carmaker_tuning_workflow.md
llm_mpc_bo/docs/standard_slalom_mpc_bo_experiment_plan.md
```

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
- Defaults to treating the logged command as the applied steering command.
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

- Later live testing showed the Simulink steering Gain should be `1`.
- `VhclCtrl.Steering.Ang` is steering wheel angle [rad].
- The MPC plant input gain was corrected so `delta_cmd` is directly a steering
  wheel angle command.
- The nominal/UserSteer CM4SL MPC completes the scenario with 5 pylon hits after
  this correction.

## Addendum: Standard Slalom Main Experiment Plan

Date: 2026-06-07

Current decision:

```text
Use standard Slalom18m/UserSteer as the main paper benchmark.
Keep LowMu/icy-road variants as stress-test or future-work extensions.
```

Reason:

- The standard slalom already exposes meaningful closed-loop MPC tuning
  difficulty.
- Low friction currently mixes control tuning with model/input/debugging issues.
- A clean nominal benchmark is better for comparing search methods.

Controller convention:

```text
MPC output delta_cmd = VhclCtrl.Steering.Ang [rad]
Simulink steering Gain = 1
Fixed constraints: MV [-12, 12], Rate [-0.6, 0.6]
```

Tuned MPC variables:

```text
q_y, q_psi, q_r, r_delta, r_d_delta
```

Do not tune:

```text
Vx_model, steering scale, delta_max_scale, delta_rate_scale
```

Compared methods:

```text
1. IPG Driver baseline
2. LHC/random search
3. BO
4. LLM-only
5. Hybrid BO
```

Initial budget:

```text
30 trials per method, then optionally 50 trials if runtime is acceptable.
```

Latest checked direct steering-wheel-angle MPC result:

```text
Status: SIM_END
J: 32.3837
Pylon hits: 5
RMSE e_t: 0.4972 m
MAX |e_t|: 2.2070 m
Max delta_cmd: 8.3915 rad
Max steer_manual: 10.5771 rad
Applied sign issue: false
```

Implementation note:

Ad-hoc MATLAB/Python snippets used for LLM-based control should be converted
into a CLI before formal experiments. The CLI should connect to the shared
MATLAB engine, apply 5 MPC weights, run `sim('UserSteer')`, analyze
`Results.mat` + ERG, and print/write J/status/pylon hits.

## Addendum: Trial CLI and Append-Only Ledger

Date: 2026-06-07

Implemented:

```text
llm_mpc_bo/scripts/mpc_trial_cli.py
```

Purpose:

```text
Run one MPC trial through a shared MATLAB engine and append one JSON line to
the experiment ledger.
```

CLI behavior:

- Accepts either explicit 5-weight JSON params or a 5D normalized vector.
- Rejects extra tuning variables outside:
  `q_y, q_psi, q_r, r_delta, r_d_delta`.
- Connects to an existing shared MATLAB engine.
- Optionally loads the CarMaker TestRun through the existing TCP runner.
- Applies MPC weights, runs `sim('UserSteer')`, analyzes `Results.mat` + ERG.
- Writes per-trial `trial_summary.json`.
- Appends `trials.jsonl`.
- Updates `best_summary.json`.

Smoke test:

```text
Experiment dir: llm_mpc_bo/results/experiments/standard_slalom_cli_smoke
Run id: cli_smoke_0001
Status: SIM_END
J: 32.3837
Pylon hits: 5
RMSE e_t: 0.4972 m
MAX |e_t|: 2.2070 m
```

The first smoke attempt failed due MATLAB string escaping and was intentionally
preserved as a failed ledger row. The second row succeeded. Experiment outputs
are ignored by git under `llm_mpc_bo/results/experiments/`.

## Addendum: BO Objective Recalibration

Date: 2026-06-07

The BO objective was recalibrated for the direct steering-wheel-angle command
convention. The previous objective over-penalized steering command and steering
rate because `delta_cmd` is now `VhclCtrl.Steering.Ang [rad]`.

Current objective:

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

Notes:

- Pylon contacts are counted separately by `pylonHitCount` from
  `Scratchpad.PylonHit.*`/ERG metadata.
- Pylon contacts are not currently treated as generic collision signals.
- Generic collision fields are included as extension points, but are currently
  false/zero unless the ERG summary provides them.
- The first BO target is reducing pylon hits while preserving `SIM_END`.

## Addendum: Resumable Optimization CLI

Date: 2026-06-07

Implemented:

```text
llm_mpc_bo/scripts/mpc_experiment_cli.py
```

Purpose:

```text
Run fixed-budget MPC tuning experiments while preserving enough state to resume
the same optimization naturally after n completed trials.
```

Supported strategies:

```text
lhc
random
bo
```

The experiment directory is the optimization state:

```text
trials.jsonl       append-only evaluated trial ledger
candidates.jsonl   append-only proposed candidate ledger
best_summary.json  current best evaluated result
candidate_plan_*   deterministic LHC/random candidate plans
trials/<run_id>/   per-trial summary and analysis output
```

Resume rule:

```text
Reuse the same --experiment-dir, --method, seed, and budget.
The CLI skips completed successful iterations and starts from the next missing
iteration.
```

BO-specific rule:

```text
BO is not planned as a static batch. It runs one trial, rereads trials.jsonl,
rebuilds the surrogate from successful observations, then proposes the next
candidate.
```

Example:

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

Dry-run verification completed:

```text
py_compile: pass
lhc --count 3 --budget 10 --seed 7 --dry-run: printed distinct candidates
bo  --count 3 --budget 10 --seed 7 --dry-run: printed sequential LHC init candidates
resume smoke with completed lhc iterations 1,2: next dry-run started at 3,4
```

## Addendum: Reproducible 100-Trial Experiment Design

Date: 2026-06-07

Decision:

```text
Use 100 trials as the main maximum budget for 5D MPC tuning.
For BO: 30 LHC initialization trials + 70 BO/EI trials.
For LHC/random baselines: 100 trials with the same seed/budget convention.
```

Reason:

- 10 trials is enough for pipeline validation but too small for a meaningful
  5D surrogate.
- 30 LHC points provide a reasonable initial design for the 5D log-scaled
  weight space.
- 70 BO/EI updates after initialization leave enough room for surrogate-based
  refinement.
- One trial currently takes about 10-20 seconds, so 100 trials is practical.

Reproducibility rule:

```text
One independent run = one method + one seed + one experiment directory.
Do not mix different seeds, budgets, BO init counts, candidate-pool sizes,
tuned-key lists, or search ranges in one directory.
```

Implemented config lock:

```text
llm_mpc_bo/results/experiments/<run>/optimizer_config.json
```

The experiment CLI writes this file on first use and stops if a later command
uses incompatible optimizer settings in the same directory.

Verification:

```text
py_compile: pass
BO dry-run, seed 1, budget 100, bo_init 30: first 3 candidates generated
LHC dry-run, seed 1, budget 100: first 3 candidates match BO init candidates
Config mismatch smoke: same directory with seed 2 failed as expected
```

Main BO command template:

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

## Addendum: Reinforcement Learning Comparison Decision

Date: 2026-06-07

Decision:

```text
Do not include reinforcement learning as a main comparison group for the first
paper.
```

Reason:

- The current study is static MPC-weight tuning:

```text
theta = [q_y, q_psi, q_r, r_delta, r_d_delta]
theta -> one CarMaker/Simulink run -> scalar objective J
```

- RL would normally learn a state-action policy over many transitions, not just
  choose one static controller parameter vector per rollout.
- A 100-rollout budget is reasonable for 5D BO but too small for a fair RL
  policy-learning baseline.
- Adding RL would change the comparison from "which optimizer tunes the same
  MPC controller better?" to "MPC-weight tuning vs a different controller
  learning formulation", which weakens the first paper's focus.

Use RL only as related work or future work unless a later experiment explicitly
redefines the problem as policy learning.
