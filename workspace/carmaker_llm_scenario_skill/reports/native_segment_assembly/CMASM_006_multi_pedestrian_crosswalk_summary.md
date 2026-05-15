# TestRun Summary: CMASM_006_multi_pedestrian_crosswalk

- Source: `workspace/carmaker_llm_scenario_skill/generated/native_segment_assembly/testruns/CMASM_006_multi_pedestrian_crosswalk`
- Road: `Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5`
- Ego vehicle: `Examples/DemoCar_BA`
- Ego routing: `Route 4235`
- Ego start: `Route 200.00 0`
- DrivMan.nMan: `1`
- Traffic.N declared/found: `3` / `3`

## Feature Counts

```json
{
  "traffic_start_types": {
    "Route": 3
  },
  "traffic_template_classes": {
    "pedestrian": 3
  },
  "dyn_types": {
    "Driver": 2,
    "FollowTraj": 12,
    "RoutingChange": 6,
    "VelTransition": 16,
    "y": 3,
    "y_abs": 1
  }
}
```

## Traffic Actors

| Index | Name | Class | Start Type | nMan | Dyn Types | Template |
| ---: | --- | --- | --- | ---: | --- | --- |
| 0 | `ped_route_4228` | pedestrian | `Route` | 1 | `FollowTraj, RoutingChange, VelTransition` | `2_People/Pedestrian_Male_Casual_01_Red` |
| 1 | `ped_route_4225` | pedestrian | `Route` | 1 | `VelTransition, y, y_abs` | `2_People/Pedestrian_Female_Child_01_142cm` |
| 2 | `ped_route_4229` | pedestrian | `Route` | 1 | `FollowTraj, RoutingChange, VelTransition` | `2_People/Pedestrian_Female_Casual_01` |
