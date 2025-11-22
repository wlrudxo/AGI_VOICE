# User Accessible Quantities: Traffic

## 26.16 Traffic

### 26.16.1 General

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Traffic.Freeze` | `Traffic.Freeze` | - | Freeze the motion of all objects (boolean): 0 = no freeze; 1 = freeze |
| `Traffic.nObjs` | `Traffic.nObjs` | - | Number of currently active traffic objects (integer) / Index+1 of last active object |
| `Traffic.nObjs_max` | `Traffic.nObjs_max` | - | Maximum number of possible traffic objects (integer) |
| `Traffic.TimeOffset` | `Traffic.TimeOffset` | s | Time offset for the global traffic time |

### 26.16.2 Traffic Object

**Template Variable**: `<preQ> := Traffic.<ObjectName>`

**Pointer**: `tTrafficObj *pObj = Traffic_GetByTrfId(<Internal TrafficId>)` or `Traffic_GetByObjId(<Global ObjId>)`

**Frame**: FrTrf: Traffic object frame

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.AutoDrv.AxTgt` | `pObj->AutoDrv.AxTgt` | m/s² | Target longitudinal acceleration of the traffic autonomous driver |
| `<preQ>.AutoDrv.DesrSpd` | `pObj->AutoDrv.DesrSpd` | m/s | Desired travel speed of the traffic autonomous driver |
| `<preQ>.a_0.x/y/z` | `pObj->a_0[0/1/2]` | m/s² (Fr0) | Global acceleration of traffic object reference point (locating in the middle of the rearmost surface) |
| `<preQ>.a_1.x/y/z` | `pObj->a_1[0/1/2]` | m/s² (FrTrf) | Global acceleration of traffic object reference point (locating in the middle of the rearmost surface) |
| `<preQ>.DetectLevel` | `pObj->DetectLevel` | - | Detection level by a sensor of object for IPGMovie visualization (integer): 0 = not detected, 1 = detected but not crucial, 2 = detected and crucial, 3-7 = not set by the sensor but could be used for user specific applications with different colors |
| `<preQ>.Distance` | `pObj->Distance` | m | Driven distance |
| `<preQ>.GCS.Long/Lat/Elev` | `pObj->t_GCS.Long/Lat/Elev` | rad/rad/m | Global position (GCS) of the traffic object's frame origin: longitude, latitude, elevation. By default disabled, can be enabled in SimParameters file (see section 3.1.20 'Geographic coordinate system') |
| `<preQ>.JuncObjId` | `pObj->JuncObjId` | - | Actual (last) road junction object Id |
| `<preQ>.nextJuncObjId` | `pObj->nextJuncObjId` | - | Next road junction object Id |
| `<preQ>.Lane.Act.*` | `pObj->Lane.Act.*` | - | Lane information of the lane on which the object is currently moving (isRight / LaneId) |
| `<preQ>.LatVel` | `pObj->LatVel` | m/s (FrR) | Lateral velocity relative to route, path y axis (derivation of `tRoad`) |
| `<preQ>.LinkObjId` | `pObj->LinkObjId` | - | Actual road link object Id |
| `<preQ>.LongAcc` | `pObj->LongAcc` | m/s² | Longitudinal acceleration of CoM in course orientation |
| `<preQ>.LongVel` | `pObj->LongVel` | m/s | Longitudinal velocity of CoM in course orientation |
| `<preQ>.Long.ManIdx` | - | - | Current longitudinal maneuver Id; -11 for default maneuvers and -12 if the object is deactivated |
| `<preQ>.Lat.ManIdx` | - | - | Current lateral maneuver Id; -11 for default maneuvers and -12 if the object is deactivated |
| `<preQ>.Long.StepIdx` | - | - | Current longitudinal maneuver step Id; -11 for default maneuver steps and -12 if the object is deactivated. Special treatment: if a start condition for the traffic object is specified and not yet true (object is still deactivated), setting StepIdx to a value >= 0 bypasses the start condition and starts the maneuver control life cycle; if the target maneuver step Id is greater than the number of steps of the current active maneuver, the active maneuver is ended; if the object after all maneuvers are completed is not deactivated/hidden, the maneuver control life cycle can be restarted with a value >= 0 |
| `<preQ>.Lat.StepIdx` | - | - | Current lateral maneuver step Id; -11 for default maneuver steps and -12 if the object is deactivated. Special treatment: if a start condition for the traffic object is specified and not yet true (object is still deactivated), setting StepIdx to a value >= 0 bypasses the start condition and starts the maneuver control life cycle; if the target maneuver step Id is greater than the number of steps of the current active maneuver, the active maneuver is ended; if the object is not deactivated/hidden after all maneuvers are completed, the maneuver control life cycle can be restarted with a value >= 0 |
| `<preQ>.Long.Attrib` | - | - | Integer attribute for the current longitudinal maneuver step |
| `<preQ>.Lat.Attrib` | - | - | Integer attribute for the current lateral maneuver step |
| `<preQ>.Man.<i>.ExecCount` | - | - | Execution count of maneuver with index i (by default disabled, can be enabled in SimParameters file, see section 3.1.28) |
| `<preQ>.Man.<i>.State` | - | - | State of maneuver with index i (by default disabled, can be enabled in SimParameters file, see section 3.1.28): 0 = Initial, 1 = Standby, 2 = Running, 3 = Complete, 4 = Final |
| `<preQ>.onJunction` | `pObj->onJunction` | - | Flag if the traffic object CoM is on junction (boolean) |
| `<preQ>.Pitch_X` | - | rad | The pitch angle of the motion model 4Wheel relative to road area |
| `<preQ>.Roll_X` | - | rad | The roll angle of the motion model 4Wheel relative to road area |
| `<preQ>.rx/ry/rz` | `pObj->r_zyx[0/1/2]` | rad (Fr0) | Rotation angles of traffic object |
| `<preQ>.rxv/ryv/rzv` | `pObj->rv_zyx[0/1/2]` | rad/s (Fr0) | Rotational velocity of traffic object |
| `<preQ>.s2lastJunc` | `pObj->s2lastJunc` | m | Road distance along road reference line from CoM to last junction |
| `<preQ>.s2nextJunc` | `pObj->s2nextJunc` | m | Road distance along road reference line from CoM to next junction |
| `<preQ>.sRoad` | `pObj->sRoad` | m | Traffic object road coordinate measured from origin of route / dynamic path (e.g. lane section) to center of mass. All traffic objects on the same route/path that are located perpendicular to the reference line have the same sRoad-coordinate |
| `<preQ>.State` | `pObj->State` | - | State of traffic object (integer): 0 = motion deactivated, object hidden; 1 = motion active, object visible; 2 = fixed visible object (e.g: building); 3 = free motion by user; 4 = temporarily not visualized and detectable by sensors |
| `<preQ>.SteerAng` | - | rad | Steering angle of front tire(s) using the motion model 2Wheel or 4Wheel |
| `<preQ>.tRoad` | `pObj->tRoad` | m (FrR) | Traffic object's lateral distance of CoM to route / path |
| `<preQ>.t2Ref` | `pObj->t2Ref` | m (FrR) | Traffic object's lateral distance of CoM referred to road reference line |
| `<preQ>.tx/ty/tz` | `pObj->t_0[0/1/2]` | m (Fr0) | Global position of the traffic object reference point (locating in the middle of the rearmost surface) |
| `<preQ>.v_0.x/y/z` | `pObj->v_0[0/1/2]` | m/s (Fr0) | Global velocity of traffic object reference point (locating in the middle of the rearmost surface) |
| `<preQ>.v_1.x/y/z` | `pObj->v_1[0/1/2]` | m/s (FrTrf) | Global velocity of traffic object reference point (locating in the middle of the rearmost surface) |
| `<preQ>.Lights.bm` | - | - | For internal use only |
| `<preQ>.Lights.Brake` | - | - | Brake light on (boolean) |
| `<preQ>.Lights.FogFront` | - | - | Front fog light on (boolean) |
| `<preQ>.Lights.FogRear` | - | - | Rear fog light on (boolean) |
| `<preQ>.Lights.Hazard` | - | - | Hazard warning light on (boolean) |
| `<preQ>.Lights.HighBeam` | - | - | High beam on (boolean) |
| `<preQ>.Lights.Ignition` | - | - | Vehicle ignition, influences only lighting (boolean) |
| `<preQ>.Lights.Indicator` | - | - | Turn indicator: -1 = Right, 0 = Off, 1 = Left |
| `<preQ>.Lights.MainLight` | - | - | Main light switch: 0 = Off, 1 = Parking light, 2 = Low beam |
| `<preQ>.Lights.Reverse` | - | - | Reversing light on (boolean) |
| `<preQ>.Lights.Custom.0` | - | - | Custom light 0 on (boolean) |
| `<preQ>.Lights.Custom.1` | - | - | Custom light 1 on (boolean) |
| `<preQ>.Lights.Custom.2` | - | - | Custom light 2 on (boolean) |
| `<preQ>.Lights.Custom.3` | - | - | Custom light 3 on (boolean) |

