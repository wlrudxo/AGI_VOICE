# User Accessible Quantities: Sensors (Part 1)

## 26.14 Sensors

### 26.14.1 Inertial Sensor

The quantities in the column "Simulink" refer to those with respect to the "Car InertialSensorTrafficObject" block in the CarMaker for Simulink library.

#### Template Variables
- `<Nb>` := 0, .., n (number)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.Inertial.<inst>.<name>`

#### Inertial Sensor Data

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| Signal Mask | `InertialSensor[Nb].SignalMask` | - | Signal frame selection (unsigned long) |
| `Pos_B x/y/z` | `InertialSensor[Nb].Pos_B[0/1/2]` | m | Position of inertial sensor with name `<nm>` in the mounted body coordinate system as defined in CarMaker Vehicle GUI |
| `OBO_0 x/y/z` | `InertialSensor[Nb].OBO_0[0/1/2]` | m | Sensor position relative to the global coordinate system |
| `OBO_B x/y/z` | `InertialSensor[Nb].OBO_B[0/1/2]` | m | Sensor position relative to mounted body coordinate system as defined in CarMaker Vehicle GUI |
| `<preQ>.Acc_0 x/y/z` | `InertialSensor[Nb].Acc_0[0/1/2]` | m/s² | Translational acceleration of inertial sensor with name `<nm>` in global frame |
| `<preQ>.Acc_B x/y/z` | `InertialSensor[Nb].Acc_B[0/1/2]` | Fr1 or Fr2 m/s² | Translational acceleration of inertial sensor with name `<nm>` in body frame (Fr1; Fr2) |
| `<preQ>.Alpha_0 x/y/z` | `InertialSensor[Nb].Alpha_0[0/1/2]` | rad/s² | Rotational acceleration of inertial sensor with name `<nm>` in global frame |
| `<preQ>.Alpha_B x/y/z` | `InertialSensor[Nb].Alpha_B[0/1/2]` | Fr1 or Fr2 rad/s² | Rotational acceleration of inertial sensor with name `<nm>` in body frame (Fr1; Fr2) |
| `<preQ>.Omega_0 x/y/z` | `InertialSensor[Nb].Omega_0[0/1/2]` | rad/s | Rotational velocity of inertial sensor with name `<nm>` in global frame |
| `<preQ>.Omega_B x/y/z` | `InertialSensor[Nb].Omega_B[0/1/2]` | Fr1 or Fr2 rad/s | Rotational velocity of inertial sensor with name `<nm>` in body frame (Fr1; Fr2) |
| `<preQ>.Pos_0 x/y/z` | `InertialSensor[Nb].Pos_0[0/1/2]` | m | Position of inertial sensor with name `<nm>` in global frame |
| `<preQ>.Vel_0 x/y/z` | `InertialSensor[Nb].Vel_0[0/1/2]` | m/s | Translational velocity of inertial sensor with name `<nm>` in global frame |
| `<preQ>.Vel_B x/y/z` | `InertialSensor[Nb].Vel_B[0/1/2]` | Fr1 or Fr2 m/s | Translational velocity of inertial sensor with name `<nm>` in body frame (Fr1; Fr2) |

### 26.14.2 Slip Angle Sensor

#### Template Variables
- `<Nb>` := 0, .., n (number)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.SAngle.<inst>.<name>`

#### Slip Angle Sensor Data

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.Ang` | `SAngleSensor[Nb].Angle` | rad | Sideslip angle sensor measurement |

### 26.14.3 Object Sensor

#### General

The quantities in the column "Simulink" refer to those with respect to the "Car ObjectSensor" block in the CarMaker Simulink library.

##### Template Variables
- `<Nb>` := 0, .., n (number)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.Object.<inst>.<name>`

##### Pointer Information
- `tObjectSensor *pOS` = `&ObjectSensor[<SensorId>]` or `ObjectSensor_GetByIndex(<SensorId>)` or `ObjectSensor_GetByIndex(ObjectSensor_FindIndexForName(<name>))`

##### General Object Sensor Data

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.DrvLaneCurv` | `pOS->DrvLaneCurv` | 1/m | Predicted driving lane curvature of sensor with the name `<nm>` |
| `<preQ>.rx_ext/ry_ext/rz_ext` | `pOS->rot_zyx_ext[0/1/2]` | rad | External sensor rotation with ZYX-orientation order |
| `<preQ>.TimeStamp` | `pOS->TimeStamp` | s | Time-stamp of updated sensor signals |
| `<preQ>.tx_ext/ty_ext/tz_ext` | `pOS->t_ext[0/1/2]` | m | External sensor travel, expressed in mounted frame |
| `Sensor.Object.nSensors` | `ObjectSensorCount` | - | Number of Sensors defined (integer) |

#### Relevant Target Data

##### Template Variables
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.Object.<inst>.<name>.relvTgt`
- `<preC>` := `pOS->relvTarget`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.dtct` | `pOS->Targ_Dtct` | - | Flag: a relevant target is detected (boolean) |
| `<preQ>.ObjId` | `pOS->relvTargetObjId` | - | Global object Id of the relevant target: value (integer) = -1 stands for no detection (please refer to section 5.4 'Object ID' for more information) |
| `<preQ>.ImgArea_LeftP/NearP/RightP` | `<preC>.ImgArea_LeftP/NearP/RightP` | - | Projection of the target points on the sensor image area |
| `<preQ>.IncAngle_alpha/beta` | `<preC>.incangle[0/1]` | rad | Angle of incidence in the nearest point |
| `<preQ>.RefPnt.alpha/NearPnt.alpha` | `<preC>.RefPnt.alpha_p/<preC>.NearPnt.alpha_p` | rad | Bearing azimuth of the relevant target (nearest point and reference point) |
| `<preQ>.RefPnt.ds_p/NearPnt.ds_p` | `<preC>.RefPnt.ds_p/<preC>.NearPnt.ds_p` | m | Distance to the relevant target (nearest point and reference point) |
| `<preQ>.RefPnt.ds x/y/z / NearPnt.ds x/y/z` | `<preC>.RefPnt.ds[0/1/2] / <preC>.NearPnt.ds[0/1/2]` | m | Distance to the relevant target in x,y,z-direction in sensor frame (nearest point and reference point) |
| `<preQ>.RefPnt.dv_p/NearPnt.dv_p` | `<preC>.RefPnt.dv_p/<preC>.NearPnt.dv_p` | m/s | Relative radial speed of the relevant target (nearest point and reference point) |
| `<preQ>.RefPnt.dv x/y/z / NearPnt.dv x/y/z` | `<preC>.RefPnt.dv[0/1/2] / <preC>.NearPnt.dv[0/1/2]` | m/s | Speed of the relevant target in x,y,z-direction in sensor frame (nearest point and reference point) |
| `<preQ>.RefPnt.r_zyx x/y/z` | `<preC>.RefPnt.r_zyx[0/1/2]` | rad | Orientation of relevant target in the reference point referring to the sensor frame with rotation order z-y-x |
| `<preQ>.RefPnt.theta/NearPnt.theta` | `<preC>.RefPnt.theta_p/<preC>.NearPnt.theta_p` | rad | Bearing elevation of the relevant target (nearest point and reference point) |

#### Object List

##### Template Variables
- `<Nb>` := 0, .., n (number)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.Object.<inst>.<name>.Obj.<name_object>`

