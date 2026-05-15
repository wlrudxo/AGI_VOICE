# TestRun Summary: CMASM_005_bus_occluded_pedestrian

- Source: `workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_005_bus_occluded_pedestrian`
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
    "FollowTraj": 2,
    "RoutingChange": 1,
    "VelTransition": 2
  }
}
```

## Traffic Actors

| Index | Name | Class | Start Type | nMan | Dyn Types | Template |
| ---: | --- | --- | --- | ---: | --- | --- |
| 0 | `static_bus_occluder` | vehicle | `Route` | 0 | `` | `1_Vehicles/MB_CitaroO345_2005` |
| 1 | `pedestrian_from_bus` | pedestrian | `Route` | 1 | `FollowTraj, RoutingChange, VelTransition` | `2_People/Pedestrian_Male_Casual_01_Red` |
