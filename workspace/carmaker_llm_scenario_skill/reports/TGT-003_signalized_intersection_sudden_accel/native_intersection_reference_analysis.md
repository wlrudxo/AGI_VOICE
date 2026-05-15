# Native CarMaker Intersection Reference Analysis

Date: 2026-05-12

## Question

TGT-003 showed that generated OpenSCENARIO path trajectories can run into:

- randomized/default junction direction when using lane routing only,
- unsupported `AssignRouteAction` in CarMaker 15 `osc2cm`,
- slow or mismatched speed behavior when path-only `FollowTrajectoryAction` is converted separately from speed control,
- velocity polynomial sign-change errors when timed trajectory points are used for ego turning.

This note checks existing CarMaker examples to decide whether intersection scenarios should be generated from scratch or assembled from native CarMaker road/routes.

## Reference Files Inspected

CarMaker install examples:

- `/mnt/c/IPG/carmaker/win64-15.0.1/Data/TestRun/Examples/DriverAssistance/BrakingAssist/AEB_CrossingCarIntersection`
- `/mnt/c/IPG/carmaker/win64-15.0.1/Data/TestRun/Examples/DriverAssistance/BrakingAssist/AEB_CrossingPedestrianCity`
- `/mnt/c/IPG/carmaker/win64-15.0.1/Data/TestRun/Examples/BasicFunctions/Traffic/Man_AutonomousJunctions`
- `/mnt/c/IPG/carmaker/win64-15.0.1/Data/TestRun/Examples/BasicFunctions/Traffic/Man_FollowPathNoRoutes`
- `/mnt/c/IPG/carmaker/win64-15.0.1/Data/TestRun/Examples/DriverAssistance/BrakingAssist/Scripts/Intersection.tcl`
- `/mnt/c/IPG/carmaker/win64-15.0.1/Data/Road/Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5`

## Key Finding

Existing CarMaker intersection examples do not primarily solve intersections by generating dense global coordinate trajectories. They use a native `.rd5` road with predefined routes, junctions, crosswalk assets, and traffic lights, then place ego and traffic on route IDs.

For our generator, the reliable first design should be:

1. Pick a known native CarMaker road with intersection/crosswalk/signal assets.
2. Select route IDs for ego and target actors.
3. Set route-relative start positions and offsets.
4. Use `Driver`/`auto` or simple `VelTransition` for longitudinal control.
5. Compute time-to-conflict by route distance and speed.

This is different from the current OpenSCENARIO-only direction, where CarMaker `osc2cm` accepts only a restricted subset and drops or degrades route actions.

## AEB Crossing Car Pattern

`AEB_CrossingCarIntersection` is the closest template for controlled vehicle conflict at an intersection.

Road:

```ini
Road.FName = Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5
```

Ego:

```ini
Vehicle.Routing.Type = Route
Vehicle.Routing.ObjId = 4235
Vehicle.StartPos.Type = Route
Vehicle.StartPos.ObjId = 4235
Vehicle.StartPos = 200.00 0
DrivMan.Man.Start.Velocity = $Speed_vut=40
DrivMan.Man.0.LongStep.0.Dyn = Driver 1 0 $Speed_vut=40
DrivMan.Man.0.LatStep.0.Dyn = Driver 0
```

Crossing target:

```ini
Traffic.0.Routing.Type = Route
Traffic.0.Routing.ObjId = 4236
Traffic.0.StartPos.Type = Route
Traffic.0.StartPos.ObjId = 4236
Traffic.0.StartPos = $Position_TO=55.00 0
Traffic.0.Man.Start.Velocity = $Speed_TO=30
Traffic.0.Man.0.CombinedSteps = 1
Traffic.0.Man.0.LongStep.0.Limit = t 150
Traffic.0.Man.0.LongStep.0.Dyn = VelTransition $Speed_TO=30 linear
Traffic.0.Man.0.LatStep.0.Limit = t 150
```

Timing script:

```tcl
# VUT starts 164m before the intersection
set Speed_vut [expr [NamedValue get Speed_vut]/3.6]
set Speed_TO [expr [NamedValue get Speed_TO]/3.6]
set time2intersection [expr (164/$Speed_vut)]
NamedValue set Position_TO [expr 173-($time2intersection*$Speed_TO)]
```

Meaning:

- Ego is route-following, not a hand-authored trajectory.
- Target is route-positioned and speed-controlled.
- Conflict timing is computed from route distance, not from visual/manual coordinate guessing.
- This avoids our previous `FollowTraj` velocity polynomial failures.

## AEB Pedestrian City Pattern

`AEB_CrossingPedestrianCity` uses the same road and ego route:

```ini
Road.FName = Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5
Vehicle.Routing.Type = Route
Vehicle.Routing.ObjId = 4235
Vehicle.StartPos = 200.00 0
DrivMan.Man.0.LongStep.0.Dyn = Driver 1 0 $Speed_vut=60
DrivMan.Man.0.LatStep.0.Dyn = Driver 0
```

Pedestrian objects are also route-based:

```ini
Traffic.7.Template.FName = 2_People/Pedestrian_Male_Casual_01_Red
Traffic.7.Routing.Type = Route
Traffic.7.Routing.ObjId = 4228
Traffic.7.StartPos.Type = Route
Traffic.7.StartPos.ObjId = 4228
Traffic.7.StartPos = 10.00 -3.55
Traffic.7.Man.Start.Velocity = 4
```

For more complex pedestrian motion, the example uses short route-relative `FollowTraj` segments and then a native routing change:

```ini
Traffic.7.Man.0.LongStep.1.Dyn = FollowTraj
Traffic.7.Man.0.LongStep.1.TimeRef = Relative
Traffic.7.Man.0.LongStep.1.ChannelInput = TimeAndVel
Traffic.7.Man.0.LatStep.1.Dyn = FollowTraj
Traffic.7.Man.0.LatStep.1.Pos.Type = RelativeRoute
Traffic.7.Man.0.LatStep.1.Pos.Reference = Ped_1
Traffic.7.Man.0.LatStep.2.Dyn = RoutingChange
Traffic.7.Man.0.LatStep.2.Routing.Type = Route
Traffic.7.Man.0.LatStep.2.Routing.ObjId = 271
```

Meaning:

- For pedestrians, native examples still anchor to routes.
- Short `FollowTraj` can be used for local crossing/body motion, but it is route-relative and bounded.
- A pedestrian crossing generator should not start with long global timed trajectories. It should choose a route/crosswalk anchor, then add small local lateral/crossing segments only when needed.

## Man_FollowPathNoRoutes Pattern

`Man_FollowPathNoRoutes` shows a useful but different native mode:

```ini
Traffic.0.Routing.Type = Off
Traffic.0.StartPos.Type = Path
Traffic.0.StartPos.ObjId = 40
Traffic.0.Man.0.LongStep.0.Dyn = auto 80
Traffic.0.Man.0.LatStep.0.Dyn = FollowPath 0.5
```

Meaning:

- CarMaker can follow predefined native paths without explicit routes.
- This is not what `osc2cm` generated from our OpenSCENARIO route experiments.
- It may be useful as a postprocessor target if we can identify or create native path IDs inside `.rd5`, but route IDs are simpler for intersection scenarios.

## Road Asset Pattern

`UrbanRoad_RuralRoad_Expressway.rd5` already has the assets we keep trying to regenerate:

```ini
nJunctions = 22
nRoutes = 17
Route.10.ID = 4235
Route.11.ID = 4236
Route.12.ID = 4237
Route.13.ID = 4238
Route.14.ID = 351
Control.TrfLight.0 = 9921 TL001 "" 3 0 15 3 15 3
Control.TrfLight.1 = 9923 TL000 "" 1 0 15 3 15 3
```

It also includes mounted pedestrian-crossing assets:

```ini
RL.322.Mount.2.0 = ... PedestrianCrossing2S ...
RL.322.Mount.3.0 = ... PedestrianCrossing2S ...
```

Meaning:

- A four-arm urban intersection with traffic lights, crosswalks, and route network already exists.
- For early validation, generating a new intersection road is unnecessary.
- We should build a route catalog for this road first: route ID, approximate maneuver type, usable start-position range, conflict point with route 4235, and any signal/crosswalk association.

## Why Our Generated Intersection Felt Hard

The hard part was not just geometry. It was that CarMaker scenario behavior depends on native route/path/control objects that OpenSCENARIO conversion does not fully preserve.

Observed causes:

- `AssignRouteAction` is part of OpenSCENARIO, but CarMaker 15 `osc2cm` supported-feature validation rejects it in maneuvers.
- Lane-only routing leaves junction choices to CarMaker/default driver behavior, causing nondeterministic or unintended turn direction.
- Timed `FollowTrajectoryAction` for ego vehicles generates polynomial velocity constraints that can fail on turns or abrupt timing.
- Path-only trajectory plus separate speed action can display the requested target speed in the maneuver but still move slowly because the speed step is not the active controller during path following.
- Traffic lights are road/control assets; making their 3D state and driver response work requires using native road control objects, not just writing an abstract OpenSCENARIO signal story.

## Recommended Generation Rule

For intersection/crosswalk/signal scenarios, prefer native CarMaker route-template generation:

```text
scenario intent
  -> choose known rd5 template road
  -> choose ego route ID and target route ID
  -> compute route-relative start positions from conflict timing
  -> write native TestRun route positions and speed controls
  -> optionally add small route-relative pedestrian FollowTraj/RoutingChange
  -> package into Data/TestRun/LLM_Generated
```

Do not generate ego intersection behavior as dense OpenSCENARIO timed trajectory unless there is no route/path alternative.

## Proposed TGT-003 Reset

Use `AEB_CrossingCarIntersection` / `AEB_CrossingPedestrianCity` as the base instead of the current generated OpenSCENARIO route experiments.

Minimal next target:

- Road: `Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5`
- Ego: route `4235`, start around `180-200 m`, `Driver 1 0 40-60 kmh`
- Crossing vehicle: route `4236`, position computed from conflict time, `VelTransition 20-35 kmh`
- Signal: use existing `Control.TrfLight.*` from the road first; only tune signal timing after the route scenario is stable
- End condition: collision, ego sRoad past conflict exit, or time limit

For pedestrian variant:

- Start with a native route-based pedestrian like `Traffic.7` in `AEB_CrossingPedestrianCity`
- Keep speed `3-5 kmh`
- Use route-relative short `FollowTraj` only for crossing step
- Avoid global pedestrian trajectories until native route/crosswalk mapping is cataloged

## Generator Implications

Add a new generator mode:

```text
native_route_template
```

Inputs:

- `road_f_name`
- `ego_route_id`
- `ego_start_s`
- `ego_speed_kmh`
- `target_route_id`
- `target_conflict_s`
- `target_speed_kmh`
- `time_to_conflict_s` or desired TTC
- optional `traffic_light_policy`

Outputs:

- CarMaker TestRun file directly, not only `.xosc`
- Documentation sidecar with selected route IDs and computed positions
- Optional validation checklist for CarMaker manual run

This should become the primary path for TGT-003 and later intersection scenarios. OpenSCENARIO generation remains useful for portable examples and conversion tests, but not as the first reliable production path for CarMaker-native intersections.

## Initial Route Catalog From Examples

These IDs are not fully semantically mapped yet, but they are already proven by IPG examples on `UrbanRoad_RuralRoad_Expressway.rd5`.

| Route ID | Seen In | Example Usage | Initial Meaning For Generator |
|---:|---|---|---|
| 4235 | AEB crossing car, AEB pedestrian city | Ego route, also cyclist route | Main ego approach through the urban intersection area |
| 4236 | AEB crossing car | `cross_ob` route | Crossing vehicle conflict route for `4235` |
| 4234 | AEB examples | fast background traffic | Through/background vehicle route |
| 4226 | AEB examples | background vehicle/cyclist route | Candidate secondary traffic route |
| 4227 | AEB examples | truck route | Candidate large-vehicle route |
| 4228 | AEB pedestrian city | `Ped_1` route | Candidate pedestrian/crosswalk approach route |
| 4225 | AEB pedestrian city | `Ped_2` and static parked objects | Candidate pedestrian/static object route |
| 4229 | AEB pedestrian city | `Ped_3`, bus/static pedestrians | Candidate pedestrian/bus/curb-side route |
| 4233 | AEB examples | cyclist/static cars | Candidate cyclist/background route |
| 4237 | AEB examples | cyclist route | Candidate cyclist/conflict route |
| 269 | AEB examples | many static parked cars/pedestrians | Static roadside or parking-side placement route |

Next catalog step:

- For each route, record usable `s` range, lane/offset convention, and approximate conflict `s` with ego route `4235`.
- The current AEB script tells us one verified pair: ego route `4235` from `s=200` has about `164 m` to the target intersection; target route `4236` has a conflict anchor around `s=173`.
- That pair should become the first deterministic TGT-003 route-template scenario.
