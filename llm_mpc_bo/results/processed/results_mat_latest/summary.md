# Results.mat Analysis

- Input: `E:\CarMakerProject\AGI\src_cm4sl\Results.mat`
- Generated: `2026-06-07 15:10:24`
- Time: `0.0000` to `37.9180` s, samples `37919`
- Final s/v/t/e_t: `525.4557` m, `0.0000` m/s, `-0.9517` m, `-1.6370` m

## Metrics

- maxAbs(e_t): `2.66146`
- rmse(e_t): `0.753622`
- maxAbs(e_psi): `0.320084`
- rmse(e_psi): `0.109731`
- delta command mode: `applied`
- maxAbs(delta_cmd logged): `0.494628`
- rmse(delta_cmd logged): `0.174751`
- maxAbs(applied_delta_cmd): `0.494628`
- rmse(applied_delta_cmd): `0.174751`
- maxAbs(applied_delta_rate): `1.5`
- rmse(applied_delta_rate): `0.45858`
- maxAbs(steer_manual): `10.2392`
- rmse(steer_manual): `4.81186`
- maxAbs(yawrate): `0.137763`
- mean speed: `13.6417`

## Sign Diagnosis

- likely sign issue logged: `0`
- likely sign issue applied: `0`
- active samples: `14150`
- corr(e_t, delta_cmd logged): `-0.906224`
- same-sign fraction e_t*delta_cmd logged: `0.0542756`
- opposite-sign fraction e_t*delta_cmd logged: `0.945724`
- corr(e_t, applied_delta_cmd): `-0.906224`
- same-sign fraction e_t*applied_delta_cmd: `0.0542756`
- opposite-sign fraction e_t*applied_delta_cmd: `0.945724`
- corr(e_t, steer_manual): `-0.872994`

## BO Objective

- J continuous: `52.9702`
- J fail-closed: `52.9702`
- objective used: `continuous`
- violation count: `10`
- crash/sim fail: `0`
- ERG status: `SIM_END`

## Events

- `first_abs_e_t_gt_0p1`: time `23.5070`, s `293.5746`, value `-0.100111`
- `first_abs_e_t_gt_0p5`: time `23.9610`, s `300.8881`, value `-0.500333`
- `first_abs_applied_delta_cmd_gt_0p1`: time `23.4600`, s `292.8174`, value `0.10024`
- `first_s_ge_280`: time `22.6650`, s `280.0090`, value `0.00430712`
- `first_s_ge_300`: time `23.9060`, s `300.0023`, value `-0.433924`
