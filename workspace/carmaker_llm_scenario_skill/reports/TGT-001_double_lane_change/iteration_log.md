# TGT-001 Double Lane Change Iteration Log

Created: 2026-05-12

Reference:

```text
E:\CarMakerProject\AGI\Data\TestRun\test_double_lanechange_trajectory
E:\CarMakerProject\AGI\Data\Road\test_double_lanechange_trajectory_road.rd5
```

## Current Best Candidate

Candidate:

```text
workspace/carmaker_llm_scenario_skill/generated/TGT-001_double_lane_change/tgt001_double_lane_change_v7.xosc
workspace/carmaker_llm_scenario_skill/generated/TGT-001_double_lane_change/tgt001_double_lane_change_v7.xodr
```

Converted TestRun:

```text
workspace/carmaker_llm_scenario_skill/conversion_scratch/AGI_LLM_TestProject/Data/TestRun/TGT001_double_lane_change_v7
```

Comparison:

```text
workspace/carmaker_llm_scenario_skill/reports/TGT-001_double_lane_change/v7/comparison.md
```

Result:

```text
STRUCTURAL PARTIAL PASS
Only failing structural gate: road filename differs.
RUNTIME START PASS in original CarMaker project.
```

Passing gates in v7:

- ego routing type: `Path`
- ego start type: `Global`
- ego maneuver count: `2`
- traffic count: `8`
- traffic actor class distribution: `7 vehicle`, `1 pedestrian`
- traffic start type distribution: `Lane=2`, `Link=1`, `RelativeGlobal=1`, `RelativeLane=1`, `RelativeLink=1`, `RelativeObject=2`
- dynamics distribution: `FollowTraj=2`, `LaneChange=4`, `VelTransition=4`
- ordered actor signature sequence

Remaining gaps:

- road identity differs: reference uses `test_double_lanechange_trajectory_road.rd5`; candidate uses generated `tgt001_double_lane_change_v7.rd5`
- CarMaker supported-feature validator still warns about `Pedestrian` declaration even though conversion creates a pedestrian traffic template

## Iteration Notes

### v0

Input:

```text
tgt001_double_lane_change_v0.xosc
simple_road.xodr
```

Result:

- strict OpenSCENARIO 1.2 API validation passed
- traffic count/classes/dynamics matched
- `RoadPosition`/`RelativeRoadPosition` were not yet used, so start type distribution failed
- ego path was emitted as FollowTraj data, but path/routing was not valid because trajectory points were not road-coherent

Key learning:

```text
WorldPosition trajectory points can produce FollowTraj rows, but they must be inside the generated road geometry if we need CarMaker Path routing.
```

### v1

Changes:

- used `RoadPosition` for the actor that should become CarMaker `Link`
- used `RelativeRoadPosition` for the actor that should become CarMaker `RelativeLink`
- added ego init speed
- used `--defaultman 99999`

Result:

- traffic start type distribution matched the reference
- actor signature sequence matched
- ego FollowTraj disappeared because LanePosition trajectory vertices exceeded `simple_road.xodr` length

Key learning:

```text
OpenSCENARIO RoadPosition maps to CarMaker StartPos.Type=Link.
OpenSCENARIO RelativeRoadPosition maps to CarMaker StartPos.Type=RelativeLink.
```

### v2

Changes:

- generated a longer 650 m OpenDRIVE road
- referenced `tgt001_double_lane_change_v2.xodr`

Result:

- road length was no longer the blocker
- ego initial `WorldPosition y=-11.5` was still outside the generated simple road lane bounds, so Path creation failed

Key learning:

```text
If ego starts with WorldPosition and then follows a LanePosition trajectory, the WorldPosition must also resolve to a valid road object.
```

### v3

Changes:

- moved ego global y from `-11.5` to `-4.5`, inside the generated 4-lane road

Result:

- ego `Vehicle.Routing.Type=Path`
- `DrivMan.nMan=2`
- all structural gates except road identity passed

Key learning:

```text
CarMaker can convert generated OpenSCENARIO FollowTrajectoryAction into ego Path routing and native FollowTraj when start and vertices are road-coherent.
```

### v4

Changes:

- changed Bus `vehicleCategory` from `truck` to `car` while keeping ScenarioObject name `Bus`

Result:

- removed the vehicle-category supported-feature warning
- structural comparison remains the same as v3

Key learning:

```text
Use CarMaker-supported vehicleCategory values conservatively; preserve semantic class in ScenarioObject/template names when needed.
```

Runtime result in original CarMaker project:

```text
SIM_START LLM_Generated/TGT001_double_lane_change_v4
ERROR Traffic object 1: Start position is outside of road
ERROR Can't get start position of traffic object 1
SIM_ABORT
```

Root cause:

```text
Ego global y = -4.5
Bus relative-global dy = 0.0
Pedestrian relative-object dy = -3.0
Resolved pedestrian y is about -7.5, outside the generated 3.0 m x 4-lane road.
```

### v5

Changes:

- changed `TrajectoryFollowingMode` from `position` to `follow`
- added explicit `0 m/s` init speed for parked cars

Result:

- removed the `followingMode=position` warning
- removed parked-car missing init speed warnings
- remaining warnings are the CarMaker supported-feature validator's pedestrian declaration warnings

### v6

Changes:

- generated `tgt001_double_lane_change_v6.xodr` with 4.0 m lane widths
- kept the v5 OpenSCENARIO improvements

Result:

- structural comparison still passes all non-road-identity gates
- osc2cm log has `0` errors and `7` warnings, all related to pedestrian supported-feature validation
- copied to original project as `LLM_Generated/TGT001_double_lane_change_v6`

Key learning:

```text
Generated roads must be sized from the resolved actor-position envelope, not only from nominal lane count.
```

Runtime result in original CarMaker project:

```text
SIM_START LLM_Generated/TGT001_double_lane_change_v6
ERROR Traffic object 2: Invalid position on link
ERROR Can't get start position of traffic object 2
SIM_ABORT
```

Root cause:

```text
Traffic.2 uses CarMaker StartPos.Type=Link from OpenSCENARIO RoadPosition.
Its position is s=100, t=-11.5, which still exceeded the generated road's usable lateral range.
```

### v7

Changes:

- added extra left/right lanes to `tgt001_double_lane_change_v7.xodr`
- kept actor positions unchanged to preserve the reference-like `Link`/`RelativeLink` semantics

Result:

- structural comparison still passes all non-road-identity gates
- copied to original project as `LLM_Generated/TGT001_double_lane_change_v7`
- user runtime check confirmed that v7 starts successfully in CarMaker

Key learning:

```text
Road generation must cover explicit RoadPosition.t values as well as relative actor offsets.
```

## Next Checks

1. Decide whether road identity should be exact filename equality or a separate road-structure comparison.
2. Add log parser gate for converter warnings instead of manually inspecting logs.
3. Observe v7 actor behavior in CarMaker if TGT-001 needs visual/trajectory validation beyond runtime start.
4. If exact reference road is required, generate an OpenDRIVE road closer to `test_double_lanechange_trajectory_road.rd5` or intentionally reuse/copy that rd5 as a native road dependency.
