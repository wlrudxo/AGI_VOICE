# Standard Slalom MPC BO Experiment Plan

Updated: 2026-06-07

## Decision

Use the current standard CarMaker Slalom18m/UserSteer scenario as the main
research target.

Do not make low-friction or icy-road operation the main benchmark for the first
paper. LowMu can remain a stress-test or future-work extension after the nominal
Slalom18m workflow is stable.

Current research story:

```text
1. Start from a broad but defensible five-dimensional MPC-weight search space.
2. Show that non-adaptive LHC/random sampling spends many trials in poor
   regions, such as under-tracking or steering-suppressed controllers.
3. Show that BO can exploit simulator feedback, but must first pay for a broad
   initial design before the surrogate becomes useful.
4. Use the LLM as a reasoning module that reads trial logs and tightens the
   weight search region for BO. The LLM does not modify physical steering
   constraints, vehicle parameters, input scaling, or the MPC structure.
```

## Scenario

CarMaker TestRun:

```text
LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL
```

Vehicle:

```text
Examples/DemoCar_UserSteer_CM4SL
```

Simulink model:

```text
E:\CarMakerProject\AGI\src_cm4sl\UserSteer.mdl
```

Controller input/output convention:

```text
MPC output delta_cmd = VhclCtrl.Steering.Ang [rad]
CarMaker quantity = steering wheel angle command [rad]
Simulink steering Gain = 1
```

No steering ratio, command input scale, or model-speed variable is included in
the optimization. The MPC manipulated variable is the steering-wheel command
sent to CarMaker through `VhclCtrl.Steering.Ang`.

## Fixed Constraints

Do not tune steering command constraints in the main experiment. Keep them as
fixed physical/safety limits:

```matlab
mpcobj.MV.Min = -12.0;
mpcobj.MV.Max =  12.0;
mpcobj.MV.RateMin = -10.0;
mpcobj.MV.RateMax =  10.0;
```

These values are intentionally wide steering-wheel angle/rate limits in the MPC
command domain. Keep them fixed during formal optimization so that the
benchmark focuses on MPC-weight tuning rather than actuator-limit exploration.

## Tuned Variables

Tune only MPC weight parameters:

```text
q_y
q_psi
r_delta
r_d_delta
```

Normalized BO vector order:

```text
[q_y, q_psi, r_delta, r_d_delta]
```

Initial search ranges for the next formal nominal Slalom18m runs:

| Variable | Meaning | Range | Scale |
| --- | --- | --- | --- |
| `q_y` | lateral error weight | `0.01 - 100` | log |
| `q_psi` | heading error weight | `0.01 - 100` | log |
| `r_delta` | steering wheel angle command weight | `0.01 - 100` | log |
| `r_d_delta` | steering wheel angle rate weight | `0.01 - 100` | log |

The yaw-rate output weight is fixed:

```text
q_r = 0
```

The formal setting uses a single equal log-scale range for the four remaining
weights. This keeps the experiment easy to describe while removing the
previously unhelpful yaw-rate-weight dimension.

Do not include `Vx_model`, steering scale, command saturation scale, or command
rate scale as main tuning variables. Those are model/setup choices, not the
MPC tuning story for this paper.

## Compared Methods

Use five groups:

```text
1. IPG Driver baseline
2. LHC/random search baseline
3. Bayesian Optimization
4. LLM-only search
5. Hybrid BO
```

Do not include reinforcement learning as a main comparison group for the first
paper. This experiment tunes five static MPC weights with a simulator-in-the-
loop objective; it is not a sequential state-action policy-learning setup.
With a 50-run budget, RL would be sample-starved and would compare a different
problem formulation rather than a different optimizer for the same controller.
Mention RL only as a related/future direction if needed.

### IPG Driver Baseline

Run the standard CarMaker/IPG driver with no MPC override or with the existing
driver reference behavior as the reference baseline.

Report:

```text
SIM_END/SIM_ABORT
pylon hit count
RMSE lateral error
MAX lateral error
steering smoothness
```

### LHC/Random Search

Use Latin Hypercube Sampling or random log-uniform samples across the same
5-dimensional MPC weight space. This is the non-adaptive black-box baseline.

