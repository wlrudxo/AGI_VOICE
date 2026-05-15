# CarMaker osc2cm Converter Gap Log

Created: 2026-05-12

## Purpose

This log records issues found while converting generated or reference OpenSCENARIO/OpenDRIVE scenarios into CarMaker TestRuns.

Each entry should classify the issue as one of:

- `input_xml`: our `.xosc` / `.xodr` generation is invalid or not CarMaker-compatible
- `converter_subset`: `osc2cm` accepts the file but drops or cannot represent part of the scenario
- `postprocess_needed`: generated CarMaker TestRun requires deterministic patching after conversion
- `unknown`: needs a focused reproduction

The likely final architecture is:

```text
Scenario IR
  -> OpenDRIVE/OpenSCENARIO 1.2 exporter
  -> osc2cm
  -> CarMaker TestRun/Road/TrafficTemplate
  -> CarMaker postprocessor
  -> validation summary
```

## Current Findings

| ID | Status | Class | Symptom | Root Cause / Current Hypothesis | Required Handling |
| --- | --- | --- | --- | --- | --- |
| GAP-001 | confirmed | `postprocess_needed` | CarMaker aborts at sim start: `DrivMan: No or invalid maneuver definition (nMan=0)` | `osc2cm` generated ego placement but no ego driver maneuver for `pedestrian_crossing.xosc` | Postprocessor must ensure `DrivMan.nMan >= 1` and add a minimal ego longitudinal/lateral maneuver when missing |
| GAP-002 | clarified | `input_xml` | Pedestrian has no movement in generated TestRun: `Traffic.0.nMan = 0` | Source `.xosc` combined pedestrian `SpeedAction` and `FollowTrajectoryAction`; `osc2cm --trajlegacy` reports `FollowTrajectoryAction cannot be combined with other maneuvers` and drops the pedestrian maneuver | Exporter should emit pedestrian trajectory as a standalone `FollowTrajectoryAction` event, without simultaneous pedestrian `SpeedAction` |
| GAP-003 | confirmed | `input_xml` | Strict `--validate` fails for copied examples | Local examples declare `revMinor="3"` and miss required `<Properties/>` elements | Exporter must emit OpenSCENARIO XML 1.2 and include `<Properties/>` for `Vehicle`/`Pedestrian` |
| GAP-004 | confirmed | `converter_subset` | Traffic speed action warning: pedestrian `SpeedActionDynamics dynamicsShape="step"` unsupported | CarMaker converter subset rejects this shape for traffic speed actions | Exporter should avoid unsupported traffic SpeedAction dynamics or move pedestrian motion into trajectory/native postprocess |
| GAP-005 | confirmed | `converter_subset` | Traffic vehicle speed action warning: `linear` + `rate` unsupported | Converter does not support `dynamicsDimension="rate"` with `dynamicsShape="linear"` for traffic | Exporter should use supported speed transition forms or native CarMaker traffic maneuvers |
| GAP-006 | confirmed | `converter_subset` | Traffic lane change warning: `LaneChangeActionDynamics dynamicsShape="sinusoidal"` unsupported | Converter does not support this lane-change dynamics shape for traffic | Exporter should avoid `sinusoidal` for traffic lane changes or postprocess to native maneuver |
| GAP-007 | confirmed | `postprocess_needed` | Simulation starts, but pedestrian does not cross in front of ego | Generated TestRun kept pedestrian as static traffic object with `Traffic.0.nMan = 0` | Postprocessor must compare IR actor behavior against generated traffic maneuvers and add native `FollowTraj` when missing |
| GAP-008 | confirmed | `postprocess_needed` | `Invalid lane position on lane with object id 41`; traffic start position fails | Manual patch changed `Traffic.0.StartPos` lateral value from converter-generated `5.000` to `-5.000`, which is invalid for lane object id 41 | Postprocessor must not blindly flip lateral signs; it must validate lane object id and lateral bounds from `.rd5` before changing start positions |
| GAP-009 | clarified | `postprocess_needed` | Pedestrian is visible before trigger, then disappears at trigger instead of crossing | Manually copied native `RelativeRoute` trajectory block was incompatible with generated road/path basis | Do not hand-copy route-based blocks; prefer converter-generated `FollowTrajectoryAction` output or generate table format from IR |
| GAP-010 | clarified | `postprocess_needed` / `input_xml` | Generated `.rd5` has `nRoutes = 0`; CarMaker route object is absent | OpenDRIVE conversion creates lane paths and lane object ids; standalone `FollowTrajectoryAction` can still produce `Traffic.*.Routing.Type = Path` and native `FollowTraj` | Do not require `Route` for first slice; use converter-supported trajectory-to-Path/Global FollowTraj output |
| GAP-011 | confirmed | `postprocess_needed` | `Wrong number of elements or syntax error in Traffic.0.Man.0.LatStep.0.Data` after changing `Pos.Type` to `RelativeObject` | The copied `FollowTraj` data table format is valid with `RelativeRoute` examples but not valid when only the `Pos.Type` is changed to `RelativeObject` | Do not switch `Pos.Type` alone; define the correct CarMaker table format per coordinate basis or generate a route/path first |
| GAP-012 | confirmed | `input_xml` | TGT-001 v0/v1 start type distribution did not match reference | OpenSCENARIO `LanePosition` maps to CarMaker `Lane`; reference needed one `Link` and one `RelativeLink` actor | Use `RoadPosition` for CarMaker `Link` and `RelativeRoadPosition` for CarMaker `RelativeLink` |
| GAP-013 | confirmed | `input_xml` | Ego `FollowTrajectoryAction` does not create valid `Vehicle.Routing.Type = Path` | Trajectory start/vertices were not road-coherent: first, `s=582m` exceeded 500m road length; then `WorldPosition y=-11.5` was outside generated lane bounds | Generated OpenDRIVE must cover the full trajectory and any global start point must resolve to a valid road/lane |
| GAP-014 | confirmed | `converter_subset` | Supported-feature validation warns about `vehicleCategory="bus"`/`"truck"` | CarMaker supported-feature validator accepts a narrower category subset than the standard schema/API validation | Use conservative `vehicleCategory="car"` unless a category is proven supported; keep semantic role in object/template name |
| GAP-015 | confirmed | `converter_subset` | Supported-feature validation warns about `Pedestrian`, but conversion still creates a pedestrian traffic template | The API/XSD validation accepts the file; CarMaker's supported-feature validator reports missing Pedestrian declaration | Treat as warning for now; runtime-check generated pedestrian/static object behavior and consider native template mapping/postprocess if it blocks simulation |
| GAP-016 | confirmed | `input_xml` / `converter_subset` | `TrajectoryFollowingMode followingMode="position"` warning appears on converted trajectories | `osc2cm` does not support `position` mode and downgrades it to `follow`; conversion can still succeed | Prefer `followingMode="follow"` if schema/validator accepts it, or whitelist this warning when generated FollowTraj output is correct |
| GAP-017 | confirmed | `input_xml` | Runtime abort: `Traffic object 1: Start position is outside of road` in `LLM_Generated/TGT001_double_lane_change_v4` | The generated road used 3.0 m lanes; ego was moved to `y=-4.5`, bus inherited that lateral position, and pedestrian `RelativeObject dy=-3.0` resolved to about `y=-7.5`, outside the generated road | IR/OpenDRIVE generation must validate the lateral envelope of all absolute and relative actor positions; v6 widens lanes to 4.0 m so the pedestrian start fits |
| GAP-018 | confirmed | `input_xml` | Runtime abort: `Traffic object 2: Invalid position on link` in `LLM_Generated/TGT001_double_lane_change_v6` | Actor `Traffic.2` is generated from OpenSCENARIO `RoadPosition s=100, t=-11.5`; even after widening lanes, the generated road did not extend far enough laterally for that `Link` start position | Road generation must include enough lane count and width for every `RoadPosition.t`; v7 adds extra right-side lanes instead of moving the actor |
| GAP-019 | confirmed | `postprocess_needed` | Traffic `FollowTraj` conversion can emit `Limit = t {}` | `osc2cm --interpolate` creates valid trajectory rows but sometimes omits the time limit literal for traffic FollowTraj steps | Common postprocessor must replace empty `Traffic.*.Man.*.(LatStep\|LongStep).*Limit = t {}` with the final time from the corresponding FollowTraj data table or IR trajectory |
| GAP-020 | confirmed | `input_xml` | Bus-stop AEB scenario semantics are wrong when actor order is ego -> pedestrian -> bus | The pedestrian is exposed before the bus can occlude it, so ego/AEB reacts to a visible static pedestrian rather than a pedestrian emerging from behind a bus | IR validation must check occlusion scenario ordering: occluder between ego and pedestrian emergence point, or pedestrian placed on the far/outer side of the occluder |
| GAP-021 | confirmed | `input_xml` | Bus is placed in ego lane in `TGT002_aeb_bus_stop_core_v3p1` | Source used OpenDRIVE `laneId=-1` for both ego and bus; converter output confirms both have `StartPos.ObjId = 31` | For current straight RHT road, keep ego in lane `-1` and place bus/curb occluder in lane `-2` or a bus-bay lane |
| GAP-022 | confirmed | `input_xml` | Pedestrian crosses much too early in `TGT002_aeb_bus_stop_core_v4p1` | Source trigger used `SimulationTime > 0.5`, independent of ego approach timing | For time-triggered movement tests, compute trigger time from ego arrival at conflict point; for this road ego reaches s=84 around 5.3 s, so v5 uses a 2.0 s trigger with a 4 s crossing-to-conflict profile |
| GAP-023 | hypothesis | `input_xml` / `postprocess_needed` | Pedestrian disappears after crossing instead of remaining visible | Converted traffic `FollowTraj` ends at the last trajectory timestamp; if the maneuver completes during the visible simulation window, CarMaker may remove/deactivate or otherwise stop displaying the actor despite `TreatAtEnd = FreezeVel` | Add a hold vertex at the final pedestrian position and postprocess `Limit` to that hold time so the trajectory does not end before scenario stop |
| GAP-024 | confirmed | `converter_subset` / `input_xml` | `RoutingAction` in `Init` fails strict supported-feature validation for `TGT003_signalized_intersection_sudden_accel_v0` | CarMaker 15 supported-feature validation reports `RoutingAction` not declared / not allowed under `PrivateAction` | Do not use Init `AssignRouteAction` in the first strict backend; use lane starts and explicit maneuvers first, then test route/path support separately |
| GAP-025 | confirmed | `input_xml` | Raw `sudden_acceleration.xosc` converts the sudden car as static traffic with `Traffic.0.nMan = 0` | Traffic `SpeedActionDynamics dynamicsShape="linear" dynamicsDimension="rate"` did not survive as a traffic maneuver in the no-validate raw conversion | Use traffic speed transitions with `dynamicsShape="linear"` and `dynamicsDimension="time"`; v1 converted to `Traffic.0.Man.0.LongStep.0.Dyn = VelTransition 22.000 linear` |
| GAP-027 | confirmed | `input_xml` | TGT-003 v4p1 waits, starts crossing, then stops or behaves as if stuck mid-crossing | Outgoing roads 2 and 3 run opposite to the desired actor travel direction; using increasing OpenDRIVE `s` after the connector made osc2cm emit a global FollowTraj that jumps forward then moves backward/holds | For outgoing roads entered at `contactPoint=end`, decrease `s` as the actor moves away from the junction; verify converted Global FollowTraj coordinates are monotonic before installing |
| GAP-028 | confirmed | `converter_subset` | `AssignRouteAction` in a maneuver is standard OpenSCENARIO but unsupported by CarMaker 15 strict osc2cm validation | Local `RoutingAction_osc2cm_ego_maneuver` and `RoutingAction_osc2cm_traffic_maneuver` allow only `FollowTrajectoryAction`; converter drops `AssignRouteAction` and falls back to `Routing.Type = Lane` | Do not depend on `AssignRouteAction`; use runtime-tested speed-only Lane routing, path-only FollowTrajectoryAction, or native postprocess Route/Path |
| GAP-029 | clarified | `postprocess_needed` | Path-only `FollowTrajectoryAction` with `TimeReference/None` converts to `TimeChan = 0` Path/FollowTraj, and traffic `Limit = t {}` remains | Native CarMaker examples also use `TimeChan = 0` FollowTraj with `Limit = t {}`; the common postprocessor must not treat the last data column as time | Permit empty `Limit` when the same step has `TimeChan = 0`; continue to reject empty limit for timed `TimeChan = 1` FollowTraj |

