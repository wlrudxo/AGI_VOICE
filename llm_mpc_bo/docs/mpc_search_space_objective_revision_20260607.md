# MPC Search Space and Objective Revision Notes

Updated: 2026-06-07 23:42 KST

## Decision Summary

The current formal experiment direction is revised from an equal range for all
five MPC weights to an engineering-motivated state/control split:

```text
q_y       [0.1, 100]   log-scale
q_psi     [0.1, 100]   log-scale
q_r       [0.1, 100]   log-scale
r_delta   [0.01, 10]   log-scale
r_d_delta [0.01, 10]   log-scale
```

The outer-loop BO objective should also be simplified. The objective should rank
closed-loop trajectory quality and pylon avoidance, while steering angle/rate
usage should be treated mainly as MPC-internal regularization and as reported
secondary metrics.

Recommended outer-loop objective:

```text
J =
  failPenalty
  + 10.0 * pylonHits
  + 8.0  * RMSE_e_t
  + 3.0  * maxAbs_e_t
  + 1.0  * RMSE_e_psi
```

Suggested fail penalty terms remain separate and large enough to keep simulation
failure or hard collision below valid SIM_END trajectories:

```text
failPenalty = 100 * simFail
            + 50  * collisionDetected
            + 25  * collisionCount
```

If generic collision fields are unavailable or redundant for the current pylon
scenario, the pylon term remains the primary feasibility penalty.

## Rationale

### 1. State and control weights should not share one identical range

The previous equal-range setting:

```text
all five weights: [0.01, 50] log-scale
```

was useful as a broad naive-search stress test, but recent runs showed that it
can make LHC/BO spend many trials in regions with poor tracking or overly
suppressed steering. If all methods fail too severely, the result risks looking
like an unrealistic search-space design rather than a meaningful optimization
benchmark.

The revised split is more defensible from an MPC tuning perspective:

- State-tracking weights (`q_y`, `q_psi`, `q_r`) directly shape lateral/path
  tracking behavior and can reasonably use a higher range.
- Control effort/rate weights (`r_delta`, `r_d_delta`) regularize steering
  usage and smoothness, and should have a lower range so that the controller is
  not encouraged to under-steer in the slalom.
- The split is simple and systematic; it does not introduce a special exception
  for a single variable or tune the range around one observed best candidate.

Paper wording candidate:

> Since state-tracking penalties and control-effort penalties have different
> physical roles and numerical sensitivities, state weights were searched over
> `[0.1, 100]`, while input and input-rate penalties were searched over
> `[0.01, 10]`, all on a logarithmic scale.

### 2. Equal broad range can remain as an ablation/motivation setting

The equal `[0.01, 50]` range does not need to be deleted from the research story.
It can be reported as a naive broad-space ablation showing that non-adaptive
sampling and vanilla BO can waste simulation budget in poor regions when the
search space is too broad or poorly structured.

Recommended role:

```text
Main formal setting:  MPC-aware state/control split range
Ablation/motivation:  equal broad range [0.01, 50] for all weights
```

This preserves the motivation for LLM-assisted search-region reasoning without
making the main comparison depend on a possibly artificial failure-heavy space.

### 3. Pylon-free trials need tracking-based ranking separation

Current results indicate that once a run avoids pylons, scalar objective values
can become too close, e.g. roughly `1.6` vs `1.8`. This makes it hard to show a
clear difference between BO, random search, and LHC if they all eventually find
collision-free trajectories.

Therefore the outer-loop objective should emphasize trajectory tracking quality
after feasibility is achieved:

- `pylonHits` remains a primary feasibility penalty.
- `RMSE_e_t` and `maxAbs_e_t` should be weighted strongly enough to separate
  pylon-free trajectories.
- `RMSE_e_psi` remains a smaller heading-tracking term.

The objective should support the following interpretation:

> Pylon contacts are treated as a feasibility violation, while tracking errors
> rank feasible trajectories.

### 4. Delta and delta-rate terms should be removed from the main BO objective

`r_delta` and `r_d_delta` are already tunable MPC weights that penalize steering
angle and steering-rate usage inside the controller. Adding `RMSE_delta` and
`RMSE_deltaRate` directly to the outer-loop objective can double-count steering
regularization and may bias BO toward under-steering candidates that use less
control but fail to track the slalom.

Revised role split:

```text
MPC internal cost:
  - uses r_delta and r_d_delta to regulate steering effort/smoothness

BO outer objective:
  - evaluates closed-loop path-following success and pylon avoidance

Reported secondary metrics:
  - RMSE_delta
  - maxAbs_delta
  - RMSE_deltaRate
  - maxAbs_deltaRate
  - steering saturation ratio, if available
```

Paper wording candidate:

> Steering smoothness was controlled through the MPC input and input-rate weights
> and reported as a secondary metric, rather than being directly penalized in the
> outer-loop optimization objective.

## Recommended Experiment Structure

Use the revised mixed range and simplified objective for the next formal nominal
Slalom18m runs:

```text
1. Random search, mixed range
2. LHC, mixed range
3. Vanilla BO, mixed range
4. LLM-assisted BO, mixed range
```

Keep the previous equal-range runs as supporting evidence:

```text
Ablation: equal broad range [0.01, 50]
Purpose: show search-space sensitivity and failure-heavy naive broad tuning
```

Primary comparison metrics:

```text
- best J under the revised objective
- pylon-free trial count
- minimum pylonHits
- trials needed to first pylon-free run
- RMSE_e_t and maxAbs_e_t of best/feasible runs
- SIM_ABORT / simFail count
```

Secondary/report-only metrics:

```text
- RMSE_delta
- maxAbs_delta
- RMSE_deltaRate
- maxAbs_deltaRate
- steering saturation ratio
```

## Implementation Notes

Files likely requiring updates before the next formal run:

```text
llm_mpc_bo/scripts/mpc_experiment_cli.py
llm_mpc_bo/scripts/mpc_trial_cli.py
llm_mpc_bo/scripts/analyze_results_mat.m
```

Documentation to keep consistent:

```text
llm_mpc_bo/docs/standard_slalom_mpc_bo_experiment_plan.md
llm_mpc_bo/docs/iccas_slalom_mpc_llm_bo_plan.md
llm_mpc_bo/docs/standard_slalom_experiment_results.md
```
