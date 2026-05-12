# XOSC/XODR Example DB and CarMaker Conversion Validation

Created: 2026-05-12

## Purpose

This folder is the first working dataset for an LLM-based CarMaker scenario generation skill.

The copied examples are intended to support:

- reference lookup before generating a new scenario
- leave-one-out validation against existing examples
- conversion tests from generated `.xosc` / `.xodr` into CarMaker `.rd5` and TestRun outputs
- regression tests for CarMaker `osc2cm.exe` compatibility

The original CarMaker project remains:

```text
E:\CarMakerProject\AGI
```

The scratch project used for conversion tests is:

```text
workspace/carmaker_llm_scenario_skill/conversion_scratch/AGI_LLM_TestProject
```

Do not run experimental conversion directly into the original AGI project unless the generated files have already passed the scratch conversion sequence.

## Copied Example DB

Raw copied examples:

```text
workspace/carmaker_llm_scenario_skill/examples/raw/xosc/
workspace/carmaker_llm_scenario_skill/examples/raw/xodr/
workspace/carmaker_llm_scenario_skill/examples/raw/testrun/
workspace/carmaker_llm_scenario_skill/examples/raw/traffic_template/
workspace/carmaker_llm_scenario_skill/examples/raw/road/
```

Structured index:

```text
workspace/carmaker_llm_scenario_skill/examples/index/examples.jsonl
workspace/carmaker_llm_scenario_skill/examples/index/summary.json
```

Current copied counts:

| Type | Count |
| --- | ---: |
| OpenSCENARIO `.xosc` | 7 |
| OpenDRIVE `.xodr` | 11 |
| Native CarMaker TestRun | 7 |

Current `.xosc` to road references:

| XOSC | Referenced XODR |
| --- | --- |
| `chain_collision.xosc` | `simple_road.xodr` |
| `cut_in_scenario.xosc` | `simple_road.xodr` |
| `emergency_braking.xosc` | `simple_road.xodr` |
| `lane_change_scenario.xosc` | `simple_road.xodr` |
| `multi_vehicle_highway.xosc` | `simple_road.xodr` |
| `pedestrian_crossing.xosc` | `simple_road.xodr` |
| `sudden_acceleration.xosc` | `signal_intersection.xodr` |

Useful scenario tags currently present:

```text
Vehicle, Pedestrian, TeleportAction, SpeedAction, LaneChangeAction,
FollowTrajectoryAction, AssignRouteAction, RelativeDistanceCondition,
RelativeSpeedCondition, SimulationTimeCondition, line, arc, spiral, junction
```

## Conversion Scratch Project

The scratch project was seeded with:

- `.CarMaker.tcl`
- `.IPGControl.conf`
- copied `.xosc` / `.xodr` files under `Data/OpenSCENARIO`
- empty output folders for `Data/TestRun`, `Data/Road`, and `Data/Traffic/Template`

Converter:

```text
C:\IPG\carmaker\win64-14.0.1\bin\osc2cm.exe
```

No-validate batch command pattern:

```bat
C:\IPG\carmaker\win64-14.0.1\bin\osc2cm.exe ^
  --cmprojpath E:\GitProject\AGI_VOICE\workspace\carmaker_llm_scenario_skill\conversion_scratch\AGI_LLM_TestProject ^
  --oscfname Data\OpenSCENARIO\<scenario>.xosc ^
  --egoname Ego ^
  --egoinf DemoCar_AEB_TEST ^
  --trfmobj ^
  --interpolate ^
  --logtoconsole ^
  --loglevel 3 ^
  --trfname LOO_<scenario>_no_validate
```

Strict validation command pattern adds:

```text
--validate
```

Logs:

```text
workspace/carmaker_llm_scenario_skill/conversion_scratch/logs/
```

Machine-readable result summary:

```text
workspace/carmaker_llm_scenario_skill/conversion_scratch/conversion_results.json
```

## Conversion Results

No-validate conversion produced CarMaker TestRun outputs for all 7 copied `.xosc` files.

Strict `--validate` failed for all 7 files.

| Scenario | No-validate conversion | Strict validate | Generated TestRun |
| --- | --- | --- | --- |
| `chain_collision` | pass | fail | `Data/TestRun/LOO_chain_collision_no_validate` |
| `cut_in_scenario` | pass | fail | `Data/TestRun/LOO_cut_in_scenario_no_validate` |
| `emergency_braking` | pass | fail | `Data/TestRun/LOO_emergency_braking_no_validate` |
| `lane_change_scenario` | pass | fail | `Data/TestRun/LOO_lane_change_scenario_no_validate` |
| `multi_vehicle_highway` | pass | fail | `Data/TestRun/LOO_multi_vehicle_highway_no_validate` |
| `pedestrian_crossing` | pass | fail | `Data/TestRun/LOO_pedestrian_crossing_no_validate` |
| `sudden_acceleration` | pass | fail | `Data/TestRun/LOO_sudden_acceleration_no_validate` |

