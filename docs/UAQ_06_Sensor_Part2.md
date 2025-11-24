# User Accessible Quantities: Sensors (Part 2)

## 26.14 Sensors

### 26.14.8 Road Sensor

**Template Variables:**
- `<inst>` := `Vhcl`, `Tr`
- `<preQ>` := `Sensor.Road.<inst>.<name>`
- `<preC>` := `RoadSensor[i]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.Lane.Act.isRight`<br/>`<preQ>.Lane.OnLeft.isRight`<br/>`<preQ>.Lane.OnRight.isRight` | `<preC>.Act.isRight`<br/>`<preC>.OnLeft.isRight`<br/>`<preC>.OnRight.isRight` | - | Indicates if the actual lane, at which the preview point along the path is, is on right side (same for lanes on left / right side) in path direction |
| `<preQ>.Lane.Act.LaneId`<br/>`<preQ>.Lane.OnLeft.LaneId`<br/>`<preQ>.Lane.OnRight.LaneId` | `<preC>.Act.LaneId`<br/>`<preC>.OnLeft.LaneId`<br/>`<preC>.OnRight.LaneId` | - | Indicates the lane Id at which the preview point along the path is, same for lanes on left / right side (-1 means no lane found) |
| `<preQ>.Lane.Act.tMidLane`<br/>`<preQ>.Lane.OnLeft.tMidLane`<br/>`<preQ>.Lane.OnRight.tMidLane` | `<preC>.Act.tMidLane`<br/>`<preC>.OnLeft.tMidLane`<br/>`<preC>.OnRight.tMidLane` | m | Lateral offset of actual lane mid to the route center line (same for lanes on left / right side) at preview point along path |
| `<preQ>.Lane.Act.Type`<br/>`<preQ>.Lane.OnLeft.Type`<br/>`<preQ>.Lane.OnRight.Type` | `<preC>.Act.Type`<br/>`<preC>.OnLeft.Type`<br/>`<preC>.OnRight.Type` | - | Type of the actual lane at preview point along path (same for lanes on left / right side): 0=legally driveable road, 4=border lane, 5=roadside, 10=bicycle lane, 11=lane only for pedestrian, 12=traffic island, 13=parking area, 14=bus lane, 15=HOV lane, 16=Emergency lane, 17=on-ramp lane, 18=off-ramp lane, 20=Vegetation strip |
| `<preQ>.Lane.Act.Width`<br/>`<preQ>.Lane.OnLeft.Width`<br/>`<preQ>.Lane.OnRight.Width` | `<preC>.Act.Width`<br/>`<preC>.OnLeft.Width`<br/>`<preC>.OnRight.Width` | m | Width of the actual roadway lane and the lanes on left / right side at preview point along the path |
| `<preQ>.Lane.nLeft`<br/>`<preQ>.Lane.nRight` | `<preC>.Lanes.nLanesL`<br/>`<preC>.Lanes.nLanesR` | - | Number of left, right roadway lanes along path / route (integer) |
| `<preQ>.onRoad` | `<preC>.onRoad` | - | Flag: preview point is on the road (boolean). 0=not on the road, Road Sensor quantities are not updated; 1=on the road, Road Sensor quantities are updated |
| `<preQ>.PreviewDist` | `<preC>.PreviewDist` | m | Sensor preview distance. Can be changed via DVA or by modifying the C-variable. |
| `<preQ>.RMarker.Attrib.<j>` | `<preC>.MarkerAttrib[j]` | - | User defined attribute `<j>` of detected road marker (float) |
| `<preQ>.Path.CurveXY`<br/>`<preQ>.Route.CurveXY` | `<preC>.Path.CurveXY`<br/>`<preC>.Route.CurveXY` | 1/m | Route / path curvature at x-y plane at preview point |
| `<preQ>.Path.DevAng`<br/>`<preQ>.Route.DevAng` | `<preC>.Path.Deviation.Ang`<br/>`<preC>.Route.Deviation.Ang` | rad | Deviation angle at preview point along path / route |
| `<preQ>.Path.DevDist`<br/>`<preQ>.Route.DevDist` | `<preC>.Path.Deviation.Dist`<br/>`<preC>.Route.Deviation.Dist` | m | Deviation distance at preview point along path projected to the sensor point; deviation distance to the route |
| `<preQ>.Path.LatSlope`<br/>`<preQ>.Route.LatSlope` | `<preC>.Path.LatSlope`<br/>`<preC>.Route.LatSlope` | rad | Lateral road slope at preview point along path / route |
| `<preQ>.Path.LongSlope`<br/>`<preQ>.Route.LongSlope` | `<preC>.Path.LongSlope`<br/>`<preC>.Route.LongSlope` | rad | Longitudinal road slope at preview point along path / route |
| `<preQ>.Path.tx/y/z`<br/>`<preQ>.Route.tx/y/z` | `<preC>.Path.P_0[0/1/2]`<br/>`<preC>.Route.P_0[0/1/2]` | m | Global position (Fr0) of the preview point along the route and path |
| `<preQ>.tx/y/z` | `<preC>.P_0[0/1/2]` | m | Global position (Fr0) of the preview point along the vehicle direction |
| `<preQ>.Z_0.x/y/z` | `<preC>.Z_0[0/1/2]` | - | Road normal vector at preview point along the vehicle direction |

