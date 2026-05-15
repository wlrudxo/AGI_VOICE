# CarMaker Scenario Generation Manual

Created: 2026-05-12

## Decision

Generate CarMaker scenarios through this path first:

```text
Natural language request
  -> strict scenario IR
  -> OpenDRIVE .xodr + OpenSCENARIO XML 1.2-compatible .xosc
  -> CarMaker osc2cm validation
  -> CarMaker Road5 .rd5 + TestRun
  -> CarMaker postprocessor
  -> manual/runtime check in CarMaker
```

Do not target OpenSCENARIO XML 1.3 or 1.4 for the first CarMaker backend. CarMaker 15.0.1's local `osc2cm` validation assets currently stop at OpenSCENARIO 1.2.

Do not route through SUMO for the first slice.

## Current Validated Rule Set

For generation details learned from the first runtime-passing targets, use:

```text
workspace/carmaker_llm_scenario_skill/generation_rules_from_validated_targets.md
```

That document contains the current hard rules and golden IR/XML patterns from:

- `TGT001_double_lane_change_v7`
- `TGT002_aeb_bus_stop_core_v5p1`

## Folder Contract

Work inside:

```text
workspace/carmaker_llm_scenario_skill/
```

Reference examples:

```text
examples/raw/xosc/
examples/raw/xodr/
examples/raw/testrun/
examples/index/examples.jsonl
examples/index/summary.json
```

Generated candidate files:

```text
generated/<scenario_id>.ir.yaml
generated/<scenario_id>.xodr
generated/<scenario_id>.xosc
logs/<scenario_id>_validate.log
logs/<scenario_id>_convert.log
```

Scratch CarMaker project:

```text
conversion_scratch/AGI_LLM_TestProject/
```

The original project:

```text
E:\CarMakerProject\AGI
```

Only copy a generated scenario into the original project after it passes scratch validation/conversion.

## Scenario Scope

A generated scenario must include:

- map / road network
- ego vehicle initial position
- ego target route or trajectory
- ego initial speed or speed behavior
- other vehicles and pedestrians
- initial positions for all actors
- actor speed, trajectory, route, or direction
- trigger conditions for dynamic actions
- CarMaker-loadable conversion output

## Intermediate Representation

Always generate and validate IR before writing XML.

Minimal IR shape:

```yaml
schema_version: 1
scenario:
  id: LLM_PedestrianCrossing_001
  description: Ego approaches a pedestrian crossing on a straight two-lane road.
  road:
    mode: generated_opendrive
    id: "0"
    kind: straight
    length_m: 250
    lane_width_m: 3.5
    lanes:
      right: [-1, -2]
      left: []
  ego:
    name: Ego
    vehicle_infofile: DemoCar_AEB_TEST
    start:
      road_id: "0"
      lane_id: -1
      s_m: 10
      offset_m: 0
    initial_speed_mps: 13.89
    behavior:
      type: speed_hold
      speed_mps: 13.89
  actors:
    - name: Pedestrian1
      type: pedestrian
      start:
        road_id: "0"
        lane_id: -2
        s_m: 60
        offset_m: 4.5
      behavior:
        type: follow_trajectory
        trigger:
          type: relative_distance
          entity: Ego
          target: Pedestrian1
          value_m: 30
          rule: lessThan
        trajectory:
          vertices:
            - {time_s: 0.0, road_id: "0", lane_id: -2, s_m: 60, offset_m: 4.5}
            - {time_s: 3.0, road_id: "0", lane_id: -1, s_m: 60, offset_m: 0.0}
            - {time_s: 6.0, road_id: "0", lane_id: 1, s_m: 60, offset_m: -4.5}
```

## IR Validation Rules

Fail before XML generation if any rule fails:

- `scenario.id` is unique and filesystem-safe.
- Ego exists and is named `Ego` unless there is a strong reason not to.
- Every actor name is unique.
- Every referenced actor exists.
- Every `road_id` exists in the road definition.
- Every `lane_id` exists in the generated OpenDRIVE lane plan.
- Every `s_m` is within road length.
- Every actor has a valid initial position.
- Speeds are in m/s.
- Trajectory times are monotonic.
- Trigger references are unambiguous.
- No two actors start in clearly overlapping positions.
- Pedestrian and vehicle categories are not mixed.
- The generated road lateral envelope contains every actor's resolved initial position, including positions derived from relative-object offsets.
- The generated road lateral envelope contains every `RoadPosition.t` / CarMaker `Link` start position directly, not just lane-center starts.
- The generated road lateral envelope contains every trajectory vertex after resolving lane/global coordinates.
- For occlusion-based AEB/pedestrian scenarios, actor ordering must match the scenario intent. The occluding vehicle should be between ego and the pedestrian's emergence point, or close enough to hide the pedestrian initially. Avoid `ego -> pedestrian -> occluder` ordering unless the intended scenario is an already exposed pedestrian.

## OpenDRIVE Output Rules

For the first generator slice, prefer simple roads:

- straight road
- no junction unless the scenario explicitly requires it
- lane ids compatible with OpenSCENARIO `LanePosition`
- explicit lane width
- conservative geometry

