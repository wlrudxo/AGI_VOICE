# Generation Rules from Validated Targets

Created: 2026-05-12

This document distills the rules learned from the first two validated CarMaker
targets:

- `TGT-001`: double lane change, validated with `TGT001_double_lane_change_v7`
- `TGT-002`: AEB bus-stop pedestrian crossing, validated with `TGT002_aeb_bus_stop_core_v5p1`

Use this as the direct generation checklist before emitting `.xodr` / `.xosc`.
The broader workflow remains in `generation_manual.md`.

## Target Compatibility Baseline

Generate for:

```text
CarMaker 14.0.1
OpenSCENARIO XML 1.2-compatible input
OpenDRIVE road input
osc2cm conversion with --interpolate
postprocess_testrun.py for known converter gaps
```

Do not emit OpenSCENARIO 1.3/1.4-only features for the current backend.

## Final Accepted Examples

### TGT-001 Double Lane Change

Accepted source:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-001_double_lane_change/tgt001_double_lane_change_v7.xosc
workspace/carmaker_llm_scenario_skill/generated/TGT-001_double_lane_change/tgt001_double_lane_change_v7.xodr
```

Accepted converted TestRun:

```text
workspace/carmaker_llm_scenario_skill/conversion_scratch/AGI_LLM_TestProject/Data/TestRun/TGT001_double_lane_change_v7
```

Runtime result:

```text
LLM_Generated/TGT001_double_lane_change_v7 starts successfully in CarMaker.
```

Key output signature:

```text
Vehicle.Routing.Type = Path
Vehicle.StartPos.Type = Global
DrivMan.nMan = 2
Traffic.N = 8
Traffic start types:
  Lane=2
  Link=1
  RelativeGlobal=1
  RelativeLane=1
  RelativeLink=1
  RelativeObject=2
Traffic dynamics:
  LaneChange
  VelTransition
```

### TGT-002 AEB Bus Stop Pedestrian Crossing

Accepted source:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-002_aeb_bus_stop_pedestrian/tgt002_aeb_bus_stop_core_v5.xosc
workspace/carmaker_llm_scenario_skill/generated/TGT-002_aeb_bus_stop_pedestrian/tgt002_aeb_bus_stop_core_v5.xodr
```

Accepted postprocessed TestRun:

```text
workspace/carmaker_llm_scenario_skill/postprocessed/TGT-002_aeb_bus_stop_pedestrian/TGT002_aeb_bus_stop_core_v5p1
```

Runtime result:

```text
LLM_Generated/TGT002_aeb_bus_stop_core_v5p1 starts successfully in CarMaker.
Pedestrian timing and disappearance issue are fixed by delayed trigger plus final hold vertex.
```

Key output signature:

```text
Vehicle.StartPos.Type = Lane
Vehicle.StartPos.ObjId = 31
Vehicle.Routing.Type = Path
Traffic.0 = stopped bus / occluder
Traffic.0.StartPos.Type = Lane
Traffic.0.StartPos.ObjId = 41
Traffic.0.nMan = 0
Traffic.1 = crossing pedestrian
Traffic.1.StartPos.Type = Global
Traffic.1.Routing.Type = Path
Traffic.1.nMan = 1
Traffic.1.Man.0.StartCond = rise(Time > 2.000)
Traffic.1.Man.0.LatStep.0.Limit = t 12.000
Traffic.1.Man.0.LongStep.0.Limit = t 12.000
```

## Mandatory Generation Rules

### 1. Generate the road from the resolved actor envelope

Do not choose lane count or lane width only from the nominal road type. First
resolve every actor and trajectory into road/global coordinates, then generate a
road that contains them.

Check all of these before XML output:

- ego initial position
- every absolute `LanePosition`
- every absolute `RoadPosition.t`
- every `WorldPosition`
- every object-relative position after resolving the referenced actor
- every trajectory vertex
- every lane-change target lane

TGT-001 failures showed that a scenario can convert structurally and still abort
at runtime if the road does not contain a single resolved traffic start position.

Required envelope rule:

```text
road lateral envelope >= max_abs_lateral_position + vehicle_half_width + margin
road length > max_s_position + stopping/continuation margin
```

Use a practical first margin:

```text
lateral margin >= 1.0 m
longitudinal margin >= 20.0 m
```

### 2. Use OpenSCENARIO position types intentionally

The converter maps OpenSCENARIO placement types into distinct CarMaker start
types. Choose the type based on the desired CarMaker output, not by convenience.

Observed useful mappings:

| Desired CarMaker start type | OpenSCENARIO input |
| --- | --- |
| `Lane` | `LanePosition` |
| `Link` | `RoadPosition` |
| `RelativeLane` | `RelativeLanePosition` |
| `RelativeLink` | `RelativeRoadPosition` |
| `RelativeObject` | `RelativeObjectPosition` |
| `RelativeGlobal` | `RelativeWorldPosition` |
| `Global` | `WorldPosition` |

TGT-001 needs this variety to reproduce reference-like traffic layout. Do not
flatten every actor into `LanePosition`; it loses important CarMaker semantics.

### 3. Keep trajectory vertices road-coherent

For ego or traffic `FollowTrajectoryAction`, every vertex must be valid on the
generated road.

Required checks:

- all `s` values are less than road length
- all lane ids exist
- all global points resolve to a road/lane
- start position and first trajectory point are compatible
- `TrajectoryFollowingMode` is `follow`
- use `--interpolate` in `osc2cm`

TGT-001 v0-v3 showed that CarMaker can create `Path` and native `FollowTraj`,
but only when the start and all vertices are road-coherent.

Good TGT-001 pattern:

```xml
<FollowTrajectoryAction>
  <TrajectoryRef>
    <Trajectory name="ego_double_lane_change_path" closed="false">
      <Shape>
        <Polyline>
          <Vertex time="0.0">
            <Position><LanePosition roadId="0" laneId="-1" s="1.0" offset="0.0"/></Position>
          </Vertex>
          <Vertex time="7.0">
            <Position><LanePosition roadId="0" laneId="-1" s="193.0" offset="0.0"/></Position>
          </Vertex>
          <Vertex time="12.0">
            <Position><LanePosition roadId="0" laneId="-2" s="332.0" offset="0.0"/></Position>
          </Vertex>
          <Vertex time="20.1">
            <Position><LanePosition roadId="0" laneId="-1" s="555.0" offset="0.0"/></Position>
          </Vertex>
        </Polyline>
      </Shape>
    </Trajectory>
  </TrajectoryRef>
  <TimeReference>
    <Timing domainAbsoluteRelative="absolute" scale="1.0" offset="0.0"/>
  </TimeReference>
  <TrajectoryFollowingMode followingMode="follow"/>
</FollowTrajectoryAction>
```

### 4. Use conservative vehicle categories

CarMaker's supported-feature validator is narrower than the OpenSCENARIO schema.
For now:

- use `vehicleCategory="car"` for buses/trucks unless a category is proven
- keep semantic role in the object/template name, such as `Bus` or `stopped_bus`

Good pattern:

```xml
<ScenarioObject name="Bus">
  <Vehicle name="stopped_bus" vehicleCategory="car">
    ...
    <Properties/>
  </Vehicle>
</ScenarioObject>
```

### 5. Pedestrian motion must be standalone trajectory motion

For generated pedestrian crossing, do not combine the pedestrian
`FollowTrajectoryAction` with another pedestrian action in the same event. The
converter can drop the maneuver or produce static traffic.

Required pattern:

- initialize pedestrian with `TeleportAction`
- optionally initialize speed separately in `Init`
- use a standalone `FollowTrajectoryAction` event for the crossing
- use `TrajectoryFollowingMode followingMode="follow"`
- after conversion, run `postprocess_testrun.py` to fill `Limit = t {}`

Good TGT-002 pattern:

```xml
<Trajectory name="pedestrian_crossing_path" closed="false">
  <Shape>
    <Polyline>
      <Vertex time="0.0">
        <Position><WorldPosition x="84.0" y="-7.0" z="0.0" h="1.57079632679"/></Position>
      </Vertex>
      <Vertex time="2.0">
        <Position><WorldPosition x="84.0" y="-4.0" z="0.0" h="1.57079632679"/></Position>
      </Vertex>
      <Vertex time="4.0">
        <Position><WorldPosition x="84.0" y="-1.0" z="0.0" h="1.57079632679"/></Position>
      </Vertex>
      <Vertex time="6.0">
        <Position><WorldPosition x="84.0" y="3.0" z="0.0" h="1.57079632679"/></Position>
      </Vertex>
      <Vertex time="12.0">
        <Position><WorldPosition x="84.0" y="3.0" z="0.0" h="1.57079632679"/></Position>
      </Vertex>
    </Polyline>
  </Shape>
</Trajectory>
```

The final duplicate-position vertex is intentional. It keeps the pedestrian at
the completed crossing position until the scenario ends and prevents early
trajectory termination from causing disappearance.

### 6. For occluded pedestrian scenarios, validate spatial ordering

The actor order must match the scenario semantics.

Accepted TGT-002 ordering:

```text
ego starts behind
bus/occluder is ahead and on curb/adjacent lane
pedestrian starts on the far side of the bus
pedestrian crosses into ego conflict area after trigger
```

For the current straight RHT generated road:

```text
ego lane: laneId=-1, converted around ObjId 31
bus/curb lane: laneId=-2, converted around ObjId 41
pedestrian start: WorldPosition x=84, y=-7
```

Do not use:

```text
ego -> pedestrian -> bus
```

That makes the pedestrian visible from the start and changes the scenario into a
static exposed-pedestrian case.

Do not place the bus in `laneId=-1` for this scenario. That blocks ego's lane
instead of acting as a curb-side occluder.

### 7. Compute trigger timing from conflict timing

Do not pick arbitrary `SimulationTimeCondition` values. Estimate when the ego
will reach the conflict point and align the pedestrian trajectory accordingly.

TGT-002 accepted timing:

```text
ego path:
  s=10 at t=0
  s=52 at t=3
  s=94 at t=6
conflict point:
  s ~= 84
estimated ego arrival:
  t ~= 5.3 s
pedestrian trigger:
  Time > 2.0 s
pedestrian reaches ego lane neighborhood:
  trigger + 3 to 4 s ~= 5 to 6 s
```

This is why `Time > 0.5` was too early and `Time > 2.0` is the current accepted
core timing.

### 8. Always add a hold segment for finite actor trajectories

If a moving traffic actor should remain visible after completing a maneuver,
extend the trajectory with a final hold vertex at the same final position.

Rule:

```text
final_hold_time >= scenario_stop_time or at least beyond expected visual check window
```

Then postprocess should set:

```text
Traffic.<i>.Man.<j>.LatStep.<k>.Limit = t <final_hold_time>
Traffic.<i>.Man.<j>.LongStep.<k>.Limit = t <final_hold_time>
```

TGT-002 accepted value:

```text
final_hold_time = 12.000
```

### 9. Treat converter warnings as gates unless documented

Known documented exception:

```text
CarMaker supported-feature validation warns about Pedestrian declaration,
but conversion can still create a traffic template and runtime can pass.
```

Everything else should fail the generation attempt until classified in
`converter_gap_log.md`.

### 10. Postprocess and package every accepted candidate

Required postprocess for current traffic trajectories:

```bash
python3 workspace/carmaker_llm_scenario_skill/scripts/postprocess_testrun.py \
  <converted_testrun> \
  --out <postprocessed_testrun> \
  --report <postprocess_report.txt>
```

Required packaging helper:

```bash
python3 workspace/carmaker_llm_scenario_skill/scripts/package_for_project.py \
  --scenario <TestRunName> \
  --testrun <converted_or_postprocessed_testrun> \
  --road <generated_rd5> \
  --templates <template_1> <template_2> ... \
  --subdir LLM_Generated \
  --install \
  --project /mnt/e/CarMakerProject/AGI
```

Manual copying is no longer the reference workflow.

## Golden IR Patterns

### Double Lane Change Pattern