### 26.14.9 Collision Sensor

**Template Variables:**
- `<preQ>` := `Sensor.Collision.Vhcl` (only possible on ego vehicle)

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.Fr1.Count` | - | - | Counter for detected collision with the vehicle body Fr1 |
| `<preQ>.Fr1.ObjId` | - | - | Detected collision of vehicle body Fr1 with the global object ObjId: value (integer) =-1 stands for no detection. Please refer to section 5.4 'Object ID' for more information |
| `<preQ>.W<pos>.Count` | - | - | Counter for detected collision with the vehicle wheel `<pos>` |
| `<preQ>.W<pos>.ObjId` | - | - | Detected collision of vehicle wheel `<pos>` with the global object ObjId: value (integer) =-1 stands for no detection. Please refer to section 5.4 'Object ID' for more information |

### 26.14.10 Object by Lane Sensor

**Template Variables:**
- `<NoS>` := 0..n (sensors)
- `<NoLS>` := 0..2 (LaneScopes)
- `<NoL>` := 0..3 (Lanes)
- `<LS>` := L, C, R
- `<inst>` := `Vhcl`, `Tr`
- `<preQ>` := `Sensor.ObjByLane.<inst>.<name>`
- `<preC>` := `ObjByLane[NoS]`

#### General

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.LaneDiff` | `<preC>.LaneDiff` | - | Offset of the current lane (POI) and the lane corresponding to the route, 99 if invalid |
| `<preQ>.tPOI` | `<preC>.tPOI` | m | t-offset from POI to current path |
| `<preQ>.tPath` | `<preC>.tPath` | m | t-offset of current path to route |
| `<preQ>.Active` | `ObjByLane_SetActive(...)` | - | 0 or 1 to deactivate or activate calculation for this sensor instance |
| `<preQ>.TimeStamp` | `<preC>.TimeStamp` | s | Time-stamp of updated sensor signals |
| `<preQ>.LanesL.nLanesMax`<br/>`<preQ>.LanesC.nLanesMax`<br/>`<preQ>.LanesR.nLanesMax` | `ObjByLane_SetNLanes(...)` | - | Set the number of lanes to be considered for each LaneScope (0..3 for "L", "R" and 0..1 for "C") |
| `<preQ>.LanesL.nLanes`<br/>`<preQ>.LanesC.nLanes`<br/>`<preQ>.LanesR.nLanes` | `<preC>.nLanes[NoLS]` | - | Number of lanes that were found for each LaneScope |
| `<preQ>.LanesL.RangeMin`<br/>`<preQ>.LanesL.RangeMax`<br/>`<preQ>.LanesC.RangeMin`<br/>`<preQ>.LanesC.RangeMax`<br/>`<preQ>.LanesR.RangeMin`<br/>`<preQ>.LanesR.RangeMax` | `ObjByLane_SetRange(...)` | m | Set min/max range for each LaneScope. Min. range has to be less or equal to zero, max. range has to be greater or equal to zero. |

#### Per Lane