## GAP-001 Detail: Missing Ego Maneuver

Observed CarMaker log:

```text
SIM_START LLM_Generated/LOO_pedestrian_crossing_no_validate
ERROR DrivMan: No or invalid maneuver definition (nMan=0)
SIM_ABORT
```

Generated TestRun had:

```text
DrivMan.nMan = 0
```

Manual patch applied in the original AGI project TestRun:

```text
DrivMan.nMan = 1
DrivMan.Man.Start.Velocity = 50
DrivMan.Man.Start.GearNo = 4
DrivMan.Man.0.nLongSteps = 1
DrivMan.Man.0.nLatSteps = 1
DrivMan.Man.0.CombinedSteps = 1
DrivMan.Man.0.MaxExec = 1
DrivMan.Man.0.ConsiderDomain = own
DrivMan.Man.0.Transition.Interrupt = end
DrivMan.Man.0.Transition.EndCond = end
DrivMan.Man.0.Transition.SimultanStart = end
DrivMan.Man.0.LongStep.0.Cmds:
DrivMan.Man.0.LongStep.0.Dyn = VelControl 50 0.0 1.0 0 1 0
DrivMan.Man.0.LatStep.0.Cmds:
DrivMan.Man.0.LatStep.0.Dyn = Driver 0
```

Postprocessor rule:

```text
if DrivMan.nMan is missing or 0:
  add a conservative default ego maneuver from IR ego.behavior
```

## GAP-002 Detail: Pedestrian Trajectory Dropped

Source snippet in `pedestrian_crossing.xosc` contains:

```xml
<FollowTrajectoryAction>
  <TrajectoryRef>
    <Trajectory name="ped_crossing" closed="false">
      <Shape>
        <Polyline>
          <Vertex time="0.0">...</Vertex>
          <Vertex time="3.0">...</Vertex>
          <Vertex time="6.0">...</Vertex>
        </Polyline>
      </Shape>
    </Trajectory>
  </TrajectoryRef>
  <TimeReference>
    <Timing domainAbsoluteRelative="relative" scale="1.0" offset="0.0"/>
  </TimeReference>
  <TrajectoryFollowingMode followingMode="position"/>
</FollowTrajectoryAction>
```

Converter log:

```text
[Conversion] Invalid maneuver definition for entity "Pedestrian1": For traffic, DynamicsShape does not support cubic, sinusoidal, and step for SpeedAction.
[Conversion] "--interpolate" is defined without FollowTrajectoryAction. This argument is ignored.
```

Generated TestRun:

```text
Traffic.0.Name = T00
Traffic.0.Template.FName = LLM_Generated/LOO_pedestrian_crossing_no_validate_Pedestrian1
Traffic.0.nMan = 0
```