##### Pointer Information
- `tObjectSensorObj *pOSO` = `ObjectSensor_GetObject(<Sensor Id>, <Internal TrafficId>)` or `ObjectSensor_GetObjectByObjId(<Sensor Id>, <Global ObjId>)` or `ObjectSensor_GetObjectForName(<Sensor Name>, <Traffic Object Name>)`

##### Object List Data

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| Traffic Object Id | `pOSO->*` | - | Traffic (internal) object's identification number (integer) |
| Global Object Id | `pOSO->ObjId` | - | Global object's identification number (integer) (please refer to section 5.4 'Object ID' for more information) |
| Height/Length/Width | `pOSO->h/l/w` | m | Traffic object's height, length, width |
| `zOff` | `pOSO->zOff` | m | Distance between the traffic object's bottom and the road |
| `<preQ>.dtct` | `pOSO->dtct` | - | Flag: Traffic object is detected by sensor `<nm>` (boolean) |
| `<preQ>.ImgArea_LeftP/NearP/RightP` | `pOSO->ImgArea_LeftP/NearP/RightP` | - | Projection of the object points on the sensor image area |
| `<preQ>.IncAngle_alpha/beta` | `pOSO->incangle[0/1]` | rad | Angle of incidence in the nearest point of the traffic object |
| `<preQ>.InLane` | `pOSO->InLane` | - | Flag: traffic object is within the vehicle driving lane (only for 'Nearest object in Path' detection) (boolean) |
| `<preQ>.obsv` | `pOSO->obsv` | - | Flag: traffic object is inside the observation area of sensor `<nm>` (all sensor quantities are calculated) (boolean) |
| `<preQ>.RefPnt.alpha/NearPnt.alpha` | `pOSO->RefPnt.alpha_p/NearPnt.alpha_p` | rad | Bearing azimuth of the traffic object (nearest point and reference point) |
| `<preQ>.RefPnt.ds_p/NearPnt.ds_p` | `pOSO->RefPnt.ds_p/NearPnt.ds_p` | m | Distance from sensor to traffic object (nearest point and reference point) |
| `<preQ>.RefPnt.ds x/y/z / NearPnt.ds x/y/z` | `pOSO->RefPnt.ds[0/1/2] / NearPnt.ds[0/1/2]` | m | Distance from sensor to traffic object in x,y,z-direction in sensor frame (nearest point and reference point) |
| `<preQ>.RefPnt.dv_p/NearPnt.dv_p` | `pOSO->RefPnt.dv_p/NearPnt.dv_p` | m/s | Relative radial speed (distance change rate) (nearest point and reference point) |
| `<preQ>.RefPnt.dv x/y/z / NearPnt.dv x/y/z` | `pOSO->RefPnt.dv[0/1/2] / NearPnt.dv[0/1/2]` | m/s | Speed of the traffic object in x,y,z-direction in sensor frame (nearest point and reference point) |
| `<preQ>.RefPnt.r_zyx x/y/z` | `pOSO->RefPnt.r_zyx[0/1/2]` | rad | Orientation of traffic object `<nm_O>` in the reference point referring to the sensor frame with rotation order z-y-x |
| `<preQ>.RefPnt.theta/NearPnt.theta` | `pOSO->RefPnt.theta_p/NearPnt.theta_p` | rad | Bearing elevation of the traffic object (nearest point and reference point) |

### 26.14.4 Ground Truth Sensor

#### General