**Template Variables:**
- `<preQ>` := `Sensor.ObjByLane.<inst>.<name>.Lanes<LS>.<NoL>`
- `<preC>` := `ObjByLane[NoS].Lane[NoLS][NoL]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.ObjID` | `<preC>.ObjID` | - | Global lane ID |
| `<preQ>.Type` | `<preC>.Type` | - | Lane type (see enum tLaneType in Sensor_ObjectByLane.h) |
| `<preQ>.DrvOn` | `<preC>.DrvOn` | - | 1 if allowed to drive on, 0 if only allowed to drive over |
| `<preQ>.LengthRear`<br/>`<preQ>.LengthFront` | `<preC>.LengthRear`<br/>`<preC>.LengthFront` | m | Length of drivable part of the lane |
| `<preQ>.Width` | `<preC>.Width` | m | Width of lane at s-pos. of POI |
| `<preQ>.tPathOff` | `<preC>.tPathOff` | m | t-offset from route to current lane-path |
| `<preQ>.InDrvDir` | `<preC>.InDrvDir` | - | -1 for oncoming lane, 1 otherwise |
| `<preQ>.nObjF`<br/>`<preQ>.nObjR` | `<preC>.nObjF`<br/>`<preC>.nObjR` | - | No. of objects in front/rear list |

#### Per Object in rear/front lists

**Template Variables:**
- `<preQ>` := `Sensor.ObjByLane.<inst>.<name>.Lanes<LS>.<NoL>.ObjF.<NoO>`
- `<preC>` := `ObjByLane[NoS].Lane[NoLS][NoL].ObjFront[NoO]`
- (same with ObjR / ObjRear)

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.ObjID` | `<preC>.ObjID` | - | Global object ID |
| `<preQ>.Oncoming` | `<preC>.Oncoming` | - | 0 if driving in the same direction, 1 for oncoming |
| `<preQ>.sMin`<br/>`<preQ>.sMax`<br/>`<preQ>.tMin`<br/>`<preQ>.tMax` | `<preC>.sMin`<br/>`<preC>.sMax`<br/>`<preC>.tMin`<br/>`<preC>.tMax` | m | sMin, sMax relative to the POI; tMin, tMax relative to the path of the lane the POI is currently on |
| `<preQ>.VelLong` | `<preC>.VelLong` | m/s | Absolute velocity in direction of the route |

### 26.14.11 Radar Sensor

**Template Variables:**
- `<NoS>` := 0..n (sensors)
- `<inst>` := `Vhcl`, `Tr`
- `<preQ>` := `Sensor.Radar.<inst>`
- `<preC>` := `RadarSensor[NoS].GlobalInf[0]`

#### General

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.nSensors` | `RadarCount` | - | Number of sensors (integer) |
| `<preQ>.<name>.RolCount` | `<preC>.RolCount` | - | Rolling cycle counter (integer) |
| `<preQ>.<name>.nObj` | `<preC>.nObj` | - | Number of detected objects (integer) |
| `<preQ>.<name>.RelvTgt` | `<preC>.RelvTgt` | - | Number of the relevant target in the object list (integer) |
| `<preQ>.<name>.nLanesL`<br/>`<preQ>.<name>.nLanesR` | `<preC>.nLanesL`<br/>`<preC>.nLanesR` | - | Number of drivable lanes left/right (integer). Includes Driving Lane, On-Ramp, Off-Ramp |
| `<preQ>.<name>.DistToLeftBorder`<br/>`<preQ>.<name>.DistToRightBorder` | `<preC>.DistToLeftBorder`<br/>`<preC>.DistToRightBorder` | m | Distance to left/right border |
| `<preQ>.<name>.TransmitPower` | `RadarSensor[NoS].TransmitPower` | dBm | Use this quantity to alter the transmit power during simulation (DVA) |

#### Object List

**Template Variables:**
- `<NoO>` := 0..m (objects)
- `<preQ>` := `Sensor.Radar.<inst>.<name>.Obj<NoO>`
- `<preC>` := `RadarSensor[NoS].ObjList[NoO]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.ObjId` | `<preC>.ObjId` | - | Global ID to identify object. Please refer to section 5.4 'Object ID' for more information |
| `<preQ>.MeasStat` | `<preC>.MeasStat` | - | Measurement status (integer): 0=no object, 1=new object, 2=(currently not used), 3=object measured |

### 26.14.12 Camera Sensor

**Template Variables:**
- `<NoS>` := 0..n (sensors)
- `<inst>` := `Vhcl`, `Tr`
- `<preQ>` := `Sensor.Camera.<inst>`
- `<preC>` := `CameraSensor[NoS]`

