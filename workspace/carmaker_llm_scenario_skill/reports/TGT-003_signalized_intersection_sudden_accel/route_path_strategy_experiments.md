# TGT-003 Route/Path Strategy Experiments

Purpose:

Determine whether the CarMaker 15.0.1 `osc2cm` backend can support vehicle
route/path intent without long timed `FollowTrajectoryAction` tables.

Current problem:

```text
Timed FollowTrajectoryAction -> osc2cm -> FollowTraj + AccFitted velocity polynomial
```

This works for deterministic geometry but is fragile around junctions because
direction, time spacing, and hold vertices can trigger CarMaker velocity
polynomial sign-change aborts.

Local converter facts:

```text
OpenSCENARIO_v120_osc2cm_ego_1401.xsd:
  PrivateAction_osc2cm_ego_init allows LongitudinalAction and TeleportAction only.
  RoutingAction_osc2cm_ego_maneuver allows FollowTrajectoryAction only.

OpenSCENARIO_v120_osc2cm_traffic_1401.xsd:
  PrivateAction_osc2cm_traffic_init allows LongitudinalAction and TeleportAction only.
  RoutingAction_osc2cm_traffic_maneuver allows FollowTrajectoryAction only.
```

Implication:

```text
AssignRouteAction is present in the generic OpenSCENARIO schema type, but not
in the CarMaker osc2cm maneuver subset used by strict supported-feature
validation.
```

## Experiment A: Default Driver Path + Speed Only

Hypothesis:

```text
If no route is assigned, CarMaker's driver may choose a default route through
the junction from lane start plus speed command.
```

Input:

```text
generated/TGT-003_signalized_intersection_sudden_accel/route_path_experiments/tgt003_routeexp_a_default_speed.xosc
```

Expected converter signal:

```text
No Vehicle.Routing.Type = Path.
No FollowTraj.
Vehicle maneuvers should be speed-only.
Runtime must determine whether the junction choice is stable.
```

Status:

```text
STRICT CONVERSION PASSED
```

Result:

```text
Validation succeeded with 0 errors and 0 warnings.
Conversion succeeded.
"--interpolate" is ignored because there is no FollowTrajectoryAction.
```

Converted TestRun:

```text
Vehicle.Routing.Type = Lane
Vehicle.Routing.ObjId =
DrivMan.Man.0.LongStep.0.Dyn = VelTransition 28.800 linear
DrivMan.Man.0.nLatSteps = 0

Traffic.0.Routing.Type = Lane
Traffic.0.Routing.ObjId =
Traffic.0.Man.0.LongStep.0.Dyn = VelTransition 8.000 linear
Traffic.0.Man.0.nLatSteps = 0
```

Road result:

```text
nJunctions = 1
nRoutes = 0
LanePath.0..31 exist
Control.TrfLight.0..3 exist
```