##### Template Variables
- `<NoS>` := 0..n (sensors)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.GroundTruth.<inst>.<name>`
- `<preC>` := `GroundTruthSensor[NoS]`

##### General Data

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| Active | `<preC>.*` | - | 0 or 1 to deactivate or activate calculation for this sensor instance (integer) |
| `<preQ>.nGTObjects` | `<preC>.nGTObjects` | - | Number of detected gtObjects. This number may include objects that are not listed in any of the type lists. |
| `<preQ>.nLines` | `<preC>.nLines` | - | Number of detected lines (integer) |
| `<preQ>.nLanes` | `<preC>.nLanes` | - | Number of detected lanes (integer) |
| `<preQ>.nRoots` | `<preC>.nRoots` | - | Number of detected roots (integer) |
| `<preQ>.nTrafficSigns` | `<preC>.nTrafficSigns` | - | Number of detected traffic signs (integer) |
| `<preQ>.nTrafficLights` | `<preC>.nTrafficLights` | - | Number of detected traffic lights (integer) |
| `<preQ>.nMounts` | `<preC>.nMounts` | - | Number of detected mounts (integer) |
| `<preQ>.nTrafficObjects` | `<preC>.nTrafficObjects` | - | Number of detected traffic objects (integer) |
| `<preQ>.nSceneObjects` | `<preC>.nSceneObjects` | - | Number of detected scene objects (integer) |
| `<preQ>.TimeStamp` | `<preC>.TimeStamp` | s | Time stamp of updated sensor signals |
| Sensor Position | `<preC>.sensorPos0[0/1/2]` | m | Sensor position in Fr0 with external motion |
| Sensor Range | `<preC>.cfg.range[0/1]` | m | Minimum and maximum range of the sensor |
| Sensor FoV | `<preC>.cfg.FoV[0/1]` | rad | Horizontal and Vertical sensor field of view |
| Sensor Cycle Time | `<preC>.cfg.cycleTime` | ms | Sensor cycle duration |
| Sensor Cycle Offset | `<preC>.cfg.cycleOffset` | ms | Time until start of first sensor cycle |
| `<preQ>.tx_ext/ty_ext/tz_ext` | `<preC>.t_ext[0/1/2]` | m | External sensor travel, expressed in mounted frame |
| `<preQ>.rx_ext/ry_ext/rz_ext` | `<preC>.rot_zyx_ext[0/1/2]` | rad | External sensor rotation with ZYX-orientation order |

#### Object Enumeration

##### Template Variables
- `<NoS>` := 0..n (sensors)
- `<NoO>` := 0..m (objects)
- `<preC>` := `GroundTruthSensor[NoS].GTObj[NoO]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preC>.ObjID` | - | - | Global ID to identify object (integer) |
| `<preC>.UserID` | - | - | User-defined ID to identify object (integer) |
| `<preC>.GTObjType` | - | - | Object type (integer): 0=GTOT_Line, 1=GTOT_Lane, 2=GTOT_Root, 3=GTOT_TrafficSign, 4=GTOT_TrafficLight, 5=GTOT_Mount, 6=GTOT_Traffic, 7=GTOT_Scene |
| `<preC>.hasData` | - | - | Indicates if more detailed data to this object is available (integer) |

#### Line Data

##### Template Variables
- `<NoS>` := 0..n (sensors)
- `<NoO>` := 0..n (lines)
- `<NoLP>` := 0..m (line points)
- `<NoDSP>` := 0..m (dash start points)
- `<NoDEP>` := 0..m (dash end points)
- `<NoPL>` := 0..m (previous lines)
- `<NoNL>` := 0..m (next lines)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.GroundTruth.<inst>.<name>.Line.<NoO>`
- `<preC>` := `GroundTruthSensor[NoS].lines[NoO]`
- `<preCC>` := `GroundTruthSensor[NoS].lines[NoO].polynomialList`