#### General

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.<name>.nObj` | `<preC>.nObj` | - | Number of detected objects (integer) |
| `<preQ>.<name>.TimeStamp` | `<preC>.TimeStamp` | s | Time-stamp of updated sensor signals |

#### Object List

**Template Variables:**
- `<NoO>` := 0..m (objects)
- `<preQ>` := `Sensor.Camera.<inst>.<name>.Obj.<NoO>`
- `<preC>` := `CameraSensor[NoS].Obj[NoO]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.ObjID` | `<preC>.ObjID` | - | Global ID to identify object (integer). Please refer to section 5.4 'Object ID' for more information. |
| `<preQ>.Type` | `<preC>.Type` | - | Camera object type (integer): 0=Car, 1=Truck, 2=Bicycle, 3=Pedestrian, 4=Traffic sign, 5=Traffic light |
| `<preQ>.nVisPixels` | `<preC>.nVisPixels` | - | Number of visible pixels (integer) |
| `<preQ>.Confidence` | `<preC>.Confidence` | - | Indicates how much of the object is visible |
| `<preQ>.MBR.BL_X/Y/Z`<br/>`<preQ>.MBR.TR_X/Y/Z` | `<preC>.MBR[0][0/1/2]`<br/>`<preC>.MBR[1][0/1/2]` | m | Minimum bounding rectangle - bottom left and top right points |
| `<preQ>.Facing` | `<preC>.Facing` | - | 0: not facing sensor, 1: facing sensor (integer) |
| `<preQ>.LightState` | `<preC>.LightState` | - | Traffic light state/phase (integer): 0=All lights off, 1=Green light on, 2=Yellow light on, 3=Red light on, 4=Red-Yellow light on |
| `<preQ>.SignMain.Val0`<br/>`<preQ>.SignMain.Val1` | `<preC>.SignMainVal[0]`<br/>`<preC>.SignMainVal[1]` | - | User-defined sign attribute values |
| `<preQ>.SignSuppl1.Val0`<br/>`<preQ>.SignSuppl1.Val1` | `<preC>.SignSuppl1Val[0]`<br/>`<preC>.SignSuppl1Val[1]` | - | User-defined sign attribute values |
| `<preQ>.SignSuppl2.Val0`<br/>`<preQ>.SignSuppl2.Val1` | `<preC>.SignSuppl2Val[0]`<br/>`<preC>.SignSuppl2Val[1]` | - | User-defined sign attribute values |

### 26.14.13 Global Navigation Sensor

**Template Variables:**
- `<preQ>` := `Sensor.GNav.Vhcl`
- `<preQ_Rec>` := `Sensor.GNav.Vhcl.Receiver`
- `<preQ_Sat>` := `Sensor.GNav.Vhcl.Sat`
- `<preQ_Rinex>` := `Sensor.GNav.Vhcl.RinexData`
- `<preQ_RinexEph>` := `Sensor.GNav.Vhcl.RinexData.Sat_Ephemeris`
- `<preC>` := `GNavSensor`
- `<preC_Rec>` := `GNavSensor.Receiver`

#### Receiver Position and Velocity

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ_Rec>.Position.ECEF.x/y/z` | `<preC_Rec>.UserPosEcefTsa[0/1/2]` | m | Exact receiver position in Earth Centered Earth Fixed (ECEF) coordinate system. |
| `<preQ_Rec>.Position.ECEF_fromPsr.x/y/z` | `<preC_Rec>.UserPosEcefTsa_fromPsr[0/1/2]` | m | Receiver position in Earth Centered Earth Fixed (ECEF) coordinate system calculated from pseudorange. |
| `<preQ_Rec>.Position.ECEF_Delta.x/y/z` | `<preC_Rec>.Delta_UserPosEcefTsa[0/1/2]` | m | Difference of receiver position from pseudorange to exact position in Earth Centered Earth Fixed (ECEF) coordinate system. |
| `<preQ_Rec>.Position.ECEFVel.x/y/z` | `<preC_Rec>.UserVelEcefTsa[0/1/2]` | m/s | Velocity of the receiver in Earth Centered Earth Fixed (ECEF) coordinate system. |
| `<preQ_Rec>.Position.LLH.Lat`<br/>`<preQ_Rec>.Position.LLH.Long`<br/>`<preQ_Rec>.Position.LLH.H` | `<preC_Rec>.UserPosLlhTsa[0/1/2]` | rad/rad/m | Exact receiver position in LLH (latitude, longitude, height) coordinate system. |
| `<preQ_Rec>.Position.LLH_fromPsr.Lat`<br/>`<preQ_Rec>.Position.LLH_fromPsr.Long`<br/>`<preQ_Rec>.Position.LLH_fromPsr.H` | `<preC_Rec>.UserPosLlhTsa_fromPsr[0/1/2]` | rad/rad/m | Receiver position in LLH (latitude, longitude, height) coordinate system calculated from pseudorange. |
| `<preQ_Rec>.Position.LLH_Delta.Lat`<br/>`<preQ_Rec>.Position.LLH_Delta.Long`<br/>`<preQ_Rec>.Position.LLH_Delta.H` | `<preC_Rec>.Delta_UserPosLlhTsa[0/1/2]` | rad/rad/m | Difference of receiver position from pseudorange to exact position in LLH (latitude, longitude, height) coordinate system. |

