# Experiment Log 2026-06-08

## Purpose

Re-run the original broad 5D nominal slalom BO experiment after restoring the
MPC prediction-model steering command calibration.

The failed broad-space runs from 2026-06-07 were confounded by removing the
MPC model input calibration factor. The restored condition is:

```text
steeringCmdInputScale = 20 in init_slalom_mpc.m
Simulink steering Gain = 1
```

This scale is fixed model calibration, not an optimization variable.

## Current Test

Scenario:

```text
LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL
```

Controller setup:

```text
MPC output: VhclCtrl.Steering.Ang [rad]
MV.Min/Max: [-12, 12] rad
MV.RateMin/RateMax: [-10, 10] rad/s
```

Search space:

```text
5D weights = [q_y, q_psi, q_r, r_delta, r_d_delta]
all weights in [0.01, 100], log scale
```

BO plan:

```text
strategy: bo
budget: 100
bo_init: 30
seed: 1
experiment_dir: llm_mpc_bo/results/experiments/standard_slalom_bo_scale20_rate10_range001_100_seed1
```

Success criterion:

```text
pylonHits = 0
SIM_END
```

## Notes

- `q_r=1e-6` and `q_r=0.01` both reproduced the previous pylon-free bo_0071
  behavior under `steeringCmdInputScale=20` and rate `[-0.6, 0.6]`.
- `q_r=100` strongly suppressed steering and failed with 10 pylon hits under the
  same calibrated condition.
- This run intentionally keeps `q_r` in the 5D search to test whether BO can
  handle the broad equal log-scale space once the model calibration is restored.

## LowMu07 Calibrated BO Observation

Scenario:

```text
LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu07
```

Setup:

```text
steeringCmdInputScale = 20
Simulink steering Gain = 1
MV.Min/Max = [-12, 12] rad
MV.RateMin/RateMax = [-10, 10] rad/s
5D weights in [0.01, 100], log scale
BO init = 30
target budget = 100
```

Manual/IPG-driver baseline for LowMu07 finished with 4 pylon hits. The
calibrated BO run also reached a best result of 4 pylon hits:

```text
best run: bo_0063
J: 41.496
pylonHits: 4
status: SIM_END
q_y: 9.514
q_psi: 31.97
q_r: 0.01
r_delta: 0.01
r_d_delta: 0.2175
```

Interpretation:

- BO is active and parameter-sensitive, but the best front-steering-only MPC
  result did not improve the pylon-hit count beyond the manual/IPG-driver
  baseline under LowMu07.
- Best candidates repeatedly push `q_r` and `r_delta` toward low values.
- A reduced 4D follow-up with fixed/removed `q_r` and a 50-trial budget is the
  next efficient experiment design.

Process note:

- The first resume command used the old CLI semantics where `--count` meant
  "new trials to append", so the run continued past 100 trials.
- `mpc_experiment_cli.py` was updated so `--count` now means target total
  completed trials. Use `--max-new-trials` only for interactive short
  continuations.
