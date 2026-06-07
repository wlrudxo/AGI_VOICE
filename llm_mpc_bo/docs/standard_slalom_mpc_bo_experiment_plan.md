# Standard Slalom MPC BO Experiment Plan

Updated: 2026-06-07

## Decision

Use the current standard CarMaker Slalom18m/UserSteer scenario as the main
research target.

Do not make low-friction or icy-road operation the main benchmark for the first
paper. LowMu can remain a stress-test or future-work extension after the nominal
Slalom18m workflow is stable.

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

The MPC plant input gain is scaled inside `init_slalom_mpc.m` so that the
controller output itself is in the same steering-wheel angle scale as the
CarMaker input.

## Fixed Constraints

Do not tune steering command constraints in the main experiment. Keep them as
fixed physical/safety limits:

```matlab
mpcobj.MV.Min = -12.0;
mpcobj.MV.Max =  12.0;
mpcobj.MV.RateMin = -0.6;
mpcobj.MV.RateMax =  0.6;
```

These values are steering wheel angle/rate limits in the MPC sample domain.

## Tuned Variables

Tune only MPC weight parameters:

```text
q_y
q_psi
q_r
r_delta
r_d_delta
```

Normalized BO vector order:

```text
[q_y, q_psi, q_r, r_delta, r_d_delta]
```

Initial search ranges:

| Variable | Meaning | Range | Scale |
| --- | --- | --- | --- |
| `q_y` | lateral error weight | `0.1 - 100` | log |
| `q_psi` | heading error weight | `0.1 - 100` | log |
| `q_r` | yaw-rate output weight | `0.01 - 30` | log |
| `r_delta` | steering wheel angle command weight | `0.01 - 10` | log |
| `r_d_delta` | steering wheel angle rate weight | `0.01 - 10` | log |

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

Use BO as the base optimizer and let the LLM assist by:

```text
proposing warm-start candidates
suggesting trust-region/range narrowing
explaining failed trials
choosing between BO candidate and LLM candidate
```

The hybrid method should still evaluate exactly one candidate per trial so that
trial counts are comparable.

## Trial Budget

Start with:

```text
30 trials per adaptive/search method
```

This is enough to prove the full pipeline and produce:

```text
best objective vs iteration
pylon hits vs iteration
best trajectory comparison
steering command comparison
method summary table
```

If runtime and stability are acceptable, extend to:

```text
50 trials per method
```

Recommended sequence:

```text
Phase 1: 30 trials, one seed, all methods
Phase 2: repeat the best two methods for 3 seeds
Phase 3: optional 50-trial rerun for final plots
```

## Objective

Use `summary.objective.JFailClosed` from:

```text
llm_mpc_bo/scripts/analyze_results_mat.m
```

The objective should be recalibrated for steering wheel angle scale. The current
implementation is usable for debugging but still over-penalizes steering command
and steering-rate after the controller output was corrected to steering wheel
angle units.

Recommended objective structure:

```text
J =
  lateral tracking term
  + heading/yaw smoothness term
  + steering wheel command smoothness term
  + pylon hit penalty
  + fail-closed simulation penalty
```

The first hard target is:

```text
pylon hits: 5 -> 0
SIM_END maintained
```

Then optimize tracking and smoothness.

## Current Verified Controller State

Current model/setup:

```text
Simulink steering Gain: 1
MPC output: steering wheel angle command [rad]
MPC plant input scale: internal input gain divided by 20
Constraints: fixed [-12, 12] rad, rate [-0.6, 0.6] rad/sample
```

Current checked parameter set:

```text
q_y = 30
q_psi = 10
q_r = 0.5
r_delta = 0.05
r_d_delta = 0.5
```

Latest result:

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

## Automation Direction

Ad-hoc MATLAB/Python snippets used during LLM-based control should be converted
into small CLI commands before running formal experiments.

Recommended CLI shape:

```text
llm_mpc_bo/scripts/mpc_trial_cli.py
  --engine MATLAB_58352
  --params-json ...
  --run-id ...
  --load-testrun false
  --analyze true
```

The CLI should:

```text
connect to a shared MATLAB engine
optionally load the CarMaker TestRun once
apply the 5 MPC weights
run sim('UserSteer')
analyze Results.mat + ERG
write trial_summary.json
return J/status/pylon hits on stdout
```

This keeps LLM-only and Hybrid BO experiments reproducible while still allowing
the LLM to reason over results and propose candidates.
