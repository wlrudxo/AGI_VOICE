# Standard Slalom Experiment Results

Updated: 2026-06-07

This file is the compact running summary of formal/near-formal experiment
results. Raw trial ledgers stay under `llm_mpc_bo/results/experiments/`.

## Current Objective and Scenario

Scenario:

```text
LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL
```

Tuned variables:

```text
[q_y, q_psi, q_r, r_delta, r_d_delta]
```

Objective:

```text
summary.objective.JFailClosed
```

Lower is better. Pylon hits dominate the current objective through a
`10 * pylonHits` penalty.

## LHC Seed 1, 100 Trials

Experiment:

```text
method: lhc
seed: 1
budget: 100
experimentDir: llm_mpc_bo/results/experiments/standard_slalom_lhc_seed1
completedAt: 2026-06-07 17:28 KST
```

Aggregate:

| Metric | Value |
| --- | ---: |
| Trials | 100 |
| Successful CLI rows | 100 |
| SIM_END | 93 |
| SIM_ABORT | 7 |
| `pylonHits = 0` | 2 |
| `pylonHits = 1` | 6 |
| `pylonHits <= 2` | 18 |

Best trial:

```text
runId: lhc_0063
J: 1.8451184758
status: SIM_END
pylonHits: 0
rmseET: 0.234335 m
maxAbsET: 0.703587 m
rmseDelta: 1.452810 rad
rmseDeltaRate: 4.766123 rad/s
maxYawRate: 0.714710 rad/s
```

Best parameters:

| Parameter | Value |
| --- | ---: |
| `q_y` | 0.3454284635 |
| `q_psi` | 1.1142697694 |
| `q_r` | 0.0252179705 |
| `r_delta` | 0.0161324102 |
| `r_d_delta` | 0.0217416626 |

Generated check plots:

```text
llm_mpc_bo/results/experiments/standard_slalom_lhc_seed1/objective_by_episode.png
llm_mpc_bo/results/experiments/standard_slalom_replay_lhc0063/trials/replay_lhc0063/trajectory_pylons.png
llm_mpc_bo/results/experiments/standard_slalom_replay_lhc0063/trials/replay_lhc0063/trial_time_signals.png
```

Interpretation:

- LHC seed 1 is a strong non-adaptive baseline; it found a clean pylon-free run.
- Because LHC is mainly a coverage/failure baseline, 100 trials is useful for
  the first full baseline, but later repeated-seed experiments can reasonably
  reduce LHC to 50 trials if runtime or paper scope becomes tight.
- `lhc_0063` is a good reference trajectory for visual comparison and for
  checking whether BO/Hybrid BO improves beyond a strong sampled baseline.

Top 10 trials by objective:

| Rank | Iter | J | Status | Pylons | RMSE e_t | Max e_t |
| ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | 63 | 1.8451 | SIM_END | 0 | 0.2343 | 0.7036 |
| 2 | 81 | 11.8690 | SIM_END | 1 | 0.2262 | 0.7898 |
| 3 | 86 | 12.1322 | SIM_END | 1 | 0.2619 | 0.9719 |
| 4 | 90 | 12.1581 | SIM_END | 1 | 0.2725 | 0.9103 |
| 5 | 85 | 12.4485 | SIM_END | 1 | 0.2979 | 1.1779 |
| 6 | 64 | 12.5481 | SIM_END | 1 | 0.3165 | 1.2141 |
| 7 | 51 | 12.5839 | SIM_END | 1 | 0.3236 | 1.2302 |
| 8 | 75 | 22.0954 | SIM_END | 2 | 0.2785 | 0.8671 |
| 9 | 8 | 22.4129 | SIM_END | 2 | 0.3083 | 1.0751 |
| 10 | 97 | 22.5837 | SIM_END | 2 | 0.3317 | 1.1868 |