Current interpretation:

- The converter requires a stricter OpenSCENARIO representation of `FollowTrajectoryAction`.
- The preceding unsupported pedestrian `SpeedAction` caused the whole pedestrian maneuver/event to be rejected.
- `FollowTrajectoryAction` can be converted when emitted as the standalone pedestrian maneuver.

Focused reproduction:

1. Create a minimal OpenSCENARIO XML 1.2 pedestrian trajectory file.
2. Include `<Properties/>`.
3. Remove the pedestrian `SpeedAction`; use only `FollowTrajectoryAction`.
4. Run `osc2cm --validate --oscversion 120 --interpolate`.
5. Check whether generated TestRun has `Traffic.0.nMan > 0`.

Result without strict validation, using `pedestrian_crossing_follow_only_v12.xosc`:

```text
[Conversion] Invalid maneuver definition for entity "Pedestrian1": FollowTrajectoryAction with " FollowingMode = position " is not supported. The mode will be implemented with mode "follow".
[Conversion] Calculating orientation for the trajectory with "Spline" mode.
Process finished successfully.
```

Generated TestRun:

```text
Traffic.0.Routing.ObjId = 18
Traffic.0.Routing.Type = Path
Traffic.0.Man.0.LatStep.0.Dyn = FollowTraj
Traffic.0.Man.0.LatStep.0.Pos.Type = Global
Traffic.0.Man.0.LongStep.0.Dyn = FollowTraj
Traffic.0.Man.0.StartCond = rise((DistToObj("T00", "Ego", "long", "trigCoM", "refRearAxle") < 30.000 && DistToObj("T00", "Ego", "long", "trigCoM", "refRearAxle") >= 0))
Traffic.0.nMan = 1
```