#### Receiver Time and Clock

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ_Rec>.Time.GPSWeek` | `<preC_Rec>.Time_GpsWeek` | - | Number of GPS week. |
| `<preQ_Rec>.Time.secsOfWeek` | `<preC_Rec>.Time_secsOfWeek` | s | Secs of GPS week. |
| `<preQ_Rec>.Time.yday` | `<preC_Rec>.Time_yday` | - | Number of day in the year. |
| `<preQ_Rec>.Time.ClockError` | `<preC_Rec>.RecClockError` | m | Exact receiver clock error. |
| `<preQ_Rec>.Time.ClockError_fromPsr` | `<preC_Rec>.RecClockError_fromPsr` | m | Receiver clock error calculated from pseudorange. |
| `<preQ_Rec>.Time.ClockError_Delta` | `<preC_Rec>.Delta_RecClockError` | m | Difference of receiver clock error from pseudorange to exact receiver clock error. |

#### Receiver Satellite Information

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ_Rec>.SatNoOverElevMask` | `<preC_Rec>.NoVisibleSat` | - | Number of satellites that are above the elevation mask. |
| `<preQ_Rec>.SatNoDirectView` | `<preC_Rec>.NoVisibleSatDirect` | - | Number of satellites that have a clear line of sight to the receiver. |
| `<preQ_Rec>.GDOP` | `<preC_Rec>.GDOP` | - | Geometrical dilution of precision. |
| `<preQ_Rec>.TDOP` | `<preC_Rec>.TDOP` | - | Time dilution of precision. |
| `<preQ_Rec>.PDOP` | `<preC_Rec>.PDOP` | - | Positional dilution of precision. |
| `<preQ_Rec>.HDOP` | `<preC_Rec>.HDOP` | - | Horizontal dilution of precision. |
| `<preQ_Rec>.VDOP` | `<preC_Rec>.VDOP` | - | Vertical dilution of precision. |
| `<preQ_Rec>.XDOP` | `<preC_Rec>.XDOP` | - | Dilution of precision (x). |
| `<preQ_Rec>.YDOP` | `<preC_Rec>.YDOP` | - | Dilution of precision (y). |
| `<preQ_Rec>.XYDOP` | `<preC_Rec>.XYDOP` | - | Dilution of precision (xy). |

#### Receiver Channel Information