Generated Road5 outputs observed:

```text
Data/Road/simple_road.rd5
Data/Road/signal_intersection.rd5
```

## What The Failures Mean

The copied `.xosc` examples are useful as semantic examples, but they are not strict CarMaker 14 validation examples yet.

Common validation failure:

```text
Unsupported OpenSCENARIO version. Validate the file with v1.2.0 OpenSCENARIO API.
Required element 'Properties' is missing
```

Local examples currently use:

```xml
<FileHeader ... revMajor="1" revMinor="3" .../>
```

CarMaker 14.0.1 installed converter assets stop at OpenSCENARIO v1.2:

```text
OpenSCENARIO_v100_osc2cm_*.xsd
OpenSCENARIO_v110_osc2cm_*.xsd
OpenSCENARIO_v120_osc2cm_*.xsd
```

So the generation backend should target OpenSCENARIO 1.2-compatible XML, not 1.3.

Entity definitions must include explicit empty properties where required:

```xml
<Vehicle ...>
  ...
  <Properties/>
</Vehicle>

<Pedestrian ...>
  ...
  <Properties/>
</Pedestrian>
```

## CarMaker Converter Subset Constraints

The no-validate conversion succeeded, but the logs show unsupported or partially ignored behavior. These warnings should be treated as generator constraints.

Avoid for traffic vehicles:

```xml
<SpeedActionDynamics dynamicsShape="linear" dynamicsDimension="rate" .../>
```

Observed warning:

```text
For traffic, DynamicsDimension does not support the rate for SpeedAction with linear.
```

Avoid for pedestrian traffic speed changes:

```xml
<SpeedActionDynamics dynamicsShape="step" .../>
```

Observed warning:

```text
For traffic, DynamicsShape does not support cubic, sinusoidal, and step for SpeedAction.
```

Avoid for traffic lane changes:

```xml
<LaneChangeActionDynamics dynamicsShape="sinusoidal" .../>
```

Observed warning:

```text
"sinusoidal" is not supported in DynamicsShape for LaneChangeAction.
```

Also note:

```text
"--interpolate" is defined without FollowTrajectoryAction. This argument is ignored.
```

This appeared even for examples expected to contain or imply trajectory behavior. The next generator test should verify whether the converter requires a stricter placement or OpenSCENARIO 1.2-compatible representation of `FollowTrajectoryAction`.

## Recommended Use As Reference DB

Use the copied examples as a retrieval/reference corpus, but do not copy their XML blindly.

Good uses:

- infer common scenario structures
- infer actor naming patterns
- inspect trigger/action combinations
- compare generated scenario tags to held-out examples
- seed prompts with small relevant examples

Bad uses:

- raw text cloning
- assuming OpenSCENARIO 1.3 validates in CarMaker 14
- assuming no-validate conversion warnings are harmless
- treating generated TestRun existence as proof of behavioral correctness

## Leave-One-Out Validation Plan

For each copied `.xosc` scenario:

1. Hold out one scenario as the target.
2. Build reference context from the other 6 `.xosc` files and the copied native TestRun examples.
3. Ask the generator to produce:
   - scenario IR
   - `.xodr`
   - `.xosc`
4. Validate the IR before writing files.
5. Run strict CarMaker validation:

```text
osc2cm.exe --validate --oscversion 120
```

6. If validation fails, repair the IR/XML and rerun.
7. Run no-validate conversion only after strict issues are understood.
8. Compare generated content against the held-out scenario by structure, not byte equality:
   - actor classes
   - initial positions
   - trigger types
   - action types
   - road reference
   - generated TestRun traffic object count
   - generated Road5 presence

Pass criteria for a generated scenario:

- strict validation passes
- conversion produces a TestRun
- generated road exists when a new OpenDRIVE map is used
- no unsupported maneuver warnings remain
- CarMaker can load the TestRun manually
- runtime telemetry shows ego and traffic actors moving as intended

## New Scenario Generation Test Plan

First generated target:

```text
LLM_PedestrianCrossing_001
```

Recommended generation sequence:

1. Prompt to strict IR.
2. Validate road/lane/actor/trigger consistency in IR.
3. Emit OpenDRIVE 1.x road.
4. Emit OpenSCENARIO 1.2-compatible `.xosc`.
5. Include `<Properties/>` under every `Vehicle` and `Pedestrian`.
6. Avoid unsupported CarMaker traffic speed/lane-change dynamics.
7. Run `osc2cm.exe --validate`.
8. Run `osc2cm.exe` no-validate only for exploratory conversion logs.
9. Inspect generated TestRun and Road5.
10. Open in CarMaker and run.

Do not route through SUMO for the first skill slice. The direct path is:

```text
natural language
  -> validated scenario IR
  -> OpenDRIVE + OpenSCENARIO
  -> CarMaker osc2cm
  -> Road5 + TestRun
  -> CarMaker manual/runtime validation
```