Strict validation still needs an additional top-level `Storyboard/StopTrigger` fix in the generated XML.

Fallback postprocessor rule:

```text
if IR actor.behavior.type == follow_trajectory and generated Traffic.<i>.nMan == 0:
  synthesize native CarMaker Traffic.<i>.Man.0 LongStep/LatStep FollowTraj
  translate IR trajectory vertices into CarMaker trajectory data rows
  set Traffic.<i>.Man.Start.StartCond from IR trigger
```

Native reference shape from `AEB_BusStop_collisiion_for_LLM`:

```text
Traffic.0.Man.Start.Velocity = 0
Traffic.0.Man.Start.StartCond = Traffic.cross_ob.sRoad-Vhcl.sRoad<24.5
Traffic.0.Man.0.LongStep.0.Dyn = FollowTraj
Traffic.0.Man.0.LatStep.0.Dyn = FollowTraj
Traffic.0.Man.0.LatStep.0.Data:
    0 0 0 0 -1 0
    0.2 0.2 90 0 0.25 10
    0.2 11 90 0 4 10
    0.4 11.2 0 0 0.25 0
```

## Postprocessor Candidate Responsibilities

The postprocessor should read:

- scenario IR
- generated `.xosc`
- generated CarMaker TestRun
- `osc2cm` log

Then it should:

- patch missing ego maneuver
- patch missing traffic maneuvers from IR
- rewrite road/template paths into the chosen CarMaker project subfolders
- check every `Traffic.<i>.Template.FName` exists
- check `Road.FName` exists
- report unsupported converter warnings as structured failures
- produce a final conversion report

## GAP-007 Detail: Behavior Mismatch Without Runtime Error

Observed runtime behavior:

```text
TestRun starts without the previous DrivMan error, but the pedestrian does not cross in front of ego.
```

Generated TestRun state before manual patch:

```text
Traffic.0.Name = T00
Traffic.0.StartPos = 60.000 5.000
Traffic.0.Man.Start.StartCond =
Traffic.0.nMan = 0
```

This is an important class of failure: CarMaker can run the TestRun, but the generated behavior is not the requested scenario.