**Template Variables:**
- `<i>` represents the channel index

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ_Rec>.channel<i>.PRN` | `<preC_Rec>.Channel[i].PRN` | - | Pseudo random noise (PRN) number of satellite visible for receiver channel i. |
| `<preQ_Rec>.channel<i>.PseudoRange` | `<preC_Rec>.Channel[i].psr` | m | Pseudorange of satellite visible for receiver channel i. |
| `<preQ_Rec>.channel<i>.RangeRate` | `<preC_Rec>.Channel[i].rr` | m/s | Range rate of satellite visible for receiver channel i. |
| `<preQ_Rec>.channel<i>.elev` | `<preC_Rec>.Channel[i].elev` | deg | Elevation angle of satellite visible for receiver channel i. |
| `<preQ_Rec>.channel<i>.azim` | `<preC_Rec>.Channel[i].azim` | deg | Azimuth angle of satellite visible for receiver channel i. |
| `<preQ_Rec>.channel<i>.geometricRange` | `<preC_Rec>.Channel[i].dist` | m | Geometrical distance to satellite visible for receiver channel i. |
| `<preQ_Rec>.channel<i>.ephError` | `<preC_Rec>.Channel[i].ephErr` | m | Ephemeris error of satellite visible for receiver channel i. |
| `<preQ_Rec>.channel<i>.ionoError` | `<preC_Rec>.Channel[i].ionoErr` | m | Ionospheric error of satellite visible for receiver channel i. |
| `<preQ_Rec>.channel<i>.tropoError` | `<preC_Rec>.Channel[i].tropoErr` | m | Tropospheric error of satellite visible for receiver channel i. |
| `<preQ_Rec>.channel<i>.SatelliteClockOffset` | `<preC_Rec>.Channel[i].dtsv` | s | Satellite clock offset of satellite visible for receiver channel i. |

#### Satellite Information

**Template Variables:**
- `<i>` represents the satellite index

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ_Sat>.sat<i>.PosECEF.x/y/z` | `<preC>.sat[i].satPosEcef[0/1/2]` | m | Position of satellite i in Earth Centered Earth Fixed (ECEF) coordinate system. |
| `<preQ_Sat>.sat<i>.VelECEF.x/y/z` | `<preC>.sat[i].satVelEcef[0/1/2]` | m/s | Velocity of satellite i in Earth Centered Earth Fixed (ECEF) coordinate system. |
| `<preQ_Sat>.sat<i>.elev` | `<preC>.sat[i].elev` | deg | Elevation angle of satellite i. |
| `<preQ_Sat>.sat<i>.azim` | `<preC>.sat[i].azim` | deg | Azimuth angle of satellite i. |
| `<preQ_Sat>.sat<i>.isVisible` | `<preC>.sat[i].satIsVisible` | - | Flag: Satellite i is over elevation mask (boolean). |
| `<preQ_Sat>.sat<i>.DirectView` | `<preC>.sat[i].satDirectVisible` | - | Flag: Satellite i has clear line of sight to receiver (boolean). |

#### RINEX Data - Ionosphere Parameters

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ_Rinex>.Klobuchar.Alpha1/Alpha2/Alpha3/Alpha4` | - | - | Ionosphere parameters A0-A3 of almanac |
| `<preQ_Rinex>.Klobuchar.Beta1/Beta2/Beta3/Beta4` | - | - | Ionosphere parameters B0-B3 of almanac |

#### RINEX Data - Ephemeris Information

**Template Variables:**
- `<i>` represents the satellite index

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ_RinexEph>.sat<i>.toe_GPSWeek` | - | - | GPS week number - Time of Ephemeris |
| `<preQ_RinexEph>.sat<i>.toe_secsOfWeek` | - | sec | Seconds of GPS week - Time of Ephemeris |
| `<preQ_RinexEph>.sat<i>.toc_GPSWeek` | - | - | GPS week number - Time of Clock |
| `<preQ_RinexEph>.sat<i>.toc_secsOfWeek` | - | sec | Seconds of GPS week - Time of Clock |
| `<preQ_RinexEph>.sat<i>.clock_a0` | - | sec | Satellite SV clock error bias |
| `<preQ_RinexEph>.sat<i>.clock_a1` | - | s/s | Satellite SV clock error drift |
| `<preQ_RinexEph>.sat<i>.clock_a2` | - | s/s² | Satellite SV clock error drift rate |
| `<preQ_RinexEph>.sat<i>.C_ic` | - | rad | Cosine correction of inclination angle |
| `<preQ_RinexEph>.sat<i>.C_is` | - | rad | Sine correction of inclination angle |
| `<preQ_RinexEph>.sat<i>.C_uc` | - | rad | Cosine correction of longitude |
| `<preQ_RinexEph>.sat<i>.C_us` | - | rad | Sine correction of longitude |
| `<preQ_RinexEph>.sat<i>.C_rc` | - | m | Cosine correction of radius of orbit |
| `<preQ_RinexEph>.sat<i>.C_rs` | - | m | Sine correction of radius of orbit |
| `<preQ_RinexEph>.sat<i>.delta_n` | - | rad/s | Mean motion difference from computed value |
| `<preQ_RinexEph>.sat<i>.e` | - | - | Eccentricity |
| `<preQ_RinexEph>.sat<i>.i_0` | - | rad | Inclination angle at Time of Ephemeris |
| `<preQ_RinexEph>.sat<i>.iDot` | - | rad/s | Rate of inclination angle |
| `<preQ_RinexEph>.sat<i>.M_0` | - | rad | Mean anomaly at Time of Ephemeris |
| `<preQ_RinexEph>.sat<i>.omega` | - | rad | Argument of perigee |
| `<preQ_RinexEph>.sat<i>.omega_0` | - | rad | Longitude of ascending node of orbit plane at weekly epoch |
| `<preQ_RinexEph>.sat<i>.omegaDot` | - | rad/s | Rate of right ascension |
| `<preQ_RinexEph>.sat<i>.sqrtA` | - | sqrt(m) | Square root of semi-major axis |

