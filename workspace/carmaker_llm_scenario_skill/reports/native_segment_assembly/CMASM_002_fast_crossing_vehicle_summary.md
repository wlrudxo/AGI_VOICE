# TestRun Summary: CMASM_002_fast_crossing_vehicle

- Source: `workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_002_fast_crossing_vehicle`
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
| 0 | `fast_crossing_beetle` | vehicle | `Route` | 1 | `VelTransition` | `1_Vehicles/VW_Beetle_2012_Blue` |
