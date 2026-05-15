# TestRun Summary: CMASM_007_cyclist_and_crossing_car

- Source: `workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_007_cyclist_and_crossing_car`
- Road: `Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5`
- Ego vehicle: `Examples/DemoCar_BA`
- Ego routing: `Route 4235`
- Ego start: `Route 200.00 0`
- DrivMan.nMan: `1`
- Traffic.N declared/found: `2` / `2`

## Feature Counts

```json
{
  "traffic_start_types": {
    "Route": 2
  },
  "traffic_template_classes": {
    "pedestrian": 1,
    "vehicle": 1
  },
  "dyn_types": {
    "Driver": 2,
    "VelTransition": 1,
    "auto": 1
  }
}
```

## Traffic Actors

| Index | Name | Class | Start Type | nMan | Dyn Types | Template |
| ---: | --- | --- | --- | ---: | --- | --- |
| 0 | `crossing_beetle` | vehicle | `Route` | 1 | `VelTransition` | `1_Vehicles/VW_Beetle_2012_Blue` |
| 1 | `cyclist_background` | pedestrian | `Route` | 1 | `auto` | `2_People/Cyclist_Male_01` |
