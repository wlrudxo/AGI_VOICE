# Experiment Report: V61 4D Entry-Ignored Slalom MPC

Updated: 2026-06-08

This document collects detailed experiment results for paper preparation for the nominal V61
slalom MPC tuning experiments. It is separate from the chronological experiment
log. Raw ledgers and plots are archived under
`llm_mpc_bo/results/experiments/`.

## Experiment Setting

```text
scenario: LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL_V61
task: CarMaker/Simulink slalom path tracking
evaluation target: SIM_END with evaluated pylonHits = 0
entry pylon contacts: ignored by objective
tuned variables: q_y, q_psi, r_delta, r_d_delta
fixed variable: q_r = 0
search range: [0.01, 100]^4, log scale
budget per seed: 50 trials
steeringCmdInputScale: 20
Simulink steering Gain: 1
MV.Min/Max: [-12, 12] rad
MV.RateMin/RateMax: [-10, 10] rad/s
```

Success means `status = SIM_END` and evaluated `pylonHits = 0`.

## Method-Level Summary

| Method | Seeds | Trials | Successes | Success rate | Mean successes/seed | Best J | Mean best J | SIM_ABORT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BO | 5 | 250 | 4 | 1.6% | 0.8 | 0.739914 | 5.198448 | 24 |
| LHC | 5 | 250 | 1 | 0.4% | 0.2 | 1.378332 | 9.451911 | 70 |
| Random | 5 | 250 | 0 | 0.0% | 0.0 | 11.169761 | 11.401798 | 70 |
| LLM-only | 5 | 250 | 101 | 40.4% | 20.2 | 1.176372 | 3.249514 | 2 |

Current interpretation:

- LLM-only found feasible pylon-free completions in four of five completed
  runs, with a much higher aggregate success count than the non-LLM baselines.
- BO still has the best single objective value (`J = 0.739914`, seed 3), which
  suggests stronger global search for low-cost basins once feasibility is found.
- LLM-only tends to exploit a local or near-feasible region after early
  discovery; this is useful evidence for a BO/LLM hybrid method rather than a
  replacement claim.
- The LLM-only result now has the same five-seed count as BO/LHC/Random. The
  qualitative pattern remains that LLM-only often exploits a discovered basin
  locally, while BO found the best current objective basin.

## Per-Seed Summary

| Method | Seed | Trials | SIM_END | SIM_ABORT | Successes | First success | Best run | Best J | Best pylons | RMSE e_t | Max e_t |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| BO | 1 | 50 | 45 | 5 | 1 | 19 | `bo_0019` | 1.377916 | 0 | 0.209008 | 0.784338 |
| BO | 2 | 50 | 46 | 4 | 1 | 39 | `bo_0039` | 1.384815 | 0 | 0.211304 | 0.769277 |
| BO | 3 | 50 | 44 | 6 | 2 | 33 | `bo_0049` | 0.739914 | 0 | 0.101015 | 0.537901 |
| BO | 4 | 50 | 48 | 2 | 0 | - | `bo_0050` | 11.143010 | 1 | 0.165090 | 0.766224 |
| BO | 5 | 50 | 43 | 7 | 0 | - | `bo_0045` | 11.346586 | 1 | 0.201196 | 0.830165 |
| LHC | 1 | 50 | 39 | 11 | 0 | - | `lhc_0016` | 11.392684 | 1 | 0.213554 | 0.763716 |
| LHC | 2 | 50 | 41 | 9 | 0 | - | `lhc_0025` | 11.201139 | 1 | 0.174543 | 0.788346 |
| LHC | 3 | 50 | 37 | 13 | 1 | 50 | `lhc_0050` | 1.378332 | 0 | 0.210175 | 0.766850 |
| LHC | 4 | 50 | 32 | 18 | 0 | - | `lhc_0026` | 11.836667 | 1 | 0.278165 | 1.052340 |
| LHC | 5 | 50 | 31 | 19 | 0 | - | `lhc_0026` | 11.450731 | 1 | 0.218393 | 0.872151 |
| Random | 1 | 50 | 35 | 15 | 0 | - | `random_0013` | 11.581418 | 1 | 0.244422 | 0.869475 |
| Random | 2 | 50 | 36 | 14 | 0 | - | `random_0005` | 11.430121 | 1 | 0.214379 | 0.865331 |
| Random | 3 | 50 | 39 | 11 | 0 | - | `random_0044` | 11.169761 | 1 | 0.168124 | 0.793839 |
| Random | 4 | 50 | 31 | 19 | 0 | - | `random_0049` | 11.567218 | 1 | 0.238503 | 0.884086 |
| Random | 5 | 50 | 39 | 11 | 0 | - | `random_0011` | 11.260473 | 1 | 0.186875 | 0.797229 |
| LLM-only | 1 | 50 | 50 | 0 | 30 | 3 | `llm_only_0034` | 1.366637 | 0 | 0.208249 | 0.762440 |
| LLM-only | 2 | 50 | 50 | 0 | 30 | 3 | `llm_only_0049` | 1.238296 | 0 | 0.189263 | 0.697427 |
| LLM-only | 3 | 50 | 49 | 1 | 0 | - | `llm_only_0035` | 11.275683 | 1 | 0.190148 | 0.794170 |
| LLM-only | 4 | 50 | 49 | 1 | 25 | 15 | `llm_only_0046` | 1.190583 | 0 | 0.173547 | 0.782723 |
| LLM-only | 5 | 50 | 50 | 0 | 16 | 10 | `llm_only_0047` | 1.176372 | 0 | 0.170483 | 0.783559 |

