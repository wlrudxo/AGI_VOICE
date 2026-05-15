# TestRun Summary: CMASM_003_slow_heavy_crossing

- Source: `workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_003_slow_heavy_crossing`
- Road: `Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5`
- Ego vehicle: `Examples/DemoCar_BA`
- Ego routing: `Route 4235`
- Ego start: `Route 200.00 0`
- DrivMan.nMan: `1`
- Traffic.N declared/found: `1` / `1`

## Feature Counts

```json
{
  "traffic_start_types": {
    "Route": 1
  },
  "traffic_template_classes": {
    "vehicle": 1
  },
  "dyn_types": {
    "Driver": 2,
    "auto": 1
  }
}
```

## Traffic Actors

| Index | Name | Class | Start Type | nMan | Dyn Types | Template |
| ---: | --- | --- | --- | ---: | --- | --- |
| 0 | `slow_crossing_truck` | vehicle | `Route` | 1 | `auto` | `1_Vehicles/Volvo_FH_2012` |
