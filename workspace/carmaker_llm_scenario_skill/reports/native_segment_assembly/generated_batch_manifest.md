# Native Segment Assembly Batch

Generated CarMaker TestRuns assembled from verified native route and actor blocks.

| Scenario | Intent | Ego | Actors | Output |
| --- | --- | --- | --- | --- |
| `CMASM_001_crossing_beetle_normal` | Baseline ego route 4235 with a blue Beetle crossing on route 4236. | route 4235, 40 km/h | cross01(src Traffic.0) | `workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_001_crossing_beetle_normal` |
| `CMASM_002_fast_crossing_vehicle` | Same route pair as baseline, but faster target speed and earlier target start. | route 4235, 50 km/h | cross02(src Traffic.0) | `workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_002_fast_crossing_vehicle` |
| `CMASM_004_crossing_with_oncoming` | Baseline crossing target with one oncoming/background vehicle to check scene readability. | route 4235, 45 km/h | cross01(src Traffic.0), oncom01(src Traffic.1) | `workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_004_crossing_with_oncoming` |