### BO

Use a Gaussian-process or comparable surrogate BO loop over the same 5 variables.
Acquisition can start simple, for example expected improvement or UCB.

### LLM-only

At each iteration, the LLM proposes the next MPC weight vector from:

```text
previous parameter/result table
current best trajectory/metrics summary
fixed search ranges
```

No surrogate optimizer is used.

### Hybrid BO

Use BO as the base optimizer and let the LLM assist by search-space reasoning,
not by changing the controller or actuator constraints. Physical steering
constraints stay fixed; the LLM may only suggest narrower weight bounds or
candidate filters within the original 4D log-scale space
(`q_y,q_psi,r_delta,r_d_delta`: `[0.01, 100]`; `q_r = 0` fixed).

The preferred Hybrid BO schedule is:

```text
trials 1-10: broad LHC initialization
trial 10: LLM diagnosis and first weight-region suggestion
trials 11-30: BO within or biased toward the suggested region
trial 30: LLM update from accumulated trial history
trials 31-50: BO within the updated region
```

LLM diagnosis should identify patterns such as:

```text
tracking weights too small -> weak path following
steering effort/rate weights too large -> steering is suppressed
steering effort/rate weights too small -> overly aggressive steering activity
yaw-rate weight fixed at 0 -> diagnose steering/tracking weights first
```

The hybrid method should still evaluate exactly one candidate per trial so that
trial counts are comparable. Final candidate selection remains simulator
validated and BO-driven.

## Trial Budget

Main calibrated design:

```text
4D BO method: 15 LHC initialization trials + BO/EI up to 50 total trials
Hybrid BO method: short BO blocks with LLM region updates every 5-10 trials
Grid/LHC baseline: 50 LHC trials
Random baseline: 50 random log-uniform trials
```

For the current normal-road follow-up, use the 4D/50-trial design:

```text
scenario = LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL
q_r = 0 fixed
budget = 50
bo_init = 15
seed = fixed per repeated experiment
```

This keeps runtime manageable and reflects the current observation that `q_r`
was repeatedly pushed to the lower bound in the calibrated 5D run.
A 3-level full factorial design over 4 variables would require `3^4 = 81`
simulations. That is useful as a coverage reference, but the formal comparison
should stay at 50 trials when the region has already been tightened by prior
BO/LLM diagnosis. A 30-trial budget is reserved for quick feasibility checks,
not final comparison.
Each completed run should produce:

```text
best objective vs iteration
pylon hits vs iteration
best trajectory comparison
steering command comparison
method summary table
```

For repeated experiments, use separate fixed seeds and separate directories:

```text
seed 1
seed 2
seed 3
```

Use the same seed number across methods when comparing methods under matched
conditions. For example, `bo_seed1`, `lhc_seed1`, and `random_seed1`.

Recommended sequence:

```text
Phase 1: BO 50 trials, seed 1, confirm the 15+35 pipeline
Phase 2: LHC/random 50 trials, seed 1, establish baseline
Phase 3: repeat BO and best baseline for seeds 2 and 3
Phase 4: add LLM-only/Hybrid BO runs with the same seed set
```

## Objective

Use `summary.objective.JFailClosed` from:

```text
llm_mpc_bo/scripts/analyze_results_mat.m
```

Current simplified BO objective structure for the next formal runs:

```text
J =
  100.0 * simFail
  + 10.0 * pylonHits
  + 4.0 * rmseET
  + 0.5 * maxAbsET
  + 5.0 * rmseEPsi
```

Here `simFail` is interpreted as road departure, crash, or simulation abort.
Pylon contacts are counted separately by `pylonHitCount` from the ERG/session
metadata. Generic collision fields are reported when available but are not
separately penalized in the current scalar objective because they duplicate the
fail-closed road-departure/crash signal in this scenario.

The outer-loop objective should prioritize closed-loop path-following success
and pylon avoidance. Steering angle and steering-rate usage should be controlled
through the MPC internal weights (`r_delta`, `r_d_delta`) and reported as
secondary metrics, rather than being directly penalized again in the BO
objective. Report `rmseDelta`, `maxAbsDelta`, `rmseDeltaRate`,
`maxAbsDeltaRate`, and steering saturation separately.

