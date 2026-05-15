# TestRun Summary: CMASM_009_late_near_miss_crossing

- Source: `workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_009_late_near_miss_crossing`
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
    "VelTransition": 1
  }
}
```

## Traffic Actors

| Index | Name | Class | Start Type | nMan | Dyn Types | Template |
| ---: | --- | --- | --- | ---: | --- | --- |
| 0 | `late_crossing_beetle` | vehicle | `Route` | 1 | `VelTransition` | `1_Vehicles/VW_Beetle_2012_Blue` |