### 26.14.14 Ultrasonic RSI

**Template Variables:**
- `<NoT>` := 0..n (transmitters)
- `<NoR>` := 0..n (receivers)
- `<NoD>` := 0..m (detections)
- `<inst>` := `Vhcl`, `Tr`
- `<preQ>` := `Sensor.USonicRSI.Tx.<inst>.<name>`
- `<preQE>` := `Sensor.USonicRSI.<inst>.<name>`
- `<preC>` := `USonicRSI[NoT]`
- `<preQR>` := `Sensor.USonicRSI.Tx.<inst>.<name>.Rx.<inst>.<name>`
- `<preCR>` := `USonicRSI[NoT].ReceiverUSonic[NoR]`
- `<preCD>` := `USonicRSI[NoT].ReceiverUSonic[NoR].DetPoints[NoD]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.TimeFired` | `<preC>.TimeFired` | s | Time stamp of the ray tracing job |
| `<preQR>.nDetections` | `<preCR>.nDetections` | - | Number of detections (int) |
| `<preQE>.tx_ext/ty_ext/tz_ext` | `<preC>.t_ext[0/1/2]` | m | External sensor travel, expressed in mounted frame |
| `<preQE>.rx_ext/ry_ext/rz_ext` | `<preC>.rot_zyx_ext[0/1/2]` | rad | External sensor rotation with ZYX-orientation order |
| `<preCD>.TimeOfFlight` | - | s | Time of flight |
| `<preCD>.SPA.real` | - | Pa | Real component of sound pressure amplitude |
| `<preCD>.SPA.imag` | - | Pa | Imaginary component of sound pressure amplitude |

### 26.14.15 Radar RSI

**Template Variables:**
- `<NoS>` := 0..n (sensors)
- `<NoD>` := 0..m (detections)
- `<NoVRx>` := 0..k (virtual receivers)
- `<inst>` := `Vhcl`, `Tr`
- `<preQ>` := `Sensor.RadarRSI.<inst>.<name>`
- `<preC>` := `RadarRSI[NoS]`
- `<preCDP>` := `RadarRSI[NoS].DetPoints[NoD]`
- `<preCVRx>` := `RadarRSI[NoS].DetVRx[NoD]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.nDetections` | `<preC>.nDetections` | - | Number of detections (int) |
| `<preQ>.TimeFired` | `<preC>.TimeFired` | s | Time stamp of the ray tracing job |
| `<preQ>.tx_ext/ty_ext/tz_ext` | `<preC>.t_ext[0/1/2]` | m | External sensor travel, expressed in mounted frame |
| `<preQ>.rx_ext/ry_ext/rz_ext` | `<preC>.rot_zyx_ext[0/1/2]` | rad | External sensor rotation with ZYX-orientation order |
| `<preCDP>.Power` | - | dBm | Power of detection |
| `<preCDP>.Velocity` | - | m/s | Relative radial velocity of detection |
| `<preCDP>.Coordinates[0]` | - | m | Longitudinal position of detection in sensor frame (output = cartesian) or Radial distance of detection in sensor frame (output = spherical) |
| `<preCDP>.Coordinates[1]` | - | m | Lateral position of detection in sensor frame (output = cartesian) or Azimuth angle in sensor frame (output = spherical) |
| `<preCDP>.Coordinates[2]` | - | m | Vertical position of detection in sensor frame (output = cartesian) or Elevation angle in sensor frame (output = spherical) |
| `<preCVRx>.Velocity` | - | m/s | Relative radial velocity of detection |
| `<preCVRx>.Range` | - | m | Radial distance of detection in sensor frame |
| `<preCVRx>.AmpVRx[<NoVRx>].real` | - | mV | Real component of amplitude for `<NoVRx>` virtual receiver. |
| `<preCVRx>.AmpVRx[<NoVRx>].imag` | - | mV | Imaginary component of amplitude for `<NoVRx>` virtual receiver. |

