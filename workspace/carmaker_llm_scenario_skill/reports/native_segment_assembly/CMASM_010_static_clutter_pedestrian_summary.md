# TestRun Summary: CMASM_010_static_clutter_pedestrian

- Source: `workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_010_static_clutter_pedestrian`
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
    "pedestrian": 1,
    "vehicle": 3
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
| 0 | `static_bus` | vehicle | `Route` | 0 | `` | `1_Vehicles/MB_CitaroO345_2005` |
| 1 | `parked_green_car_a` | vehicle | `Route` | 0 | `` | `1_Vehicles/Porsche_911Turbo_2012` |
| 2 | `parked_green_car_b` | vehicle | `Route` | 0 | `` | `1_Vehicles/VW_Beetle_2012_DemoCar` |
| 3 | `moving_pedestrian` | pedestrian | `Route` | 1 | `FollowTraj, RoutingChange, VelTransition` | `2_People/Pedestrian_Male_Casual_01_Red` |
