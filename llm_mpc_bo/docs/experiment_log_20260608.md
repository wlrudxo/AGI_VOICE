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

## Standard Slalom 4D qr0 BO Budget50

Scenario:

```text
LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL
```

Setup:

```text
steeringCmdInputScale = 20
Simulink steering Gain = 1
MV.Min/Max = [-12, 12] rad
MV.RateMin/RateMax = [-10, 10] rad/s
q_r = 0 fixed/removed from search
4D weights in [0.01, 100], log scale
BO init = 15
budget = 50
seed = 1
experiment_dir = llm_mpc_bo/results/experiments/standard_slalom_4d_bo_qr0_budget50_seed1
```

Run note:

- Started with shared engine `MATLAB_25884`.
- The first run stopped after 17 completed trials when that engine raised a
  MATLAB `Unknown exception` during iteration 18.
- `MATLAB_25884` disappeared and the active shared engine became
  `MATLAB_6952`; the run resumed from the target-count ledger and completed
  through 50 trials.
- Iteration 18 produced `SIM_END` output files and was ultimately recorded in
  the ledger during the resumed run.

Result:

```text
completed trials: 50
ok trials: 50
status counts: SIM_END 49, SIM_ABORT 1
zero-pylon trials: 18
best run: bo_0046
J: 1.105666
pylonHits: 0
status: SIM_END
q_y: 12.2943
q_psi: 28.7875
r_delta: 0.133960
r_d_delta: 0.0285438
```

Artifacts:

```text
best_summary.json
objective_by_episode.png
best_trajectory_pylons.png
best_trial_time_signals.png
```

## Runtime and Resume Workflow Updates

Changes made during the V61 follow-up:

- `mpc_trial_cli.py` now records per-trial timing breakdowns in each
  `trials.jsonl` row.
- `mpc_experiment_cli.py --load-testrun` now loads the CarMaker TestRun once at
  the batch level by default instead of reloading it inside every trial
  subprocess.
- The old per-trial reload behavior remains available with
  `--reload-testrun-each-trial`.
- Existing experiment directories can now be resumed with a larger `--budget`
  when all other optimizer settings are unchanged. This enabled extending the
  V61 BO run from 50 to 150 total trials.

Timing observation from 3-trial smoke tests:

```text
per-trial LoadTestRun:
  loadTestrunWallS avg: 0.846 s/trial
  load + MATLAB avg: 10.45 s/trial

batch load once:
  loadTestrunWallS in trial rows: 0
  MATLAB avg: 9.801 s/trial
```

The dominant runtime cost remains the CarMaker/Simulink `sim(mdl)` call, with
`analyze_results_mat` as the next largest repeated cost.

## Speed-Increased TestRun Variants

The original TestRun was copied in the CarMaker project to create speed variants
outside the Git repository:

```text
source:
E:\CarMakerProject\AGI\Data\TestRun\LLM_MPC_BO\ICCAS_Slalom18m_UserSteer_CM4SL

V61:
E:\CarMakerProject\AGI\Data\TestRun\LLM_MPC_BO\ICCAS_Slalom18m_UserSteer_CM4SL_V61
Driver.Vel.CruisingSpeed = 61

V64:
E:\CarMakerProject\AGI\Data\TestRun\LLM_MPC_BO\ICCAS_Slalom18m_UserSteer_CM4SL_V64
Driver.Vel.CruisingSpeed = 64
```

The first V61/V64 checks were run while manual steering was still enabled and
should not be treated as MPC-only results. After manual steering was disabled,
the previous V58 BO best (`bo_0046`) was replayed on V61:

```text
scenario: LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL_V61
experiment_dir: llm_mpc_bo/results/experiments/single_trial_v61_bo0046_mpc
params source: standard_slalom_4d_bo_qr0_budget50_seed1 best bo_0046

J: 11.1768
pylonHits: 1
status: SIM_END
meanSpeed: 49.62 km/h
q_y: 12.2943
q_psi: 28.7875
r_delta: 0.133960
r_d_delta: 0.0285438
```

