# UrbanRoad Catalog

Source map: `Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5`.

This catalog is the current allow-list for native CarMaker scenario generation. Use `generation_library` entries tagged `visible` and `validated`; require `conflict` when the scenario target is a crash/near-crash.

## Counts

- Routes: 17
- Junctions: 22
- Lane paths: 275
- Traffic lights: 2
- Right-of-way control entries: 72
- Mounted control assets: 44

## Generation Allow-List

| Key | Actor | Ego route/start | Actor route/start | Speed | Tags | Note |
| --- | --- | --- | --- | --- | --- | --- |
| `aeb_crossing_vehicle_cross_ob` | vehicle `cross01` | 4235 / `200.00 0` | 4236 / `55.00 0` | 30 | visible, validated, conflict | Primary verified AEB crossing target. Conflict timing is controlled by ego speed and target start around route 4236 s=55. |
| `aeb_crossing_vehicle_fast` | vehicle `cross02` | 4235 / `200.00 0` | 4236 / `42.00 0` | 45 | visible, validated, conflict, derived_timing | Derived from the same verified route pair; user validation showed route pair works, but exact severity depends on timing. |
| `aeb_crossing_vehicle_late_no_conflict` | vehicle `cross09` | 4235 / `200.00 0` | 4236 / `75.00 0` | 25 | visible, validated, no_conflict | Usable as non-conflict control only. |
| `aeb_oncoming_background` | vehicle `oncom01` | 4235 / `200.00 0` | 4232 / `0.00 0` | 50 | visible, validated, background | Background vehicle from IPG example; not a primary conflict actor. |
| `aeb_pedestrian_same_route_cross_ob` | pedestrian `pedx01` | 4235 / `200.00 0` | 4235 / `400.00 -2.5` | 0 | visible, validated, conflict, needs_source_block | IPG pedestrian AEB target. Current native generator template is car-intersection based, so this requires importing the PedestrianCity actor block before generation. |

## Route Catalog

