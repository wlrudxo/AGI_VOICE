# TGT-003 Signalized Intersection Sudden Acceleration Iteration Log

Created: 2026-05-12

Reference inputs:

```text
workspace/carmaker_llm_scenario_skill/examples/raw/xosc/sudden_acceleration.xosc
workspace/carmaker_llm_scenario_skill/examples/raw/xodr/signal_intersection.xodr
```

Goal:

```text
Validate the first signalized-intersection slice:
- OpenDRIVE junction survives conversion to CarMaker Road5
- OpenDRIVE traffic signals survive as CarMaker traffic-light controls
- ego and a crossing/conflicting vehicle have converted speed maneuvers
- generated TestRun can be installed under LLM_Generated for runtime check
```

## Raw Example Baseline

The copied raw example uses:

```text
FileHeader revMinor = 3
RoadNetwork LogicFile = signal_intersection.xodr
Ego start = road 0 lane -1 s=90
SuddenCar start = road 1 lane -1 s=85
SpeedActionDynamics dynamicsShape=linear dynamicsDimension=rate
AssignRouteAction in Init
```

Earlier no-validate conversion created:

```text
workspace/carmaker_llm_scenario_skill/conversion_scratch/AGI_LLM_TestProject/Data/TestRun/LOO_sudden_acceleration_no_validate
```

Important finding:

```text
Traffic.0.nMan = 0
```

So the raw example is useful semantically, but not a valid generation template.

## v0

Generated input:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-003_signalized_intersection_sudden_accel/tgt003_signalized_intersection_sudden_accel_v0.xosc
workspace/carmaker_llm_scenario_skill/generated/TGT-003_signalized_intersection_sudden_accel/tgt003_signalized_intersection_sudden_accel_v0.xodr
```

Source changes from raw:

- changed OpenSCENARIO header to `revMinor="2"`
- added required `<Properties/>`
- changed traffic speed dynamics from `linear/rate` to `linear/time`
- kept the raw `AssignRouteAction` route intent

Strict validation result:

```text
Failed.
RoutingAction is not allowed for content model PrivateAction in CarMaker's supported-feature validation subset.
```

Rule:

```text
Do not use Init AssignRouteAction in the first strict CarMaker 15 backend.
Use lane starts and explicit maneuvers first; later route/path support should be tested as a separate target.
```

## v1

Generated input:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-003_signalized_intersection_sudden_accel/tgt003_signalized_intersection_sudden_accel_v1.xosc
workspace/carmaker_llm_scenario_skill/generated/TGT-003_signalized_intersection_sudden_accel/tgt003_signalized_intersection_sudden_accel_v1.xodr
```

Source changes from v0:

- removed `AssignRouteAction` blocks
- kept lane starts
- kept ego speed transition: `Time > 1.0`, target `15.0 m/s`, `linear/time 4.0`
- kept sudden-car speed transition: `Time > 1.5`, target `22.0 m/s`, `linear/time 2.0`

Strict validation/conversion result:

```text
PASS
```

Converted TestRun:

```text
workspace/carmaker_llm_scenario_skill/conversion_scratch/AGI_LLM_TestProject/Data/TestRun/TGT003_signalized_intersection_sudden_accel_v1
```

Key converted TestRun traits:

```text
Road.FName = tgt003_signalized_intersection_sudden_accel_v1.rd5
Vehicle.Routing.Type = Lane
Vehicle.StartPos = 90.000 0.000
Vehicle.StartPos.ObjId = 22
DrivMan.nMan = 2
DrivMan.Man.0.LongStep.0.Dyn = VelTransition 54.000 linear
Traffic.N = 1
Traffic.0.StartPos = 85.000 0.000
Traffic.0.StartPos.ObjId = 65
Traffic.0.Man.0.LongStep.0.Dyn = VelTransition 22.000 linear
Traffic.0.Man.0.LongStep.0.Limit = t 2.000
Traffic.0.nMan = 1
```

Converted Road5 signal/junction traits:

```text
nJunctions = 1
RL.1.Mount.0.0.Tag = odrSignalId:100
RL.44.Mount.0.0.Tag = odrSignalId:101
RL.683.Mount.0.0.Tag = odrSignalId:102
RL.726.Mount.0.0.Tag = odrSignalId:103
Control.TrfLight.0 = 40 traffic_light_0 "" 0 0 30 3 25 3
Control.TrfLight.1 = 83 traffic_light_1 "" 0 0 30 3 25 3
Control.TrfLight.2 = 722 traffic_light_2 "" 0 0 30 3 25 3
Control.TrfLight.3 = 765 traffic_light_3 "" 0 0 30 3 25 3
```