##### Line Data Attributes

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.ObjID` | `<preC>.ObjID` | - | Global ID to identify object (integer) |
| `<preQ>.UserID` | `<preC>.UserID` | - | User-defined ID to identify object (integer) |
| `<preQ>.SubsectionID` | `<preC>.SubsectionID` | - | Id to handle multiple separate sections of one line inside FOV (integer) |
| `<preQ>.Type` | `<preC>.lineType` | - | Line type (integer): 0=GTLT_Centerline, 1=GTLT_LaneBoundary, 2=GTLT_RoadBoundary, 3=GTLT_Path, 4=GTLT_RMSolid, 5=GTLT_RMBroken, 6=GTLT_RMDotted, 7=GTLT_RMDoubleSolid, 8=GTLT_RMDoubleBroken, 9=GTLT_RMDoubleDotted, 10=GTLT_RMDoubleBrokenL, 11=GTLT_RMDoubleBrokenR, 12=GTLT_RMDoubleDottedL, 13=GTLT_RMDoubleDottedR, 14=GTLT_GuardRail1, 15=GTLT_GuardRail2, 16=GTLT_GuardRail3, 17=GTLT_JerseyBarrier, 18=GTLT_Wall |
| `<preQ>.Width` | `<preC>.width` | m | Line width |
| `<preQ>.Height` | `<preC>.height` | m | Line height |
| `<preQ>.Length` | `<preC>.length` | m | Length of line section inside field of view |
| `<preQ>.Color_R/G/B` | `<preC>.colorRGB[0/1/2]` | - | RGB triplet for line color, digital 8-bit per channel [0..255] |
| Dash Length | `<preC>.dashLength` | m | Length of dashes in broken line |
| Interval Length | `<preC>.intervalLength` | m | Length of intervals between dashes in broken line |
| Number of Points | `<preC>.nPoints` | - | Number of 3-dimensional arrays in points (integer) |
| Line Points | `<preC>.points[<NoLP>][0/1/2]` | m | x/y/z coordinates of line points (only valid for pointlist output) |
| Line Curvature | `<preC>.curvature[<NoLP>]` | 1/m | Curvature of line points (only valid for pointlist output) |
| Line Gradient | `<preC>.gradient[<NoLP>]` | 1/m | Gradient of line points (only valid for pointlist output) |
| Number of Dash Start Points | `<preC>.nDashStartPoints` | - | Number of 3-dimensional arrays in dashStartPosition (integer) |
| Dash Start Position | `<preC>.dashStartPosition[<NoDSP>][0/1/2]` | m | x/y/z coordinates of dash start points in broken lines |
| Number of Dash End Points | `<preC>.nDashEndPoints` | - | Number of 3-dimensional arrays in dashEndPosition (integer) |
| Dash End Position | `<preC>.dashEndPosition[<NoDEP>][0/1/2]` | m | x/y/z coordinates of dash end points in broken lines |
| Previous Elements | `<preC>.nPrev` | - | Number of elements in prev (integer) |
| Previous List | `<preC>.prev[<NoPL>]` | - | List of pointers to previous elements inside field of view (*tGTObject) |
| Next Elements | `<preC>.nNext` | - | Number of elements in next (integer) |
| Next List | `<preC>.next[<NoNL>]` | - | List of pointers to next elements inside field of view (*tGTObject) |
| Polynomial List | `<preC>.polynomialList` | - | First element of a linked polynomialList list (*tGTParametricCubicPolynomial) |
| Polynomial ObjID | `<preCC>.ObjID` | - | Object Id of road marking, path, etc. suitable to object id in the Scenario Editor (integer) |
| Detection Probability | `<preC>.detectionProbability` | - | Detection probability of the object |
| Polynomial Previous | `<preCC>.prev` | - | Pointer to the previous polynomial (*tGTParametricCubicPolynomial) |
| Polynomial Next | `<preCC>.next` | - | Pointer to next polynomial (*tGTParametricCubicPolynomial) |
| X Polynomial Coefficients | `<preCC>.cx[0/1/2/3]` | - | dx/cx/bx/ax coefficients of polynomial for x coordinate |
| Y Polynomial Coefficients | `<preCC>.cy[0/1/2/3]` | - | dy/cy/by/ay coefficients of polynomial for y coordinate |
| Z Polynomial Coefficients | `<preCC>.cz[0/1/2/3]` | - | dz/cz/bz/az coefficients of polynomial for z coordinate |
| Polynomial S Coordinate | `<preCC>.s` | - | s coordinate at start of polynomial |
| Polynomial S on Curve | `<preCC>.sCurve` | - | s coordinate at start of polynomial on complete curve |
| Polynomial Interval | `<preCC>.interval` | - | Range of s coordinate of polynomial |

#### Lane Data

##### Template Variables
- `<NoS>` := 0..n (sensors)
- `<NoO>` := 0..n (lanes)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.GroundTruth.<inst>.<name>.Lane.<NoO>`
- `<preC>` := `GroundTruthSensor[NoS].lanes[NoO]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.ObjID` | `<preC>.ObjID` | - | Global ID to identify object (integer) |
| `<preQ>.UserID` | `<preC>.UserID` | - | User-defined ID to identify object (integer) |
| `<preQ>.Type` | `<preC>.type` | - | Lane type (integer): 0=GTLaneType_Driving, 1=GTLaneType_Border, 2=GTLaneType_RoadSide, 3=GTLaneType_Biking, 4=GTLaneType_Pedestrian, 5=GTLaneType_TrafficIsland, 6=GTLaneType_Parking, 7=GTLaneType_Bus, 8=GTLaneType_HOV, 9=GTLaneType_Emergency, 10=GTLaneType_OnRamp, 11=GTLaneType_OffRamp, 12=GTLaneType_Vegetation |
| Path Pointer | `<preC>.path` | - | Pointer to the path (*tGTObject) |
| Inner Lane Boundary | `<preC>.innerLaneBoundary` | - | Pointer to the inner lane boundary (*tGTObject) |
| Outer Lane Boundary | `<preC>.outerLaneBoundary` | - | Pointer to the outer lane boundary (*tGTObject) |
| Previous Elements | `<preC>.nPrev` | - | Number of elements in prev (integer) |
| Previous Lanes | `<preC>.prev` | - | List of pointers to the previous lanes (*tGTObject) |
| Next Elements | `<preC>.nNext` | - | Number of elements in next (integer) |
| Next Lanes | `<preC>.next` | - | List of pointers to the next lanes (*tGTObject) |
| Right Adjacent Lane | `<preC>.rightAdjacentLane` | - | Pointer to the right adjacent lane with respect to path direction defined in road (*tGTObject) |
| Left Adjacent Lane | `<preC>.leftAdjacentLane` | - | Pointer to the left adjacent lane with respect to path direction defined in road (*tGTObject) |
| Current Lane Flag | `<preC>.isCurrentLane` | - | Flag indicating if the sensor is currently on this lane (integer) |
| Current Lane Direction | `<preC>.currentLaneData.isRight` | - | Flag indicating the lane direction with respect to current viewing direction (integer). Only valid if isCurrentLane = 1 |
| Left Lanes Count | `<preC>.currentLaneData.nLanesLeft` | - | Number of left lanes in viewing direction (integer). Only valid if isCurrentLane = 1 |
| Right Lanes Count | `<preC>.currentLaneData.nLanesRight` | - | Number of right lanes in viewing direction (integer). Only valid if isCurrentLane = 1 |
| Current Lane Index | `<preC>.currentLaneData.currentLaneIndex` | - | Index indicating the position of the current lane in nLanesLeft/nLanesRight from inside to outside (integer). Only valid if isCurrentLane = 1 |

#### Root Data