| Route ID | Index | Length m | LanePath IDs | RL Indices | Route Assets | Example Usage | Feedback Tags |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| 4225 | 0 | 262.8 | `4255 4248 4243` | `482 339 327` |  | AEB_CrossingCarIntersection:pedestrian:Ped_2@5.00 -3.55; AEB_CrossingCarIntersection:pedestrian:Ped_4@49.00 -3.55; AEB_CrossingCarIntersection:vehicle:S_Car_1@140.10 -7.75; AEB_CrossingCarIntersection:vehicle:S_Car_2@137.00 -7.25; AEB_CrossingCarIntersection:vehicle:S_Car_3@128.50 -2.25; AEB_CrossingCarIntersection:vehicle:S_Car_4@125.50 -3.25; AEB_CrossingCarIntersection:vehicle:S_Car_5@122.50 -7.25; AEB_CrossingCarIntersection:vehicle:S_Car_6@119.50 -2.25 | needs_segment_context, not_visible, wrong_speed_context |
| 4226 | 1 | 996.3 | `4319 4270 4266 4262 4597 4255 4248 4243 4614 4299 4303 4307 4618 4315 4631` | `1176 618 608 598 897 482 339 327 1086 949 959 969 1326 1125 1732` |  | AEB_CrossingCarIntersection:vehicle:L_NX@75.00 0.0; AEB_CrossingCarIntersection:cyclist:Bikerf_1@190.00 -0.75; AEB_CrossingPedestrianCity:vehicle:L_NX@75.00 0.0; AEB_CrossingPedestrianCity:cyclist:Bikerf_1@190.00 -0.75; Man_AutonomousJunctions:vehicle:T04@360 -0.302 | name_length_error, not_validated |
| 4227 | 2 | 7032.4 | `4438 4464 4477 4488 4498 4508 4518 4527 4537 4397 4350 4452 4427` | `2422 2677 2713 2741 2769 2796 2821 2841 2866 2005 1475 2586 2330` |  | AEB_CrossingCarIntersection:vehicle:Truck_1@1800.00 -3.75; AEB_CrossingPedestrianCity:vehicle:Truck_1@1800.00 -3.75 | name_length_error, not_validated |
| 4228 | 3 | 433.6 | `4246 4251 4253 4602 4241 4611` | `333 345 478 823 262 1270` |  | AEB_CrossingCarIntersection:pedestrian:Ped_1@10.00 -3.55; AEB_CrossingPedestrianCity:pedestrian:Ped_1@10.00 -3.55 | needs_segment_context, not_visible, stops_at_18s, wrong_speed_context |
| 4229 | 4 | 70.0 | `4276 4281 4286 4291 4295` | `728 739 750 761 771` |  | AEB_CrossingCarIntersection:pedestrian:Ped_3@0.00 -3.55; AEB_CrossingCarIntersection:vehicle:S_Bus_1@33.00 7.75; AEB_CrossingCarIntersection:pedestrian:S_Ped_1@23.00 10.75; AEB_CrossingCarIntersection:pedestrian:S_Ped_2@23.50 11.75; AEB_CrossingCarIntersection:pedestrian:S_Ped_3@26.00 11.75; AEB_CrossingCarIntersection:pedestrian:S_Ped_4@26.00 11.35; AEB_CrossingCarIntersection:pedestrian:S_Ped_5@30.00 13.25; AEB_CrossingPedestrianCity:pedestrian:Ped_3@0.00 -3.55 | name_length_error, needs_segment_context, not_validated, not_visible, stops_at_18s, wrong_speed_context |
| 269 | 5 | 98.2 | `4363 4368 181 4375 4381 4387 253 4391` | `1646 1658 1672 1684 1696 1707` |  | AEB_CrossingCarIntersection:vehicle:S_Car_14@34.50 12; AEB_CrossingCarIntersection:vehicle:S_Car_15@44.50 6; AEB_CrossingCarIntersection:vehicle:S_Car_16@44.50 12; AEB_CrossingCarIntersection:vehicle:S_Car_17@44.50 16.5; AEB_CrossingCarIntersection:vehicle:S_Car_18@28.00 22; AEB_CrossingCarIntersection:vehicle:S_Car_19@53.00 22; AEB_CrossingCarIntersection:pedestrian:S_Ped_7@32.00 23.3; AEB_CrossingCarIntersection:pedestrian:S_Ped_8@40.00 14 | name_length_error, not_validated |
| 271 | 6 | 10803.8 | `4356 4645 4258 4599 4255 4248 4243 4614 4299 4303 4307 4617 4323 4328 4332 4632 4336 4340 4655 4565 4559 273 4560 4553 4587 4585 4442 276 4441 4467 4479 279 4478 4489 4499 4509 282 4520 4530 4540 288 4541 4575 4573 4563 285 4562 4567 4657 4412 4653` | `1564 1859 557 976 482 339 327 1086 949 959 969 1298 1234 1245 1255 1760 1376 1387 2147 3622 3606 3608 3523 4009 4001 2431 2429 2686 2717 2715 2743 2771 2798 2825 2850 2873 2875 3760 3752 3615 3613 3626 2264 2190 2047` |  | Man_AutonomousJunctions:vehicle:T02@323.599 0.012 |  |
| 4232 | 7 | 638.2 | `4356 4645 4258 4600 4241 4611 4246 4251 4253 4603 4264 4268 4272` | `1564 1859 557 777 262 1270 333 345 478 884 602 612 622` |  | AEB_CrossingCarIntersection:vehicle:Oncoming@0.00 0 | collision_observed, conflict, validated, visible |
| 4233 | 8 | 3019.3 | `4299 4303 4307 4617 4323 4328 4332 4632 4336 4340 4656 4412 4653 4356 4645 4258 4600 4241 4612` | `949 959 969 1298 1234 1245 1255 1760 1376 1387 2206 2190 2047 1564 1859 557 777 262 1019` |  | AEB_CrossingCarIntersection:cyclist:Bikerm_1@1311.25 -1.25; AEB_CrossingCarIntersection:vehicle:S_Car_20@951.25 15.75; AEB_CrossingCarIntersection:vehicle:S_Car_21@947.25 15.25; AEB_CrossingPedestrianCity:cyclist:Bikerm_1@1311.25 -1.25; AEB_CrossingPedestrianCity:vehicle:S_Car_20@951.25 15.75; AEB_CrossingPedestrianCity:vehicle:S_Car_21@947.25 15.25; Man_AutonomousJunctions:vehicle:T05@2278.291 0.053 | crossing_car_visible, cyclist_not_visible |
| 4234 | 9 | 7032.4 | `4533 4523 4513 4503 4493 4482 4470 4457 4432 4421 4447 4343 4403` | `2857 2833 2808 2785 2757 2728 2694 2661 2406 2314 2573 1453 2024` |  | AEB_CrossingCarIntersection:vehicle:SClass@0.00 -3.75; AEB_CrossingCarIntersection:vehicle:Tesla@800.00 -3.75; AEB_CrossingCarIntersection:vehicle:S3@2000.00 -3.75; AEB_CrossingCarIntersection:vehicle:GSFe@5000.00 -3.75; AEB_CrossingPedestrianCity:vehicle:SClass@0.00 -3.75; AEB_CrossingPedestrianCity:vehicle:Tesla@800.00 -3.75; AEB_CrossingPedestrianCity:vehicle:S3@2000.00 -3.75; AEB_CrossingPedestrianCity:vehicle:GSFe@5000.00 -3.75 | name_length_error, not_validated |
| 4235 | 10 | 522.7 | `4305 4301 4297 4606 4239` | `965 955 945 1032 258` |  | AEB_CrossingCarIntersection:ego:ego@200.00 0; AEB_CrossingCarIntersection:cyclist:Bikerm_2@380.00 -0.75; AEB_CrossingPedestrianCity:ego:ego@200.00 0; AEB_CrossingPedestrianCity:pedestrian:cross_ob@400.00 -2.5; AEB_CrossingPedestrianCity:cyclist:Bikerm_2@380.00 -0.75; Man_AutonomousJunctions:vehicle:T06@4.191 0.121 | collision_observed, conflict, crossing_car_visible, cyclist_not_visible, name_length_error, needs_segment_context, no_conflict, not_validated, not_visible, stops_at_18s, validated, visible, wrong_speed_context |
| 4236 | 11 | 251.4 | `4248 4243 4615 4276 4281 4286 4291 4295` | `339 327 1187 728 739 750 761 771` |  | AEB_CrossingCarIntersection:vehicle:cross_ob@$Position_TO=55.00 0 | collision_observed, conflict, crossing_car_visible, cyclist_not_visible, name_length_error, no_conflict, not_validated, validated, visible |
| 4237 | 12 | 2807.3 | `4338 4334 4637 4330 4325 4321 4620 4315 4631 4319 4270 4266 4262 4596 4260 4642 4358 4650 4414 4659` | `1383 1372 1747 1251 1240 1230 1424 1125 1732 1176 618 608 598 869 561 1872 1568 2060 2194 2175` |  | AEB_CrossingCarIntersection:cyclist:Bikerf_2@1422.30 -4.25; AEB_CrossingPedestrianCity:cyclist:Bikerf_2@1422.30 -4.25; Man_AutonomousJunctions:vehicle:T01@1993.556 -0.147; Man_AutonomousJunctions:vehicle:T03@2054.148 -0.172; Man_AutonomousJunctions:vehicle:T07@1258.283 0.003; Man_AutonomousJunctions:vehicle:T08@1686.295 0.038 |  |
| 4238 | 13 | 341.4 | `4311 4293 4288 4283 4278 4274 4609 4246 4251` | `1082 767 756 745 734 724 1200 333 345` |  |  |  |
| 351 | 14 | 7993.0 | `4356 4645 4258 4600 4241 4613 4276 4281 4286 4291 4295 4309 4628 4315 4630 4336 4340 4655 4565 4559 273 4560 4553 4587 4585 4442 276 4441 4467 4479 279 4478 4489 4499` | `1564 1859 557 777 262 1132 728 739 750 761 771 1077 1516 1125 1625 1376 1387 2147 3622 3606 3608 3523 4009 4001 2431 2429 2686 2717 2715 2743 2771` |  | Man_AutonomousJunctions:ego:ego@0.00 0; Man_AutonomousJunctions:vehicle:Ahead@20 0.010 |  |
| 358 | 15 | 2275.7 | `4509 282 4520 4530 4540 288 4541 4575 4573 4563 285 4562 4567 4657 4412 4654 4363 4368 4374 4380 4386 4391 4643 4358 4650 4414 4660 4565 4559 273 4560 4553 4587 4585 4442 276 4441 4467 4479 279 4478 4489` | `2798 2825 2850 2873 2875 3760 3752 3615 3613 3626 2264 2190 2075 1646 1658 1671 1683 1695 1707 1900 1568 2060 2194 2221 3622 3606 3608 3523 4009 4001 2431 2429 2686 2717 2715 2743` |  |  |  |
| 367 | 16 | 7032.4 | `4499 4509 4519 4528 4538 4398 4351 4453 4428 4439 4465 4478 4489` | `2771 2798 2823 2843 2868 2007 1477 2587 2332 2424 2679 2715 2743` |  |  |  |