Installed runtime candidate:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\TGT003_routeexp_a_default_speed
```

Runtime question:

```text
Does CarMaker's Lane routing make a stable default junction choice?
If the ego chooses a different outgoing road per run, this approach is not
deterministic enough for scenario generation.
```

## Experiment B: AssignRouteAction In Maneuver

Hypothesis:

```text
If AssignRouteAction works outside Init, the converter can express route intent
without timed trajectories.
```

Input:

```text
generated/TGT-003_signalized_intersection_sudden_accel/route_path_experiments/tgt003_routeexp_b_assign_route_maneuver.xosc
```

Expected converter signal:

```text
Strict validation likely fails because RoutingAction_osc2cm_*_maneuver only
allows FollowTrajectoryAction.
```

Status:

```text
FAILED FOR ROUTE INTENT
```

Result:

```text
Generic API validation succeeded.
osc2cm supported-feature validation reported AssignRouteAction as unsupported.
Conversion continued, but route actions were dropped.
```

Key converter lines:

```text
no declaration found for element 'AssignRouteAction'
element 'AssignRouteAction' is not allowed for content model 'RoutingAction'
Invalid maneuver definition for entity "Ego": AssignRouteAction is not supported.
Invalid maneuver definition for entity "SuddenCar": AssignRouteAction is not supported.
```

Converted TestRun:

```text
Vehicle.Routing.Type = Lane
Vehicle.Routing.ObjId =
Traffic.0.Routing.Type = Lane
Traffic.0.Routing.ObjId =
```

Decision:

```text
Do not use AssignRouteAction as the CarMaker 15 strict backend route mechanism.
It is standard OpenSCENARIO, but not supported by the local osc2cm maneuver
subset.
```

## Experiment C: Path-Only FollowTrajectoryAction + Separate Speed

Hypothesis:

```text
If TimeReference None and vertices without time are accepted, the converter may
create a path/route while separate SpeedAction controls longitudinal motion.
```

Input:

```text
generated/TGT-003_signalized_intersection_sudden_accel/route_path_experiments/tgt003_routeexp_c_trajectory_none_speed.xosc
```

Expected converter signal:

```text
If accepted, inspect whether generated TestRun uses FollowTraj with no fragile
time-channel velocity polynomial, or whether osc2cm still converts it into
timed FollowTraj.
```

Status:

```text
PARTIAL / NOT INSTALLABLE YET
```

Result:

```text
Generic API validation succeeded.
osc2cm supported-feature validation warned that every trajectory Vertex misses
required attribute time.
Conversion still succeeded and generated TimeChan = 0 FollowTraj tables plus
separate speed maneuvers.
```

Converted ego structure:

```text
Vehicle.Routing.Type = Path
DrivMan.Man.0.LatStep.0.Dyn = FollowTraj
DrivMan.Man.0.LatStep.0.TimeChan = 0
DrivMan.Man.0.nLongSteps = 0
DrivMan.Man.1.LongStep.0.Dyn = VelTransition 28.800 linear
```

Converted traffic structure:

```text
Traffic.0.Routing.Type = Path
Traffic.0.Man.0.LatStep.0.Dyn = FollowTraj
Traffic.0.Man.0.LatStep.0.TimeChan = 0
Traffic.0.Man.0.LatStep.0.Limit = t {}
Traffic.0.Man.1.LongStep.0.Dyn = VelTransition 8.000 linear
```

Important postprocessor finding:

```text
The common FollowTraj limit postprocessor must not infer final time from a
TimeChan = 0 data table. In this format, the last column is heading, not time.
The postprocessor now reports this and leaves the limit unchanged.
```

Packaging result:

```text
Initially rejected by package verification because Traffic.0.Man.0.LatStep.0.Limit remains t {}.
Local CarMaker examples show TimeChan = 0 FollowTraj steps with Limit = t {},
so the package policy was too strict.
```

Decision:

```text
This is the most promising non-timed path direction. It is a runtime candidate,
even though it does not pass osc2cm supported-feature validation cleanly.
```

Installed runtime candidate:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\TGT003_routeexp_c_trajectory_none_speed
```

## Current Backend Decision

Evidence so far:

```text
A. Speed-only Lane routing is strict-clean but runtime selected a right turn, so it is not deterministic enough for this target.
B. AssignRouteAction is standard OpenSCENARIO but unsupported by CarMaker 15 osc2cm strict maneuver subset.
C. Path-only FollowTrajectoryAction can create Path routing without timed velocity polynomials. It uses TimeChan = 0 and separate speed maneuvers.
```

## Runtime Feedback: A/C Speed And Direction

User runtime observation:

```text
A: slow and turns right.
C: goes straight, but also slow.
```

Interpretation:

```text
A is rejected as a deterministic route strategy for the intersection target.
C is still the best current candidate because it preserves straight-through path
intent without timed trajectory velocity fitting.
The original C target speed was only 8 m/s, which is 28.8 km/h. If the UI shows
about 8.2, verify whether that quantity is m/s rather than km/h.
```

## Experiment C2: Path-Only FollowTrajectoryAction + 50 km/h Speed

Purpose:

```text
Keep C's deterministic path-only routing but raise the speed target to normal
urban speed.
```

Input:

```text
generated/TGT-003_signalized_intersection_sudden_accel/route_path_experiments/tgt003_routeexp_c2_path_speed_50kph.xosc
```

Converted TestRun:

```text
DrivMan.Man.0.LatStep.0.TimeChan = 0
DrivMan.Man.1.LongStep.0.Dyn = VelTransition 50.040 linear
Traffic.0.Man.0.LatStep.0.TimeChan = 0
Traffic.0.Man.1.LongStep.0.Dyn = VelTransition 13.900 linear
Traffic.SpeedUnit = ms
Vehicle.Routing.Type = Path
Traffic.0.Routing.Type = Path
```

Installed runtime candidate:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\TGT003_routeexp_c2_path_speed_50kph
```

Recommendation:

```text
Run C2 in CarMaker next.

If C2 keeps straight-through behavior and avoids velocity polynomial aborts,
path-only FollowTrajectoryAction plus separate speed should become the preferred
vehicle backend for generated junction scenarios.
```