Manual postprocess experiment applied in:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\LOO_pedestrian_crossing_no_validate
```

Patch intent:

- trigger crossing when ego approaches
- add native CarMaker `FollowTraj` maneuver

Manual patch attempt:

```text
Traffic.0.StartPos = 60.000 -5.000
Traffic.0.Man.Start.StartCond = Traffic.T00.sRoad-Vhcl.sRoad<30
Traffic.0.Man.TreatAtEnd = FreezePos
Traffic.0.nMan = 1
Traffic.0.Man.0.nLongSteps = 1
Traffic.0.Man.0.nLatSteps = 1
Traffic.0.Man.0.CombinedSteps = 1
Traffic.0.Man.0.MaxExec = 1
Traffic.0.Man.0.ConsiderDomain = own
Traffic.0.Man.0.Transition.Interrupt = end
Traffic.0.Man.0.Transition.EndCond = end
Traffic.0.Man.0.Transition.SimultanStart = end
Traffic.0.Man.0.LongStep.0.Limit = t 4.5
Traffic.0.Man.0.LongStep.0.Dyn = FollowTraj
Traffic.0.Man.0.LongStep.0.TimeRef = Relative
Traffic.0.Man.0.LongStep.0.ChannelInput = TimeAndVel
Traffic.0.Man.0.LatStep.0.Limit = t 4.5
Traffic.0.Man.0.LatStep.0.Dyn = FollowTraj
Traffic.0.Man.0.LatStep.0.Data:
    0 0 0 0 -1 0
    0.2 0.2 90 0 0.25 10
    0.2 11 90 0 4 10
    0.4 11.2 0 0 0.25 0
Traffic.0.Man.0.LatStep.0.CurvatureActive = 1
Traffic.0.Man.0.LatStep.0.Shape = Spline
Traffic.0.Man.0.LatStep.0.TimeChan = 1
Traffic.0.Man.0.LatStep.0.Pos.Type = RelativeRoute
Traffic.0.Man.0.LatStep.0.Pos.Reference = T00
Traffic.0.Man.0.LatStep.0.Pos.Orientation.Type = Relative
```

This patch is intentionally copied from the known-good native pedestrian crossing pattern in `AEB_BusStop_collisiion_for_LLM`. Runtime result showed the lateral sign change was invalid for the generated road/lane:

```text
ERROR Invalid lane position on lane with object id 41
ERROR Traffic object 0: Failed to get start position
ERROR Can't get start position of traffic object 0
SIM_ABORT
```

Correction applied:

```text
Traffic.0.StartPos = 60.000 5.000
```

Keep the converter-generated lane object id and lateral start position until a road-aware postprocessor can validate safe lateral offsets.

Postprocessor rule refinement:

```text
For each IR actor with follow_trajectory:
  locate matching Traffic.<i> by actor name or converter-generated order
  if Traffic.<i>.nMan == 0:
    synthesize native FollowTraj
  do not change Traffic.<i>.StartPos unless the target lane object and offset are validated against the .rd5
  after simulation, verify that actor sRoad/tRoad crosses the ego path envelope