Interpretation:

- V61 is a useful intermediate difficulty: the V58 best no longer completes
  pylon-free, but it remains near the boundary with one pylon hit.
- V64 was more aggressive and produced four pylon hits in the preliminary
  replay, so V61 was selected for the next LHC/BO comparisons.

## V61 4D qr0 LHC Budget50

Scenario:

```text
LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL_V61
```

Setup:

```text
q_r = 0 fixed/removed from search
4D weights in [0.01, 100], log scale
strategy = lhc
budget = 50
seed = 1
experiment_dir = llm_mpc_bo/results/experiments/standard_slalom_v61_4d_lhc_qr0_budget50_seed1
```

Result:

```text
completed trials: 50
ok trials: 50
status counts: SIM_END 39, SIM_ABORT 11
zero-pylon trials: 1
best run: lhc_0025
J: 11.5053
pylonHits: 1
status: SIM_END
q_y: 19.0285
q_psi: 11.5477
r_delta: 0.0700846
r_d_delta: 1.30613
```

The single zero-pylon LHC trial was not the best valid outcome because the best
valid objective still had one pylon hit. LHC confirmed V61 is substantially
harder than V58.

## V61 4D qr0 BO Budget150

The V61 BO run started with a 50-trial target and was later extended to 150
total trials to test whether the remaining one-pylon result was a budget issue.

Setup:

```text
scenario: LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL_V61
q_r = 0 fixed/removed from search
4D weights in [0.01, 100], log scale
strategy = bo
BO init = 15
seed = 1
experiment_dir = llm_mpc_bo/results/experiments/standard_slalom_v61_4d_bo_qr0_budget50_seed1
final target count: 150
```

Interim 50-trial result:

```text
completed trials: 50
zero-pylon trials: 2
best run: bo_0049
J: 11.4681
pylonHits: 1
status: SIM_END
q_y: 1.54163
q_psi: 1.41200
r_delta: 0.0313211
r_d_delta: 0.0110932
```

Final 150-trial result:

```text
completed trials: 150
ok trials: 150
status counts: SIM_END 136, SIM_ABORT 14
zero-pylon trials: 5
zero-pylon SIM_END trials: 0
best run: bo_0088
J: 11.3866
pylonHits: 1
status: SIM_END
q_y: 93.8685
q_psi: 0.0449184
r_delta: 1.18758
r_d_delta: 0.102389
```

Top valid BO trials all remained at one pylon hit:

```text
bo_0088  J=11.3866  pylonHits=1
bo_0049  J=11.4681  pylonHits=1
bo_0140  J=11.4849  pylonHits=1
bo_0054  J=11.4870  pylonHits=1
bo_0063  J=11.4895  pylonHits=1
```

The five zero-pylon rows were all `SIM_ABORT`, so they are not valid
pylon-free completions.

Interpretation:

- Extending BO from 50 to 150 trials did not find a valid pylon-free completion.
- The limiting factor is probably not BO budget alone.
- V61 appears to expose a structural limitation of the current
  lateral-only/front-steering MPC plus fixed reference setup: the optimizer
  repeatedly finds near-boundary one-pylon solutions but not a clean
  completion.
- Further progress likely requires problem-definition changes, such as
  pylon-safe reference margins, lateral corridor constraints, or including
  longitudinal speed control in the optimization problem.

Open direction:

- A low-mu safe-performance formulation may be more meaningful than another
  fixed-speed lateral-only sweep.
- Candidate formulation: tune lateral MPC weights plus `speedScale`, reward
  speed only for pylon-free completions, and keep large penalties for pylon
  hits and `SIM_ABORT`.

## LLM-Only V61 Runtime Notes

The first two LLM-only V61 4D runs were executed through the separated
`AI_AUTO_Calibration` workspace and then archived under
`llm_mpc_bo/results/experiments/`.