Note: the LLM-only seed 1 ledger contains repeated best-parameter trials with
the same objective value. The archived `best_summary.json` points to
`llm_only_0034`, so that run is used as the representative best trial here.

## Best Parameters

| Method | Seed | Best run | q_y | q_psi | r_delta | r_d_delta |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| BO | 1 | `bo_0019` | 62.9582265 | 4.71519965 | 0.190087651 | 1.13420609 |
| BO | 2 | `bo_0039` | 86.5849400 | 0.0405614 | 0.0208786 | 1.75831520 |
| BO | 3 | `bo_0049` | 13.3212279 | 89.7584159 | 0.0114192 | 0.0125498 |
| BO | 4 | `bo_0050` | 10.7451587 | 0.4316210 | 0.0643997 | 0.0100000 |
| BO | 5 | `bo_0045` | 95.4025170 | 0.0606845 | 0.7933108 | 0.2250606 |
| LHC | 1 | `lhc_0016` | 45.3832237 | 0.0112911 | 0.5866160 | 0.0175066 |
| LHC | 2 | `lhc_0025` | 41.0104724 | 0.6336469 | 0.1763949 | 0.3416373 |
| LHC | 3 | `lhc_0050` | 29.1126739 | 0.2279453 | 0.1461200 | 0.5335709 |
| LHC | 4 | `lhc_0026` | 58.0041514 | 6.5484998 | 0.1684424 | 7.8299986 |
| LHC | 5 | `lhc_0026` | 5.2109660 | 0.4302695 | 0.0215424 | 0.0753124 |
| Random | 1 | `random_0013` | 20.8998309 | 4.7997903 | 0.1634835 | 2.2403838 |
| Random | 2 | `random_0005` | 62.7454000 | 1.5021323 | 0.6017509 | 0.1182941 |
| Random | 3 | `random_0044` | 16.7892526 | 0.2405089 | 0.0330184 | 0.1471538 |
| Random | 4 | `random_0049` | 0.7692021 | 1.2753653 | 0.0127519 | 0.0137004 |
| Random | 5 | `random_0011` | 37.5808597 | 0.1567312 | 0.2784580 | 0.0461131 |
| LLM-only | 1 | `llm_only_0034` | 25.0000000 | 10.0000000 | 0.0308000 | 0.5000000 |
| LLM-only | 2 | `llm_only_0049` | 15.7000000 | 25.0000000 | 0.1200000 | 0.2000000 |
| LLM-only | 3 | `llm_only_0035` | 8.9000000 | 8.9000000 | 0.0600000 | 0.0600000 |
| LLM-only | 4 | `llm_only_0046` | 45.0900000 | 20.2900000 | 0.1000000 | 0.4500000 |
| LLM-only | 5 | `llm_only_0047` | 80.0000000 | 45.7650000 | 0.1000000 | 0.8000000 |

## LLM-Only Seed 3 Collision Note

The best LLM-only seed 3 trial had two raw pylon contacts, but the first one was
an ignored entry contact. The objective counted one evaluated pylon hit.

```text
best run: llm_only_0035
raw pylon hits: 2
ignored entry pylon hits: 1
evaluated pylon hits: 1

ignored entry contact:
  time: 23.215 s
  sRoad: 290.835 m
  pylon position: x=300.0, y=1.5

evaluated contact:
  time: 27.671 s
  sRoad: 363.690 m
  pylon position: x=372.0, y=-0.25
  geometry: roadLayer=1, markerIndex=11, upper pylon,
            gateCenterY=-2.625, gateWidth=4.75
```

The trial also reported a likely road-departure event near `x=437.269`,
`y=-6.00078`, but this did not change the objective pylon-hit count.

## LLM-Only Runtime and Token Notes

| Run | Wall-clock | Total tokens | Input | Cached input | Output | Reasoning output |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LLM-only seed 1 | 28 min 22 s | 374,567 | 336,259 | 7,660,032 | 38,308 | 3,250 |
| LLM-only seed 2 | 33 min 42 s | 281,843 | 249,407 | 5,895,936 | 32,436 | 1,847 |
| LLM-only seed 3 | 34 min 18 s | 287,955 | 255,426 | 5,151,872 | 32,529 | 2,408 |
| LLM-only seed 4 | about 32 min | 223,581 | - | - | - | - |
| LLM-only seed 5 | 29 min 34 s | 244,573 | 220,280 | 2,375,552 | 24,293 | 1,665 |

These wall-clock values include agent reasoning and sequential trial-tool
execution, not just CarMaker simulation time.

## Archived Result Directories

```text
BO:
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_bo_entryignored_init15_seed1
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_bo_entryignored_budget50_seed2
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_bo_entryignored_budget50_seed3
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_bo_entryignored_budget50_seed4
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_bo_entryignored_budget50_seed5

LHC:
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_lhc_entryignored_budget50_seed1
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_lhc_entryignored_budget50_seed2
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_lhc_entryignored_budget50_seed3
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_lhc_entryignored_budget50_seed4
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_lhc_entryignored_budget50_seed5

Random:
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_random_entryignored_budget50_seed1
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_random_entryignored_budget50_seed2
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_random_entryignored_budget50_seed3
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_random_entryignored_budget50_seed4
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_random_entryignored_budget50_seed5

LLM-only:
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_llm_only_seed1
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_llm_only_seed2
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_llm_only_seed3
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_llm_only_seed4
llm_mpc_bo/results/experiments/standard_slalom_v61_4d_llm_only_seed5
```
