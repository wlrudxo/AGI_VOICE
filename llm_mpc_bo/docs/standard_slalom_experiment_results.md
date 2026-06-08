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

## Current Comparison

| Method | Seed | Trials | SIM_END | SIM_ABORT | Pylon-free | `pylonHits <= 2` | Best run | Best J | Best RMSE e_t | Best max e_t |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| LHC | 1 | 100 | 93 | 7 | 2 | 18 | `lhc_0063` | 1.8451 | 0.2343 | 0.7036 |
| BO, 30 LHC init + 70 EI | 1 | 100 | 99 | 1 | 13 | 40 | `bo_0071` | 1.6997 | 0.2082 | 0.6969 |
| Random | 1 | 100 | 91 | 9 | 2 | 16 | `random_0083` | 2.3219 | 0.2924 | 1.0648 |

Interpretation:

- BO is currently the strongest non-LLM optimizer on this scenario: it improved
  best `J`, produced more pylon-free candidates, and had fewer aborts than LHC
  or random search under the same 100-trial budget.
- Random search remains useful as a plain sampling baseline, but it is weaker
  than LHC and BO in this seed.
- Keep `boInit=30` for the main experiment. A `boInit` ablation such as
  10/20/30/50 is methodologically valid, but it is a secondary study rather
  than necessary for the first comparison.

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
llm_mpc_bo/results/experiments/standard_slalom_lhc_seed1/best_trajectory_pylons.png
llm_mpc_bo/results/experiments/standard_slalom_lhc_seed1/best_trial_time_signals.png
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

## BO Seed 1, 100 Trials

Experiment:

```text
method: bo
seed: 1
budget: 100
boInit: 30
experimentDir: llm_mpc_bo/results/experiments/standard_slalom_bo_seed1
completedAt: 2026-06-07 18:17 KST
```

Aggregate:

| Metric | Value |
| --- | ---: |
| Trials | 100 |
| Successful CLI rows | 100 |
| SIM_END | 99 |
| SIM_ABORT | 1 |
| `pylonHits = 0` | 13 |
| `pylonHits = 1` | 11 |
| `pylonHits <= 2` | 40 |

Best trial:

```text
runId: bo_0071
J: 1.6996505791
status: SIM_END
pylonHits: 0
rmseET: 0.208163 m
maxAbsET: 0.6968829 m
rmseDelta: 1.373435 rad
rmseDeltaRate: 4.569954 rad/s
maxYawRate: 0.699621 rad/s
```

Best parameters:

| Parameter | Value |
| --- | ---: |
| `q_y` | 3.0285391641 |
| `q_psi` | 14.1305688054 |
| `q_r` | 0.0100000000 |
| `r_delta` | 0.0192763649 |
| `r_d_delta` | 0.3122725205 |

Generated check plot:

```text
llm_mpc_bo/results/experiments/standard_slalom_bo_seed1/objective_by_episode.png
llm_mpc_bo/results/experiments/standard_slalom_bo_seed1/best_trajectory_pylons.png
llm_mpc_bo/results/experiments/standard_slalom_bo_seed1/best_trial_time_signals.png
```

Interpretation:

- BO seed 1 improved slightly beyond the best LHC seed 1 result within the same
  100-trial budget.
- The current best BO trial is pylon-free and keeps the same direct
  steering-wheel-angle convention as the rest of the formal experiments.

## Random Seed 1, 100 Trials

Experiment:

```text
method: random
seed: 1
budget: 100
experimentDir: llm_mpc_bo/results/experiments/standard_slalom_random_seed1
completedAt: 2026-06-07 18:46 KST
```

Aggregate:

| Metric | Value |
| --- | ---: |
| Trials | 100 |
| Successful CLI rows | 100 |
| SIM_END | 91 |
| SIM_ABORT | 9 |
| `pylonHits = 0` | 2 |
| `pylonHits = 1` | 5 |
| `pylonHits <= 2` | 16 |

Best trial:

```text
runId: random_0083
J: 2.3218586095
status: SIM_END
pylonHits: 0
rmseET: 0.292382 m
maxAbsET: 1.064809 m
rmseDelta: 1.615388 rad
rmseDeltaRate: 4.597987 rad/s
maxYawRate: 0.713366 rad/s
```

Best parameters:

| Parameter | Value |
| --- | ---: |
| `q_y` | 44.5685708544 |
| `q_psi` | 0.8617992177 |
| `q_r` | 2.5592018542 |
| `r_delta` | 3.5234926302 |
| `r_d_delta` | 0.1302695738 |

Generated check plot:

```text
llm_mpc_bo/results/experiments/standard_slalom_random_seed1/objective_by_episode.png
llm_mpc_bo/results/experiments/standard_slalom_random_seed1/best_trajectory_pylons.png
llm_mpc_bo/results/experiments/standard_slalom_random_seed1/best_trial_time_signals.png
```

Top 10 trials by objective:

| Rank | Iter | J | Status | Pylons | RMSE e_t | Max e_t |
| ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | 83 | 2.3219 | SIM_END | 0 | 0.2924 | 1.0648 |
| 2 | 50 | 11.8063 | SIM_END | 1 | 0.2214 | 0.7617 |
| 3 | 76 | 12.0118 | SIM_END | 1 | 0.2562 | 0.7967 |
| 4 | 60 | 12.0586 | SIM_END | 1 | 0.2602 | 0.9154 |
| 5 | 52 | 12.3518 | SIM_END | 1 | 0.2969 | 0.9698 |
| 6 | 80 | 12.5686 | SIM_END | 1 | 0.3403 | 1.1185 |
| 7 | 78 | 22.6536 | SIM_END | 2 | 0.3256 | 1.3118 |
| 8 | 92 | 22.8952 | SIM_END | 2 | 0.3436 | 1.7039 |
| 9 | 19 | 23.0127 | SIM_END | 2 | 0.3675 | 1.6408 |
| 10 | 51 | 23.2565 | SIM_END | 2 | 0.3932 | 1.9403 |

## LowMu06 BO Seed 1, 150 Trials, Rate Limit 0.6 rad/s

Experiment:

```text
method: bo
seed: 1
budget: 150
boInit: 50
scenario: LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu06
experimentDir: llm_mpc_bo/results/experiments/lowmu06_bo_seed1
completedAt: 2026-06-07 19:52 KST
```

Best trial:

```text
runId: bo_0081
J: 53.6016778463
status: SIM_END
pylonHits: 5
rmseET: 0.550112 m
maxAbsET: 1.749648 m
mvRateMin/Max: [-0.6, 0.6] rad/s
```

Interpretation:

- The controller improved tracking compared with the manual LowMu06 run, but
  did not approach the manual pylon-hit count of 2.
- Manual steering stayed within the `±12 rad` angle limit but exceeded the
  `±0.6 rad/s` rate limit frequently, so the next run relaxes the fixed
  steering-wheel rate constraint to `±10 rad/s`.

## LowMu06 BO Seed 1, 150 Trials, Rate Limit 10 rad/s

Experiment:

```text
method: bo
seed: 1
budget: 150
boInit: 50
scenario: LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_LowMu06
experimentDir: llm_mpc_bo/results/experiments/lowmu06_bo_rate10_seed1
completedAt: 2026-06-07 20:37 KST
```

Aggregate:

| Metric | Value |
| --- | ---: |
| Trials | 150 |
| Successful CLI rows | 150 |
| Minimum pylon hits | 5 |
| `pylonHits = 5` | 17 |
| `pylonHits <= 4` | 0 |

Best trial:

```text
runId: bo_0046
J: 51.8673143817
status: SIM_END
pylonHits: 5
rmseET: 0.244035 m
maxAbsET: 0.810291 m
rmseDelta: 1.756321 rad
rmseDeltaRate: 10.709694 rad/s
mvRateMin/Max: [-10, 10] rad/s
```

Best parameters:

| Parameter | Value |
| --- | ---: |
| `q_y` | 8.5728823207 |
| `q_psi` | 1.3806865208 |
| `q_r` | 0.1377094269 |
| `r_delta` | 0.0463628419 |
| `r_d_delta` | 0.1764682553 |

Interpretation:

- Relaxing the steering-rate constraint improved the best tracking metrics, but
  did not reduce pylon contacts below 5.
- The best result appeared at iteration 46; later BO iterations did not break
  the 5-hit plateau.
- This run used the previous search range
  `q_y,q_psi=[0.1,100]`, `q_r=[0.01,30]`,
  `r_delta,r_d_delta=[0.01,10]`. It should be treated as a LowMu06 stress-test
  result, not as the final widened-range formal setting.

Next planned formal setting:

```text
Scenario: nominal Slalom18m/UserSteer unless explicitly running a stress test
Steering constraints: MV.Min/Max = [-12, 12] rad
Steering rate constraints: MV.RateMin/Max = [-10, 10] rad/s
No steering ratio, input scale, or Vx_model tuning variable
Weight ranges:
  all five MPC weights: [0.01, 100] on a logarithmic scale
```