```text
standard_slalom_v61_4d_llm_only_seed1
elapsed wall-clock: 28 min 22 s
completed trials: 50
successful trials: 30
best J: 1.3666374633557083
best run: llm_only_0034
Codex token usage: total=374567, input=336259, cached_input=7660032, output=38308, reasoning_output=3250

standard_slalom_v61_4d_llm_only_seed2
elapsed wall-clock: 33 min 42 s
completed trials: 50
successful trials: 30
best J: 1.2382963821899589
best run: llm_only_0049
Codex token usage: total=281843, input=249407, cached_input=5895936, output=32436, reasoning_output=1847

standard_slalom_v61_4d_llm_only_seed3
elapsed wall-clock: 34 min 18 s
completed trials: 50
successful trials: 0
best J: 11.27568330553485
best run: llm_only_0035
best pylonHits: 1
Codex token usage: total=287955, input=255426, cached_input=5151872, output=32529, reasoning_output=2408

standard_slalom_v61_4d_llm_only_seed4
elapsed wall-clock: about 32 min
completed trials: 50
successful trials: 25
best J: 1.190583334580786
best run: llm_only_0046
best pylonHits: 0
Codex goal usage: total=223581

standard_slalom_v61_4d_llm_only_seed5
elapsed wall-clock: 29 min 34 s
completed trials: 50
successful trials: 16
best J: 1.1763721380276833
best run: llm_only_0047 / llm_only_0050 tie
best pylonHits: 0
Codex token usage: total=244573, input=220280, cached_input=2375552, output=24293, reasoning_output=1665
```

These wall-clock values may be useful later when comparing LLM-only overhead
against BO/LHC/random baselines. They include agent reasoning and sequential
tool execution, not just CarMaker simulation time.

## Sobol Landscape-Audit Setup

Added `sobol` as a resumable `mpc_experiment_cli.py --strategy` option for a
V61 4D landscape audit. The implementation is pure Python and works
under the Python 3.12 MATLAB-engine environment, so it does not require SciPy
during trial execution.

Validation performed:

```text
Python 3.12 py_compile: pass
Sobol dry-run count=8 budget=8: pass
Sobol dry-run count=1024 budget=1024 max-new-trials=1: pass
Generated plan length: 1024
Normalized per-dimension range: approximately [0, 0.999]
```

Audit command is documented in `llm_mpc_bo/README.md`. Treat Sobol 1024 as a
landscape audit for local-region/feasibility structure, not as another adaptive
optimizer baseline.

## Sobol Landscape-Audit Completion

Completed `standard_slalom_v61_4d_sobol_entryignored_budget1024_seed1`.

```text
total trials: 1024
ok records: 1024
SIM_END: 775
road-departure/fail records: 249
pylon-free completions: 2
best run: sobol_0279
best J: 1.3736389747278646
best pylonHits: 0
best params:
  q_y = 7.914755447897558
  q_psi = 0.04141784518805329
  r_delta = 0.06853895845998999
  r_d_delta = 0.11341944047188682
best diagnostics:
  rmseET = 0.20939653435589176
  maxAbsET = 0.7634938112106826
  rmseEPsi = 0.030861186339791277
  rmseDelta = 1.654457782846247
  rmseDeltaRate = 11.870396139126475
  maxYawRate = 0.8094310738119657
```

The second pylon-free Sobol point was `sobol_0219` with `J=1.379176`. Both
pylon-free Sobol points are in low-heading-weight regions, supporting the
interpretation that the landscape contains non-intuitive feasible local regions
that are unlikely to be selected by LLM-based physical reasoning alone.

## Zero-Hit Local-Region Summary

Collected all `SIM_END` trials with evaluated `pylonHits=0` from the current
nominal 4D result set:

```text
BO: 4
LHC: 1
Random: 0
LLM-based: 101
Sobol: 2
BO-advised LLM: 0
total: 108
```