##### Template Variables
- `<NoS>` := 0..n (sensors)
- `<NoO>` := 0..n (roots)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.GroundTruth.<inst>.<name>.Root.<NoO>`
- `<preC>` := `GroundTruthSensor[NoS].roots[NoO]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.ObjID` | `<preC>.ObjID` | - | Global ID to identify object (integer) |
| `<preQ>.UserID` | `<preC>.UserID` | - | User-defined ID to identify object (integer) |
| `<preQ>.Type` | `<preC>.type` | - | Lane type (integer): 0=GTRootType_Junction, 1=GTRootType_Link |
| Road Type | `<preC>.roadType` | - | Road type (integer): 0=GTRoadType_Urban, 1=GTRoadType_Countryroad, 2=GTRoadType_Motorway, 3=GTRoadType_Roundabout, 4=GTRoadType_Ramp, 5=GTRoadType_Dirttrack, 6=GTRoadType_User, 7=GTRoadType_Undefined |
| Centerlines Count | `<preC>.nCenterlines` | - | Number of elements in centerline (integer) |
| Centerlines | `<preC>.centerline` | - | List of pointers to centerlines (*tGTObject) |
| Road Boundaries Count | `<preC>.nRoadBoundaries` | - | Number of elements in roadBoundaries (integer) |
| Road Boundaries | `<preC>.roadBoundaries` | - | List of pointers to road boundaries of this root (*tGTObject) |
| Connected Roots Count | `<preC>.nConnectedRoots` | - | Number of elements in connectedRoots (integer) |
| Connected Roots | `<preC>.connectedRoots` | - | List of pointers to centerlines of this root (*tGTObject) |

#### Traffic Sign Data

##### Template Variables
- `<NoS>` := 0..n (sensors)
- `<NoO>` := 0..n (traffic signs)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.GroundTruth.<inst>.<name>.TrafficSign.<NoO>`
- `<preC>` := `GroundTruthSensor[NoS].trafficSigns[NoO]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.ObjID` | `<preC>.ObjID` | - | Global ID to identify object (integer) |
| `<preQ>.UserID` | `<preC>.UserID` | - | User-defined ID to identify object (integer) |
| `<preQ>.Length` | `<preC>.dimensions.length` | m | Length of the object's bounding box along x-axis |
| `<preQ>.Width` | `<preC>.dimensions.width` | m | Width of the object's bounding box along y-axis |
| `<preQ>.Height` | `<preC>.dimensions.height` | m | Height of the object's bounding box along z-axis |
| `<preQ>.SignID` | `<preC>.main.signId` | - | Identifier for the type of the Traffic sign (integer) |
| `<preQ>.Val0/Val1` | `<preC>.main.val[0/1]` | - | Values 0 / 1 displayed on the Traffic sign (integer) |
| `<preQ>.IsInFoV` | `<preC>.isInFoV` | - | Flag indicating if the object is inside the sensors FoV (integer) |
| `<preQ>.PercentageVisible` | `<preC>.percentageVisible` | % | Percentage of the object's visible area when occlusion is enabled |
| `<preQ>.IsVisible` | `<preC>.isVisible` | - | Flag indicating if the object is visible for the sensor. 1 if PercentageVisible is > 0 (integer) |
| Reference Point | `<preC>.referencePoint` | - | Center point of the object's bounding box (observed point) |
| Nearest Point | `<preC>.nearestPoint` | - | Nearest point of the object's bounding box (observed point) |
| Position in Link Frame | `<preC>.pos_st[0/1]` | m | s/t position in link frame, not valid on junctions |
| Detection Probability | `<preC>.detectionProbability` | - | Detection probability of the object |
| Facing Flag | `<preC>.facing` | - | Flag indicating if the sign is facing towards the sensor (integer) |
| Main Sign Structure | `<preC>.main` | - | Main sign structure (tRoadSign). See Road API for more information |
| Supplementary Sign 1 | `<preC>.suppl` | - | First supplementary sign structure (tRoadSign). See Road API for more information |
| Supplementary Sign 2 | `<preC>.supp` | - | Second supplementary sign structure (tRoadSign). See Road API for more information |
| Painted on Road Flag | `<preC>.isPaintedOnRoad` | - | Flag indicating if the traffic sign is painted on the road (integer) |
| Mount Pointer | `<preC>.mount` | - | Pointer to the mount the traffic sign is mounted on (*tGTObject). Not valid if isPaintedOnRoad = 1 or "Mount" type is not active |
| Lane Pointer | `<preC>.lane` | - | Pointer to the lane the traffic sign is mounted above (*tGTObject). Not valid if "Lane" type is not active |
| Root Pointer | `<preC>.root` | - | Pointer to the root the traffic sign is mounted above (*tGTObject). Not valid if "Root" type is not active |

#### Traffic Light Data

##### Template Variables
- `<NoS>` := 0..n (sensors)
- `<NoO>` := 0..n (traffic lights)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.GroundTruth.<inst>.<name>.TrafficLight.<NoO>`
- `<preC>` := `GroundTruthSensor[NoS].trafficLights[NoO]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.ObjID` | `<preC>.ObjID` | - | Global ID to identify object (integer) |
| `<preQ>.UserID` | `<preC>.UserID` | - | User-defined ID to identify object (integer) |
| `<preQ>.Length` | `<preC>.dimensions.length` | m | Length of the object's bounding box along x-axis |
| `<preQ>.Width` | `<preC>.dimensions.width` | m | Width of the object's bounding box along y-axis |
| `<preQ>.Height` | `<preC>.dimensions.height` | m | Height of the object's bounding box along z-axis |
| `<preQ>.Type` | `<preC>.type` | - | Traffic light type (integer): 0=GTTrafficLightType_RYG, 1=GTTrafficLightType_RYG_straight, 2=GTTrafficLightType_RYG_left, 3=GTTrafficLightType_RYG_right, 4=GTTrafficLightType_RYG_straightLeft, 5=GTTrafficLightType_RYG_straightRight, 6=GTTrafficLightType_RYG_small, 7=GTTrafficLightType_RY, 8=GTTrafficLightType_YG, 9=GTTrafficLightType_YG_left, 10=GTTrafficLightType_YG_right, 11=GTTrafficLightType_YG_left_large, 12=GTTrafficLightType_YG_right_large, 13=GTTrafficLightType_R_large, 14=GTTrafficLightType_ped_R, 15=GTTrafficLightType_ped_RG |
| `<preQ>.State` | `<preC>.state` | - | Traffic light state (integer): 0=GTTrafficLightState_Off, 1=GTTrafficLightState_Green, 2=GTTrafficLightState_Yellow, 3=GTTrafficLightState_Red, 4=GTTrafficLightState_RedYellow |
| `<preQ>.IsInFoV` | `<preC>.isInFoV` | - | Flag indicating if the object is inside the sensors FoV (integer) |
| `<preQ>.PercentageVisible` | `<preC>.percentageVisible` | % | Percentage of the object's visible area when occlusion is enabled |
| `<preQ>.IsVisible` | `<preC>.isVisible` | - | Flag indicating if the object is visible for the sensor. 1 if PercentageVisible is > 0 (integer) |
| Reference Point | `<preC>.referencePoint` | - | Center point of the object's bounding box (observed point) |
| Nearest Point | `<preC>.nearestPoint` | - | Nearest point of the object's bounding box (observed point) |
| Position in Link Frame | `<preC>.pos_st[0/1]` | m | s/t position in link frame, not valid on junctions |
| Detectability | `<preC>.detectability` | - | Detectability as set in the Scenario Editor (double) |
| Facing Flag | `<preC>.facing` | - | Flag indicating if the light is facing towards the sensor (integer) |
| Mount Pointer | `<preC>.mount` | - | Pointer to the mount the traffic light is mounted on (*tGTObject). Not valid if isPaintedOnRoad = 1 or "Mount" type is not active |
| Lane Pointer | `<preC>.lane` | - | Pointer to the lane the traffic light is mounted above (*tGTObject). Not valid if "Lane" type is not active |
| Root Pointer | `<preC>.root` | - | Pointer to the root the traffic light is mounted above (*tGTObject). Not valid if "Root" type is not active |

#### Mount Data

##### Template Variables
- `<NoS>` := 0..n (sensors)
- `<NoO>` := 0..n (mounts)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.GroundTruth.<inst>.<name>.Mount.<NoO>`
- `<preC>` := `GroundTruthSensor[NoS].mounts[NoO]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.ObjID` | `<preC>.ObjID` | - | Global ID to identify object (integer) |
| `<preQ>.UserID` | `<preC>.UserID` | - | User-defined ID to identify object (integer) |
| `<preQ>.Length` | `<preC>.dimensions.length` | m | Length of the object's bounding box along x-axis |
| `<preQ>.Width` | `<preC>.dimensions.width` | m | Width of the object's bounding box along y-axis |
| `<preQ>.Height` | `<preC>.dimensions.height` | m | Height of the object's bounding box along z-axis |
| `<preQ>.Type` | `<preC>.type` | - | Mount type (integer): 0=GTMountType_Pole, 3=GTMountType_PoleTrafficLight |
| `<preQ>.IsInFoV` | `<preC>.isInFoV` | - | Flag indicating if the object is inside the sensors FoV (integer) |
| `<preQ>.PercentageVisible` | `<preC>.percentageVisible` | % | Percentage of the object's visible area when occlusion is enabled |
| `<preQ>.IsVisible` | `<preC>.isVisible` | - | Flag indicating if the object is visible for the sensor. 1 if PercentageVisible is > 0 (integer) |
| Reference Point | `<preC>.referencePoint` | - | Center point of the object's bounding box (observed point) |
| Nearest Point | `<preC>.nearestPoint` | - | Nearest point of the object's bounding box (observed point) |
| Position in Link Frame | `<preC>.pos_st[0/1]` | m | s/t position in link frame, not valid on junctions |
| Lane Pointer | `<preC>.lane` | - | Pointer to the lane the mount is placed on (*tGTObject). Not valid if "Lane" type is not active |
| Root Pointer | `<preC>.root` | - | Pointer to the root the mount is placed on (*tGTObject). Not valid if "Root" type is not active |