```

## GAP-008 Detail: Invalid Lane Start Position

Observed CarMaker log:

```text
ERROR Invalid lane position on lane with object id 41
ERROR Traffic object 0: Failed to get start position
ERROR Can't get start position of traffic object 0
SIM_ABORT
```

Cause:

```text
Traffic.0.StartPos.ObjId = 41
Traffic.0.StartPos = 60.000 -5.000
```

The converter-generated value was:

```text
Traffic.0.StartPos.ObjId = 41
Traffic.0.StartPos = 60.000 5.000
```

Rule:

```text
Preserve converter-generated StartPos unless the postprocessor can prove the new s/t pair is valid for that lane object id.
```

## GAP-009 Detail: Pedestrian Disappears At Trigger

Observed runtime behavior:

```text
Pedestrian is visible before the trigger point, then disappears when the trigger should start crossing.
```

State before current test patch:

```text
Traffic.0.StartPos.Type = Lane
Traffic.0.StartPos.ObjId = 41
Traffic.0.StartPos = 60.000 5.000
Traffic.0.Man.0.LatStep.0.Dyn = FollowTraj
Traffic.0.Man.0.LatStep.0.Pos.Type = RelativeRoute
Traffic.0.Man.0.LatStep.0.Pos.Reference = T00
```

Generated road:

```text
nRoutes = 0
```

Hypothesis:

```text
The copied FollowTraj block expects a route-based coordinate basis, but this generated road/TestRun is lane-based. At trigger time the trajectory is evaluated against an unavailable/invalid route basis, so the object disappears.
```

Failed test patch:

```text
Traffic.0.Man.0.LatStep.0.Pos.Type = RelativeObject
Traffic.0.Man.0.LatStep.0.Pos.Reference = T00
```

Runtime result:

```text
ERROR Wrong number of elements or syntax error in 'Traffic.0.Man.0.LatStep.0.Data'
ERROR Traffic object 0: LatStep 0 in Man. 0 table could not be read, or had no entries.
ERROR Traffic object 0: failed to initialize lateral step 0 in maneuver 0
ERROR Can't get parameters of traffic object 0 (2)
SIM_ABORT
```

Correction applied:

```text
Traffic.0.Man.0.LatStep.0.Pos.Type = RelativeRoute
```

This restores the known table syntax but returns to the previous behavioral issue. The better fix is to regenerate `.xosc` so `osc2cm` creates its own `Path`/`Global` FollowTraj table.

Focused converter output from standalone `FollowTrajectoryAction`:

```text
Traffic.0.Man.0.LatStep.0.Data:
    60.000 0.500 0.000 -90.000 0.000
    60.000 -1.500 0.000 90.000 3.000
    60.000 6.500 0.000 90.000 6.000
Traffic.0.Man.0.LatStep.0.Pos.Type = Global
Traffic.0.Routing.Type = Path
Traffic.0.Routing.ObjId = 18
```

Rule under test:

```text
If generated .rd5 has no routes and Traffic.<i>.StartPos.Type = Lane, do not synthesize RelativeRoute FollowTraj. Prefer standalone OpenSCENARIO `FollowTrajectoryAction` and let `osc2cm` generate `Routing.Type = Path` plus `Pos.Type = Global`.
```

## GAP-011 Detail: FollowTraj Table Format Depends On Coordinate Basis

Observed CarMaker log:

```text
ERROR Wrong number of elements or syntax error in 'Traffic.0.Man.0.LatStep.0.Data', file 'Data/TestRun/LLM_Generated/LOO_pedestrian_crossing_no_validate'
ERROR Traffic object 0: LatStep 0 in Man. 0 table could not be read, or had no entries.
ERROR Traffic object 0: failed to initialize lateral step 0 in maneuver 0
ERROR Can't get parameters of traffic object 0 (2)
SIM_ABORT
```

Cause:

```text
Traffic.0.Man.0.LatStep.0.Data:
    0 0 0 0 -1 0
    0.2 0.2 90 0 0.25 10
    0.2 11 90 0 4 10
    0.4 11.2 0 0 0.25 0