Packaged for original project:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\TGT003_signalized_intersection_sudden_accel_v1
E:\CarMakerProject\AGI\Data\Road\LLM_Generated\tgt003_signalized_intersection_sudden_accel_v1.rd5
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT003_signalized_intersection_sudden_accel_v1_SuddenCar
```

Current status:

```text
READY FOR USER RUNTIME CHECK
```

## Strategy reset: native route-template v1

Decision:

```text
For complex CarMaker scenarios with intersections, traffic lights, pedestrians, and surrounding vehicles,
switch the primary generation path from monolithic OpenDRIVE/OpenSCENARIO generation to native segment assembly.
Keep OpenDRIVE/OpenSCENARIO generation as a secondary path for simple roads, lane changes, and regression tests.
```

Reason:

```text
TGT-003 OpenSCENARIO experiments exposed CarMaker 15 osc2cm limitations:
- AssignRouteAction is standard OpenSCENARIO but not supported by the CarMaker maneuver subset.
- Lane-only routing caused unintended/default junction behavior.
- Timed FollowTraj through intersections caused velocity-polynomial sign-change errors.
- Path-only FollowTraj plus separate speed action did not reliably control actual vehicle speed.
- Traffic light/crosswalk behavior is tied to native rd5 control assets.
```

New test candidate:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-003_signalized_intersection_sudden_accel/native_route_template/TGT003_native_route_template_v1
workspace/carmaker_llm_scenario_skill/reports/TGT-003_signalized_intersection_sudden_accel/native_route_template_v1_summary.md
```

Installed in original project:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\TGT003_native_route_template_v1
```

Native route-template signature:

```text
Road.FName = Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5
Vehicle.Routing.Type = Route
Vehicle.Routing.ObjId = 4235
Traffic.0.Name = cross_ob
Traffic.0.Routing.Type = Route
Traffic.0.Routing.ObjId = 4236
Traffic.0.Man.0.LongStep.0.Dyn = VelTransition $Speed_TO=30 linear
Traffic.N = 48
```

Manual runtime check needed:

```text
Load and run LLM_Generated/TGT003_native_route_template_v1 in CarMaker.
Check that ego follows route 4235 deterministically.
Check that cross_ob follows route 4236 and crosses ego's path.
Check whether the large native scene is too crowded for a minimal generated target.
If it runs, next step is to create a slim parameterized native_route_template generator
that keeps only ego + crossing target + optional selected actors.
```

User runtime observation:

```text
The scenario still did not clearly pass through the intersection before the end condition.
The ego waits near the beginning.
The 3D traffic-light animation did not visibly change, so script-level signal state must not be inferred from the rendered mesh alone.
```

Finding:

```text
v3p1 still had DrivMan.Global.EndCond = rise(Time > 12.000).
This was too short for the current red-start / waiting / intersection-crossing intent.
The generated Road5 contains Control.TrfLight.0..3, but visible 3D light switching is not yet validated.
The original project has TrfLight.*.State in Data/Config/OutputQuantities_Anim, so runtime signal-state logging should be checked separately from visual animation.
```

## v4p1

Generated input:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-003_signalized_intersection_sudden_accel/tgt003_signalized_intersection_sudden_accel_v4.xosc
workspace/carmaker_llm_scenario_skill/generated/TGT-003_signalized_intersection_sudden_accel/tgt003_signalized_intersection_sudden_accel_v4.xodr
```

Source changes:

- extended the storyboard stop trigger from 12 s to 30 s
- extended both ego and sudden-car FollowTrajectory tables to 24 s
- kept short timing across the junction connector to avoid the v2p1 velocity polynomial sign-change abort
- kept ego start farther from the junction with a 4 s initial wait
- kept the crossing vehicle with a 4.5 s initial wait

Converted/postprocessed checks:

```text
DrivMan.Global.EndCond = rise(Time > 30.000)
DrivMan.Man.0.StartCond = rise(Time > 4.000)
Traffic.0.Man.0.StartCond = rise(Time > 4.500)
Traffic.0.Man.0.LatStep.0.Limit = t 24.000
Traffic.0.Man.0.LongStep.0.Limit = t 24.000
Vehicle.Routing.Type = Path
Traffic.0.Routing.Type = Path
nJunctions = 1
Control.TrfLight.0..3 exist
```