```yaml
scenario:
  id: TGT001_double_lane_change
  road:
    kind: straight
    length_m: 650
    lanes:
      right: [-1, -2, -3, -4]
      left: [1, 2, 3, 4]
    rule: contain every RoadPosition.t and relative-object lateral offset
  ego:
    start:
      type: world
      x_m: 1.0
      y_m: -4.5
      heading_rad: 0.0
    behavior:
      type: follow_trajectory
      following_mode: follow
      vertices:
        - {time_s: 0.0, road_id: "0", lane_id: -1, s_m: 1.0}
        - {time_s: 7.0, road_id: "0", lane_id: -1, s_m: 193.0}
        - {time_s: 12.0, road_id: "0", lane_id: -2, s_m: 332.0}
        - {time_s: 20.1, road_id: "0", lane_id: -1, s_m: 555.0}
  actors:
    - role: occluding_bus
      category: car
      start: {type: relative_world, entity: Ego, dx_m: 80.0, dy_m: 0.0}
    - role: pedestrian
      start: {type: relative_object, entity: Bus, dx_m: -30.0, dy_m: -3.0}
    - role: lane_change_vehicle
      start: {type: road, road_id: "0", s_m: 100.0, t_m: -11.5}
      behavior: lane_change_sequence
    - role: speed_change_vehicle
      start: {type: relative_road, entity: car2, ds_m: 60.0, dt_m: -3.5}
      behavior: speed_transition_sequence
```

### AEB Bus Stop Pedestrian Pattern

```yaml
scenario:
  id: TGT002_aeb_bus_stop_core
  stop_time_s: 12.0
  road:
    kind: straight
    lanes:
      right: [-1, -2]
    lane_meaning:
      -1: ego travel lane
      -2: curb_or_bus_lane
  ego:
    start: {type: lane, road_id: "0", lane_id: -1, s_m: 10.0}
    behavior:
      type: follow_trajectory
      vertices:
        - {time_s: 0.0, lane_id: -1, s_m: 10.0}
        - {time_s: 3.0, lane_id: -1, s_m: 52.0}
        - {time_s: 6.0, lane_id: -1, s_m: 94.0}
        - {time_s: 9.0, lane_id: -1, s_m: 136.0}
  actors:
    - role: stopped_bus_occluder
      category: car
      start: {type: lane, road_id: "0", lane_id: -2, s_m: 78.0}
      initial_speed_mps: 0.0
    - role: crossing_pedestrian
      type: pedestrian
      start: {type: world, x_m: 84.0, y_m: -7.0, heading_rad: 1.57079632679}
      behavior:
        type: follow_trajectory
        trigger: {type: simulation_time, value_s: 2.0}
        following_mode: follow
        vertices:
          - {time_s: 0.0, x_m: 84.0, y_m: -7.0}
          - {time_s: 2.0, x_m: 84.0, y_m: -4.0}
          - {time_s: 4.0, x_m: 84.0, y_m: -1.0}
          - {time_s: 6.0, x_m: 84.0, y_m: 3.0}
          - {time_s: 12.0, x_m: 84.0, y_m: 3.0}
```

## Pre-Conversion Checklist

Before running `osc2cm`, verify:

- `FileHeader revMinor="2"`
- every entity has `<Properties/>`
- all vehicle categories are conservative
- road length covers max `s`
- road lateral envelope covers max `t`, `y`, and relative offsets
- no pedestrian trajectory event is mixed with another pedestrian action
- `followingMode="follow"`
- occlusion ordering is semantically correct
- pedestrian crossing path is monotonic unless a non-monotonic path is intended
- time trigger aligns with conflict-point arrival
- finite crossing trajectories include final hold vertex

## Post-Conversion Checklist

Before installing into `E:\CarMakerProject\AGI`, verify:

- generated `.rd5` exists
- generated TestRun exists
- `Vehicle.Routing.Type` matches expectation
- all moving actors have `nMan > 0`
- no remaining `Limit = t {}`
- generated template files exist
- no runtime-blocking converter warnings are unclassified
- package helper rewrites `Road.FName` and generated templates into `LLM_Generated/`