## Junction Catalog

| Index | ID | Type | RST | Knot XY | Arms | Links | RLs |
| ---: | ---: | --- | --- | --- | ---: | ---: | ---: |
| 0 | 0 | Standard | Urban | -68.60, 4.40 | 4 | 6 | 28 |
| 1 | 28 | Standard | Urban | 91.40, 4.40 | 4 | 6 | 25 |
| 2 | 54 | Standard | Countryroad | 91.40, 184.40 | 4 | 6 | 25 |
| 3 | 80 | Standard | Countryroad | -68.60, 184.40 | 4 | 6 | 25 |
| 4 | 106 | Standard | Urban | -93.60, 4.40 | 3 | 3 | 18 |
| 5 | 133 | Direct | Urban | -18.60, -65.60 | 2 | 0 | 0 |
| 6 | 138 | Direct | Urban | -68.60, 84.40 | 2 | 0 | 0 |
| 7 | 149 | Direct | Countryroad | 91.40, 84.40 | 2 | 0 | 0 |
| 8 | 158 | Standard | User | -21.59, -23.54 | 3 | 2 | 9 |
| 9 | 162 | Direct | Ramp | -865.88, 149.40 | 3 | 0 | 0 |
| 10 | 166 | Direct | Ramp | -865.88, 279.40 | 4 | 0 | 0 |
| 11 | 171 | Direct | Ramp | -542.80, 184.27 | 3 | 0 | 0 |
| 12 | 175 | Direct | Ramp | -865.88, -10.60 | 3 | 0 | 0 |
| 13 | 179 | Direct | Ramp | -865.88, 284.40 | 2 | 0 | 0 |
| 14 | 183 | Standard | Countryroad | -203.60, 4.40 | 3 | 3 | 15 |
| 15 | 202 | Direct | Ramp | -865.88, 444.40 | 3 | 0 | 0 |
| 16 | 206 | Direct | Ramp | -865.88, 519.40 | 3 | 0 | 0 |
| 17 | 210 | Direct | Ramp | -550.30, 184.27 | 3 | 0 | 0 |
| 18 | 214 | Direct | Ramp | -720.30, 184.27 | 3 | 0 | 0 |
| 19 | 218 | Direct | Ramp | -725.37, 184.27 | 3 | 0 | 0 |
| 20 | 222 | Standard | Countryroad | -424.24, 184.27 | 3 | 3 | 15 |
| 21 | 241 | Direct | Countryroad | -990.33, 358.76 | 3 | 0 | 0 |