#### Transformation Matrix

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.Tr2Fr0[a][b]` | `pObj->Tr2Fr0[a][b]` | - | Transformation matrix from FrTraffic to Fr0 where a, b = [0..2] (Fr2Fr0) |

### 26.16.3 Smart Traffic Generator

**Template Variable**: `<pre> := Traffic.SmartGen`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.TrfSwarm.Density` | `Traffic_SmartGen_TrfSwarm_SetDensity()` / `Traffic_SmartGen_TrfSwarm_GetDensity()` | - | Currently used traffic density for Traffic Swarm |
| `<pre>.Source.<i>.Active` | - | - | Flag if source is currently enabled (boolean) |
| `<pre>.Source.<i>.Density` | - | - | Currently used traffic density in source |
| `<pre>.Source.<i>.Rate` | - | Veh/h | Currently used vehicle flow rate in source |
| `<pre>.Source.<i>.Speed` | - | m/s | Currently used starting speed in source (only for rate) |
| `<pre>.Source.<i>.Lane.<j>.Density` | - | - | Currently used traffic density on lane of source |
| `<pre>.Source.<i>.Lane.<j>.Rate` | - | Veh/h | Currently used vehicle flow rate on lane of source |
| `<pre>.Source.<i>.Lane.<j>.Speed` | - | m/s | Currently used starting speed on lane of source (only for rate) |
| `<pre>.Sink.<i>.Active` | - | - | Flag if sink is currently enabled (boolean) |
| `<pre>.Sink.<i>.Rate` | - | Veh/h | Currently used removing traffic flow rate in sink |
| `<pre>.Sink.<i>.Lane.<j>.Rate` | - | Veh/h | Currently used removing traffic flow rate on lane of sink |