The first hard target is:

```text
pylon hits: 5 -> 0
SIM_END maintained
```

Then rank pylon-free runs by tracking quality, while reporting steering smoothness
as a secondary metric.

## Current Verified Controller State

Current model/setup:

```text
Simulink steering Gain: 1
MPC output: steering wheel angle command [rad]
MPC prediction input calibration: steeringCmdInputScale = 20
Constraints: fixed [-12, 12] rad, rate [-10, 10] rad/s
```

Current checked parameter set:

```text
q_y = 30
q_psi = 10
q_r = 0 fixed
r_delta = 0.05
r_d_delta = 0.5
```

Latest result:

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

## Automation Direction

Ad-hoc MATLAB/Python snippets used during LLM-based control should be converted
into small CLI commands before running formal experiments.

Implemented initial CLI:

```text
llm_mpc_bo/scripts/mpc_trial_cli.py
```

Example:

```powershell
py -3.12 llm_mpc_bo/scripts/mpc_trial_cli.py `
  --engine MATLAB_58352 `
  --experiment-dir llm_mpc_bo/results/experiments/standard_slalom_latest `
  --method llm_only `
  --iter 7 `
  --run-id llm_only_0007 `
  --params-json "{""q_y"":30,""q_psi"":10,""r_delta"":0.05,""r_d_delta"":0.5}"
```

The CLI:

```text
connect to a shared MATLAB engine
optionally load the CarMaker TestRun once
apply the 5 MPC weights
run sim('UserSteer')
analyze Results.mat + ERG
write trial_summary.json
append trials.jsonl
update best_summary.json
return J/status/pylon hits on stdout
```

This keeps LLM-only and Hybrid BO experiments reproducible while still allowing
the LLM to reason over results and propose candidates.

## Resumable Optimization CLI

Implemented batch/resume CLI:

```text
llm_mpc_bo/scripts/mpc_experiment_cli.py
```

Use one `--experiment-dir` as the persistent optimization state. After an
optimization has already run `n` trials, reuse the same directory and the CLI
continues from the next missing iteration instead of starting over.

`--count` means the target total number of completed trials in that experiment
directory. It is not the number of additional trials to append. For example, if
`trials.jsonl` already contains 42 completed BO trials, `--count 50 --budget
50` runs only trials 43-50 and then stops. Use `--max-new-trials N` when an
interactive session should intentionally stop after at most `N` newly executed
simulations.

State files:

```text
optimizer_config.json                locked strategy/seed/budget/range config
trials.jsonl                         append-only evaluated trial ledger
candidates.jsonl                     append-only proposed candidate ledger
best_summary.json                    current best evaluated trial
candidate_plan_lhc_seed*_budget*.json deterministic LHC plan
candidate_plan_random_seed*_budget*.json deterministic random plan
trials/<run_id>/trial_summary.json   per-trial result snapshot
```

LHC/random plans are fixed by `strategy + seed + budget`, so interrupted runs
can resume the same candidate sequence. BO rereads `trials.jsonl` after every
trial, rebuilds the surrogate from all successful observations, and then
chooses the next candidate. This is important because BO candidates are
result-dependent and should not be planned as a static batch.

`optimizer_config.json` prevents accidentally mixing different seeds, budgets,
BO initialization counts, candidate-pool sizes, tuned keys, or search ranges in
one experiment directory. Use a new `--experiment-dir` for every independent
seed/method run.

Examples:

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
  --count 50 `
  --budget 50 `
  --bo-init 15 `
  --seed 1 `
  --engine MATLAB_58352 `
  --experiment-dir llm_mpc_bo/results/experiments/standard_slalom_4d_bo_qr0_budget50_seed1
```

Dry-run can be used to inspect the next candidates without running CarMaker:

```powershell
py -3.12 llm_mpc_bo/scripts/mpc_experiment_cli.py `
  --strategy bo `
  --count 50 `
  --budget 50 `
  --max-new-trials 3 `
  --bo-init 15 `
  --seed 1 `
  --experiment-dir llm_mpc_bo/results/experiments/standard_slalom_4d_bo_qr0_budget50_seed1 `
  --dry-run
```