## Traffic Lights

| Key | Object | Name | Raw |
| --- | --- | --- | --- |
| `Control.TrfLight.0` | 9921 | TL001 | `9921 TL001 "" 3 0 15 3 15 3` |
| `Control.TrfLight.1` | 9923 | TL000 | `9923 TL000 "" 1 0 15 3 15 3` |

## Example TestRun Overlay

| TestRun | Ego | Actors | Notes |
| --- | --- | ---: | --- |
| `AEB_CrossingCarIntersection` | R4235 `200.00 0`, $Speed_vut=40 km/h | 48 | cross_ob:vehicle@R4236 $Position_TO=55.00 0, Oncoming:vehicle@R4232 0.00 0, SClass:vehicle@R4234 0.00 -3.75, Tesla:vehicle@R4234 800.00 -3.75, S3:vehicle@R4234 2000.00 -3.75, GSFe:vehicle@R4234 5000.00 -3.75, L_NX:vehicle@R4226 75.00 0.0, Truck_1:vehicle@R4227 1800.00 -3.75, Ped_1:pedestrian@R4228 10.00 -3.55, Ped_2:pedestrian@R4225 5.00 -3.55 |
| `AEB_CrossingPedestrianCity` | R4235 `200.00 0`, $Speed_vut=60 km/h | 47 | cross_ob:pedestrian@R4235 400.00 -2.5, SClass:vehicle@R4234 0.00 -3.75, Tesla:vehicle@R4234 800.00 -3.75, S3:vehicle@R4234 2000.00 -3.75, GSFe:vehicle@R4234 5000.00 -3.75, L_NX:vehicle@R4226 75.00 0.0, Truck_1:vehicle@R4227 1800.00 -3.75, Ped_1:pedestrian@R4228 10.00 -3.55, Ped_2:pedestrian@R4225 5.00 -3.55, Ped_3:pedestrian@R4229 0.00 -3.55 |
| `Man_AutonomousJunctions` | R351 `0.00 0`, 51 km/h | 9 | Ahead:vehicle@R351 20 0.010, T01:vehicle@R4237 1993.556 -0.147, T02:vehicle@R271 323.599 0.012, T03:vehicle@R4237 2054.148 -0.172, T04:vehicle@R4226 360 -0.302, T05:vehicle@R4233 2278.291 0.053, T06:vehicle@R4235 4.191 0.121, T07:vehicle@R4237 1258.283 0.003, T08:vehicle@R4237 1686.295 0.038 |

