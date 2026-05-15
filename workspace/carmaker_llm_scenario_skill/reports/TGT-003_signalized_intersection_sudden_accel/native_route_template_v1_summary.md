# TestRun Summary: TGT003_native_route_template_v1

- Source: `workspace/carmaker_llm_scenario_skill/generated/TGT-003_signalized_intersection_sudden_accel/native_route_template/TGT003_native_route_template_v1`
- Road: `Examples/Synthetic/Scenario/UrbanRoad_RuralRoad_Expressway.rd5`
- Ego vehicle: `Examples/DemoCar_BA`
- Ego routing: `Route 4235`
- Ego start: `Route 200.00 0`
- DrivMan.nMan: `1`
- Traffic.N declared/found: `48` / `48`

## Feature Counts

```json
{
  "traffic_start_types": {
    "Route": 48
  },
  "traffic_template_classes": {
    "pedestrian": 18,
    "vehicle": 30
  },
  "dyn_types": {
    "Driver": 2,
    "FollowTraj": 18,
    "RoutingChange": 7,
    "VelTransition": 21,
    "auto": 8,
    "y": 3,
    "y_abs": 1
  }
}
```

## Traffic Actors

| Index | Name | Class | Start Type | nMan | Dyn Types | Template |
| ---: | --- | --- | --- | ---: | --- | --- |
| 0 | `cross_ob` | vehicle | `Route` | 1 | `VelTransition` | `1_Vehicles/VW_Beetle_2012_Blue` |
| 1 | `Oncoming` | vehicle | `Route` | 0 | `` | `1_Vehicles/Mitsubishi_OutlanderSport_2016` |
| 2 | `SClass` | vehicle | `Route` | 1 | `auto` | `1_Vehicles/MB_SClass_2015_Cabriolet` |
| 3 | `Tesla` | vehicle | `Route` | 1 | `auto` | `1_Vehicles/Tesla_S_2016` |
| 4 | `S3` | vehicle | `Route` | 1 | `auto` | `1_Vehicles/Audi_S3_2015` |
| 5 | `GSFe` | vehicle | `Route` | 1 | `auto` | `1_Vehicles/Hyundai_GrandSantaFe_2015` |
| 6 | `L_NX` | vehicle | `Route` | 1 | `auto` | `1_Vehicles/Lexus_NX300h_2015` |
| 7 | `Truck_1` | vehicle | `Route` | 1 | `auto` | `1_Vehicles/Volvo_FH_2012` |
| 8 | `Ped_1` | pedestrian | `Route` | 1 | `FollowTraj, RoutingChange, VelTransition` | `2_People/Pedestrian_Male_Casual_01_Red` |
| 9 | `Ped_2` | pedestrian | `Route` | 1 | `VelTransition, y, y_abs` | `2_People/Pedestrian_Female_Child_01_142cm` |
| 10 | `Ped_3` | pedestrian | `Route` | 1 | `FollowTraj, RoutingChange, VelTransition` | `2_People/Pedestrian_Female_Casual_01` |
| 11 | `Ped_4` | pedestrian | `Route` | 1 | `FollowTraj, RoutingChange, VelTransition` | `2_People/Pedestrian_Male_Casual_01_IPG` |
| 12 | `Bikerm_1` | pedestrian | `Route` | 1 | `auto` | `2_People/Cyclist_Male_01` |
| 13 | `Bikerm_2` | pedestrian | `Route` | 1 | `VelTransition` | `2_People/Cyclist_Male_01` |
| 14 | `Bikerf_2` | pedestrian | `Route` | 1 | `FollowTraj, auto` | `2_People/Cyclist_Female_01` |
| 15 | `Bikerf_1` | pedestrian | `Route` | 1 | `VelTransition` | `2_People/Cyclist_Female_01` |
| 16 | `S_Bus_1` | vehicle | `Route` | 0 | `` | `1_Vehicles/MB_CitaroO345_2005` |
| 17 | `S_Car_1` | vehicle | `Route` | 0 | `` | `1_Vehicles/BMW_5_2017` |
| 18 | `S_Car_2` | vehicle | `Route` | 0 | `` | `1_Vehicles/Audi_TT_2015` |
| 19 | `S_Car_3` | vehicle | `Route` | 0 | `` | `1_Vehicles/Tesla_S_2016` |
| 20 | `S_Car_4` | vehicle | `Route` | 0 | `` | `1_Vehicles/Honda_Fit_2015` |
| 21 | `S_Car_5` | vehicle | `Route` | 0 | `` | `1_Vehicles/Citroen_C3_2015` |
| 22 | `S_Car_6` | vehicle | `Route` | 0 | `` | `1_Vehicles/Hyundai_GrandSantaFe_2015` |
| 23 | `S_Car_7` | vehicle | `Route` | 0 | `` | `1_Vehicles/KIA_Sorento_2015` |
| 24 | `S_Car_8` | vehicle | `Route` | 0 | `` | `1_Vehicles/MB_SClass_2015_Coupe` |
| 25 | `S_Car_9` | vehicle | `Route` | 0 | `` | `1_Vehicles/Suzuki_Vitara_2015` |
| 26 | `S_Car_10` | vehicle | `Route` | 0 | `` | `1_Vehicles/Lexus_NX300h_2015` |
| 27 | `S_Car_11` | vehicle | `Route` | 0 | `` | `1_Vehicles/Lexus_CT200h_2015` |
| 28 | `S_Car_12` | vehicle | `Route` | 0 | `` | `1_Vehicles/Audi_R8_2016` |
| 29 | `S_Car_13` | vehicle | `Route` | 0 | `` | `1_Vehicles/Audi_S3_2015` |
| 30 | `S_Car_14` | vehicle | `Route` | 0 | `` | `1_Vehicles/Porsche_911Turbo_2012` |
| 31 | `S_Car_15` | vehicle | `Route` | 0 | `` | `1_Vehicles/VW_Beetle_2012_DemoCar` |
| 32 | `S_Car_16` | vehicle | `Route` | 0 | `` | `1_Vehicles/Skoda_Superb_2016_Combi` |
| 33 | `S_Car_17` | vehicle | `Route` | 0 | `` | `1_Vehicles/MB_SClass_2015_Cabriolet` |
| 34 | `S_Car_18` | vehicle | `Route` | 0 | `` | `1_Vehicles/Peugeot_108_2015` |
| 35 | `S_Car_19` | vehicle | `Route` | 0 | `` | `1_Vehicles/Opel_Combo_2015` |
| 36 | `S_Car_20` | vehicle | `Route` | 0 | `` | `1_Vehicles/Skoda_Superb_2016_Combi` |
| 37 | `S_Car_21` | vehicle | `Route` | 0 | `` | `1_Vehicles/Volvo_XC90_2016` |
| 38 | `S_Ped_1` | pedestrian | `Route` | 0 | `` | `2_People/Pedestrian_Male_Casual_01` |
| 39 | `S_Ped_2` | pedestrian | `Route` | 0 | `` | `2_People/Pedestrian_Female_Casual_01` |
| 40 | `S_Ped_3` | pedestrian | `Route` | 0 | `` | `2_People/Pedestrian_Female_Child_01_115cm` |
| 41 | `S_Ped_4` | pedestrian | `Route` | 0 | `` | `2_People/Pedestrian_Female_Sportive_01` |
| 42 | `S_Ped_5` | pedestrian | `Route` | 0 | `` | `2_People/Pedestrian_Female_Child_01_142cm` |
| 43 | `S_Ped_7` | pedestrian | `Route` | 0 | `` | `2_People/Pedestrian_Male_Casual_01` |
| 44 | `S_Ped_8` | pedestrian | `Route` | 0 | `` | `2_People/Pedestrian_Female_Child_01_115cm` |
| 45 | `S_Ped_9` | pedestrian | `Route` | 0 | `` | `2_People/Pedestrian_Female_Sportive_01` |
| 46 | `S_Ped_10` | pedestrian | `Route` | 0 | `` | `2_People/Pedestrian_Male_Casual_01_Red` |
| 47 | `S_Ped_11` | pedestrian | `Route` | 0 | `` | `2_People/Pedestrian_Male_Casual_01` |