### 26.14.16 Lidar RSI

**Template Variables:**
- `<NoT>` := 0..n (transceivers)
- `<NoSP>` := 0..m (scan points)
- `<inst>` := `Vhcl`, `Tr`
- `<preQ>` := `Sensor.LidarRSI.<inst>.<name>`
- `<preC>` := `LidarRSI[NoT]`
- `<preCC>` := `LidarRSI[NoT].ScanPoint[NoSP]`
- `<preS>` := `ScanPoint[NoSP]`

| UAQ Name | C-Code | Simulink | Unit | Info |
|---|---|---|---|---|
| `<preQ>.nScanPoints` | `<preC>.nScanPoints` | `nScanPoints` | - | Number of scan points (int) |
| `<preQ>.ScanTime` | `<preC>.ScanTime` | `ScanTime` | s | Time stamp of the ray tracing job |
| `<preQ>.ScanNumber` | `<preC>.ScanNumber` | `ScanNumber` | - | Number of the ray tracing job |
| `<preQ>.tx_ext/ty_ext/tz_ext` | `<preC>.t_ext[0/1/2]` | `t_ext_x/t_ext_y/t_ext_z` | m | External sensor travel, expressed in mounted frame |
| `<preQ>.rx_ext/ry_ext/rz_ext` | `<preC>.rot_zyx_ext[0/1/2]` | `rot_zyx_ext_x/rot_zyx_ext_y/rot_zyx_ext_z` | rad | External sensor rotation with ZYX-orientation order |
| `<preCC>.TimeOF` | `<preS>.TimeOF` | - | ns | Time of flight |
| `<preCC>.LengthOF` | `<preS>.LengthOF` | - | m | Length of flight |
| `<preCC>.BeamID` | `<preS>.BeamID` | - | - | Beam ID corresponds to specified beam ID in beam-file |
| `<preCC>.EchoID` | `<preS>.EchoID` | - | - | Echo ID (unique per beam) - either 0..2 with signal processing active or ray-index within beam otherwise (from bottom left ray to top right) |
| `<preCC>.Origin[0/1/2]` | `<preS>.Origin_x/Origin_y/Origin_z` | - | m | x/y/z coordinate of ray origin in sensor frame |
| `<preCC>.Intensity` | `<preS>.Intensity` | - | nW | Intensity of reflected light |
| `<preCC>.PulseWidth` | `<preS>.PulseWidth` | - | ns | Echo pulse width |
| `<preCC>.nRefl` | `<preS>.nRefl` | - | - | Number of reflections. For a single ray the number of reflections describes how often this ray has hit something in the scene before it is reflected back to the sensor. This value applies only if the Separation Distance of the sensor is set to 0. If the Separation Distance is not 0, multiple rays may be combined to a single ScanPoint. In this case the number of reflections is not valid, because a single value would not be as meaningful. |

### 26.14.17 Camera RSI

**Template Variables:**
- `<NoS>` := 0..n (sensors)
- `<inst>` := `Vhcl`, `Tr`
- `<preQ>` := `Sensor.CameraRSI.<inst>.<name>`
- `<preC>` := `CameraRSI[NoS]`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preQ>.TimeStamp` | `<preC>.Profiler.TimeStamp` | s | Simulation timestamp of the rendering cycle |
| `<preQ>.FrameDeltaT` | `<preC>.Profiler.FrameDeltaT` | s | Time elapsed between frame start and rendering end |
| `<preQ>.TotalDeltaT` | `<preC>.Profiler.TotalDeltaT` | s | Time elapsed between frame start and frame end |
| `<preQ>.RelativeStartTime` | `<preC>.Profiler.RelativeStartTime` | s | Real time stamp of the frame start, based on the start of the simulation (optional UAQ, see section 21.22.12 'Performance Quantities'). |
| `<preQ>.UpdateDeltaT` | `<preC>.Profiler.UpdateDeltaT` | s | Time elapsed between frame start and scene update end (optional UAQ, see section 21.22.12 'Performance Quantities'). |