## Manual Feedback Overlay

| Scenario | Status | Routes | Tags | Interpretation |
| --- | --- | --- | --- | --- |
| `CMASM_004_crossing_with_oncoming` | intentional_conflict | 4235, 4236, 4232 | validated, visible, conflict, collision_observed | Ego route 4235 and crossing target route 4236 are the IPG AEB conflict pair. Collision can be intentional, but scenario naming must say collision-risk. |
| `CMASM_005_bus_occluded_pedestrian` | failed_visibility | 4235, 4229, 4228 | not_visible, stops_at_18s, needs_segment_context | User reported bus and pedestrian not visible; ego stopped around 18 s. Treat copied bus/ped blocks as local to another viewpoint until revalidated. |
| `CMASM_006_multi_pedestrian_crosswalk` | failed_visibility | 4235, 4228, 4225, 4229 | not_visible, wrong_speed_context, needs_segment_context | User reported pedestrians not visible and ego around 30 kph; do not compose these pedestrian routes with ego route 4235 start 200 without a validated viewpoint. |
| `CMASM_007_cyclist_and_crossing_car` | partial_visibility | 4235, 4236, 4233 | crossing_car_visible, cyclist_not_visible | Crossing car is visible, cyclist on route 4233 at s=1311.25 is not visible from the chosen ego segment. |
| `CMASM_008_dense_urban_background` | syntax_abort | 4235, 4236, 4226, 4227, 4234 | name_length_error, not_validated | CarMaker traffic names are effectively limited to 8 characters. Long names were truncated and duplicate truncations caused Too many warnings abort. |
| `CMASM_009_late_near_miss_crossing` | no_conflict | 4235, 4236 | visible, validated, no_conflict | Scenario ran but had no collision risk; route pair is usable, timing is not a conflict recipe. |
| `CMASM_010_static_clutter_pedestrian` | syntax_abort | 4235, 4229, 269 | name_length_error, not_validated | Same >8-character traffic-name failure as CMASM_008. Static clutter positions also need visible-segment validation. |

## Current Generation Rules

- Traffic actor `Name` must be unique and 8 characters or shorter.
- Default generator inputs must come from `generation_library` entries containing both `visible` and `validated`.
- Collision-risk scenarios must include at least one actor placement tagged `conflict`.
- Pedestrian/cyclist placements copied from unrelated example viewpoints are not allowed until they get a visible validation tag for the same ego route/start.
- The IPG pedestrian `cross_ob` from `AEB_CrossingPedestrianCity` is valid but requires importing that TestRun actor block; the current car-intersection template cannot synthesize it from the vehicle block alone.