The points were grouped in 4D log-scaled weight space
`log10(q_y), log10(q_psi), log10(r_delta), log10(r_d_delta)`. With a connected
distance threshold around `0.65`, the non-overlapping representative regions are:

| Region | Found by | Zero-hit pts | Rep. J | q_y | q_psi | r_delta | r_d_delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| R1 BO aggressive high-heading | BO | 1 | 0.7399 | 13.321 | 89.758 | 0.0114 | 0.0126 |
| R2 LLM-based high-heading | LLM-based, BO | 102 | 1.1764 | 80.000 | 45.765 | 0.1000 | 0.8000 |
| R3 low-heading mid-penalty | BO, LHC, Sobol | 3 | 1.3714 | 56.001 | 0.0459 | 0.3501 | 0.9510 |
| R4 Sobol low-heading low-penalty | Sobol | 1 | 1.3736 | 7.915 | 0.0414 | 0.0685 | 0.1134 |
| R5 BO low-heading high-q_y | BO | 1 | 1.3848 | 86.585 | 0.0406 | 0.0209 | 1.7583 |

Interpretation for the paper:

- LLM-based search densely exploited one high-heading feasible local region.
- BO found the best current objective in a separate aggressive high-heading
  region.
- BO, LHC, and Sobol also revealed several low-heading feasible local regions.
- Random and BO-advised LLM produced no pylon-free representative point in the
  current result set.

## Axis-Wise Local Tolerance Scan

Completed one-axis-at-a-time log-space tolerance scans around the five
representative zero-hit regions. Each scan used the representative center plus
`+-0.1, +-0.2, +-0.3, +-0.4` decade perturbations on one variable at a time,
with the remaining three variables fixed. This is a local sensitivity check, not
a full 4D robustness volume estimate.

```text
scan budget per region: 33 trials
variables: q_y, q_psi, r_delta, r_d_delta
search bounds: [0.01, 100] for each variable
TestRun: LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL_V61
engine: MATLAB_58008
```

| Region | Center J | Best scanned J | zero-hit trials / 33 | q_y zero range | q_psi zero range | r_delta zero range | r_d_delta zero range |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| R1 BO aggressive high-heading | 0.7399 | 0.6993 | 9 | none | none | -0.4 to -0.1 | -0.4 to -0.1 |
| R2 LLM-based high-heading | 1.1764 | 1.1764 | 2 | none | -0.1 only | none | none |
| R3 low-heading mid-penalty | 1.3714 | 1.3714 | 9 | none | -0.4 to +0.4 | none | none |
| R4 Sobol low-heading low-penalty | 1.3736 | 1.3736 | 9 | none | -0.4 to +0.4 | none | none |
| R5 BO low-heading high-q_y | 1.3848 | 1.3847 | 17 | none | -0.4 to +0.4 | -0.4 to +0.4 | none |

Interpretation:

- R1 has the best objective found so far, but it is sharp in `q_y` and `q_psi`.
  Lowering `r_delta` or `r_d_delta` toward the search lower bound preserves
  zero-hit behavior and slightly improves J.
- R2 is a narrow LLM-based high-heading region. Only a small decrease in
  `q_psi` preserved zero-hit behavior among the tested single-axis changes.
- R3 and R4 show the same low-heading pattern: `q_psi` is almost irrelevant over
  the tested local range, while changing `q_y`, `r_delta`, or `r_d_delta` causes
  pylon contact.
- R5 is the widest scanned local minimum area among the representatives:
  `q_psi` and `r_delta` both tolerate the full tested `+-0.4` decade range, but
  `q_y` and `r_d_delta` remain sensitive.

This supports a more precise paper claim: the pylon-free objective does not have
one smooth region. It contains several separated local minimum areas with
different local sensitivities. Some are sharp high-performance points, while
others are wider but have higher objective values.