#### Traffic Object Data

##### Template Variables
- `<NoS>` := 0..n (sensors)
- `<NoO>` := 0..n (traffic objects)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.GroundTruth.<inst>.<name>.TrafficObject.<NoO>`
- `<preC>` := `GroundTruthSensor[NoS].trafficObjects[NoO]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.ObjID` | `<preC>.ObjID` | - | Global ID to identify object (integer) |
| `<preQ>.UserID` | `<preC>.UserID` | - | User-defined ID to identify object (integer) |
| `<preQ>.Length` | `<preC>.dimensions.length` | m | Length of the object's bounding box along x-axis |
| `<preQ>.Width` | `<preC>.dimensions.width` | m | Width of the object's bounding box along y-axis |
| `<preQ>.Height` | `<preC>.dimensions.height` | m | Height of the object's bounding box along z-axis |
| `<preQ>.IsInFoV` | `<preC>.isInFoV` | - | Flag indicating if the object is inside the sensors FoV (integer) |
| `<preQ>.IsInTrajectory` | `<preC>.isInTrajectory` | - | Flag indicating if the object is in the current projected path of the sensor (integer) |
| `<preQ>.PercentageVisible` | `<preC>.percentageVisible` | % | Percentage of the object's visible area when occlusion is enabled |
| `<preQ>.IsVisible` | `<preC>.isVisible` | - | Flag indicating if the object is visible for the sensor. 1 if PercentageVisible is > 0 (integer) |
| Reference Point | `<preC>.referencePoint` | - | Reference point of the traffic object (observed point) |
| Nearest Point | `<preC>.nearestPoint` | - | Nearest point of the object's bounding box (observed point) |
| Position in Link Frame | `<preC>.pos_st[0/1]` | m | s/t position in link frame, not valid on junctions |
| Detect Mask | `<preC>.detectMask` | - | Flag if this object can be seen by sensors or other traffic: 1st bit -> detectable by sensors, 2nd bit -> detectable by other traffic |
| Lane Pointer | `<preC>.lane` | - | Pointer to the lane the traffic object is driving on (*tGTObject). Not valid if "Lane" type is not active |
| Root Pointer | `<preC>.root` | - | Pointer to the root the traffic object is driving on (*tGTObject). Not valid if "Root" type is not active |

#### Special Traffic Objects (Mounted Object & Relevant Target)

##### Template Variables
- `<NoS>` := 0..n (ground truth sensors)
- `<inst>` := Vhcl, Tr
- `<objectQ>` := MountedObj, RelevantTarget
- `<objectC>` := mountedObject, relevantTarget
- `<preQ>` := `Sensor.GroundTruth.<inst>.<name>.TrafficObject.<objectQ>`
- `<preC>` := `GroundTruthSensor[NoS].<objectC>.trafficObject`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.ObjID` | `<preC>.ObjID` | - | Global ID to identify object (integer) |
| `<preQ>.UserID` | `<preC>.UserID` | - | User-defined ID to identify object (integer) |
| `<preQ>.Length` | `<preC>.dimensions.length` | m | Length of the object's bounding box along x-axis |
| `<preQ>.Width` | `<preC>.dimensions.width` | m | Width of the object's bounding box along y-axis |
| `<preQ>.Height` | `<preC>.dimensions.height` | m | Height of the object's bounding box along z-axis |
| `<preQ>.IsInFoV` | `<preC>.isInFoV` | - | Flag indicating if the object is inside the sensors FoV (integer) |
| `<preQ>.IsInTrajectory` | `<preC>.isInTrajectory` | - | Flag indicating if the object is in the current projected path of the sensor (integer) |
| `<preQ>.PercentageVisible` | `<preC>.percentageVisible` | % | Percentage of the object's visible area when occlusion is enabled |
| `<preQ>.IsVisible` | `<preC>.isVisible` | - | Flag indicating if the object is visible for the sensor. 1 if PercentageVisible is > 0 (integer) |
| Reference Point | `<preC>.referencePoint` | - | Reference point of the traffic object (observed point) |
| Nearest Point | `<preC>.nearestPoint` | - | Nearest point of the object's bounding box (observed point) |
| Position in Link Frame | `<preC>.pos_st[0/1]` | m | s/t position in link frame, not valid on junctions |
| Detect Mask | `<preC>.detectMask` | - | Flag if this object can be seen by sensors or other traffic: 1st bit -> detectable by sensors, 2nd bit -> detectable by other traffic |
| Lane Pointer | `<preC>.lane` | - | Pointer to the lane the traffic object is driving on (*tGTObject). Not valid if "Lane" type is not active |
| Root Pointer | `<preC>.root` | - | Pointer to the root the traffic object is driving on (*tGTObject). Not valid if "Root" type is not active |

