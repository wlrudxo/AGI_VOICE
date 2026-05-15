# Native Segment Assembly Implementation Log

Date: 2026-05-12

## Objective

Implement the first native CarMaker map assembly system that can generate multiple new actor/timing/route combinations on a verified map.

User validation will be done manually in CarMaker, so this implementation stops at:

1. existing-system analysis,
2. route/actor segment selection,
3. generator implementation,
4. scenario planning,
5. generation and installation of 10 TestRuns.

## Basis

The route-template approach was selected after `LLM_Generated/TGT003_native_route_template_v1` ran successfully:

```text
SIM_END LLM_Generated/TGT003_native_route_template_v1 22.211s 194m
```

No runtime error was recorded for that smoke test.

## Implemented Files

Generator:

```text
workspace/carmaker_llm_scenario_skill/scripts/generate_native_route_scenarios.py
```

Manual:

```text
workspace/carmaker_llm_scenario_skill/native_segment_assembly_manual.md
```

Batch manifest:

```text
workspace/carmaker_llm_scenario_skill/reports/native_segment_assembly/generated_batch_manifest.md
workspace/carmaker_llm_scenario_skill/reports/native_segment_assembly/generated_batch_manifest.json
```

Generated TestRuns:

```text
workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_001_crossing_beetle_normal
workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_002_fast_crossing_vehicle
workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_003_slow_heavy_crossing
workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_004_crossing_with_oncoming
workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_005_bus_occluded_pedestrian
workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_006_multi_pedestrian_crosswalk
workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_007_cyclist_and_crossing_car
workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_008_dense_urban_background
workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_009_late_near_miss_crossing
workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_010_static_clutter_pedestrian
```

Installed TestRuns:

```text
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\CMASM_001_crossing_beetle_normal
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\CMASM_002_fast_crossing_vehicle
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\CMASM_003_slow_heavy_crossing
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\CMASM_004_crossing_with_oncoming
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\CMASM_005_bus_occluded_pedestrian
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\CMASM_006_multi_pedestrian_crosswalk
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\CMASM_007_cyclist_and_crossing_car
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\CMASM_008_dense_urban_background
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\CMASM_009_late_near_miss_crossing
E:\CarMakerProject\AGI\Data\TestRun\LLM_Generated\CMASM_010_static_clutter_pedestrian
```

## Structural Summary

The generated summaries report:

```text
CMASM_001_crossing_beetle_normal: declared=1 found=1 classes={'vehicle': 1}
CMASM_002_fast_crossing_vehicle: declared=1 found=1 classes={'vehicle': 1}
CMASM_003_slow_heavy_crossing: declared=1 found=1 classes={'vehicle': 1}
CMASM_004_crossing_with_oncoming: declared=2 found=2 classes={'vehicle': 2}
CMASM_005_bus_occluded_pedestrian: declared=2 found=2 classes={'pedestrian': 1, 'vehicle': 1}
CMASM_006_multi_pedestrian_crosswalk: declared=3 found=3 classes={'pedestrian': 3}
CMASM_007_cyclist_and_crossing_car: declared=2 found=2 classes={'pedestrian': 1, 'vehicle': 1}
CMASM_008_dense_urban_background: declared=4 found=4 classes={'vehicle': 4}
CMASM_009_late_near_miss_crossing: declared=1 found=1 classes={'vehicle': 1}
CMASM_010_static_clutter_pedestrian: declared=4 found=4 classes={'pedestrian': 1, 'vehicle': 3}
```

Additional checks:

```text
Road.FName = Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5
Vehicle.Routing.ObjId = 4235
No generated TestRun contains leftover $Speed_* or $Position_* placeholders.
Pedestrian Pos.Reference entries are updated to the generated actor names.
```

## Manual Validation Queue

Run these in CarMaker:

```text
LLM_Generated/CMASM_001_crossing_beetle_normal
LLM_Generated/CMASM_002_fast_crossing_vehicle
LLM_Generated/CMASM_003_slow_heavy_crossing
LLM_Generated/CMASM_004_crossing_with_oncoming
LLM_Generated/CMASM_005_bus_occluded_pedestrian
LLM_Generated/CMASM_006_multi_pedestrian_crosswalk
LLM_Generated/CMASM_007_cyclist_and_crossing_car
LLM_Generated/CMASM_008_dense_urban_background
LLM_Generated/CMASM_009_late_near_miss_crossing
LLM_Generated/CMASM_010_static_clutter_pedestrian
```

Record for each:

```text
starts or aborts
ego route behavior
actor visibility
actor movement direction
collision/near-miss timing
unexpected signal/route behavior
whether the scenario looks sufficiently new
```