Installed for original project:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\TGT003_signalized_intersection_sudden_accel_v4p1
E:\CarMakerProject\AGI\Data\Road\LLM_Generated\tgt003_signalized_intersection_sudden_accel_v4.rd5
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT003_signalized_intersection_sudden_accel_v4_SuddenCar
```

Runtime check focus:

```text
1. Does the ego actually enter and clear the intersection before 30 s?
2. Does the crossing vehicle move through the intersection on the intended conflicting approach?
3. Does TrfLight.*.State change in output data even if the 3D signal mesh does not visibly animate?
4. If the signal state is static, add a Road5 traffic-light phase postprocessor instead of treating OpenDRIVE signal import as sufficient.
```

User runtime observation:

```text
The 4 s wait is understood, but the vehicle stops in the middle of crossing.
Traffic-light animation is not visible.
```

Root cause for mid-crossing stop:

```text
The v4p1 converted ego FollowTraj table was not monotonic after the junction:
60 -> 82 -> 99 -> 112 -> 199 -> 169 -> 169

The crossing vehicle had the same problem:
y 57 -> 32 -> 13 -> 0 -> -87 -> -57 -> -57
```

OpenDRIVE interpretation:

```text
Road 2 and road 3 are opposite-direction outgoing roads.
After entering them from the junction, moving away from the intersection requires decreasing OpenDRIVE s.
v4 used increasing s after the connector, so osc2cm converted the path as a forward jump followed by backward motion/hold.
```

## v5p1

Generated input:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-003_signalized_intersection_sudden_accel/tgt003_signalized_intersection_sudden_accel_v5.xosc
workspace/carmaker_llm_scenario_skill/generated/TGT-003_signalized_intersection_sudden_accel/tgt003_signalized_intersection_sudden_accel_v5.xodr
```

Source changes:

- kept the same road and 30 s stop trigger
- changed ego outgoing road 2 vertices from increasing `s=25 -> 55 -> 55` to decreasing `s=85 -> 55 -> 35`
- changed crossing vehicle outgoing road 3 vertices from increasing `s=25 -> 55 -> 55` to decreasing `s=85 -> 55 -> 35`
- kept traffic FollowTraj limit postprocessing

Converted/postprocessed checks:

```text
DrivMan.Global.EndCond = rise(Time > 30.000)
Ego converted FollowTraj x: 60 -> 82 -> 99 -> 112 -> 139 -> 169 -> 189
Traffic converted FollowTraj y: 57 -> 32 -> 13 -> 0 -> -27 -> -57 -> -77
Traffic.0.Man.0.LatStep.0.Limit = t 24.000
Traffic.0.Man.0.LongStep.0.Limit = t 24.000
Vehicle.Routing.Type = Path
Traffic.0.Routing.Type = Path
nJunctions = 1
Control.TrfLight.0..3 exist
```

Installed for original project:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\TGT003_signalized_intersection_sudden_accel_v5p1
E:\CarMakerProject\AGI\Data\Road\LLM_Generated\tgt003_signalized_intersection_sudden_accel_v5.rd5
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT003_signalized_intersection_sudden_accel_v5_SuddenCar
```

Open issue:

```text
Traffic-light 3D animation is still not visible.
Do not treat this as solved by v5p1; v5p1 fixes the path-direction issue only.
```

Runtime check request:

```text
Run LLM_Generated/TGT003_signalized_intersection_sudden_accel_v1.
Check whether it starts without CarMaker errors, whether the signalized road appears, and whether the traffic vehicle moves through the intersection.
```

Known limitation:

```text
This slice validates signalized road conversion and speed-event conversion.
It does not yet validate traffic-light compliance or OpenSCENARIO TrafficSignalController behavior.
That should become the next target after runtime start passes.
```

Runtime/user feedback:

```text
The intersection exists. Ego can enter a different road on repeated runs.
```

Root cause:

```text
v1 removed AssignRouteAction to pass strict validation, leaving ego with Lane routing and a longitudinal speed maneuver only.
At a junction, CarMaker's driver/path choice is therefore not fixed.
```

## v2p1

Generated input:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-003_signalized_intersection_sudden_accel/tgt003_signalized_intersection_sudden_accel_v2.xosc
workspace/carmaker_llm_scenario_skill/generated/TGT-003_signalized_intersection_sudden_accel/tgt003_signalized_intersection_sudden_accel_v2.xodr
```