#### Scene Object Data

##### Template Variables
- `<NoS>` := 0..n (sensors)
- `<NoO>` := 0..n (scene objects)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.GroundTruth.<inst>.<name>.SceneObject.<NoO>`
- `<preC>` := `GroundTruthSensor[NoS].sceneObjects[NoO]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.ObjID` | `<preC>.ObjID` | - | Global ID to identify object (integer) |
| `<preQ>.UserID` | `<preC>.UserID` | - | User-defined ID to identify object (integer) |
| `<preQ>.Length` | `<preC>.dimensions.length` | m | Length of the object's bounding box along x-axis |
| `<preQ>.Width` | `<preC>.dimensions.width` | m | Width of the object's bounding box along y-axis |
| `<preQ>.Height` | `<preC>.dimensions.height` | m | Height of the object's bounding box along z-axis |
| `<preQ>.Type` | `<preC>.type` | - | Scene object type (integer): 0=GTSceneObjectType_TB_Pole, 1=GTSceneObjectType_TreeStrip, 2=GTSceneObjectType_Geometry, 3=GTSceneObjectType_Guidepost, 4=GTSceneObjectType_SignPlate (not yet available) |
| `<preQ>.IsInFoV` | `<preC>.isInFoV` | - | Flag indicating if the object is inside the sensors FoV (integer) |
| `<preQ>.PercentageVisible` | `<preC>.percentageVisible` | % | Percentage of the object's visible area when occlusion is enabled |
| `<preQ>.IsVisible` | `<preC>.isVisible` | - | Flag indicating if the object is visible for the sensor. 1 if PercentageVisible is > 0 (integer) |
| Reference Point | `<preC>.referencePoint` | - | Center point of the object's bounding box (observed point) |
| Nearest Point | `<preC>.nearestPoint` | - | Nearest point of the object's bounding box (observed point) |
| Position in Link Frame | `<preC>.pos_st[0/1]` | m | s/t position in link frame, not valid on junctions |
| Detection Probability | `<preC>.detectionProbability` | - | Detection probability of the object |

#### Observed Point Data

##### Template Variables
- `<NoS>` := 0..n (ground truth sensors)
- `<NoO>` := 0..n (traffic signs)
- `<inst>` := Vhcl, Tr
- `<typeQ>` := TrafficSign, TrafficLight, Mount, TrafficObject, SceneObject
- `<typeC>` := trafficSign, trafficLight, mount, trafficObject, sceneObject
- `<obsvPntC>` := referencePoint, nearestPoint
- `<preQ>` := `Sensor.GroundTruth.<inst>.<name>.<typeQ>.<NoO>.RefPnt`
- `<preC>` := `GroundTruthSensor[NoS].<typeC>.[NoO].<obsvPntC>`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.PosFr0 x/y/z` | `<preC>.posFr0[0/1/2]` | m | x/y/z coordinate in global frame |
| `<preQ>.RotFr0 roll/pitch/yaw` | `<preC>.rotFr0[0/1/2]` | rad | roll/pitch/yaw coordinate in global frame |
| `<preQ>.PosFrS x/y/z` | `<preC>.posFrS[0/1/2]` | m | x/y/z coordinate in sensor frame |
| `<preQ>.RotFrS roll/pitch/yaw` | `<preC>.rotFrS[0/1/2]` | rad | roll/pitch/yaw coordinate in sensor frame |
| `<preQ>.velFr0 x/y/z` | `<preC>.velFr0[0/1/2]` | m/s | (only traffic objects) x/y/z coordinate of velocity in global frame |
| `<preQ>.velFrS x/y/z` | `<preC>.velFrS[0/1/2]` | m/s | (only traffic objects) x/y/z coordinate of velocity in sensor frame |
| Acceleration (Global Frame) | `<preC>.accFr0[0/1/2]` | m/s² | (only traffic objects) x/y/z coordinate of acceleration in global frame |
| Rotation Velocity (Global Frame) | `<preC>.rotvelFr0[0/1/2]` | m/s² | (only traffic objects) roll/pitch/yaw rate in global frame |
| Radial Distance | `<preC>.pos_sphericalFrS[0]` | m | radial distance to the sensor frame |
| Azimuthal Angle | `<preC>.pos_sphericalFrS[1]` | rad | azimuthal angle in sensor frame |
| Elevation Angle | `<preC>.pos_sphericalFrS[2]` | rad | elevation angle in sensor frame |
| Radial Velocity | `<preC>.vel_radialFrS` | rad/s | (only traffic objects) radial velocity relative to sensor frame |

### 26.14.5 Free Space Sensor

#### General