Use more complex OpenDRIVE features only after the simple straight-road cases pass conversion.

## OpenSCENARIO XML Rules

Target OpenSCENARIO XML 1.2-compatible output:

```xml
<FileHeader revMajor="1" revMinor="2" .../>
```

Every `Vehicle` and `Pedestrian` must include `Properties`:

```xml
<Vehicle ...>
  ...
  <Properties/>
</Vehicle>
```

```xml
<Pedestrian ...>
  ...
  <Properties/>
</Pedestrian>
```

Use SI units:

- speed: m/s
- distance: m
- time: s
- angle: rad

Prefer these action primitives first:

- `TeleportAction` for initial placement
- `SpeedAction` for simple speed setup
- `AssignRouteAction` for route following
- `FollowTrajectoryAction` for explicit trajectories
- `RelativeDistanceCondition` and `SimulationTimeCondition` for triggers

For pedestrian trajectory conversion, emit `FollowTrajectoryAction` as a standalone maneuver event. Do not combine it with a pedestrian `SpeedAction` in the same event/maneuver; CarMaker `osc2cm` may drop the whole traffic maneuver.

For CarMaker start-position shape control:

- use `LanePosition` when CarMaker `StartPos.Type = Lane` is acceptable
- use `RoadPosition` when CarMaker `StartPos.Type = Link` is required
- use `RelativeLanePosition` when CarMaker `StartPos.Type = RelativeLane` is required
- use `RelativeRoadPosition` when CarMaker `StartPos.Type = RelativeLink` is required
- use `RelativeWorldPosition` or `RelativeObjectPosition` when object-relative placement is required

For `FollowTrajectoryAction` conversion into CarMaker `Path`/`FollowTraj`:

- every trajectory vertex must lie inside the generated road network
- OpenDRIVE road length must exceed the maximum trajectory `s`
- if ego starts from `WorldPosition`, that global point must resolve to a road object
- if the generated road is narrow, do not reuse global lateral offsets from a wider reference road
- relative actor positions must be checked after resolving the reference actor position; for example, ego `y=-4.5`, bus `dy=0`, pedestrian `dy=-3.0` requires road coverage near `y=-7.5`
- use `--interpolate` for polyline trajectories
- use `--defaultman 99999` when ego should continue after the trajectory maneuver

For bus-stop / occluded pedestrian crossing scenarios:

- place the bus or stopped vehicle as an occluder in ego's forward path or adjacent lane before the pedestrian becomes visible
- place the pedestrian on the far side or outer side of the occluder, not between ego and the occluder at simulation start
- if the pedestrian is visible at init, ego/AEB may stop before a distance-based pedestrian trigger fires
- use a time trigger for early core validation when the objective is to verify pedestrian movement first
- after movement is verified, tune a physically meaningful trigger such as ego-to-occluder distance or ego-to-crossing distance

For generated straight RHT roads used in the current tests:

```text
OpenDRIVE lane -1: ego travel lane, CarMaker lane object around ObjId 31
OpenDRIVE lane -2: curb/bus lane on the same side, CarMaker lane object around ObjId 41
OpenDRIVE lane +1/+2: oncoming-side lanes
```

Do not place the bus in `laneId=-1` when the scenario is a bus-stop occlusion
case. That puts the bus in ego's lane. Use `laneId=-2` or an explicit bus-bay
lane/shoulder, then place the pedestrian on the outside/far side of that bus.

For semantic vehicle roles not accepted by CarMaker's supported-feature validator:

- keep the semantic role in the `ScenarioObject` name, for example `Bus`
- use a conservative supported `vehicleCategory`, currently `car`, unless a category is proven to pass validation

Avoid in the first CarMaker backend:

- OpenSCENARIO XML 1.3/1.4-only elements
- `RandomRouteAction`
- `MonitorDeclaration`
- `SetMonitorAction`
- `TrailerAction`
- `ClothoidSpline`
- traffic `SpeedActionDynamics` with `dynamicsShape="linear"` and `dynamicsDimension="rate"`
- pedestrian traffic speed changes with `dynamicsShape="step"`
- traffic `LaneChangeActionDynamics` with `dynamicsShape="sinusoidal"`

These are not necessarily bad standard features. They are excluded because current CarMaker 15.0.1 `osc2cm` logs showed validation or conversion subset issues.

## Reference DB Usage

Use examples for structure, not direct cloning.

Good reference use:

- road reference pattern
- entity layout
- action/trigger nesting
- actor naming style
- common tags
- CarMaker native TestRun comparison

Bad reference use:

- copying OpenSCENARIO 1.3 headers
- copying unsupported dynamics
- assuming no-validate conversion is enough
- treating XML text similarity as validation

## Conversion Workflow

Copy generated `.xosc` and `.xodr` into the scratch project:

```text
conversion_scratch/AGI_LLM_TestProject/Data/OpenSCENARIO/
```

Run strict validation first:

```bat
C:\IPG\carmaker\win64-15.0.1\bin\osc2cm.exe ^
  --cmprojpath E:\GitProject\AGI_VOICE\workspace\carmaker_llm_scenario_skill\conversion_scratch\AGI_LLM_TestProject ^
  --oscfname Data\OpenSCENARIO\<scenario_id>.xosc ^
  --egoname Ego ^
  --egoinf DemoCar_AEB_TEST ^
  --trfmobj ^
  --interpolate ^
  --defaultman 99999 ^
  --validate ^
  --oscversion 120 ^
  --logtoconsole ^
  --loglevel 3 ^
  --trfname LLM_<scenario_id>_validate
```

If strict validation fails, fix the IR/XML. Do not proceed as if the scenario is valid.

After strict issues are resolved, run exploratory conversion without `--validate` only to inspect generated CarMaker outputs and converter warnings:

```bat
C:\IPG\carmaker\win64-15.0.1\bin\osc2cm.exe ^
  --cmprojpath E:\GitProject\AGI_VOICE\workspace\carmaker_llm_scenario_skill\conversion_scratch\AGI_LLM_TestProject ^
  --oscfname Data\OpenSCENARIO\<scenario_id>.xosc ^
  --egoname Ego ^
  --egoinf DemoCar_AEB_TEST ^
  --trfmobj ^
  --interpolate ^
  --logtoconsole ^
  --loglevel 3 ^
  --trfname LLM_<scenario_id>
```

## Pass Criteria

A generated scenario is usable only when:

- IR validation passes.
- `.xodr` and `.xosc` are emitted.
- `osc2cm --validate --oscversion 120` passes.
- `osc2cm` creates a TestRun.
- postprocessor checks and patches known converter gaps.
- generated `.rd5` exists when a generated OpenDRIVE road is used.
- converter logs have no unsupported maneuver warnings.
- CarMaker can open the generated TestRun.
- runtime telemetry confirms ego and actor behavior.

Minimum runtime telemetry to inspect:

```text
Car.v
Vhcl.sRoad
Vhcl.tRoad
Traffic.nObjs
Traffic.T00.sRoad
Traffic.T00.tRoad
```

## Postprocessor Rules

Track discovered rules in:

```text
converter_gap_log.md
```

Initial required postprocessor checks:

- If `DrivMan.nMan` is missing or `0`, add a conservative ego maneuver from IR.
- If an IR actor has `follow_trajectory` but generated `Traffic.<i>.nMan` is `0`, synthesize native CarMaker `Traffic.<i>.Man.* FollowTraj`.
- If `Traffic.*.Man.*.(LatStep|LongStep).*Dyn = FollowTraj` and the same step has `Limit = t {}`, replace it with the final time from the matching `LatStep.*.Data` table or, in an IR-aware pass, the source trajectory's final `time_s`.
- If `Road.FName` points to a generated road, rewrite it into the selected CarMaker project subfolder and verify the `.rd5` exists.
- If `Traffic.<i>.Template.FName` points to a generated template, rewrite it into the selected CarMaker project subfolder and verify the template exists.
- Treat every unsupported converter warning as a structured failure until there is a documented patch.

Current common postprocessor command:

```bash
python3 workspace/carmaker_llm_scenario_skill/scripts/postprocess_testrun.py \
  <converted_testrun> \
  --out <postprocessed_testrun> \
  --report <postprocess_report.txt>
```

## Packaging Workflow

Use the packaging helper instead of manually copying generated files into the
original CarMaker project.

Staging package only:

```bash
python3 workspace/carmaker_llm_scenario_skill/scripts/package_for_project.py \
  --scenario <TestRunName> \
  --testrun <converted_or_postprocessed_testrun> \
  --road <generated_rd5> \
  --templates <template_1> <template_2> ... \
  --subdir LLM_Generated
```

Install into the original CarMaker project:

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

The helper:

- copies the TestRun, road, and traffic templates into a package folder
- rewrites `Road.FName` to `LLM_Generated/<road>`
- rewrites generated `Traffic.*.Template.FName` paths to `LLM_Generated/<template>`
- verifies all package files exist
- fails if `Limit = t {}` remains in the TestRun
- optionally installs into `<project>/Data/...`

## Leave-One-Out Validation

Use this for regression testing the generator:

1. Hold out one copied `.xosc` scenario.
2. Build reference context from the remaining examples.
3. Generate a new IR, `.xodr`, and `.xosc`.
4. Convert through scratch CarMaker project.
5. Compare structure against the held-out example:
   - actor count and classes
   - initial position pattern
   - trigger types
   - action types
   - route/trajectory usage
   - generated Road5/TestRun existence

Do not compare raw XML text. The goal is functionally equivalent scenario structure, not byte-level reproduction.

## First Milestone

The first implementation target should be:

```text
LLM_PedestrianCrossing_001
```

It should contain:

- simple straight OpenDRIVE road
- ego vehicle at `s=10 m`
- pedestrian near `s=60 m`
- ego speed around `50 km/h`
- pedestrian crossing triggered by ego relative distance
- strict OpenSCENARIO 1.2-compatible XML
- successful CarMaker `osc2cm` validation and conversion