Traffic.0.Man.0.LatStep.0.Pos.Type = RelativeObject
```

The data rows were copied from known `RelativeRoute` examples. Changing only `Pos.Type` to `RelativeObject` made the row syntax invalid.

Rule:

```text
The postprocessor must treat FollowTraj table generation as format-specific. Coordinate basis, row arity, and reference fields must be generated together.
```

## GAP-010 Detail: Why Generated Roads Have No Routes

Observed generated road:

```text
Data/Road/LLM_Generated/simple_road.rd5
nRoutes = 0
LanePath.0 = ...
LanePath.1 = ...
LanePath.2 = ...
LanePath.3 = ...
```

The source OpenDRIVE file contains:

```text
road geometry
lane sections
lane ids
lane widths
road markings
```

It does not contain CarMaker Scenario Editor route objects. After conversion, CarMaker has lane object ids and lane paths, but not `Route.*` entries.

Important distinction:

```text
OpenDRIVE road/lane network != CarMaker route object
```

Existing native AEB scenarios can use:

```text
Vehicle.Routing.Type = Route
Vehicle.Routing.ObjId = 4238
Traffic.0.Routing.Type = Route
Traffic.0.Routing.ObjId = 4238
```

because their referenced road file or native setup has route/path objects created in CarMaker's scenario/road tooling. The generated `simple_road.rd5` does not have `Route.*`, but it does have `LanePath.*`.

Focused test result:

```text
OpenSCENARIO FollowTrajectoryAction only
  -> osc2cm --interpolate
  -> Traffic.0.Routing.Type = Path
  -> Traffic.0.Routing.ObjId = 18
  -> Traffic.0.Man.0.* FollowTraj generated
```

Rules:

```text
Do not assume generated OpenDRIVE roads contain CarMaker Route objects.
Do not require Route objects for pedestrian trajectory in the first slice.
Let osc2cm generate Path/Global FollowTraj by emitting standalone FollowTrajectoryAction.
If a postprocessor emits RelativeRoute or Routing.Type=Route, first verify nRoutes > 0 and target route object ids exist.
```

## Manual Update Rule

Whenever a new CarMaker error appears:

1. Paste the exact CarMaker log line.
2. Identify the generated TestRun key involved.
3. Classify as `input_xml`, `converter_subset`, `postprocess_needed`, or `unknown`.
4. Add a deterministic postprocessor or exporter rule.
5. Re-run the same TestRun.

## GAP-026 Detail: Signalized Intersection Runtime Is More Than Road Signal Import

Observed in TGT-003:

```text
The converted Road5 contains Control.TrfLight.0..3.
The 3D animation did not visibly change during the user's runtime check.
The ego did not complete the intended intersection passage before the earlier 12 s stop trigger.
```

Classification:

```text
unknown / postprocess_needed
```

Current distinction:

```text
OpenDRIVE signal import -> Road5 Control.TrfLight.* exists
Runtime signal logic -> TrfLight.*.State changes during simulation
3D animation -> rendered traffic-light mesh visibly changes
```

These are not the same validation layer. A generated signalized-intersection
scenario must not be accepted solely because `Control.TrfLight.*` exists.

Rules:

```text
For signalized scenarios, set a StopTrigger long enough for wait, release, conflict, and clear phases.
Record runtime signal-state output such as TrfLight.*.State when available.
If state stays static or does not match the intended red-start/release phase, add a Road5 traffic-light phase postprocessor.
If state changes but the mesh does not animate, classify it as visualization linkage rather than scenario logic.
```

## GAP-027 Detail: OpenDRIVE `s` Direction Can Reverse Converted Junction Paths

Observed in TGT-003 v4p1:

```text
Ego converted FollowTraj x:
60 -> 82 -> 99 -> 112 -> 199 -> 169 -> 169

Traffic converted FollowTraj y:
57 -> 32 -> 13 -> 0 -> -87 -> -57 -> -57
```

Classification:

```text
input_xml
```

Cause:

```text
Road 2 and road 3 are geometrically opposite to the desired travel direction after the junction.
Using increasing LanePosition s on those outgoing roads makes the converted global path move back toward the intersection.
```

Rule:

```text
For every junction path, inspect the outgoing road geometry and contact point.
If the actor enters an outgoing road at contactPoint=end, use decreasing OpenDRIVE s to move away from the junction.
After conversion, check the generated Global FollowTraj coordinates for monotonic progress in the intended world direction.
Do not install a candidate only because osc2cm validation passes.
```