##### Template Variables
- `<Nb>` := 0, .., n (number of sensors)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.FSpace.<inst>.<name>`
- `<preC>` := `FSpaceSensor[Nb]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.rx_ext/ry_ext/rz_ext` | `<preC>.rot_zyx_ext[0/1/2]` | rad | Additional external rotation of sensor, expressed in mounted frame with ZYX-orientation order |
| `<preQ>.TimeStamp` | `<preC>.TimeStamp` | s | Time-stamp of updated sensor signal |
| `<preQ>.tx_ext/ty_ext/tz_ext` | `<preC>.t_ext[0/1/2]` | m | Additional external travel of sensor, expressed in mounted frame |

#### Segments

##### Description
The segment numeration begins on the upper left and ends on the lower right.

##### Template Variables
- `<Nb>` := 0, .., n (number of sensors)
- `<Nb_S>` := 0, .., nS (number of segments)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.FSpace.<inst>.<name>`
- `<preC>` := `FSpaceSensor[Nb]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.Segm.<Nb_S>.alpha` | `<preC>.Segm[Nb_S].alpha_p` | rad | Bearing azimuth of the nearest point in sensor frame (polar coordinates) |
| `<preQ>.Segm.<Nb_S>.ds` | `<preC>.Segm[Nb_S].ds_p` | m | Distance to the nearest point |
| `<preQ>.Segm.<Nb_S>.ds x/y/z` | `<preC>.Segm[Nb_S].ds[0/1/2]` | m | Position of the nearest point in x,y,z-coordinates of sensor frame. Not provided by Free Space Sensor Plus |
| `<preQ>.Segm.<Nb_S>.dv` | `<preC>.Segm[Nb_S].dv_p` | m/s | Relative radial speed (distance change rate) of the nearest point |
| `<preQ>.Segm.<Nb_S>.dv x/y/z` | `<preC>.Segm[Nb_S].dv[0/1/2]` | m/s | Velocity of the nearest point in x,y,z-coordinates of sensor frame. Not provided by Free Space Sensor Plus |
| `<preQ>.Segm.<Nb_S>.theta` | `<preC>.Segm[Nb_S].theta_p` | rad | Bearing elevation of the nearest point in sensor frame (polar coordinates) |
| `<preQ>.Segm.<Nb_S>.ObjId` | `<preC>.Segm[Nb_S].ObjId` | - | Identification number of detected global object: value (integer) = -1 means no detection, free space (please refer to section 5.4 'Object ID' for more information) |

#### Additional Quantities for FSpace Sensor Plus

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.Segm.<Nb_S>.MatId` | `<preC>.Segm[Nb_S].MatId` | - | Material Id |
| `<preQ>.Segm.<Nb_S>.CosIncid` | `<preC>.Segm[Nb_S].CosIncid` | - | Cosine of angle between sensor ray and the object's surface normal at hit point |

### 26.14.6 Traffic Sign Sensor

#### General

##### Template Variables
- `<Nb>` := 0, .., n (number)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.TSign.<inst>.<name>`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.nSign` | `TSignSensor[Nb].nSign` | - | Total number of detected signs (integer) |
| `<preQ>.rx_ext/ry_ext/rz_ext` | `TSignSensor[Nb].rot_zyx_ext[0/1/2]` | rad | Additional external rotation of sensor, expressed in mounted frame with rotation sequence ZYX |
| `<preQ>.TimeStamp` | `TSignSensor[Nb].TimeStamp` | s | Time stamp of updated sensor signals |
| `<preQ>.tx_ext/ty_ext/tz_ext` | `TSignSensor[Nb].t_ext[0/1/2]` | m | Additional external travel of sensor, expressed in mounted frame |

#### Detected Signs

##### Template Variables
- `<Nb>` := 0, ..., n (number)
- `<Nb_TS>` := 0, ... 39 (number of traffic sign)
- `<inst>` := Vhcl, Tr
- `<preQ>` := `Sensor.TSign.<inst>.<name>.<i>` with i=0...39 (if the sensor selects all signs)
- `<preQ>` := `Sensor.TSign.<inst>.<name>.<sign>.<i>` with i=0...3 (if the sensor selects specified signs)

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.ds` | `TSignSensor[Nb].Sign[Nb_TS].ds_p` | m | Distance to traffic sign position |
| `<preQ>.ds x/y/z` | `TSignSensor[Nb].Sign[Nb_TS].ds[0/1/2]` | m | Distance to traffic sign position in sensor frame or mounted frame |
| `<preQ>.Main.val0/val1` | `TSignSensor[Nb].Sign[Nb_TS].main.val[0/1]` | - | User-defined sign attribute values (float) |
| `<preQ>.ObjId` | `TSignSensor[Nb].Sign[Nb_TS].objId` | - | Traffic sign object Id (integer) (please refer to section 5.4 'Object ID' for more information) |

### 26.14.7 Line Sensor

The UAQ `LineDetect.*` are meant for visualization purposes only.

#### General

##### Template Variables
- `<Nb>` := 0, .., n (sensor number)
- `<inst>` := Vhcl
- `<preQ>` := `Sensor.Line.<inst>.<name>`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.nLine_Left/nLine_Right` | `LineSensor[Nb].LLines.nLine / LineSensor[Nb].RLines.nLine` | - | Number of lines detected at left / Number of lines detected at right (integer) |
| `<preQ>.rx_ext/ry_ext/rz_ext` | `LineSensor[Nb].rot_zyx_ext[0/1/2]` | rad | Additional external rotation of sensor, expressed in mounted frame with ZYX-orientation order |
| `<preQ>.TimeStamp` | `LineSensor[Nb].TimeStamp` | s | Time stamp of updated sensor signal |
| `<preQ>.tx_ext/ty_ext/tz_ext` | `LineSensor[Nb].t_ext[0/1/2]` | m | Additional external travel of sensor, expressed in mounted frame |

#### Detected Lines

##### Template Variables
- `<Nb>` := 0, .., n (sensor number)
- `<inst>` := Vhcl
- `<preQ>` := `Sensor.Line.<inst>.<name>.LLines.<i>` or
- `<preQ>` := `Sensor.Line.<inst>.<name>.RLines.<i>`
- `<preC>` := `LineSensor[<Nb>].LLines.L[<i>]` or
- `<preC>` := `LineSensor[<Nb>].RLines.L[<i>]`
- with i=1...100 (1 is the nearest line) for `<preQ>` and i=0...99 for `<preC>`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.ColorCode` | `<preC>.colorCode` | - | User-defined color index of detected line left/right (only for sensor, independent of color displayed in IPGMovie) (integer) |
| `<preQ>.Height` | `<preC>.lineHeight` | m | Line height used for traffic barrier |
| `<preQ>.Type` | `<preC>.type` | - | Line type (integer): 1=continuous single line, 2=broken line, 3=dotted line, 4=double line continuous, 5=double line broken, 6=double line dotted, 7=double line continuous right broken left, 8=double line continuous left broken right, 9=double line continuous right dotted left, 10=double line continuous left dotted right, 12=Traffic barrier |
| `<preQ>.Width` | `<preC>.lineWidth` | m | Line width |
| `<preQ>.Id` | `<preC>.id` | - | Line identification number (integer) |
