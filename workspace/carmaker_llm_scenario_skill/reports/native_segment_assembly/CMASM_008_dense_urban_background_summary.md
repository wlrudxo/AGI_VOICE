# TestRun Summary: CMASM_008_dense_urban_background

- Source: `workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_008_dense_urban_background`
- Road: `Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5`
- Ego vehicle: `Examples/DemoCar_BA`
- Ego routing: `Route 4235`
- Ego start: `Route 200.00 0`
- DrivMan.nMan: `1`
- Traffic.N declared/found: `4` / `4`

## Feature Counts

```json
{
  "traffic_start_types": {
    "Route": 4
  },
  "traffic_template_classes": {
    "vehicle": 4
  },
  "dyn_types": {
    "Driver": 2,
    "VelTransition": 1,
    "auto": 3
  }
}
```

## Traffic Actors

| Index | Name | Class | Start Type | nMan | Dyn Types | Template |
| ---: | --- | --- | --- | ---: | --- | --- |
| 0 | `crossing_beetle` | vehicle | `Route` | 1 | `VelTransition` | `1_Vehicles/VW_Beetle_2012_Blue` |
| 1 | `background_nx` | vehicle | `Route` | 1 | `auto` | `1_Vehicles/Lexus_NX300h_2015` |
| 2 | `background_truck` | vehicle | `Route` | 1 | `auto` | `1_Vehicles/Volvo_FH_2012` |
| 3 | `background_sclass` | vehicle | `Route` | 1 | `auto` | `1_Vehicles/MB_SClass_2015_Cabriolet` |