Source changes:

- moved ego farther from the intersection: road `0`, lane `-1`, `s=60`
- moved the other vehicle farther from the intersection: road `1`, lane `-1`, `s=55`
- replaced ego speed-only behavior with a deterministic `FollowTrajectoryAction`
- replaced sudden-car speed-only behavior with a deterministic `FollowTrajectoryAction`
- delayed ego start to `Time > 4.0` to represent an initial red-light wait window
- delayed sudden-car start to `Time > 4.5`

Converted/postprocessed checks:

```text
Vehicle.Routing.Type = Path
Vehicle.StartPos = 60.000 0.000
DrivMan.Man.0.StartCond = rise(Time > 4.000)
Traffic.0.Routing.Type = Path
Traffic.0.StartPos = 55.000 0.000
Traffic.0.Man.0.StartCond = rise(Time > 4.500)
Traffic.0.Man.0.LatStep.0.Limit = t 10.000
Traffic.0.Man.0.LongStep.0.Limit = t 10.000
nJunctions = 1
Control.TrfLight.0..3 exist
```

Packaged for original project:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\TGT003_signalized_intersection_sudden_accel_v2p1
E:\CarMakerProject\AGI\Data\Road\LLM_Generated\tgt003_signalized_intersection_sudden_accel_v2.rd5
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT003_signalized_intersection_sudden_accel_v2_SuddenCar
```

Note:

```text
The road has CarMaker traffic-light controllers, but the exact visible initial color still needs runtime confirmation.
The current source enforces red-start behavior as a stopped/waiting ego phase before trajectory start.
If the rendered signal color is not red at t=0, add a Road5 traffic-light phase postprocessor or native road-control generation rule.
```

Runtime result:

```text
TGT003_signalized_intersection_sudden_accel_v2p1 starts but aborts at t=8.226.
CarMaker error:
Ego vehicle: LatStep 0 in Man. 0 Follow traj. velocity polynom between table entry 2 and 3 contains a sign change of the velocity.
Suggested by CarMaker: reduce the relative time between points to less than 3.71 s.
```

Root cause:

```text
The deterministic ego path crosses from incoming road 0 through junction connector road 101 to outgoing road 2.
The generated path was deterministic, but the timing around the junction connector was too slow for CarMaker's FollowTraj velocity polynomial.
```

Rule:

```text
For FollowTraj through junction connector roads, keep the relative time across connector entry/exit points short enough for CarMaker's velocity polynomial.
If CarMaker reports a threshold, use a stricter value than the reported limit and record the affected table entries.
```

## v3p1

Generated input:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-003_signalized_intersection_sudden_accel/tgt003_signalized_intersection_sudden_accel_v3.xosc
workspace/carmaker_llm_scenario_skill/generated/TGT-003_signalized_intersection_sudden_accel/tgt003_signalized_intersection_sudden_accel_v3.xodr
```

Source changes:

- kept the same deterministic ego and sudden-car paths
- changed junction timing from broad 2 s spacing to shorter connector intervals
- ego path table after conversion uses `4.400 -> 5.400` for the problematic junction connector interval
- sudden-car path uses the same stabilized timing pattern

Converted/postprocessed checks:

```text
DrivMan.Man.0.StartCond = rise(Time > 4.000)
Traffic.0.Man.0.StartCond = rise(Time > 4.500)
Traffic.0.Man.0.LatStep.0.Limit = t 9.800
Traffic.0.Man.0.LongStep.0.Limit = t 9.800
Vehicle.Routing.Type = Path
Traffic.0.Routing.Type = Path
nJunctions = 1
Control.TrfLight.0..3 exist
```

Packaged for original project:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\TGT003_signalized_intersection_sudden_accel_v3p1
E:\CarMakerProject\AGI\Data\Road\LLM_Generated\tgt003_signalized_intersection_sudden_accel_v3.rd5
E:\CarMakerProject\AGI\Data\Traffic\Template\LLM_Generated\TGT003_signalized_intersection_sudden_accel_v3_SuddenCar
```

Current status:

```text
READY FOR USER RUNTIME CHECK
```
