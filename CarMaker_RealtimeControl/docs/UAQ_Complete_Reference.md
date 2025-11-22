
# User Accessible Quantities: General & Control

## 26.1 General

### 26.1.1 TCPU
| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `TCPU.Main.Total` | - | s | Total time-consumption for calculation of the current cycle. This should not be confused with DeltaT (float) |
| `TCPU.Main.AposEvalSend` | - | s | Time-consumption for function AposEvalSend during the current calculation cycle (float) |
| `TCPU.Main.AposPoll` | - | s | Time-consumption for function AposPoll during the current calculation cycle (float) |
| `TCPU.Main.Brake` | - | s | Time-consumption for calculation of the Brake module during the current calculation cycle (float) |
| `TCPU.Main.Sensors` | - | s | Time-consumption for calculation of the sensor modules during the current calculation cycle (float) |
| `TCPU.Main.DrivMan` | - | s | Time-consumption for calculation of the DrivMan module during the current calculation cycle (float) |
| `TCPU.Main.In` | - | s | Time-consumption for calculation of the IO_In module during the current calculation cycle (float) |
| `TCPU.Main.Out` | - | s | Time-consumption for calculation of the IO_Out module during the current calculation cycle (float) |
| `TCPU.Main.PowerTrain` | - | s | Time-consumption for calculation of the PowerTrain module during the current calculation cycle (float) |
| `TCPU.Main.Traffic` | - | s | Time-consumption for calculation of the Traffic module during the current calculation cycle (float) |
| `TCPU.Main.Trailer` | - | s | Time-consumption for calculation of the Trailer module during the current calculation cycle (float) |
| `TCPU.Main.User` | - | s | Time-consumption for calculation of the Usermodule during the current calculation cycle (float) |
| `TCPU.Main.Vehicle` | - | s | Time-consumption for calculation of the Vehicle module during the current calculation cycle (float) |
| `TCPU.Main.VehicleControl` | - | s | Time-consumption for calculation of the VehicleControl module during the current calculation cycle (float) |

### 26.1.2 TGPU
| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `DeltaT` | `DeltaT` | s | Duration of completed calculation cycle |
| `DeltaTPeak` | - | s | Maximum duration of completed calculation cycle |
| `Implicit` | - | - | Sample number in IPGControl |
| `Time` | `SimCore.Time` | s | Simulation-time of the current Test Run. Time starts after initialization process is finished. This time may be accelerated or delayed during non-real-time simulations. |
| `Time.Global` | `TimeGlobal` | s | Simulation-time since the start of the application. This time may be accelerated or delayed during non-real-time simulations. |
| `Time.WC` | `SimCore.TimeWC` | s | “Wall-clock-time”. This is the real time elapsed since the start of the application. In non-real-time simulations this time may differ from Time.Global. |
| `TGPU.GPUSensor.<No>.Total` | - | s | Time-consumption for GPU Sensor calculation cycle (float). `<No>` increments with each cluster starting from 1 for IPGMovie and from 128 for Movie NX. Note: this UAQ is not valid for a GPU Sensor instance with CameraRSI sensor(s) in VIB mode since this instance is not synchronised with the simulation. |

### 26.1.3 Misc
| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Log.nError` | `Log_nError` | - | Counter for log file errors (long) |
| `Log.nLog` | `Log_nLog` | - | Counter for log file messages (long) |
| `Log.nWarn` | `Log_nWarn` | - | Counter for log file warnings (long) |
| `SC.GPUSensor.<no>.TimeJobStart` | - | s | Time stamp sensor calculation started |
| `SC.GPUSensor.<no>.TimeJobFinish` | - | s | Time stamp sensor calculation finished |
| `SC.MemFree` | - | - | For internal use only (unsigned integer) |
| `SC.MemUsed` | - | - | For internal use only (unsigned integer) |
| `SC.MemUsed.TRNo` | - | - | For internal use only (unsigned integer) |
| `SC.Start.No` | `SimCore.Start.No` | - | Number of Test Run started and stopped since the start of the application (unsigned integer) |
| `SC.State` | `SimCore.State` | - | Simulation state (integer) |
| `SC.TAccel` | `SimCore.TAccel` | - | Time acceleration factor for offline simulation |
| `RealtimeMeasurement.Percent_at_lower_timeborder<no>` | - | % | Percentage of cycles at lower timeboarder (Only in CarMaker Office Extended) |
| `RealtimeMeasurement.Percent_at_upper_timeborder<no>` | - | % | Percentage of cycles at upper timeboarder (Only in CarMaker Office Extended) |

## 26.2 Environment
| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Env.AirDensity` | `Env.AirDensity` | kg/m3 | Environment air density |
| `Env.AirHumidity` | `Env.AirHumidity` | - | Environment air relative humidity |
| `Env.AirPressure` | `Env.AirPressure` | bar | Environment air pressure |
| `Env.SpeedOfSound` | `Env.SpeedOfSound` | m/s | Speed of sound in environmental air |
| `Env.SolarRadiation` | `Env.SolarRadiation` | W/m2 | Environment solar radiation |
| `Env.Temperature` | `Env.Temperature` | K | Environment air temperature |
| `Env.RainRate` | `Env.RainRate` | mm/h | Environment rain rate, read-only, computed from Env.Precipitation.Type and Env.Precipitation.Intensity |
| `Env.VisRangeInFog` | `Env.VisRangeInFog` | m | Environment visual range in fog |
| `Env.Time` | `Env.Time` | hours | Time of day (0..24) |
| `Env.YearDay` | `Env.yDay` | days | Day of the year |
| `Env.PoI_GCS.Elev` | `Env.PoI_GCS.Elev` | m | Global position for PoI, expressed in GCS coordinates (geodetic elevation) |
| `Env.PoI_GCS.Long` | `Env.PoI_GCS.Long` | rad | Global position for PoI, expressed in GCS coordinates (longitude) |
| `Env.PoI_GCS.Lat` | `Env.PoI_GCS.Lat` | rad | Global position for PoI, expressed in GCS coordinates (latitude) |
| `Env.sRoad` | `Env.sRoad` | m | Vehicle route / path coordinate |
| `Env.WindVel_ext.x` | `Env.WindVel_ext[0]` | m/s | Additional user defined wind in inertial frame (x) |
| `Env.WindVel_ext.y` | `Env.WindVel_ext[1]` | m/s | Additional user defined wind in inertial frame (y) |
| `Env.WindVel_ext.z` | `Env.WindVel_ext[2]` | m/s | Additional user defined wind in inertial frame (z) |
| `Env.WindVel_tot.x` | `Env.WindVel_tot[0]` | m/s | Total environment global wind in inertial frame (x) |
| `Env.WindVel_tot.y` | `Env.WindVel_tot[1]` | m/s | Total environment global wind in inertial frame (y) |
| `Env.WindVel_tot.z` | `Env.WindVel_tot[2]` | m/s | Total environment global wind in inertial frame (z) |
| `Env.Event.<i>.State` | - | - | State of event with index i. 0: Initial, 1: Standby, 2: Running, 3: Complete, 4: Final |
| `Env.Event.<i>.ExecCount` | - | - | Execution count of event with index i |
| `Env.Event.<i>.Act.No` | - | - | Current action index of event with index i (integer). >= 0: number of defined action, -11: global event control active but no action, -12: global event control deactivated |
| `Env.Event.<i>.Act.Time` | - | s | Time of current action in event with index i. -1: event is currently not active |

## 26.3 Driving Maneuvers
| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `DM.ax.Trgt` | - | m/s2 | Target acceleration used for Speed Profile |
| `DM.Brake` | `DrivMan.Brake` | - | Brake/decelerator activity, relative pedal force (0..1) |
| `DM.BrakePark` | `DrivMan.BrakePark` | - | Park brake activity (0..1) |
| `DM.Clutch` | `DrivMan.Clutch` | - | Clutch activity (0..1) |
| `DM.Gas` | `DrivMan.Gas` | - | Gas/throttle/accelerator activity (0..1) |
| `DM.GearNo` | `DrivMan.GearNo` | - | Gear number (integer) |
| `DM.GearNo.Trgt` | `DrivMan.GearNoTrgt` | - | Target gear number set at the beginning of the shifting procedure during manual shifting (integer) |
| `DM.Key` | `DrivMan.Key` | - | Vehicle key position (integer): 0: Key out, 1: Key in power off, 2: Key in power accessory, 3: Key in power on, 4: Key in starter active |
| `DM.LaneOffset` | `DrivMan.LaneOffset` | m | Lateral offset from center line of vehicle’s current lane for IPGDriver, that is provided by the user |
| `DM.Lap.No` | - | - | Lap number (racing mode) (integer) |
| `DM.Lap.Time` | - | s | Lap time (racing mode) |
| `DM.Lat.Attrib` | - | - | Integer attribute for the current lateral Step |
| `DM.Lat.StepDist` | `DrivMan.ActStepLat.Dist` | m | Lateral Step distance |
| `DM.Lat.ManIdx` | `DrivMan.ActManLat.No` | - | Current lateral Maneuver index (integer). >=0: Number of user defined maneuver, -1: Start maneuver active, -11: internal Default Controller, -12: Maneuver Control deactivated |
| `DM.Lat.StepIdx` | `DrivMan.ActStepLat.No` | - | Current lateral Step index (integer) |
| `DM.Lat.StepTime` | `DrivMan.ActStepLat.Time` | s | Lateral Step time |
| `DM.Lights.FogFront` | `DrivMan.Lights.FogFront` | - | Front fog light on (boolean) |
| `DM.Lights.FogRear` | `DrivMan.Lights.FogRear` | - | Rear fog light on (boolean) |
| `DM.Lights.Hazard` | `DrivMan.Lights.Hazard` | - | Hazard warning light on (boolean) |
| `DM.Lights.HighBeam` | `DrivMan.Lights.HighBeam` | - | High beam: 0=Off; 1=On; 2=Automatic |
| `DM.Lights.Indicator` | `DrivMan.Lights.Indicator` | - | Turn indicator: -1=Right, 0=Off, 1=Left |
| `DM.Lights.MainLight` | `DrivMan.Lights.MainLight` | - | Main light switch: 0=Off, 1=Parking light, 2=Low beam, 3=Automatic |
| `DM.Long.Attrib` | - | - | Integer attribute for the current longitudinal Step |
| `DM.Long.StepDist` | `DrivMan.ActStepLong.Dist` | m | Longitudinal Step distance |
| `DM.Long.ManIdx` | `DrivMan.ActManLong.No` | - | Current longitudinal Maneuver index (integer) |
| `DM.Long.StepIdx` | `DrivMan.ActStepLong.No` | - | Current longitudinal Step index (integer) |
| `DM.Long.StepTime` | `DrivMan.ActStepLong.Time` | s | Longitudinal Step time |
| `DM.Man.<i>.ExecCount` | - | - | Execution count of maneuver with index i |
| `DM.Man.<i>.State` | - | - | State of maneuver with index i. 0: Initial, 1: Standby, 2: Running, 3: Complete, 4: Final |
| `DM.ManCombined` | `DrivMan.ManCombined` | - | 1: Current Maneuver has combined steps. 0: else |
| `DM.ManNo` | `DrivMan.ActualMan.No` | - | Mini maneuver number (integer). Warning: deprecated since CarMaker 12.0 |
| `DM.OperationState_trg` | `DrivMan.OperationState_trg` | - | Target operation state for the vehicle operator (integer): 0: Absent, 1: Power off, 2: Power accessory, 3: Power on, 4: Driving |
| `DM.OperatorActive` | `DrivMan.OperatorActive` | - | Vehicle operator active (boolean) |
| `DM.sDelta` | - | m | Deviations between the target position of the Follow trajectory maneuver step and the actual position |
| `DM.SelectorCtrl` | `DrivMan.SelectorCtrl` | - | Automatic gear selector position (integer): -9=P, -1=R, 0=N, 1=D, 2=M, 3=S |
| `DM.DigitalSelectorCtrl.0` | `DrivMan.DigitalSelectorCtrl[0]` | - | Generic signals that create a square wave signal, that can be used to model a digital selector control joystick |
| `DM.Shifting` | `DrivMan.Shifting` | - | Gear shift in progress (boolean) |
| `DM.SpeedLimit` | `DrivMan.SpeedLimit` | m/s | Current speed limit set by road marker |
| `DM.SpeedOffset` | `DrivMan.SpeedOffset` | m/s | Longitudinal speed offset for IPGDriver |
| `DM.SST` | `DrivMan.SST` | - | Powertrain start-stop button (boolean): 0=off, 1=on |
| `DM.Steer.Ang` | `DrivMan.Steering.Ang` | rad | Steering angle at steering wheel |
| `DM.Steer.AngAcc` | `DrivMan.Steering.AngAcc` | rad/s2 | Steering angle acceleration at steering wheel |
| `DM.Steer.AngVel` | `DrivMan.Steering.AngVel` | rad/s | Steering angle velocity at steering wheel |
| `DM.SteerBy` | `DrivMan.ActualMan.SteerBy` | - | Steering mode (integer): 1=by angle, 2=by torque |
| `DM.Steer.SinusFreq` | - | Hz | Steering angle frequency for sine maneuver |
| `DM.Steer.Trq` | `DrivMan.Steering.Trq` | Nm | Steering torque at steering wheel |
| `DM.StopDist` | `DrivMan.StopDist` | m | Distance to the next stop sign. -1=no stop sign ahead |
| `DM.StopTime` | `DrivMan.StopTime` | s | Remaining time standing at current stop sign. -1=no stop sign ahead |
| `DM.Trf_Consider_trg` | - | - | Target state for the consideration of traffic objects by IPGDriver (integer) |
| `DM.Trf_Overtake_trg` | - | - | Target state for the overtaking of traffic objects by IPGDriver (integer) |
| `DM.TriggerPoint.Dist` | - | m | Trigger point distance |
| `DM.TriggerPoint.Id` | - | - | Trigger point Id (integer) |
| `DM.TriggerPoint.Time` | - | s | Time measured at trigger point |
| `DM.UserSignal_<i>` | `DrivMan.UserSignal[]` | - | User-defined signal `<i>` from vehicle operator to powertrain control |
| `DM.vdelta.Trgt` | - | m/s | Difference between current velocity and target velocity |
| `DM.v.Trgt` | - | m/s | Target velocity used for Speed Control, Speed Profile, etc. |
| `DM.v.Trgt_LimitLo` | - | m/s | Lower target velocity limit (used for Speed Profile) |
| `DM.v.Trgt_LimitHi` | - | m/s | Upper target velocity limit (used for Speed Profile) |
| `DM.Route.ObjId` | `DrivMan.Route.ObjId` | - | Object ID of currently active route the IPGDriver follows |

## 26.4 Driver
| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Driver.Adapt.Phase` | - | - | Current learning phase during the basic learning procedure (integer) |
| `Driver.Brake` | - | - | Brake/decelerator activity, relative pedal force (0..1) |
| `Driver.Brake_UDrvIn` | - | - | Brake/decelerator activity from user driver (float, 0..1) |
| `Driver.BrakePark` | - | - | Park brake activity (0..1) |
| `Driver.BrakePark_UDrvIn` | - | - | Park brake activity from user driver (float, 0..1) |
| `Driver.Clutch` | - | - | Clutch activity (0..1) |
| `Driver.Clutch_UDrvIn` | - | - | Clutch activity from user driver (float, 0..1) |
| `Driver.Gas` | - | - | Gas/throttle/accelerator activity (0..1) |
| `Driver.Gas_UDrvIn` | - | - | Gas/throttle/accelerator activity from user driver (float, 0..1) |
| `Driver.GearNo` | - | - | Gear number set by driver (integer) |
| `Driver.GearNo_UDrvIn` | - | - | Gear number set by user driver (integer) |
| `Driver.GearNoTrgt` | - | - | Target gear number set at the beginning of the shifting procedure (integer) |
| `Driver.Lat.dy` | - | m | Lateral deviation from the desired static course |
| `Driver.Lat.passive` | - | - | Passive flag of lateral controller (boolean) |
| `Driver.Long.dv` | - | m/s | Speed deviation from the desired static velocity |
| `Driver.Long.passive` | - | - | Passive flag of longitudinal controller (boolean) |
| `Driver.ReCon.Accel` | - | m/s2 | Max. admitted acceleration for speeding up the vehicle while driving backwards |
| `Driver.ReCon.ADAS_LD_Coef` | - | - | ADAS Interface: -1=max. brake, 0=neutral, +1=max. throttle |
| `Driver.ReCon.ADAS_LD_T` | - | s | ADAS Interface: Time delay of pedal actuation |
| `Driver.ReCon.AddDrivOrder_active` | - | - | Activates IPGDrv_AddDrivOrder for additional, user-defined driver commands |
| `Driver.ReCon.Decel` | - | m/s2 | Max. admitted deceleration e.g. for stopping the vehicle |
| `Driver.ReCon.DriveChar.CF_axy` | - | - | Correction factor for axmin, axmax, aymax |
| `Driver.ReCon.DriveChar.CF_GGExp` | - | - | Correction factor for GG-Exponent |
| `Driver.ReCon.DriveChar.iChange` | - | - | Change flag; no continuous change possible (boolean) |
| `Driver.ReCon.DriveMode` | - | - | Driving mode (0..6) |
| `Driver.ReCon.Speed` | - | km/h | Target speed for the selected driving mode |
| `Driver.ReCon.StopDist` | - | m | Distance for stopping (e.g. at traffic sign). -1=no stop requested |
| `Driver.ReCon.StopTask` | - | - | Driver stop task (0..5) |
| `Driver.ReCon.StopTime` | - | s | Time to stop (e.g. at a traffic sign). -1=no stop requested |
| `Driver.ReCon.Task` | - | - | Driver’s current task for longitudinal dynamics (0..32) |
| `Driver.ReCon.Task_lat` | - | - | Driver’s current task for lateral dynamics (-18..16) |
| `Driver.ReCon.Trf_Consider` | - | - | Flag: Consider traffic (boolean) |
| `Driver.ReCon.Trf_<kind>.dDist` | - | m | Distance to target traffic object |
| `Driver.ReCon.Trf_<kind>.dSpeed` | - | m/s | Relative speed of target traffic object |
| `Driver.ReCon.Trf_<kind>.ObjId` | - | - | Identification number of target object Id. -1 stands for no detection |
| `Driver.ReCon.Trf_<kind>.State` | - | - | State of the current situation (-9..20) |
| `Driver.ReCon.Trf_<kind>.Targ_Dtct` | - | - | Flag: Target traffic object is detected by driver (boolean) |
| `Driver.ReCon.Trf_Overtake` | - | - | Flag: Overtake traffic objects (boolean) |
| `Driver.SelectorCtrl` | - | - | Automatic gear selector position (integer) |
| `Driver.SetGearNo` | - | - | Change gear number to the desired gear (integer) |
| `Driver.Shifting` | - | - | Driver is shifting (boolean) |
| `Driver.Steer.Ang` | - | rad | Steering angle at steering wheel |
| `Driver.Steer.AngAcc` | - | rad/s2 | Steering angle acceleration at steering wheel |
| `Driver.Steer.AngVel` | - | rad/s | Steering angle velocity at steering wheel |
| `Driver.Steer.Trq` | - | Nm | Steering torque at steering wheel |
| `Driver.UDrv.Active` | - | - | Flag: User driver is activated (boolean) |
| `Driver.WaitFlag` | - | - | Flag: Wait to start (boolean) |

## 26.5 Vehicle
| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Vhcl.Trq_DL2Bdy1` | `Vehicle.Trq_DL2Bdy1` | Nm | Drive torque supported by vehicle body Fr1A (vector) |
| `Vhcl.Trq_DL2Bdy1B` | `Vehicle.Trq_DL2Bdy1B` | Nm | Drive torque supported by vehicle body Fr1B (vector) |
| `Vhcl.Trq_DL2BdyEng` | `Vehicle.Trq_DL2BdyEng` | Nm | Drive torque supported by vehicle engine body (vector) |
| `Vhcl.AeroMarkerPos` | `Vehicle.AeroMarkerPos` | m | Aero marker position in global frame (Fr0) (vector) |
| `Vhcl.Distance` | `Vehicle.Distance` | m | Distance the vehicle (center of mass) has travelled since the start of simulation |
| `Vhcl.Engine.rotv` | `Vehicle.Engine_rotv` | rad/s | Engine rotation speed |
| `Vhcl.Fr1B.rx/ry` | `Vehicle.Fr1B_r_xy` | rad | Rotation angles of flexible vehicle body with rotation order XY |
| `Vhcl.Fr1.x/y/z` | `Vehicle.Fr1A.t_0` | m | Position of vehicle frame origin (Fr1) in global frame (Fr0) |
| `Vhcl.GearNo` | `Vehicle.GearNo` | - | Current gear number (integer) |
| `Vhcl.Hitch.x/y/z` | `Vehicle.Hitch.t_0` | m | Hitch position in global frame (Fr0) |
| `Vhcl.Ignition` | `Vehicle.Ignition` | - | Vehicle ignition (boolean) |
| `Vhcl.OperationError` | `Vehicle.OperationError` | - | Current vehicle operation error from powertrain control (integer) |
| `Vhcl.OperationState` | `Vehicle.OperationState` | - | Current vehicle operation state from powertrain control (integer) |
| `Vhcl.Pitch` | `Vehicle.Pitch` | rad | Vehicle pitch angle |
| `Vhcl.PitchAcc` | `Vehicle.PitchAcc` | rad/s2 | Pitch rotation acceleration |
| `Vhcl.PitchVel` | `Vehicle.PitchVel` | rad/s | Pitch rotation speed |
| `Vhcl.PoI.ax/ay/az_1` | `Vehicle.PoI_Acc_1` | m/s2 | Acceleration vector for PoI in vehicle frame (Fr1) |
| `Vhcl.PoI.ax/ay/az` | `Vehicle.PoI_Acc` | m/s2 | Acceleration vector for PoI in global frame (Fr0) |
| `Vhcl.PoI.GCS.Elev/Long/Lat` | `Vehicle.PoI_GCS` | m/rad | Global position for PoI, expressed in GCS coordinates |
| `Vhcl.PoI.vx/vy/vz_1` | `Vehicle.PoI_Vel_1` | m/s | Velocity vector for PoI in vehicle frame (Fr1) |
| `Vhcl.PoI.vx/vy/vz` | `Vehicle.PoI_Vel` | m/s | Velocity vector for PoI in global frame (Fr0) |
| `Vhcl.PoI.x/y/z` | `Vehicle.PoI_Pos` | m | Position for PoI in global frame (Fr0) |
| `Vhcl.<pos>.Fx/Fy/Fz` | `<pre>.Fx/Fy/Fz` | N | Longitudinal, lateral and vertical ground reaction force at wheel/road contact point |
| `Vhcl.<pos>.LongSlip` | `<pre>.LongSlip` | - | Longitudinal slip at wheel |
| `Vhcl.<pos>.rot` | `<pre>.rot` | rad | Wheel rotation angle |
| `Vhcl.<pos>.rotv` | `<pre>.rotv` | rad/s | Wheel rotation speed |
| `Vhcl.<pos>.rx/ry/rz` | `<pre>.r_zxy` | rad | Rotation angles of carrier at mounted position in rotation order ZXY |
| `Vhcl.<pos>.SideSlip` | `<pre>.SideSlip` | rad | Sideslip angle at wheel |
| `Vhcl.<pos>.Trq_B2WC` | `<pre>.Trq_B2WC` | Nm | Supported brake torque at wheel carrier |
| `Vhcl.<pos>.Trq_Brake` | `<pre>.Trq_Brake` | Nm | Total brake torque at wheel |
| `Vhcl.<pos>.Trq_BrakeReg_trg` | `<pre>.Trq_BrakeReg_trg` | Nm | Target regenerative brake torque at wheel |
| `Vhcl.<pos>.Trq_DL2WC` | `<pre>.Trq_DL2WC` | Nm | Supported driving torque at wheel carrier |
| `Vhcl.<pos>.Trq_Drive` | `<pre>.Trq_Drive` | Nm | Total driving torque |
| `Vhcl.<pos>.Trq_T2W` | `<pre>.Trq_T2W` | Nm | Tire torque around wheel spin axle of wheel |
| `Vhcl.<pos>.Trq_WhlBearing` | `<pre>.Trq_WhlBearing` | Nm | Wheel bearing friction torque around wheel spin axle |
| `Vhcl.<pos>.tx/ty/tz` | `<pre>.t` | m | Translation of carrier at mounted position |
| `Vhcl.<pos>.vBelt` | `<pre>.vBelt` | m/s | Wheel velocity (based on wheel rotation speed and effective rolling tire radius) |
| `Vhcl.Roll` | `Vehicle.Roll` | rad | Roll angle of the vehicle |
| `Vhcl.RollAcc` | `Vehicle.RollAcc` | rad/s2 | Roll acceleration of the vehicle |
| `Vhcl.RollVel` | `Vehicle.RollVel` | rad/s | Roll velocity of the vehicle |
| `Vhcl.Road.JuncObjId` | `Vehicle.Road.JuncObjId` | - | Actual (last) road junction object Id |
| `Vhcl.Road.nextJuncObjId` | `Vehicle.Road.nextJuncObjId` | - | Next road junction object Id |
| `Vhcl.Road.LinkObjId` | `Vehicle.Road.LinkObjId` | - | Actual road link object Id |
| `Vhcl.Road.onJunction` | `Vehicle.Road.onJunction` | - | Flag if the vehicle is on junction? |
| `Vhcl.Road.s2lastJunc` | `Vehicle.Road.s2lastJunc` | m | Road distance to last junction |
| `Vhcl.Road.s2nextJunc` | `Vehicle.Road.s2nextJunc` | m | Road distance to next junction |
| `Vhcl.tRoad` | `Vehicle.tRoad` | m | Lateral distance to route centerline |
| `Vhcl.sRoad` | `Vehicle.sRoad` | m | Vehicle route / path coordinate |
| `Vhcl.Steer.Acc` | `Vehicle.Steering.AngAcc` | rad/s2 | Steering acceleration at steering wheel |
| `Vhcl.Steer.Ang` | `Vehicle.Steering.Ang` | rad | Steering angle at steering wheel |
| `Vhcl.Steer.Trq` | `Vehicle.Steering.Trq` | Nm | Steering torque at steering wheel |
| `Vhcl.Steer.Vel` | `Vehicle.Steering.AngVel` | rad/s | Steering velocity at steering wheel |
| `Vhcl.v` | `Vehicle.v` | m/s | Vehicle velocity |
| `Vhcl.Wind.vx/vy/vz` | `Vehicle.Wind_vel_0` | m/s | Wind velocity vector |
| `Vhcl.Yaw` | `Vehicle.Yaw` | rad | Vehicle yaw angle |
| `Vhcl.YawAcc` | `Vehicle.YawAcc` | rad/s2 | Vehicle yaw acceleration |
| `Vhcl.YawRate` | `Vehicle.YawRate` | rad/s | Vehicle yaw velocity |

## 26.6 Vehicle Control

### 26.6.1 General
| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `VC.Brake` | `VehicleControl.Brake` | - | Brake/decelerator activity (0..1) |
| `VC.BrakePark` | `VehicleControl.BrakePark` | - | Park brake activity (0..1) |
| `VC.Clutch` | `VehicleControl.Clutch` | - | Clutch activity (0..1) |
| `VC.Gas` | `VehicleControl.Gas` | - | Gas/throttle/accelerator activity (0..1) |
| `VC.GearNo` | `VehicleControl.GearNo` | - | Target gear number (integer) |
| `VC.Key` | `VehicleControl.Key` | - | Vehicle key position (integer) |
| `VC.Lights.bm` | `VehicleControl.Lights.bm` | - | For internal use only |
| `VC.Lights.Brake` | `VehicleControl.Lights.Brake` | - | Brake light on (boolean) |
| `VC.Lights.Daytime` | `VehicleControl.Lights.Daytime` | - | Daytime running light on (boolean) |
| `VC.Lights.FogFrontL/R` | `VehicleControl.Lights.FogFrontL/R` | - | Front fog left/right light on (boolean) |
| `VC.Lights.FogRear` | `VehicleControl.Lights.FogRear` | - | Rear fog light on (boolean) |
| `VC.Lights.HighBeam` | `VehicleControl.Lights.HighBeam` | - | High beam/full headlight on (boolean) |
| `VC.Lights.IndL/R` | `VehicleControl.Lights.IndL/R` | - | Indicator left/right (integer) |
| `VC.Lights.LowBeam` | `VehicleControl.Lights.LowBeam` | - | Low beam/dipped headlight on (boolean) |
| `VC.Lights.ParkL/R` | `VehicleControl.Lights.ParkL/R` | - | Parking left/right light on (boolean) |
| `VC.Lights.Reverse` | `VehicleControl.Lights.Reverse` | - | Reversing light on (boolean) |
| `VC.SelectorCtrl` | `VehicleControl.SelectorCtrl` | - | Automatic gear selector position (integer) |
| `VC.SST` | `VehicleControl.SST` | - | Powertrain start-stop button (boolean) |
| `VC.Steer.Ang` | `VehicleControl.Steering.Ang` | rad | Steering angle at steering wheel |
| `VC.Steer.AngAcc` | `VehicleControl.Steering.AngAcc` | rad/s2 | Steering acceleration at steering wheel |
| `VC.Steer.AngVel` | `VehicleControl.Steering.AngVel` | rad/s | Steering velocity at steering wheel |
| `VC.Steer.Trq` | `VehicleControl.Steering.Trq` | Nm | Steering torque at steering wheel |
| `VC.UserSignal_<i>` | `VehicleControl.UserSignal[]` | - | User defined signal `<i>` from vehicle operator to powertrain control |

### 26.6.2 ACC-Controller and AccelCtrl
| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `AccelCtrl.DesiredAx` | `AccelCtrl.DesrAx` | m/s2 | Desired longitudinal acceleration for the acceleration controller AccelCtrl |
| `AccelCtrl.ACC.IsActive` | `AccelCtrl.ACC_ECU.IsActive` | - | Flag if the ACC controller is activated |
| `AccelCtrl.ACC.DesiredAx` | `AccelCtrl.ACC_ECU.DesrAx` | m/s2 | Desired longitudinal acceleration of ACC controller |
| `AccelCtrl.ACC.DesiredDist` | `AccelCtrl.ACC_ECU.DesrDist` | m | Desired distance to the target vehicle |
| `AccelCtrl.ACC.DesiredSpd` | `AccelCtrl.ACC_ECU.DesrSpd` | m/s | Desired longitudinal velocity of ACC controller |
| `AccelCtrl.ACC.DesiredTGap` | `AccelCtrl.ACC_ECU.DesrTGap` | s | Desired time distance to the target vehicle |
| `AccelCtrl.ACC.Time2Collision` | `AccelCtrl.ACC_ECU.Time2Collision` | s | Time to collision with the target vehicle |

### 26.6.3 Generic Longitudinal Control
| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `LongCtrl.AEB.SwitchedOn` | - | - | Flag if AEB system is switched on |
| `LongCtrl.AEB.IsActive` | - | - | Flag if AEB system is active (=braking) |
| `LongCtrl.AEB.Target.ObjId` | - | - | Identification number of relevant target global object |
| `LongCtrl.AEB.Target.Vel` | - | m/s | Longitudinal velocity of relevant target object |
| `LongCtrl.AEB.Target.Decel` | - | m/s2 | Longitudinal deceleration of relevant target object |
| `LongCtrl.AEB.dDist` | - | m | Relative distance to relevant target object |
| `LongCtrl.AEB.dVel` | - | m/s | Relative velocity to relevant target object |
| `LongCtrl.AEB.dDecel` | - | m/s2 | Relative deceleration to relevant target object |
| `LongCtrl.AEB.Decel_req` | - | m/s2 | Required deceleration to brake to equal velocity of the target object |
| `LongCtrl.AEB.Decel_trg` | - | m/s2 | Target deceleration by AEB system for the acceleration controller |
| `LongCtrl.AEB.Time2Collision` | - | s | Time to collision with the target vehicle |
| `LongCtrl.AEB.Time2Brake` | - | s | Time threshold to brake to equal velocity of the target object |
| `LongCtrl.FCW.SwitchedOn` | - | - | Flag if FCW system is switched on |
| `LongCtrl.FCW.WarnLevel` | - | - | Warning level of FCW system (0..2) |

### 26.6.4 Generic Lateral Control
| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `LatCtrl.LKAS.SwitchedOn` | - | - | Flag if LKAS system is switched on |
| `LatCtrl.LKAS.IsActive` | - | - | Flag if LKAS system is active (steering assist torque) |
| `LatCtrl.LKAS.UsePrioLines` | - | - | Flag if priority (=yellow) lines are used for lane identification |
| `LatCtrl.LKAS.AssistTrq` | - | Nm | Assist steering torque calculated by LKAS system |
| `LatCtrl.LKAS.AssistTrq_raw` | - | Nm | Raw (unfiltered) assist steering torque |
| `LatCtrl.LKAS.CurveXY_trg` | - | 1/m | Target path curvature on xy-plane |
| `LatCtrl.LDW.SwitchedOn` | - | - | Flag if LDW system is switched on |
| `LatCtrl.LDW.IsReady` | - | - | Flag if LDW system is ready |
| `LatCtrl.LDW.IsActive` | - | - | Flag if LDW system is active (warning on) |
| `LatCtrl.LineDetectMode` | - | - | Specifies the line detection mode: 0=with Road Sensor, 1=with Line Sensor |
| `LatCtrl.DistToLeft` | - | m | Distance to left detected line of the identified lane |
| `LatCtrl.DistToRight` | - | m | Distance to right detected line of the identified lane |
| `LatCtrl.DevDist` | - | m | Deviation distance to path (middle of the lane) |
| `LatCtrl.Lines.ValidPairExists` | - | - | Flag if a valid pair of priority or standard lines exists |
| `LatCtrl.Lines.<LineId>.exists` | - | - | Flag if priority/standard line (<LineId>=PrioL, PrioR, StdL, StdR) exists |# User Accessible Quantities: Car

## 26.7 Car

### 26.7.1 Car Convenience Quantities

The following frequently needed quantities are aliases for some of the `Car.Con*` quantities. The systematic naming convention for other User Accessible Quantities was dropped in favor of ease of use and faster access.

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.alHori` | `Car.ConBdy1.alHori` | m/s² | Centripetal acceleration (in horizontal plane). `Car.alHori` is perpendicular to `Car.v` and to Z-axis (ISO 8855:2011, 5.1.15) |
| `Car.atHori` | `Car.ConBdy1.atHori` | m/s² | Tangential acceleration (in horizontal plane). `Car.atHori` is parallel to `Car.v` and perpendicular to Z-axis (ISO 8855:2011, 5.1.14) |
| `Car.ax/y/z` | `Car.ConBdy1.a_1[0/1/2]` | m/s² | Translational acceleration of vehicle connected body without considering gravity in vehicle frame Fr1 |
| `Car.tx/y/z` | `Car.ConBdy1.t_0[0/1/2]` | m | Translational position of vehicles connected body in global frame Fr0 |
| `Car.v` | `Car.ConBdy1.v` | m/s | Absolute velocity of vehicle connected body |
| `Car.vx/y/z` | `Car.ConBdy1.v_1[0/1/2]` | m/s | Translational velocity of vehicle connected body in vehicle frame Fr1 |
| `Car.vHori` | `Car.vx² + Car.vy²` | m/s | Horizontal vehicle velocity (ISO 8855:2011, 5.1.5) |

### 26.7.2 Car Suspension and Aerodynamics

#### Template Variable Definitions

- `<pos>` := FL, FR, RL, RR (wheel positions)
- `<part>` := Buf, Damp, Spring, Stabi (suspension component types)
- `<preSC>` := `Car.SuspControl<j>` where `<j>` = 0, 1, 2, 3, 4 (control unit number)
- `<preParaFric>` := `Car.Parasitic.Friction`; `<preParaStiff>` := `Car.Parasitic.Stiffness`
- `<i>` := 0, 1, 2 (generalized coordinates: q0=wheel compression, q1=opposite wheel compression, q2=steer influence)
- Twin := used by the quantities for a twin wheel (describes the inner tire)
- `<preLane>` := `Car.Road.Lane`; `<preRS>` := `Car.FARoadSensor`
- `[i]` := 0, 1, 2, 3, 4, 5, 6, 7 (Applicable in C-Code, numbers represent FL, FR, RL, RR, FL2, FR2, RL2, RR2 respectively)

#### Aerodynamic Forces

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Aero.Frc_1.x/y/z` | `car Aero Frc_1 x/y/z` | N | Aerodynamic forces to the vehicle in vehicle frame Fr1 |
| `Car.Aero.tau_1` | `car Aero tau_1` | rad | Angle of wind approach direction in vehicle frame Fr1 |
| `Car.Aero.tau2_1` | `-` | rad | Angle of wind direction in vehicle frame (Fr1) shifted by 2π: `Car.Aero.tau_1 + π` |
| `Car.Aero.PoA_1.x/y/z` | `car Aero PoA_1 x/y/z` | m | Attack point for the aero forces in vehicle frame Fr1 |
| `Car.Aero.Trq_1.x/y/z` | `car Aero Trq_1 x/y/z` | Nm | Aerodynamic torques to vehicle at reference point in vehicle frame Fr1 |
| `Car.Aero.vres_1.x/y/z` | `car Aero ApproachVel_1 x/y/z` | m/s | Relative wind velocity in vehicle frame Fr1 |

#### Buffer Forces

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Buffer<pos>.Frc` | `<pos> BufferForce` | N | Buffer force internal |
| `Car.Buffer<pos>.Frc_ext` | `FBuf_ext <pos>` | N | Buffer force external |
| `Car.Buffer<pos>.Frc_tot` | `-` | N | Buffer force total (section 'Optional. Specifies the number of the optional control output signals the user requires from the control unit. For CM4SL/TM4SL and Simulink Plugin models this value is fixed to 16 per wheel carrier. Default: 16 per wheel carrier') |
| `Car.Buffer<pos>.Frc_tot.q<i>` | `-` | N | Buffer force due to the generalized coordinate q<i> |
| `Car.Buffer<pos>.l` | `lBuf <pos>` | m | Buffer length total |
| `Car.Buffer<pos>.l_com` | `-` | m | Buffer length by compliance |
| `Car.Buffer<pos>.l_ext` | `-` | m | Buffer length extra, offset |
| `Car.Buffer<pos>.l_kin` | `-` | m | Buffer length by kinematics |
| `Car.Buffer<pos>.v` | `vBuf <pos>` | m/s | Buffer compression/extension velocity in vehicle frame Fr1 |

#### Camber Angle

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Camber<pos>` | `Car.Tire[i].Camber` | rad | Camber angle (ISO 8855:2011, 7.1.17). Angle between z-axis of the vehicle and wheel plane. Positive if the top of the wheel is inclined towards the outside of the vehicle. (Please note the difference between camber angle and inclination angle.) |

#### Control Body Motion

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Con.alHori` | `Car.ConBdy1.alHori` | m/s² | Centripetal acceleration (in horizontal plane). `Car.alHori` is perpendicular to `Car.v` and to Z-axis (ISO 8855:2011, 5.1.15) |
| `Car.ConA.Pitch_X` | `-` | rad | Pitch angle of the vehicle of body A in frame FrX |
| `Car.ConA.Roll_X` | `-` | rad | Roll angle of the vehicle of body A in frame FrX |
| `Car.Con.atHori` | `Car.ConBdy1.atHori` | m/s² | Tangential acceleration (in horizontal plane). `Car.atHori` is parallel to `Car.v` and perpendicular to y-axis (ISO 8855:2011, 5.1.14) |
| `Car.Con.ax_1/y_1/z_1` | `Car.ConBdy1.a_1[0/1/2]` | m/s² | Translational acceleration of vehicle connected body without considering gravity in vehicle frame Fr1 |
| `Car.Con.ax/y/z` | `Car.ConBdy1.a_0[0/1/2]` | m/s² | Translational acceleration of vehicle connected body without considering gravity in global frame Fr0 |
| `Car.ConB.Pitch_X` | `-` | rad | Pitch angle of the vehicle of body B in frame FrX |
| `Car.ConB.Roll_X` | `-` | rad | Roll angle of the vehicle of body B in frame FrX |
| `Car.Con.tx/y/z` | `Car.ConBdy1.t_0[0/1/2]` | m | Translational position of vehicle connected body in global frame Fr0 |
| `Car.Con.v` | `Car.ConBdy1.v` | m/s | Velocity of vehicle connected body |
| `Car.Con.vHori` | `Car.ConBdy1.vHori` | m/s | Horizontal vehicle velocity (ISO 8855:2011, 5.1.5) |
| `Car.Con.vx_1/y_1/z_1` | `Car.ConBdy1.v_1[0/1/2]` | m/s | Translational velocity of vehicle connected body in vehicle frame Fr1 |

### 26.7.3 Wheel Carrier (Suspension Points)

#### Acceleration and Position

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.C<pos>.C.a_0.x/y/z` | `Car.Susp[i].WC_a_0[0/1/2]` | m/s² | Acceleration of the carrier center point in global frame Fr0 |
| `Car.C<pos>.C.t_0.x/y/z` | `-` | m | Translation of carrier center point in global frame Fr0 |
| `Car.C<pos>.C.v_0.x/y/z` | `-` | m/s | Velocity of the carrier center point in global frame Fr0 |

#### Axle and Steering

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.C<pos>.AxleFrc` | `-` | N | Total generalized axle force due to suspension force elements projected on vehicle z-axis in vehicle frame Fr1 |
| `Car.C<pos>.CastorAng` | `-` | rad | Caster angle at ground (ISO 8855:2011, 7.2.2) |
| `Car.C<pos>.CastorOffset` | `-` | m | Caster offset at ground (ISO 8855:2011, 7.2.3) |
| `Car.C<pos>.KingpinAng` | `-` | rad | Kingpin angle at ground (ISO 8855:2011, 7.2.5) |
| `Car.C<pos>.KingpinOffset` | `-` | m | Kingpin offset at ground (ISO 8855:2011, 7.2.6) |

#### Forces on Wheel Carrier

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.C<pos>.Frc2C_1.x/y/z` | `-` | N | Total force to the wheel carrier in vehicle frame Fr1 |
| `Car.C<pos>.Frc2C_2.x/y/z` | `-` | N | Total force to the wheel carrier in carrier frame Fr2 |
| `Car.C<pos>.Frc2CExt_0.x/y/z` | `Susp_Ext.Frc2CExt_0[<pos>][0/1/2]` | N | External forces to the wheel carrier, defined in global frame Fr0 |
| `Car.C<pos>.Frc2CExt_1.x/y/z` | `Susp_Ext.Frc2CExt_1[<pos>][0/1/2]` | N | External forces to the wheel carrier, defined in vehicle frame Fr1 |
| `Car.C<pos>.Frc2CExt_2.x/y/z` | `Susp_Ext.Frc2CExt_2[<pos>][0/1/2]` | N | External forces to the wheel carrier, defined in carrier frame Fr2 |

#### Generalized Forces and Inertia

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.C<pos>.GenFrc0/1/2` | `car Susp <pos> GenFrc2` | N | Generalized force for the generalized coordinate q<i> |
| `Car.C<pos>.GenInert0/1/2` | `car Susp <pos> GenInert2` | kg | Generalized inertia for the generalized coordinate q<i> |

#### Maggi Matrix Elements

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.C<pos>.Maggi0.x/y/z` | `-` | Fr1 | Elements of the "Maggi-Matrix" (describes the relation between the generalized coordinate q0 and the rotation of the wheel carrier) |
| `Car.C<pos>.Maggi1.x/y/z` | `-` | Fr1 | Elements of the "Maggi-Matrix" (describes the relation between the generalized coordinate q1 and the rotation of the wheel carrier) |
| `Car.C<pos>.Maggi2.x/y/z` | `-` | Fr1 | Elements of the "Maggi-Matrix" (describes the relation between the generalized coordinate q2 and the rotation of the wheel carrier) |

#### Tire Contact Point and Velocity

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.C<pos>.P.t_0.x/y/z` / `Car.C<pos>.Twin.P.t_0.x/y/z` | `Car.Tire[i].P_0[0/1/2]` / `Car.TwinTire[i].P_0[0/1/2]` | m | Translation tire contact point in global frame Fr0 |
| `Car.C<pos>.P.v01_W.x/y/z` / `Car.C<pos>.Twin.P.v01_W.x/y/z` | `-` | m/s | Velocity of the tire contact point in tire frame FrW |

#### Generalized Coordinates (Displacement, Velocity, Acceleration)

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.C<pos>.q<i>` | `-` | m | Generalized coordinate q<i> (displacement) |
| `Car.C<pos>.q<i>p` | `-` | m/s | Generalized coordinate q<i> (velocity) |
| `Car.C<pos>.q<i>pp` | `-` | m/s² | Generalized coordinate q<i> (acceleration) |

#### Rotation Angles of Carrier

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.C<pos>.rx/y/z` | `Car.Susp[i].r_zxy[0/1/2]` | rad | Rotation angles of carrier <pos> at wheel center with rotation sequence ZXY |
| `Car.C<pos>.rx_com/y_com/z_com` | `-` | rad | Rotation angles of carrier <pos> by compliance with rotation sequence ZXY |
| `Car.C<pos>.rx_dq<i>/y_dq<i>/z_dq<i>` | `-` | - | Change of the angle at <pos> in direction of the generalized coordinate q<i> |
| `Car.C<pos>.rx_ext/y_ext/z_ext` | `Susp_Ext.Kin_rExt[<pos>][3/4/5]` | rad | Rotation angles of carrier <pos> extra, offset with rotation sequence ZXY (section 13.7 'Additional External Movement') |
| `Car.C<pos>.rx_kin/y_kin/z_kin` | `-` | rad | Rotation angles of carrier <pos> by kinematics with rotation sequence ZXY |
| `Car.C<pos>.rxv/yv/zv` | `-` | rad/s | Rotation speed of the carrier reference point by kinematics with rotation sequence ZXY |
| `Car.C<pos>.rxv_ext/yv_ext/zv_ext` | `Susp_Ext.Kin_vExt[<pos>][3/4/5]` | rad/s | External rotation speed of the carrier reference point with rotation sequence ZXY (section 13.7 'Additional External Movement') |

#### Tire Forces and Torques

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.C<pos>.Tire.FrcC.x/y/z` | `-` | N | Tire force to the wheel carrier in carrier frame Fr2 |
| `Car.C<pos>.Tire.TrqC.x/y/z` | `-` | Nm | Tire torque to the wheel carrier in carrier frame Fr2 |
| `Car.C<pos>.Trq2C_1.x/y/z` | `-` | Nm | Total torque to the wheel carrier in vehicle frame Fr1 |
| `Car.C<pos>.Trq2C_2.x/y/z` | `-` | Nm | Total torque to the wheel carrier in carrier frame Fr2 |
| `Car.C<pos>.Trq2CExt_1.x/y/z` | `Susp_Ext.Trq2CExt_1[<pos>][0/1/2]` | Nm | External torques to the wheel carrier in vehicle frame Fr1 |
| `Car.C<pos>.Trq2CExt_2.x/y/z` | `Susp_Ext.Trq2CExt_2[<pos>][0/1/2]` | Nm | External torques to the wheel carrier in carrier frame Fr2 |
| `Car.C<pos>.Trq_B2C` | `-` | Nm | Brake torque at wheel carrier <pos> after reduction |
| `Car.C<pos>.TrqGyro_2.x/z` | `-` | Nm | Gyroscopic torque at wheel carrier <pos> in carrier frame Fr2 |
| `Car.C<pos>.Trq_T2W` / `Car.C<pos>.Twin.Trq_T2W` | `Car Trq_T2W<pos>` | Nm | Tire torque around wheel spin axis |

#### Translation of Carrier

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.C<pos>.tx/y/z` | `Car.Susp[i].t[0/1/2]` | m | Translation of carrier reference point at <pos> in vehicle frame Fr1 |
| `Car.C<pos>.tx_com/y_com/z_com` | `-` | m | Translation of carrier reference point by compliance in vehicle frame Fr1 |
| `Car.C<pos>.tx_dq<i>/y_dq<i>/z_dq<i>` | `-` | m | Translation of wheel carrier at <pos> in direction of the generalized coordinate q<i> (Example: `Car.CFL.tz_dq0`) |
| `Car.C<pos>.tx_ext/y_ext/z_ext` | `Susp_Ext.Kin_tExt[<pos>][0/1/2]` | m | Translation of carrier reference point extra, offset (section 13.7 'Additional External Movement') |
| `Car.C<pos>.tx_kin/y_kin/z_kin` | `-` | m | Translation of carrier reference point by kinematics in vehicle frame Fr1 |
| `Car.C<pos>.txv/yv/zv` | `-` | m/s | Velocity of the carrier reference point by kinematics in vehicle frame Fr1 |
| `Car.C<pos>.txv_ext/yv_ext/zv_ext` | `Susp_Ext.Kin_vExt[<pos>][0/1/2]` | m/s | Additional external velocity (user-defined) of the carrier reference point (section 13.7 'Additional External Movement') |

### 26.7.4 Damper Component

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Damp<pos>.Frc` | `<pos> DamperForce` | N | Damper force internal |
| `Car.Damp<pos>.Frc_ext` | `FDamp_ext <pos>` | N | Damper force external |
| `Car.Damp<pos>.Frc_tot` | `-` | N | Damper force total (section 'Optional. Specifies the number of the optional control output signals the user requires from the control unit. For CM4SL/TM4SL and Simulink Plugin models this value is fixed to 16 per wheel carrier. Default: 16 per wheel carrier') |
| `Car.Damp<pos>.Frc_tot.q<i>` | `-` | N | Damper force due to the generalized coordinate q<i> |
| `Car.Damp<pos>.l` | `lDamp <pos>` | m | Damper length total |
| `Car.Damp<pos>.l_com` | `-` | m | Damper length by compliance |
| `Car.Damp<pos>.l_ext` | `-` | m | Damper length extra, offset |
| `Car.Damp<pos>.l_kin` | `-` | m | Damper length by kinematics |
| `Car.Damp<pos>.TopMnt.l` | `-` | m | Top mount length |
| `Car.Damp<pos>.TopMnt.v` | `-` | m/s | Top mount compression/extension velocity |
| `Car.Damp<pos>.TopMnt.a` | `-` | m/s² | Top mount compression/extension acceleration (only for Kelvin-Voigt TopMount) |
| `Car.Damp<pos>.TopMnt.Frc_tot` | `-` | N | Top mount force |
| `Car.Damp<pos>.v` | `vDamp <pos>` | m/s | Damper compression/extension velocity in vehicle frame Fr1 |

### 26.7.5 Distance and Frame References

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Distance` | `Car.Distance` | m | Driving distance since Test Run start; calculation: ∫`Car.v dt` |
| `Car.Fr1.ax/y/z` | `Car.Fr1.a_0[0/1/2]` | m/s² | Acceleration of origin Fr1 in global coordinate system |
| `Car.Fr1.rx/y/z` | `Car.Fr1.r_zyx[0/1/2]` | rad | Rotation angles of origin Fr1 in global coordinate system, Cardan angles with rotation sequence ZYX (ISO 8855:2011, 5.2.1, 5.2.2 and 5.2.3) |
| `Car.Fr1.tx/y/z` | `Car.Fr1.t_0[0/1/2]` | m | Position of origin Fr1 in global coordinate system Fr0 |
| `Car.Fr1.vx/y/z` | `Car.Fr1.v_0[0/1/2]` | m/s | Translational velocity of origin Fr1 in global coordinate system Fr0 |

### 26.7.6 Tire Forces and Slip

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Fx<pos>` / `Car.FxTwin<pos>` | `Car.Tire[i].Frc_W[0]` / `Car.TwinTire[i].Frc_W[0]` | N | Longitudinal ground reaction force at wheel/road contact point in tire frame FrW |
| `Car.Fy<pos>` / `Car.FyTwin<pos>` | `Car.Tire[i].Frc_W[1]` / `Car.TwinTire[i].Frc_W[1]` | N | Lateral ground reaction force at wheel/road contact point in tire frame FrW |
| `Car.Fz<pos>` / `Car.FzTwin<pos>` | `Car.Tire[i].Frc_W[2]` / `Car.TwinTire[i].Frc_W[2]` | N | Vertical ground reaction force at wheel/road contact point in tire frame FrW |

#### Generalized Vehicle Body

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Gen.ax_1/y_1/z_1` | `Car.GenBdy1.a_1[0/1/2]` | m/s² | Acceleration of generalized vehicle body in vehicle frame Fr1 without considering gravity |
| `Car.Gen.ax/y/z` | `Car.GenBdy1.a_0[0/1/2]` | m/s² | Acceleration of generalized vehicle body in global frame Fr0 without considering gravity |
| `Car.Gen.tx/y/z` | `Car.GenBdy1.t_0[0/1/2]` | m | Position of generalized vehicle body in global frame Fr0 |
| `Car.Gen.vx_1/y_1/z_1` | `Car.GenBdy1.v_1[0/1/2]` | m/s | Velocity of generalized vehicle body in vehicle frame Fr1 |

### 26.7.7 Hitch and Trailer Interface

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Hitch.Frc2Car.x/y/z` | `Car.Hitch.Frc2Car_0[0/1/2]` | N | Trailer hitch force acting on car in global frame Fr0 |
| `Car.Hitch.Trq2Car.x/y/z` | `Car.Hitch.Trq2Car_0[0/1/2]` | Nm | Trailer hitch torque acting on car in global frame Fr0 |
| `Car.Hitch.tx/y/z` | `Car.Hitch.t_0[0/1/2]` | m | Trailer hitch position (hitch center reference point) in global frame Fr0 |
| `Car.Hitch.vx/y/z` | `Car.Hitch.v_0[0/1/2]` | m/s | Trailer hitch velocity (hitch center reference point) in global frame Fr0 |

### 26.7.8 Inclination and Jack

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.InclinAngle<pos>` / `Car.InclinAngleTwin<pos>` | `Car.Tire[i].InclinAngle` | rad | Wheel inclination angle (ISO 8855:2011, 7.1.16). Angle between z-axis of the wheel axis system and wheel plane. Positive for positive rotation around x-axis of the wheel. |
| `Car.Jack.Fz<pos>` | `-` | N | Externally applied force from jack to vehicle body (component in z-direction) in global frame Fr0 |
| `Car.Jack.tz<pos>` | `Car.Jack[i].tz` | m | Externally applied jack translation along the z-axis in global frame Fr0 |

### 26.7.9 Kinematic Centers

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.KinPitchCenter_L.x_1/y_1/z_1` | `-` | m | Kinematical pitch center on the plane through the left side wheel contact points, expressed in vehicle frame Fr1 (section 13.5.2 'Kinematic characteristic parameters') |
| `Car.KinPitchCenter_L.x/z` | `-` | m | Kinematical pitch center on the plane through the left side wheel contact points, expressed in plane coordinates (section 13.5.2 'Kinematic characteristic parameters') |
| `Car.KinPitchCenter_R.x_1/y_1/z_1` | `-` | m | Kinematical pitch center on the plane through the right side wheel contact points, expressed in vehicle frame Fr1 (section 13.5.2 'Kinematic characteristic parameters') |
| `Car.KinPitchCenter_R.x/z` | `-` | m | Kinematical pitch center on the plane through the right side wheel contact points, expressed in plane coordinates (section 13.5.2 'Kinematic characteristic parameters') |
| `Car.KinRollCenter_F.x_1/y_1/z_1` | `-` | m | Kinematical roll center on the front transverse plane through the wheel contact points, expressed in vehicle frame Fr1 (section 13.5.2 'Kinematic characteristic parameters') |
| `Car.KinRollCenter_F.y/z` | `-` | m | Kinematical roll center on the front transverse plane through the wheel contact points, expressed in plane coordinates (section 13.5.2 'Kinematic characteristic parameters') |
| `Car.KinRollCenter_R.x_1/y_1/z_1` | `-` | m | Kinematical roll center on the rear transverse plane through the wheel contact points, expressed in vehicle frame Fr1 (section 13.5.2 'Kinematic characteristic parameters') |
| `Car.KinRollCenter_R.y/z` | `-` | m | Kinematical roll center on the rear transverse plane through the wheel contact points, expressed in plane coordinates (section 13.5.2 'Kinematic characteristic parameters') |

### 26.7.10 Vehicle Load

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Load.<i>.mass` | `Car.Load[i].mass` | kg | Mass of car load <i> |
| `Car.Load.<i>.tx/y/z` | `Car.Load[i].pos[0/1/2]` | m | Position of car load <i> in vehicle frame Fr1 |

### 26.7.11 Slip and Friction

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.LongSlip<pos>` / `Car.LongSlipTwin<pos>` | `Car.Tire[i].LongSlip` | - | Longitudinal slip. Definition depends on tire model (section 18.1.1 'Tire Model with Contact Point Interface (CPI)') |
| `Car.muRoad<pos>` / `Car.muRoadTwin<pos>` | `Car.Tire[i].muRoad` / `Car.TwinTire[i].muRoad` | - | Road friction coefficient at tire <pos> |
| `<preParaFric><pos>.Frc_tot` | `<pos> ParasiticFrictionForce` | N | Parasitic friction force |
| `<preParaFric><pos>.Frc_tot.q<i>` | `-` | N | Generalized force for the coordinate q<i> due to the parasitic friction force |
| `<preParaStiff><pos>.Frc_tot` | `<pos> ParasiticStiffnessForce` | N | Parasitic stiffness force |
| `<preParaStiff><pos>.Frc_tot.q<i>` | `-` | N | Generalized force for the coordinate q<i> due to the parasitic stiffness force |

### 26.7.12 Vehicle Orientation and Pitch

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Pitch` | `Car.Pitch` | rad | Vehicle pitch angle (ISO 8855:2011, 5.2.2). Positive if front goes down and rear of the car comes up |
| `Car.PitchAcc` | `Car.PitchAcc` | rad/s² | Pitch rotation acceleration |
| `Car.PitchVel` | `Car.PitchVel` | rad/s | Pitch rotation velocity in vehicle frame Fr1 |

### 26.7.13 Road and Sensor Information

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Road.GCS.Long/Lat/Elev` | `<preRS>.P_GCS.Long/Lat/Elev` | rad / rad / m | Global position of the road reference point (in the middle of the front axle) in GCS coordinates: longitude, latitude, elevation |
| `Car.Road.JuncObjId` | `<preRS>.JuncObjId` | - | Actual (last) road junction object Id |
| `Car.Road.nextJuncObjId` | `<preRS>.nextJuncObjId` | - | Next road junction object Id |
| `<preLane>.Act.isRight` / `<preLane>.OnLeft.isRight` / `<preLane>.OnRight.isRight` | `<preRS>.Act.isRight` / `<preRS>.OnLeft.isRight` / `<preRS>.OnRight.isRight` | - | Indicates if the actual lane, at which the road sensor reference point (in the middle of the front axle) is, is on right side along route (same for lanes on left / right side) |
| `<preLane>.Act.LaneId` / `<preLane>.OnLeft.LaneId` / `<preLane>.OnRight.LaneId` | `<preRS>.Act.LaneId` / `<preRS>.OnLeft.LaneId` / `<preRS>.OnRight.LaneId` | - | Indicates the lane Id at which the road sensor reference point (in the middle of the front axle) is, same for lanes on left / right side (-1 means no lane found) |
| `<preLane>.Act.tMidLane` / `<preLane>.OnLeft.tMidLane` / `<preLane>.OnRight.tMidLane` | `<preRS>.Act.tMidLane` / `<preRS>.OnLeft.tMidLane` / `<preRS>.OnRight.tMidLane` | m | Lateral offset of lane mid to the route center line |
| `<preLane>.Act.Type` / `<preLane>.OnLeft.Type` / `<preLane>.OnRight.Type` | `<preRS>.Act.Type` / `<preRS>.OnLeft.Type` / `<preRS>.OnRight.Type` | - | Type of the actual lane: 0=Legally driveable road, 1=Bicycle lane, 2=Lane only for pedestrian, 3=Traffic island, 4=Border lane, 5=Roadside |
| `<preLane>.Act.Width` / `<preLane>.OnLeft.Width` / `<preLane>.OnRight.Width` | `<preRS>.Act.Width` / `<preRS>.OnLeft.Width` / `<preRS>.OnRight.Width` | m | Width of the actual roadway lane and the lanes on left / right side |
| `Car.Road.Lane.nLeft` / `Car.Road.Lane.nRight` | `<preRS>.Lanes.nLanesL` / `<preRS>.Lanes.nLanesR` | - | Number of left, right roadway lanes along route (integer) |
| `Car.Road.LinkObjId` | `<preRS>.LinkObjId` | - | Actual road link object Id |
| `Car.Road.onJunction` | `<preRS>.onJunction` | - | Flag if the vehicle is on junction |
| `Car.Road.Path.DevAng` / `Car.Road.Route.DevAng` | `<preRS>.Path.Deviation.Ang` / `<preRS>.Route.Deviation.Ang` | rad | Deviation angle between vehicle and path / route center line in the road sensor reference point (in the middle of the front axle) (section 'Previewed road point along route reference line') |
| `Car.Road.Path.DevDist` / `Car.Road.Route.DevDist` | `<preRS>.Path.Deviation.Dist` / `<preRS>.Route.Deviation.Dist` | m | Deviation distance between vehicle and path / route center line in the road sensor reference point (in the middle of the front axle) (section 'Previewed road point along route reference line') |
| `Car.Road.Path.LatSlope` / `Car.Road.Route.LatSlope` | `<preRS>.Path.LatSlope` / `<preRS>.Route.LatSlope` | rad | Lateral road slope at road sensor reference point in the middle of the front axle along path / route |
| `Car.Road.Path.LongSlope` / `Car.Road.Route.LongSlope` | `<preRS>.Path.LongSlope` / `<preRS>.Route.LongSlope` | rad | Longitudinal road slope at road sensor reference point (in the middle of the front axle) along path / route |
| `Car.Road.s2lastJunc` / `Car.Road.s2nextJunc` | `<preRS>.s2lastJunc` / `<preRS>.s2nextJunc` | m | Road distance along road reference line (from the middle of the front axle) to last / next junction |
| `Car.Road.sRoad` | `Car.sRoad` | m | Vehicle road coordinate in the road sensor reference point (in the middle of the front axle) along route / path |
| `Car.Road.tx/y/z` | `Car.RoadSensor.P_0[0/1/2]` | m | Position of the road sensor reference point (in the middle of the front axle) in global frame Fr0 |

### 26.7.14 Roll Motion

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Roll` | `Car.Roll` | rad | Roll angle of the vehicle (ISO 8855:2011, 5.2.3). Positive if right side goes down and left side comes up |
| `Car.RollAcc` | `Car.RollAcc` | rad/s² | Roll rotation acceleration |
| `Car.RollKin_F` / `Car.RollKin_R` | `Car.RollKin_F` / `Car.RollKin_R` | rad | Kinematic roll angle (ISO 8855:2011, 5.2.5), angle between front/rear axle and z-axis of vehicle frame. Positive if right side goes down and left side comes up |
| `Car.RollVel` | `Car.RollVel` | rad/s | Roll rotation speed in vehicle frame Fr1 |

### 26.7.15 Sideslip and Simulation State

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.SideSlipAngle` | `Car.ConBdy1.SideSlipAngle` | rad | Sideslip angle (ISO 8855:2011, 5.2.9). Angle between x-axis of the car and direction of `Car.vHori`. Value range: -pi .. +pi. Calculation: arctan(`Car.vy` / `Car.vx`); = 0 if `Car.vx` = `Car.vy` = 0 |
| `Car.SideSlipAngle2` | `Car.ConBdy1.SideSlipAngle2` | rad | Sideslip angle, value range 0 ... 2 pi |
| `Car.SideSlipAngleVel` | `Car.ConBdy1.SideSlipAngleVel` | rad/s | Sideslip angle velocity (ISO 8855:2011, 5.2.9) |
| `Car.SimPhase` | `Car.SimPhase` | - | Car simulation phase |

### 26.7.16 Slip Angle

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.SlipAngle<pos>` / `Car.SlipAngleTwin<pos>` | `Car.Tire[i].SlipAngle` | rad | Slip angle (ISO 8855:2011, 5.2.12). Angle between x-axis of the wheel and the tangent of the trajectory of the center of tire contact. Positive for positive rotation around z-axis. Calculation: arctan(`Car.vyFL` / `Car.vxFL`); = 0 if `Car.vxFL` = `Car.vyFL` = 0 |

### 26.7.17 SlotCar Mode

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.SlotCar.Deviation` | `Car.SlotCar.Deviation` | m | Tolerated deviation along road centerline within SlotCar Mode is disabled |
| `Car.SlotCar.State` | `-` | - | Specifies if SlotCar correction is active (boolean) (section 25.2 'SlotCar Mode') |

### 26.7.18 Spring Component

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Spring<pos>.Frc` | `<pos> SpringForce` | N | Spring force internal |
| `Car.Spring<pos>.Frc_ext` | `FSpring_ext <pos>` | N | Spring force external |
| `Car.Spring<pos>.Frc_tot` | `-` | N | Spring force total (section 'Optional. Specifies the number of the optional control output signals the user requires from the control unit. For CM4SL/TM4SL and Simulink Plugin models this value is fixed to 16 per wheel carrier. Default: 16 per wheel carrier') |
| `Car.Spring<pos>.Frc_tot.q<i>` | `-` | N | Spring force due to the generalized coordinate q<i> |
| `Car.Spring<pos>.l` | `lSpring <pos>` | m | Spring length total |
| `Car.Spring<pos>.l_com` | `-` | m | Spring length by compliance |
| `Car.Spring<pos>.l_ext` | `-` | m | Spring length extra, offset |
| `Car.Spring<pos>.l_kin` | `-` | m | Spring length by kinematics |
| `Car.Spring<pos>.v` | `vSpring <pos>` | m/s | Spring compression/extension velocity in vehicle frame Fr1 |

### 26.7.19 Stabilizer Component

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Stabi<pos>.Frc` | `<pos> StabiForce` | N | Stabilizer force internal |
| `Car.Stabi<pos>.Frc_ext` | `FStabi_ext <pos>` | N | Stabilizer force external |
| `Car.Stabi<pos>.Frc_tot` | `-` | N | Stabilizer force total (section 'Optional. Specifies the number of the optional control output signals the user requires from the control unit. For CM4SL/TM4SL and Simulink Plugin models this value is fixed to 16 per wheel carrier. Default: 16 per wheel carrier') |
| `Car.Stabi<pos>.Frc_tot.q<i>` | `-` | N | Stabilizer force due to the generalized coordinate q<i> |
| `Car.Stabi<pos>.l` | `lStabi <pos>` | m | Stabilizer length total |
| `Car.Stabi<pos>.l_com` | `-` | m | Stabilizer length by compliance |
| `Car.Stabi<pos>.l_ext` | `-` | m | Stabilizer length extra, offset |
| `Car.Stabi<pos>.l_kin` | `-` | m | Stabilizer length by kinematics |
| `Car.Stabi<pos>.v` | `vStabi <pos>` | m/s | Stabilizer compression/extension velocity in vehicle frame Fr1 |

### 26.7.20 Steering

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.SuspF.Ackermann.percentage` | `-` | - | Ackermann percentage (0..1) |
| `Car.SuspF.Ackermann.drz_l/drz_r` | `-` | rad | Correction term for Ackermann steering that is added to parallel steering for left and right wheel |
| `Car.SteerAngle<pos>` | `Car.Susp[i].SteerAngle` | rad | Steer angle (ISO 8855:2011, 7.1.1) |
| `<preSC>.Buffer<pos>.CtrlOut` | `<pos> BufferCtrlOut` | - | Car suspension control unit output signal for buffer component at wheel carrier <pos> (value NOTSET = -99999 means no buffer control signal at <pos>) |
| `<preSC>.BufferCtrlOutOpt.<i>` | `-` | - | Car suspension control unit optional output signal number <i> for buffer component (value NOTSET = -99999 means no optional buffer control output signal <i>, not available for FMU) |
| `<preSC>.BufferCtrlInOpt.<i>` | `-` | - | Car suspension control unit optional input signal number <i> for buffer component (value NOTSET = -99999 means no optional buffer control input signal <i>, not available for FMU) |
| `<preSC>.Damper<pos>.CtrlOut` | `<pos> DamperCtrlOut` | - | Car suspension control unit output signal for damper component at wheel carrier <pos> (value NOTSET = -99999 means no damper control signal at <pos>) |
| `<preSC>.DamperCtrlOutOpt.<i>` | `-` | - | Car suspension control unit optional output signal number <i> for damper component (value NOTSET = -99999 means no optional damper control output signal <i>, not available for FMU) |
| `<preSC>.DamperCtrlInOpt.<i>` | `-` | - | Car suspension control unit optional input signal number <i> for damper component (value NOTSET = -99999 means no optional damper control input signal <i>, not available for FMU) |
| `<preSC>.Spring<pos>.CtrlOut` | `<pos> SpringCtrlOut` | - | Car suspension control unit output signal for spring force component at wheel carrier <pos> (value NOTSET = -99999 means no spring control signal at <pos>) |
| `<preSC>.SpringCtrlOutOpt.<i>` | `-` | - | Car suspension control unit optional output signal number <i> for spring component (value NOTSET = -99999 means no optional spring control output signal <i>, not available for FMU) |
| `<preSC>.SpringCtrlInOpt.<i>` | `-` | - | Car suspension control unit optional input signal number <i> for spring component (value NOTSET = -99999 means no optional spring control input signal <i>, not available for FMU) |
| `<preSC>.Stabi<pos>.CtrlOut` | `<pos> StabiCtrlOut` | - | Car suspension control unit output signal for stabi component at wheel carrier <pos> (value NOTSET = -99999 means no stabi control signal at <pos>) |
| `<preSC>.StabiCtrlOutOpt.<i>` | `-` | - | Car suspension control unit optional output signal number <i> for stabi component (value NOTSET = -99999 means no optional stabi control output signal <i>, not available for FMU) |
| `<preSC>.StabiCtrlInOpt.<i>` | `-` | - | Car suspension control unit optional input signal number <i> for stabi component (value NOTSET = -99999 means no optional stabi control input signal <i>, not available for FMU) |
| `<preSC>.SystemCtrlOutOpt.<i>` | `-` | - | Car suspension control unit optional additional output signal number <i> for force system (value NOTSET = -99999 means no optional force system control output signal <i>, not available for FMU) |
| `<preSC>.SystemCtrlInOpt.<i>` | `-` | - | Car suspension control unit optional additional input signal number <i> for force system (value NOTSET = -99999 means no optional force system control input signal <i>, not available for FMU) |
| `Car.Toe<pos>` / `Car.ToeTwin<pos>` | `Car.Susp[i].Toe` | rad | Toe angle (ISO 8855:2011, 7.1.6). The toe angle is positive if the front section of the wheel is turned toward the vehicle's longitudinal center plane and is negative (toe-out) if the front section is turned away from this plane. |

### 26.7.21 Track Curvature and Radius

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.TrackCurv` | `Car.ConBdy1.TrackCurv` | 1/m | Curvature of trajectory (ISO 8855:2011, 5.3.5) (float). Calculation: `Car.TrackCurv` = 1 / `Car.TrackRadius`; = 0 if `Car.TrackRadius` = ∞; = ∞ if `Car.TrackRadius` = 0 |
| `Car.TrackRadius` | `Car.ConBdy1.TrackRadius` | m | Radius of path/trajectory (ISO 8855:2011, 5.3.3) (float). Distance between a point of the trajectory and the belonging instantaneous center. Calculation: `Car.TrackRadius` = (`Car.vHori`)² / `Car.alHori`; = ∞ if `Car.alHori` = 0 |

### 26.7.22 Tire Torques

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.TrqAlign<pos>` / `Car.TrqAlignTwin<pos>` | `Car.Tire[i].Trq_W[2]` | Nm | Aligning torque (ISO 8855:2011, 10.2.13). Component of the ground reaction moment. Positive for positive direction around z-axis. In tire frame FrW |
| `Car.TrqOvert<pos>` / `Car.TrqOvertTwin<pos>` | `Car.Tire[i].Trq_W[0]` | Nm | Overturning torque in the tire contact point. Positive for positive direction around x-axis. In tire frame FrW |
| `Car.TrqRoll<pos>` / `Car.TrqRollTwin<pos>` | `Car.Tire[i].Trq_W[1]` | Nm | Rolling torque in the tire contact point. Positive for positive direction around y-axis. In tire frame FrW |

### 26.7.23 Turn Slip

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.TurnSlip<pos>` / `Car.TurnSlip Twin<pos>` | `Car.Tire[i].TurnSlip` | 1/m | Turn slip |

### 26.7.24 Virtual Forces and Torques

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Virtual.Frc_0.x/y/z` | `Car.Virtual.Frc_0[0/1/2]` | N | Virtual force, defined in global frame Fr0 |
| `Car.Virtual.Frc_1.x/y/z` | `Car.Virtual.Frc_1[0/1/2]` | N | Virtual force, defined in vehicle frame Fr1 |
| `Car.Virtual.Trq_0.x/y/z` | `Car.Virtual.Trq_0[0/1/2]` | Nm | Virtual torque, defined in global frame Fr0 |
| `Car.Virtual.Trq_1.x/y/z` | `Car.Virtual.Trq_1[0/1/2]` | Nm | Virtual torque, defined in vehicle frame Fr1 |

### 26.7.25 Wheel Velocity and Rotation

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.v<pos>` / `Car.vTwin<pos>` | `Car.Tire[i].v` | m/s | Wheel velocity (based on wheel rotation and effective rolling radius) |
| `Car.vx<pos>` / `Car.vxTwin<pos>` | `Car.Tire[i].P_vel_W[0]` | m/s | Longitudinal velocity of the tire contact point in tire frame FrW |
| `Car.vy<pos>` / `Car.vyTwin<pos>` | `Car.Tire[i].P_vel_W[1]` | m/s | Lateral velocity of the tire contact point in tire frame FrW |
| `Car.vz<pos>` | `Car.Tire[i].P_vel_W[2]` | m/s | Vertical velocity of the tire contact point |
| `Car.WheelSpd_<pos>` / `Car.WheelSpd_Twin<pos>` | `Car.Tire[i].WheelSpd` | rad/s | Wheel rotation speed |
| `Car.WheelTurnSpd_<pos>` | `Car.Tire[i].WheelTurnSpd` | rad/s | Wheel turning (yaw) velocity |
| `Car.W<pos>.Radius` / `Car.W<pos>.Twin.Radius` | `Car.Tire[i].WRadius` | m | Current wheel radius (distance road to wheel center) |
| `Car.W<pos>.rot` | `Car.Tire[i].rot` | rad | Wheel rotation angle. Is used for the visualization in IPGMovie and therefore set to zero at very low speeds. Calculation: `Car.vFL` = `Car.WheelSpd_FL` × `Car.WFL_KinRollRadius` |

### 26.7.26 Yaw Motion

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Yaw` | `Car.Yaw` | rad | Vehicle yaw angle (ISO 8855:2011, 5.2.1). Angle between x-axis of the car and x-axis of earth fixed system. Positive for positive rotation around z-axis. |
| `Car.YawAcc` | `Car.YawAcc` | rad/s² | Vehicle yaw acceleration |
| `Car.YawRate` | `Car.YawRate` | rad/s | Vehicle yaw velocity (ISO 8855:2011, 5.2.19) in vehicle frame Fr1 |
| `Car.YawVel` | `Car.YawRate` | rad/s | Vehicle yaw velocity (ISO 8855:2011, 5.2.19) |

## 26.7.3 CarFlex (Elastic Mounted Engine)

### 26.7.3.1 Flexible Body Dynamics

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.ConA.Pitch_X` | `-` | rad | Pitch angle of Fr1A in frame FrX |
| `Car.ConA.Roll_X` | `-` | rad | Roll angle of Fr1A in frame FrX |
| `Car.ConB.Pitch_X` | `-` | rad | Pitch angle of Fr1B in frame FrX |
| `Car.ConB.Roll_X` | `-` | rad | Roll angle of Fr1B in frame FrX |
| `Car.Fr1B.rax/ray` | `-` | rad/s² | Rotational accelerations of body flexibility joint |
| `Car.Fr1B.rvx/rvy` | `-` | rad/s | Rotational velocity of body flexibility joint |
| `Car.Fr1B.rx/ry` | `-` | rad | Rotation angles of body flexibility joint |
| `Car.Fr1B.Trq_B2A.x/y` | `-` | Nm | Spring-damper torque of body flexibility joint from Fr1B to Fr1A in frame Fr1A |
| `Car.Fr1B.Trq_B2A.x_ext/y_ext` | `-` | Nm | External torque from Fr1B to Fr1A in frame Fr1A |

Note: FrX is a frame defined by the tire road contact points

### 26.7.4 Elastic Mounted Engine

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Car.Eng.ax/y/z` | `Car.FrEng.a[0/1/2]` | m/s² | Translational acceleration of the engine along x/y/z-axis in frame Fr1A |
| `Car.Eng.Frc.<i>.Frc.x/y/z` | `-` | N | Total spring-damper force of the mounting <i> (i=0...3) in direction x/y/z in frame Fr1A |
| `Car.Eng.Frc.<i>.lx/ly/lz` | `-` | m | Spring length of the mounting <i> in x/y/z in frame Fr1A |
| `Car.Eng.Frc.<i>.vx/vy/vz` | `-` | m/s | Damper velocity of the mounting <i> in frame Fr1A |
| `Car.Eng.GenFrc.x/y/z` | `-` | N | Spring-damper force along x/y/z of the joint between engine and body A in frame Fr1A |
| `Car.Eng.GenTrq.x/y` | `-` | Nm | Total spring-damper torque around x- and y-axle in the joint between engine and body A in frame Fr1A |
| `Car.Eng.rax/ray` | `Car.FrEng.ra_xy[0/1]` | rad/s² | Rotational acceleration of the engine around x-axle and y-axle in frame FrEng |
| `Car.Eng.rvx/rvy` | `Car.FrEng.rv_xy[0/1]` | rad/s | Rotational speed of the engine around x-axle and y-axle in frame FrEng |
| `Car.Eng.rx/ry` | `Car.FrEng.r_xy[0/1]` | rad | Rotation of the engine around x-axle and y-axle in frame FrEng |
| `Car.Eng.tx/y/z` | `Car.FrEng.t[0/1/2]` | m | Translation of the engine along x/y/z-axis in frame Fr1A |
| `Car.Eng.vx/y/z` | `Car.FrEng.v[0/1/2]` | m/s | Translational velocity of the engine along x/y/z-axis in frame Fr1A |

Note: FrEng is the frame of the elastic supported vehicle body containing engine

## 26.8 MBS Suspension

### 26.8.1 Bushing Components

Following quantities describe the quantities which are declared for each bushing component:

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<BushingPre>.tx/y/z` | `-` | m | Relative compression along the bushing x/y/z-axis |
| `<BushingPre>.vx/y/z` | `-` | m/s | Relative compression velocity along the bushing x/y/z-axis |
| `<BushingPre>.rx/y/z` | `-` | rad | Relative rotational compression around the bushing x/y/z-axis |
| `<BushingPre>.Frc.x/y/z` | `-` | N | Bushing force along the bushing x/y/z-axis |
| `<BushingPre>.Trq.x/y/z` | `-` | Nm | Bushing torque around the bushing x/y/z-axis |
# User Accessible Quantities: Suspension

## 26.8 Bushing

Following quantities describe the quantities which are declared for each bushing component:

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<BushingPre>.t.x/y/z` | - | m | Relative compression along the bushing x,y,z-axis |
| `<BushingPre>.v.x/y/z` | - | m/s | Relative compression velocity along the bushing x,y,z-axis |
| `<BushingPre>.r.x/y/z` | - | rad | Relative rotational compression around the bushing x,y,z-axis |
| `<BushingPre>.Frc.x/y/z` | - | N | Bushing force along the bushing x,y,z-axis |
| `<BushingPre>.Trq.x/y/z` | - | Nm | Bushing torque around the bushing x,y,z-axis |

## 26.8.2 McPherson Suspension

Template variables:
- `<pre> := McPherson.<pos>`
- `<pos> := SuspF`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.DamperL.t` | - | m | Translation of the left damper relative to the wheel carrier along the thrust damper axis |
| `<pre>.DamperL.v` | - | m/s | Translation of the left damper relative to the wheel carrier along the thrust damper axis |
| `<pre>.DamperL.a` | - | m/s² | Translation of the left damper relative to the wheel carrier along the thrust damper axis |
| `<pre>.DamperR.t` | - | m | Translation of the right damper relative to the wheel carrier along the thrust damper axis |
| `<pre>.DamperR.v` | - | m/s | Translation of the right damper relative to the wheel carrier along the thrust damper axis |
| `<pre>.DamperR.a` | - | m/s² | Translation of the right damper relative to the wheel carrier along the thrust damper axis |
| `<pre>.OSRate` | - | - | Model oversampling rate (integer) |
| `<pre>.PlungL.Frc2Wheel` | - | N | Normal force at the left tire contact point |
| `<pre>.PlungR.Frc2Wheel` | - | N | Normal force at the right tire contact point |
| `<pre>.StbBarL.ra_y` | - | rad/s² | Rotation acceleration of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarL.rv_y` | - | rad/s | Rotation velocity of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarL.r_y` | - | rad | Rotation of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.ra_y` | - | rad/s² | Rotation acceleration of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.rv_y` | - | rad/s | Rotation velocity of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.r_y` | - | rad | Rotation of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbLinkL.Bush2WC.*` | - | - | Parameters of the bushing between the left stabilizer link and wheel carrier body |
| `<pre>.StbLinkR.Bush2WC.*` | - | - | Parameters of the bushing between the right stabilizer link and wheel carrier body |
| `<pre>.StbLinkL.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.rv_yx.x/y` | - | rad/s | Rotation velocity of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.r_yx.x/y` | - | rad | Rotation of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.rv_yx.x/y` | - | rad/s | Rotation velocity of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.r_yx.x/y` | - | rad | Rotation of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StrRack.a_y` | - | m/s² | Translation acceleration of the steering rack body relative to the vehicle chassis along the y-axis (information imposed by steering model) |
| `<pre>.StrRack.t_y` | - | m | Translation of the steering rack body relative to the vehicle chassis along the y-axis (information imposed by steering model) |
| `<pre>.StrRack.v_y` | - | m/s | Translation velocity of the steering rack body relative to the vehicle chassis along the y-axis (information imposed by steering model) |
| `<pre>.StrRodL.Bush2StrRack.*` | - | - | Parameters of the bushing between the left steering rod and steering rack body |
| `<pre>.StrRodR.Bush2StrRack.*` | - | - | Parameters of the bushing between the right steering rod and steering rack body |
| `<pre>.StrRodL.ra_zx.x/z` | - | rad/s² | Rotation acceleration of the left steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodL.rv_zx.x/z` | - | rad/s | Rotation velocity of the left steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodL.r_zx.x/z` | - | rad | Rotation of the left steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodR.ra_zx.x/z` | - | rad/s² | Rotation acceleration of the right steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodR.rv_zx.x/z` | - | rad/s | Rotation velocity of the right steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodR.r_zx.x/z` | - | rad | Rotation of the right steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.Vhcl.Bush2DampL.*` | - | - | Parameters of the strut bushing between the left damper body and vehicle chassis |
| `<pre>.Vhcl.Bush2DampR.*` | - | - | Parameters of the strut bushing between the right damper body and vehicle chassis |
| `<pre>.WCL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.r_zxy.x/y/z` | - | rad | Rotation of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.t.x/y/z` | - | m | Translation of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.v.x/y/z` | - | m/s | Translation velocity of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.a.x/y/z` | - | m/s² | Translation acceleration of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.r_zxy.x/y/z` | - | rad | Rotation of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.t.x/y/z` | - | m | Translation of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.v.x/y/z` | - | m/s | Translation velocity of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.a.x/y/z` | - | m/s² | Translation acceleration of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WshbL.BushF2Vhcl.*` | - | - | Parameters of the front bushing between the left wishbone body and vehicle chassis |
| `<pre>.WshbL.BushR2Vhcl.*` | - | - | Parameters of the rear bushing between the left wishbone body and vehicle chassis |
| `<pre>.WshbL.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the left wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WshbL.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the left wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WshbL.r_zyx.x/y/z` | - | rad | Rotation of the left wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WshbR.BushF2Vhcl.*` | - | - | Parameters of the front bushing between the right wishbone body and vehicle chassis |
| `<pre>.WshbR.BushR2Vhcl.*` | - | - | Parameters of the rear bushing between the right wishbone body and vehicle chassis |
| `<pre>.WshbR.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the right wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WshbR.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the right wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WshbR.r_zyx.x/y/z` | - | rad | Rotation of the right wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |

## 26.8.3 McPherson Suspension with ForceCoupling

At this point only the additional quantities for the stabilizer bar due to the numerical compliance and the resulting forces and torques at the attachment frame are listed. For the description of the other bodies please refer to section 26.8.2.

Template variables:
- `<pre> := McPherson.<pos>`
- `<pos> := SuspF`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.WCL.*` | - | - | All quantities describing the motion of the wheel carrier bodies are expressed in Fr0 with respect to Fr0 |
| `<pre>.WCR.*` | - | - | All quantities describing the motion of the wheel carrier bodies are expressed in Fr0 with respect to Fr0 |
| `<pre>.StBarL.Bush2Vhcl.*` | - | - | Parameters of numerical bushing between left stabilizer bar and vehicle chassis |
| `<pre>.StBarR.Bush2Vhcl.*` | - | - | Parameters of numerical bushing between right stabilizer bar and vehicle chassis |
| `<pre>.FrcCpl.Frc_1.x/y/z` | - | N | Resulting forces at attachment frame expressed in Fr1 |
| `<pre>.FrcCpl.Trq_1.x/y/z` | - | Nm | Resulting torques at attachment frame expressed in Fr1 with respect to Fr1 |
| `<pre>.FrcCpl.Frc_Susp.x/y/z` | - | N | Resulting forces at attachment frame expressed in FrSusp |
| `<pre>.FrcCpl.Trq_Susp.x/y/z` | - | Nm | Resulting torques at attachment frame expressed in FrSusp with respect to FrSusp |

## 26.8.4 McPherson Extended Suspension

At this point only the additional quantities for the two bodies subframe and steering box are listed. For the description of the other bodies please refer to section 26.8.2.

Template variables:
- `<pre> := McPherson.<pos>`
- `<pos> := SuspF`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.StrBox.ra_zx.x/z` | - | rad/s² | Rotation acceleration of the steering box relative to the subframe body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrBox.rv_zx.x/z` | - | rad/s | Rotation velocity of the steering box relative to the subframe body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrBox.r_zx.x/z` | - | rad | Rotation of the steering box relative to the subframe body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrBox.t.x/y/z` | - | m | Translation of the steering box relative to the subframe body along the x,y,z-axis |
| `<pre>.StrBox.v.x/y/z` | - | m/s | Translation velocity of the steering box relative to the subframe body along the x,y,z-axis |
| `<pre>.StrBox.a.x/y/z` | - | m/s² | Translation acceleration of the steering box relative to the subframe body along the x,y,z-axis |
| `<pre>.Subfrm.BushFL2Vhcl.*` | - | - | Parameters of the front left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushFR2Vhcl.*` | - | - | Parameters of the front right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.BushRL2Vhcl.*` | - | - | Parameters of the rear left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushRR2Vhcl.*` | - | - | Parameters of the rear right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.L2StrBox.*` | - | - | Parameters of the left bushing between the subframe and the steering box body |
| `<pre>.Subfrm.R2StrBox.*` | - | - | Parameters of the right bushing between the subframe and the steering box body |
| `<pre>.Subfrm.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.r_zyx.x/y/z` | - | rad | Rotation of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.t.x/y/z` | - | m | Translation of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.Subfrm.v.x/y/z` | - | m/s | Translation velocity of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.Subfrm.a.x/y/z` | - | m/s² | Translation acceleration of the subframe body relative to the vehicle chassis along the x,y,z-axis |

## 26.8.5 Fourlink Suspension

Template variables:
- `<pre> := FourLink.<pos>`
- `<pos> := SuspR`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.OSRate` | - | - | Model oversampling rate (integer) |
| `<pre>.PlungL.Frc2Wheel` | - | N | Normal force at the left tire contact point |
| `<pre>.PlungR.Frc2Wheel` | - | N | Normal force at the right tire contact point |
| `<pre>.StbBarL.ra_y` | - | rad/s² | Rotation acceleration of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarL.rv_y` | - | rad/s | Rotation velocity of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarL.r_y` | - | rad | Rotation of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.ra_y` | - | rad/s² | Rotation acceleration of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.rv_y` | - | rad/s | Rotation velocity of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.r_y` | - | rad | Rotation of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbLinkL.Bush.*` | - | - | Parameters of the bushing between the left stabilizer link and wheel carrier (or lower wishbone) body |
| `<pre>.StbLinkL.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.rv_yx.x/y` | - | rad/s | Rotation velocity of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.r_yx.x/y` | - | rad | Rotation of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.Bush.*` | - | - | Parameters of the bushing between the right stabilizer link and wheel carrier (or lower wishbone) body |
| `<pre>.StbLinkR.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.rv_yx.x/y` | - | rad/s | Rotation velocity of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.r_yx.x/y` | - | rad | Rotation of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StrRodL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left steering rod body and vehicle chassis |
| `<pre>.StrRodL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodL.r_zxy.x/y/z` | - | rad | Rotation of the left steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right steering rod body and vehicle chassis |
| `<pre>.StrRodR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodR.r_zxy.x/y/z` | - | rad | Rotation of the right steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.TrailArmL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left trailing arm body and vehicle chassis |
| `<pre>.TrailArmL.ra_z` | - | rad/s² | Rotation acceleration of the left trailing arm relative to wheel carrier body around the z-axis |
| `<pre>.TrailArmL.rv_z` | - | rad/s | Rotation velocity of the left trailing arm relative to wheel carrier body around the z-axis |
| `<pre>.TrailArmL.r_z` | - | rad | Rotation of the left trailing arm relative to wheel carrier body around the z-axis |
| `<pre>.TrailArmL.Trq2WC_z` | - | Nm | Spring-damper torque of the left trailing arm body |
| `<pre>.TrailArmR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right trailing arm body and vehicle chassis |
| `<pre>.TrailArmR.ra_z` | - | rad/s² | Rotation acceleration of the right trailing arm relative to wheel carrier body around the z-axis |
| `<pre>.TrailArmR.rv_z` | - | rad/s | Rotation velocity of the right trailing arm relative to wheel carrier body around the z-axis |
| `<pre>.TrailArmR.r_z` | - | rad | Rotation of the right trailing arm relative to wheel carrier body around the z-axis |
| `<pre>.TrailArmR.Trq2WC_z` | - | Nm | Spring-damper torque of the right trailing arm body |
| `<pre>.WCL.a.x/y/z` | - | m/s² | Translation acceleration of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.r_zxy.x/y/z` | - | rad | Rotation of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.t.x/y/z` | - | m | Translation of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.v.x/y/z` | - | m/s | Translation velocity of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.a.x/y/z` | - | m/s² | Translation acceleration of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.r_zxy.x/y/z` | - | rad | Rotation of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.t.x/y/z` | - | m | Translation of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.v.x/y/z` | - | m/s | Translation velocity of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WishLowL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left lower wishbone body and vehicle chassis |
| `<pre>.WishLowL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowL.r_zxy.x/y/z` | - | rad | Rotation of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right lower wishbone body and vehicle chassis |
| `<pre>.WishLowR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowR.r_zxy.x/y/z` | - | rad | Rotation of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left upper wishbone body and vehicle chassis |
| `<pre>.WishUppL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppL.r_zxy.x/y/z` | - | rad | Rotation of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right upper wishbone body and vehicle chassis |
| `<pre>.WishUppR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppR.r_zxy.x/y/z` | - | rad | Rotation of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |

## 26.8.6 Fourlink Suspension with ForceCoupling

At this point only the additional quantities for the stabilizer bar due to the numerical compliance and the resulting forces and torques at the attachment frame are listed. For the description of the other bodies please refer to section 26.8.5.

Template variables:
- `<pre> := FourLink.<pos>`
- `<pos> := SuspR`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.WCL.*` | - | - | All quantities describing the motion of the wheel carrier bodies are expressed in Fr0 with respect to Fr0 |
| `<pre>.WCR.*` | - | - | All quantities describing the motion of the wheel carrier bodies are expressed in Fr0 with respect to Fr0 |
| `<pre>.StBarL.Bush2Vhcl.*` | - | - | Parameters of numerical bushing between left stabilizer bar and vehicle chassis |
| `<pre>.StBarR.Bush2Vhcl.*` | - | - | Parameters of numerical bushing between right stabilizer bar and vehicle chassis |
| `<pre>.FrcCpl.Frc_1.x/y/z` | - | N | Resulting forces at attachment frame expressed in Fr1 |
| `<pre>.FrcCpl.Trq_1.x/y/z` | - | Nm | Resulting torques at attachment frame expressed in Fr1 with respect to Fr1 |
| `<pre>.FrcCpl.Frc_Susp.x/y/z` | - | N | Resulting forces at attachment frame expressed in FrSusp |
| `<pre>.FrcCpl.Trq_Susp.x/y/z` | - | Nm | Resulting torques at attachment frame expressed in FrSusp with respect to FrSusp |

## 26.8.7 Fourlink Extended Suspension

At this point only the additional quantities for the body subframe are listed. For the description of the other bodies please refer to section 26.8.5.

Template variables:
- `<pre> := FourLink.<pos>`
- `<pos> := SuspR`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.Subfrm.BushFL2Vhcl.*` | - | - | Parameters of the front left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushFR2Vhcl.*` | - | - | Parameters of the front right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.BushRL2Vhcl.*` | - | - | Parameters of the rear left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushRR2Vhcl.*` | - | - | Parameters of the rear right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.r_zyx.x/y/z` | - | rad | Rotation of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.t.x/y/z` | - | m | Translation of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.Subfrm.v.x/y/z` | - | m/s | Translation velocity of the subframe body relative to the vehicle chassis along the x,y,z-axis |

## 26.8.8 Fourlink Modified Extended Suspension

Template variables:
- `<pre> := FourLink.<pos>`
- `<pos> := SuspR`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.OSRate` | - | - | Model oversampling rate (integer) |
| `<pre>.PlungL.Frc2Wheel` | - | N | Normal force at the left tire contact point |
| `<pre>.PlungR.Frc2Wheel` | - | N | Normal force at the right tire contact point |
| `<pre>.StbBarL.ra_y` | - | rad/s² | Rotation acceleration of the left stabilizer bar body relative to subframe body around the y-axis |
| `<pre>.StbBarL.rv_y` | - | rad/s | Rotation velocity of the left stabilizer bar body relative to subframe body around the y-axis |
| `<pre>.StbBarL.r_y` | - | rad | Rotation of the left stabilizer bar body relative to subframe body around the y-axis |
| `<pre>.StbBarR.ra_y` | - | rad/s² | Rotation acceleration of the right stabilizer bar body relative to subframe body around the y-axis |
| `<pre>.StbBarR.rv_y` | - | rad/s | Rotation velocity of the right stabilizer bar body relative to subframe body around the y-axis |
| `<pre>.StbBarR.r_y` | - | rad | Rotation of the right stabilizer bar body relative to subframe body around the y-axis |
| `<pre>.StbLinkL.Bush.*` | - | - | Parameters of the bushing between the left stabilizer link and wheel carrier (or lower/upper wishbone) body |
| `<pre>.StbLinkL.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.rv_yx.x/y` | - | rad/s | Rotation velocity of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.r_yx.x/y` | - | rad | Rotation of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.Bush.*` | - | - | Parameters of the bushing between the right stabilizer link and wheel carrier (or lower/upper wishbone) body |
| `<pre>.StbLinkR.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.rv_yx.x/y` | - | rad/s | Rotation velocity of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.r_yx.x/y` | - | rad | Rotation of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StrRodL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left steering rod body and subframe body |
| `<pre>.StrRodL.a.x/y/z` | - | m/s² | Translation acceleration of the left steering rod body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.StrRodL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodL.r_zxy.x/y/z` | - | rad | Rotation of the left steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodL.t.x/y/z` | - | m | Translation of the left steering rod body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.StrRodL.v.x/y/z` | - | m/s | Translation velocity of the left steering rod body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.StrRodR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right steering rod body and subframe body |
| `<pre>.StrRodR.a.x/y/z` | - | m/s² | Translation acceleration of the right steering rod body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.StrRodR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodR.r_zxy.x/y/z` | - | rad | Rotation of the right steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodR.t.x/y/z` | - | m | Translation of the right steering rod body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.StrRodR.v.x/y/z` | - | m/s | Translation velocity of the right steering rod body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.Subfrm.BushFL2Vhcl.*` | - | - | Parameters of the front left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushFR2Vhcl.*` | - | - | Parameters of the front right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.BushRL2Vhcl.*` | - | - | Parameters of the rear left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushRR2Vhcl.*` | - | - | Parameters of the rear right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.r_zyx.x/y/z` | - | rad | Rotation of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.t.x/y/z` | - | m | Translation of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.Subfrm.v.x/y/z` | - | m/s | Translation velocity of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.Subfrm.a.x/y/z` | - | m/s² | Translation acceleration of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.TrailArmL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left trailing arm body and the subframe body |
| `<pre>.TrailArmL.a.x/y/z` | - | m/s² | Translation acceleration of the left trailing arm body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.TrailArmL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left trailing arm relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.TrailArmL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left trailing arm relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.TrailArmL.r_zxy.x/y/z` | - | rad | Rotation of the left trailing arm relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.TrailArmL.t.x/y/z` | - | m | Translation of the left trailing arm body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.TrailArmL.v.x/y/z` | - | m/s | Translation velocity of the left trailing arm body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.TrailArmR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right trailing arm body and the subframe body |
| `<pre>.TrailArmR.a.x/y/z` | - | m/s² | Translation acceleration of the right trailing arm body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.TrailArmR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right trailing arm relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.TrailArmR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right trailing arm relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.TrailArmR.r_zxy.x/y/z` | - | rad | Rotation of the right trailing arm relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.TrailArmR.t.x/y/z` | - | m | Translation of the right trailing arm body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.TrailArmR.v.x/y/z` | - | m/s | Translation velocity of the right trailing arm body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.WCL.Bush2WishLow.*` | - | - | Parameters of the bushing between the left lower wishbone body and the wheel carrier body |
| `<pre>.WCL.Bush2TrailArm.*` | - | - | Parameters of the bushing between the left trailing arm body and the wheel carrier body |
| `<pre>.WCL.Bush2SteerRod.*` | - | - | Parameters of the bushing between the left steering rod body and the wheel carrier body |
| `<pre>.WCL.a.x/y/z` | - | m/s² | Translation acceleration of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.r_zxy.x/y/z` | - | rad | Rotation of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.t.x/y/z` | - | m | Translation of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.v.x/y/z` | - | m/s | Translation velocity of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.Bush2WishLow.*` | - | - | Parameters of the bushing between the right lower wishbone body and the wheel carrier body |
| `<pre>.WCR.Bush2TrailArm.*` | - | - | Parameters of the bushing between the right trailing arm body and the wheel carrier body |
| `<pre>.WCR.Bush2SteerRod.*` | - | - | Parameters of the bushing between the right steering rod body and the wheel carrier body |
| `<pre>.WCR.a.x/y/z` | - | m/s² | Translation acceleration of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.r_zxy.x/y/z` | - | rad | Rotation of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.t.x/y/z` | - | m | Translation of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.v.x/y/z` | - | m/s | Translation velocity of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WishLowL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left lower wishbone body and the subframe body |
| `<pre>.WishLowL.a.x/y/z` | - | m/s² | Translation acceleration of the left lower wishbone body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.WishLowL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowL.r_zxy.x/y/z` | - | rad | Rotation of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowL.t.x/y/z` | - | m | Translation of the left lower wishbone body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.WishLowL.v.x/y/z` | - | m/s | Translation velocity of the left lower wishbone body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.WishLowR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right lower wishbone body and the subframe body |
| `<pre>.WishLowR.a.x/y/z` | - | m/s² | Translation acceleration of the right lower wishbone body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.WishLowR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowR.r_zxy.x/y/z` | - | rad | Rotation of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowR.t.x/y/z` | - | m | Translation of the right lower wishbone body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.WishLowR.v.x/y/z` | - | m/s | Translation velocity of the right lower wishbone body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.WishUppL.BushF2Vhcl.*` | - | - | Parameters of the bushing between the left front upper wishbone body and the subframe body |
| `<pre>.WishUppL.BushR2Vhcl.*` | - | - | Parameters of the bushing between the left rear upper wishbone body and the subframe body |
| `<pre>.WishUppL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppL.r_zxy.x/y/z` | - | rad | Rotation of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppR.BushF2Vhcl.*` | - | - | Parameters of the bushing between the right front upper wishbone body and the subframe body |
| `<pre>.WishUppR.BushR2Vhcl.*` | - | - | Parameters of the bushing between the right rear upper wishbone body and the subframe body |
| `<pre>.WishUppR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppR.r_zxy.x/y/z` | - | rad | Rotation of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |

## 26.8.9 Twistrbeam Suspension

Template variables:
- `<pre> := TwistBeam.<pos>`
- `<pos> := SuspR`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.OSRate` | - | - | Model oversampling rate (integer) |
| `<pre>.PlungL.Frc2Wheel` | - | N | Normal force at the left tire contact point |
| `<pre>.PlungR.Frc2Wheel` | - | N | Normal force at the right tire contact point |
| `<pre>.TorsBeam.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the torsion beam body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TorsBeam.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the torsion beam body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TorsBeam.r_zyx.x/y/z` | - | rad | Rotation of the torsion beam body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TorsBeam.t.x/y/z` | - | m | Translation of the torsion beam body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.TorsBeam.v.x/y/z` | - | m/s | Translation velocity of the torsion beam body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.TorsBeam.a.x/y/z` | - | m/s² | Translation acceleration of the torsion beam body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.TrlArmL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left trailing arm body and vehicle chassis |
| `<pre>.TrlArmL.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the left trailing arm body relative to torsion beam around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TrlArmL.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the left trailing arm body relative to torsion beam around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TrlArmL.r_zyx.x/y/z` | - | rad | Rotation of the left trailing arm body relative to torsion beam around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TrlArmL.Trq2TorsBeam.x/y/z` | - | Nm | Spring-damper torque of the left trailing arm body to the torsion beam around the x,y,z-axis |
| `<pre>.TrlArmR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right trailing arm body and vehicle chassis |
| `<pre>.TrlArmR.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the right trailing arm body relative to torsion beam around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TrlArmR.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the right trailing arm body relative to torsion beam around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TrlArmR.r_zyx.x/y/z` | - | rad | Rotation of the right trailing arm body relative to torsion beam around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TrlArmR.Trq2TorsBeam.x/y/z` | - | Nm | Spring-damper torque of the right trailing arm body to the torsion beam around the x,y,z-axis |
| `<pre>.WCL.ra_z` | - | rad/s² | Rotation acceleration of the left wheel carrier body relative to trailing arm body around the z-axis |
| `<pre>.WCL.rv_z` | - | rad/s | Rotation velocity of the left wheel carrier body relative to trailing arm body around the z-axis |
| `<pre>.WCL.r_z` | - | rad | Rotation of the left wheel carrier body relative to trailing arm body around the z-axis |
| `<pre>.WCL.Trq2TrailArm_z` | - | Nm | Spring-damper torque of the left wheel carrier body to trailing arm body |
| `<pre>.WCR.ra_z` | - | rad/s² | Rotation acceleration of the right wheel carrier body relative to trailing arm body around the z-axis |
| `<pre>.WCR.rv_z` | - | rad/s | Rotation velocity of the right wheel carrier body relative to trailing arm body around the z-axis |
| `<pre>.WCR.r_z` | - | rad | Rotation of the right wheel carrier body relative to trailing arm body around the z-axis |
| `<pre>.WCR.Trq2TrailArm_z` | - | Nm | Spring-damper torque of the right wheel carrier body to trailing arm body |

## 26.8.10 Twistrbeam Extended Suspension

At this point only the quantities for the additional model elements are listed. For the description of the other bodies please refer to section 26.8.9.

Template variables:
- `<pre> := TwistBeam.<pos>`
- `<pos> := SuspR`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.TrlArmL.Bush2TorsBeam.*` | - | - | Parameters of the bushing between the left trailing arm body and the torsion beam body |
| `<pre>.TrlArmL.t.x/y/z` | - | m | Translation of the left trailing arm body relative to the torsion beam along the x,y,z-axis |
| `<pre>.TrlArmL.v.x/y/z` | - | m/s | Translation velocity of the left trailing arm body relative to the torsion beam along the x,y,z-axis |
| `<pre>.TrlArmL.a.x/y/z` | - | m/s² | Translation acceleration of the left trailing arm body relative to the torsion beam along the x,y,z-axis |
| `<pre>.TrlArmR.Bush2TorsBeam.*` | - | - | Parameters of the bushing between the right trailing arm body and the torsion beam body |
| `<pre>.TrlArmR.t.x/y/z` | - | m | Translation of the right trailing arm body relative to the torsion beam along the x,y,z-axis |
| `<pre>.TrlArmR.v.x/y/z` | - | m/s | Translation velocity of the right trailing arm body relative to the torsion beam along the x,y,z-axis |
| `<pre>.TrlArmR.a.x/y/z` | - | m/s² | Translation acceleration of the right trailing arm body relative to the torsion beam along the x,y,z-axis |

## 26.8.11 Double Wishbone Suspension

Template variables:
- `<pre> := DoubleWishbone.<pos>`
- `<pos> := SuspF`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.OSRate` | - | - | Model oversampling rate (integer) |
| `<pre>.PlungL.Frc2Wheel` | - | N | Normal force at the left tire contact point |
| `<pre>.PlungR.Frc2Wheel` | - | N | Normal force at the right tire contact point |
| `<pre>.StbBarL.ra_y` | - | rad/s² | Rotation acceleration of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarL.rv_y` | - | rad/s | Rotation velocity of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarL.r_y` | - | rad | Rotation of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.ra_y` | - | rad/s² | Rotation acceleration of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.rv_y` | - | rad/s | Rotation velocity of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.r_y` | - | rad | Rotation of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbLinkL.Bush2WC.*` | - | - | Parameters of the bushing between the left stabilizer link and wheel carrier body |
| `<pre>.StbLinkR.Bush2WC.*` | - | - | Parameters of the bushing between the right stabilizer link and wheel carrier body |
| `<pre>.StbLinkL.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.rv_yx.x/y` | - | rad/s | Rotation velocity of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.r_yx.x/y` | - | rad | Rotation of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.rv_yx.x/y` | - | rad/s | Rotation velocity of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.r_yx.x/y` | - | rad | Rotation of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StrRack.a_y` | - | m/s² | Translation acceleration of the steering rack body relative to the vehicle chassis along the y-axis (information imposed by steering model) |
| `<pre>.StrRack.t_y` | - | m | Translation of the steering rack body relative to the vehicle chassis along the y-axis (information imposed by steering model) |
| `<pre>.StrRack.v_y` | - | m/s | Translation velocity of the steering rack body relative to the vehicle chassis along the y-axis (information imposed by steering model) |
| `<pre>.StrRodL.Bush2StrRack.*` | - | - | Parameters of the bushing between the left steering rod and steering rack body |
| `<pre>.StrRodR.Bush2StrRack.*` | - | - | Parameters of the bushing between the right steering rod and steering rack body |
| `<pre>.StrRodL.ra_zx.x/z` | - | rad/s² | Rotation acceleration of the left steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodL.rv_zx.x/z` | - | rad/s | Rotation velocity of the left steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodL.r_zx.x/z` | - | rad | Rotation of the left steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodR.ra_zx.x/z` | - | rad/s² | Rotation acceleration of the right steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodR.rv_zx.x/z` | - | rad/s | Rotation velocity of the right steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodR.r_zx.x/z` | - | rad | Rotation of the right steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.Vhcl.Bush2DampL.*` | - | - | Parameters of the strut bushing between the left damper body and vehicle chassis |
| `<pre>.Vhcl.Bush2DampR.*` | - | - | Parameters of the strut bushing between the right damper body and vehicle chassis |
| `<pre>.WCL.a.x/y/z` | - | m/s² | Translation acceleration of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.r_zxy.x/y/z` | - | rad | Rotation of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.t.x/y/z` | - | m | Translation of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.v.x/y/z` | - | m/s | Translation velocity of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.a.x/y/z` | - | m/s² | Translation acceleration of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.r_zxy.x/y/z` | - | rad | Rotation of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.t.x/y/z` | - | m | Translation of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.v.x/y/z` | - | m/s | Translation velocity of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WishLowL.BushF2Vhcl.*` | - | - | Parameters of the front bushing between the left lower wishbone body and vehicle chassis |
| `<pre>.WishLowL.BushR2Vhcl.*` | - | - | Parameters of the rear bushing between the left lower wishbone body and vehicle chassis |
| `<pre>.WishLowL.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishLowL.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishLowL.r_zyx.x/y/z` | - | rad | Rotation of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishLowR.BushF2Vhcl.*` | - | - | Parameters of the front bushing between the right lower wishbone body and vehicle chassis |
| `<pre>.WishLowR.BushR2Vhcl.*` | - | - | Parameters of the rear bushing between the right lower wishbone body and vehicle chassis |
| `<pre>.WishLowR.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishLowR.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishLowR.r_zyx.x/y/z` | - | rad | Rotation of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishUppL.BushF2Vhcl.*` | - | - | Parameters of the front bushing between the left upper wishbone body and vehicle chassis |
| `<pre>.WishUppL.BushR2Vhcl.*` | - | - | Parameters of the rear bushing between the left upper wishbone body and vehicle chassis |
| `<pre>.WishUppL.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishUppL.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishUppL.r_zyx.x/y/z` | - | rad | Rotation of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishUppR.BushF2Vhcl.*` | - | - | Parameters of the front bushing between the right upper wishbone body and vehicle chassis |
| `<pre>.WishUppR.BushR2Vhcl.*` | - | - | Parameters of the rear bushing between the right upper wishbone body and vehicle chassis |
| `<pre>.WishUppR.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishUppR.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishUppR.r_zyx.x/y/z` | - | rad | Rotation of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |

## 26.8.12 Double Wishbone Suspension with ForceCoupling

At this point only the additional quantities for the stabilizer bar due to the numerical compliance and the resulting forces and torques at the attachment frame are listed. For the description of the other bodies please refer to section 26.8.11.

Template variables:
- `<pre> := DoubleWishbone.<pos>`
- `<pos> := SuspF, SuspR`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.WCL.*` | - | - | All quantities describing the motion of the wheel carrier bodies are expressed in Fr0 with respect to Fr0 |
| `<pre>.WCR.*` | - | - | All quantities describing the motion of the wheel carrier bodies are expressed in Fr0 with respect to Fr0 |
| `<pre>.StBarL.Bush2Vhcl.*` | - | - | Parameters of numerical bushing between left stabilizer bar and vehicle chassis |
| `<pre>.StBarR.Bush2Vhcl.*` | - | - | Parameters of numerical bushing between right stabilizer bar and vehicle chassis |
| `<pre>.FrcCpl.Frc_1.x/y/z` | - | N | Resulting forces at attachment frame expressed in Fr1 |
| `<pre>.FrcCpl.Trq_1.x/y/z` | - | Nm | Resulting torques at attachment frame expressed in Fr1 with respect to Fr1 |
| `<pre>.FrcCpl.Frc_Susp.x/y/z` | - | N | Resulting forces at attachment frame expressed in FrSusp |
| `<pre>.FrcCpl.Trq_Susp.x/y/z` | - | Nm | Resulting torques at attachment frame expressed in FrSusp with respect to FrSusp |

## 26.8.13 Double Wishbone Extended Suspension

At this point only the additional quantities for the two bodies subframe and steering box are listed. For the description of the other bodies please refer to section 26.8.11.

Template variables:
- `<pre> := DoubleWishbone.<pos>`
- `<pos> := SuspF`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.StrBox.ra_zx.x/z` | - | rad/s² | Rotation acceleration of the steering box relative to the subframe body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrBox.rv_zx.x/z` | - | rad/s | Rotation velocity of the steering box relative to the subframe body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrBox.r_zx.x/z` | - | rad | Rotation of the steering box relative to the subframe body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrBox.t.x/y/z` | - | m | Translation of the steering box relative to the subframe body along the x,y,z-axis |
| `<pre>.StrBox.v.x/y/z` | - | m/s | Translation velocity of the steering box relative to the subframe body along the x,y,z-axis |
| `<pre>.StrBox.a.x/y/z` | - | m/s² | Translation acceleration of the steering box relative to the subframe body along the x,y,z-axis |
| `<pre>.Subfrm.BushFL2Vhcl.*` | - | - | Parameters of the front left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushFR2Vhcl.*` | - | - | Parameters of the front right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.BushRL2Vhcl.*` | - | - | Parameters of the rear left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushRR2Vhcl.*` | - | - | Parameters of the rear right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.L2StrBox.*` | - | - | Parameters of the left bushing between the subframe and the steering box body |
| `<pre>.Subfrm.R2StrBox.*` | - | - | Parameters of the right bushing between the subframe and the steering box body |
| `<pre>.Subfrm.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.r_zyx.x/y/z` | - | rad | Rotation of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.t.x/y/z` | - | m | Translation of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.Subfrm.v.x/y/z` | - | m/s | Translation velocity of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.Subfrm.a.x/y/z` | - | m/s² | Translation acceleration of the subframe body relative to the vehicle chassis along the x,y,z-axis |

---

**Document Information:**
- Source: CarMaker Reference Manual Version 14.0
- Category: MBS Suspension
- Section: User Accessible Quantities
- Generated from: UAQ_03_Suspension.txt
- Conversion completed with ligature fixes (fl, fi) and vector component normalization (x/y/z notation)
# User Accessible Quantities: Suspension, Tire & Brake

## 26.9 Steering System

### 26.9.1 Steering System – General

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Steer.AssistFrc` | `<pre>.AssistFrc` | N | Assisting force at steering rack |
| `Steer.AssistFrc_Ext` | `-` | N | Assisting external force at steering rack |
| `Steer.AssistTrqCol` | `<pre>.AssistTrqCol` | Nm | Assisting torque at column |
| `Steer.AssistTrqCol_Ext` | `-` | Nm | Assisting external torque at column |
| `Steer.AssistTrqPin` | `<pre>.AssistTrqPin` | Nm | Assisting torque at pinion |
| `Steer.AssistTrqPin_Ext` | `-` | Nm | Assisting external torque at pinion |
| `Steer.Cfg.PosSign` | `<pre>.CfgIF->PosSign` | - | Sign of the steering rack movement, depending on the front suspension kinematics: +1: positive rack movement leads to a positive wheel rotation around z-axis; -1: positive rack movement leads to a negative wheel rotation around z-axis |
| `Steer.L.iSteer2q` / `Steer.R.iSteer2q` | `<pre>.L.iSteer2q` / `<pre>.R.iSteer2q` | m/rad | Current ratio steering wheel angle to generalized steering coordinate on left/right side |
| `Steer.L.q` / `Steer.R.q` | `<pre>.L.q` / `<pre>.R.q` | m | Generalized steering coordinate for the front left/right suspension |
| `Steer.L.qp` / `Steer.R.qp` | `<pre>.L.qp` / `<pre>.R.qp` | m/s | Generalized steering velocity for the front left/right suspension |
| `Steer.L.qpp` / `Steer.R.qpp` | `<pre>.L.qpp` / `<pre>.R.qpp` | m/s² | Generalized steering acceleration for the front left/right suspension |
| `Steer.RL.q` / `Steer.RR.q` | `Steering.RL.q` / `Steering.RR.q` | m | Generalized steering coordinate for the rear left/right suspension |
| `Steer.RL.qp` / `Steer.RR.qp` | `Steering.RL.qp` / `Steering.RR.qp` | m/s | Generalized steering velocity for the rear left/right suspension |
| `Steer.SteerBy` | `<pre>.SteerBy` | - | Type of steering mode: (0..2); 1 = Steer by Angle; 2 = Steer by Torque |
| `Steer.WhlAcc` | `<pre>.AngAcc` | rad/s² | Steering wheel rotational acceleration |
| `Steer.WhlAng` | `<pre>.Ang` | rad | Steering wheel angle |
| `Steer.WhlTrq` | `<pre>.Trq` | Nm | Steering wheel torque (input torque from DrivMan/VehicleControl or internal feedback torque) |
| `Steer.WhlTrqStatic` | `<pre>.TrqStatic` | Nm | Steering wheel torque required to compensate wheel forces to steering rack (static conditions) |
| `Steer.WhlVel` | `<pre>.AngVel` | rad/s | Steering wheel rotational speed |

### 26.9.2 Steering System – Pfeffer

Note: `<pre> := Steer.Pfeffer`

#### EPS (Electric Power Steering)

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.EPS.iA` | `-` | A | Internal motor current |
| `<pre>.EPS.iA_stat` | `-` | A | Target motor current (from boost curve) |
| `<pre>.EPS.Motor.q` / `.Motor.qp` / `.Motor.qpp` | `-` | rad / rad/s / rad/s² | Degree of freedom of the motor: angle, rotational velocity, rotational acceleration |
| `<pre>.EPS.RCBN.Frc_Fric` | `-` | N | Exponential spring friction force in the recirculating ball nut system |
| `<pre>.EPS.RCBN.qBN` / `.RCBN.qpBN` / `.RCBN.qppBN` | `-` | m / m/s / m/s² | First degree of freedom of recirculating ball nut system: position, velocity, acceleration |
| `<pre>.EPS.RCBN.qKGT` / `.RCBN.qpKGT` / `.RCBN.qppKGT` | `-` | rad / rad/s / rad/s² | Second degree of freedom of recirculating ball nut system: angle, rotational velocity, rotational acceleration |
| `<pre>.EPS.RCBN.Trq_Fric` | `-` | Nm | Exponential spring friction torque in the recirculating ball nut system |
| `<pre>.EPS.Trq_Demand` | `-` | Nm | Demanded torque for the PI-Controller |
| `<pre>.EPS.Trq_E` | `-` | Nm | Motor torque (iA*Kt) |
| `<pre>.EPS.Trq_Eext` | `-` | Nm | External motor torque |
| `<pre>.EPS.Trq_L` | `-` | Nm | Torque in the spring-damper element of the belt |

#### HPS (Hydraulic Power Steering)

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.HPS.pDelta` | `-` | Pa | Internal pressure difference between the chambers |
| `<pre>.HPS.pDelta_stat` | `-` | Pa | Target pressure difference (from boost curve) |
| `<pre>.HPS.pL` / `.HPS.pR` | `-` | Pa | Internal pressure in the left/right chamber |
| `<pre>.HPS.pL_stat` / `.HPS.pR_stat` | `-` | Pa | Target pressure in the left/right chamber |
| `<pre>.HPS.Trq_Pump` | `-` | Nm | Required pump torque |
| `<pre>.HPS.VolL` / `.HPS.VolR` | `-` | m³ | Volume in the left/right chamber |

#### Mechanical Components

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.Mech.Column.iUpp2Low` | `-` | - | Non-uniformity ratio from upper to lower column |
| `<pre>.Mech.Column.LowAng` | `-` | rad | Lower column angle |
| `<pre>.Mech.Column.Trq_FricDamp` | `-` | Nm | Damping torque of the column's friction element |
| `<pre>.Mech.Column.Trq_FricStiff` | `-` | Nm | Stiffness torque of the column's friction element |
| `<pre>.Mech.Column.UppAng` | `-` | rad | Upper column angle |
| `<pre>.Mech.DeltaAng` | `-` | rad | Relative angle between steering wheel angle and the pinion angle, contains the torsion of all steering shaft components (column, hardy disc, torsion bar) |
| `<pre>.Mech.DeltaAngVel` | `-` | rad/s | Derivation of the relative angle between steering wheel angle and the pinion angle |
| `<pre>.Mech.Rack.Frc_FricDamp` | `-` | N | Damping force of the rack's friction element |
| `<pre>.Mech.Rack.Frc_FricStiff` | `-` | N | Stiffness force of the rack's friction element |
| `<pre>.Mech.Rack.Frc_RubberSleeve` | `-` | N | Rubber sleeve force in the rack |
| `<pre>.Mech.Torsbar.Trq_Fric` | `-` | Nm | Exponential spring friction torque in the torsion bar |
| `<pre>.Mech.Torsbar.Trq_Twist` | `-` | Nm | Twist torque in the torsion bar |
| `<pre>.Mech.Torsbar.TwistAng` | `-` | rad | Twist angle in the torsion bar |
| `<pre>.Mech.Trq_LowSprDamp` | `-` | Nm | Torque in the lower spring-damper element |
| `<pre>.Mech.Trq_Pinion` | `-` | Nm | Torque in the pinion |
| `<pre>.Mech.Trq_UppSprDamp` | `-` | Nm | Torque in the upper spring-damper element |

## 26.10 Tire

### 26.10.1 Tire Model TameTire

Note: `<pos> := FL, FR, RL, RR or FL.Twin, FR.Twin, RL.Twin, RR.Twin`

| UAQ Name | C-Code | Unit | Info (data type, if not integer) |
|---|---|---|---|
| `TameTire.<pos>.Press` | `-` | bar | Inflation pressure at `<pos>` |
| `TameTire.<pos>.TempCore` | `-` | °C | Core temperature of the compound at `<pos>` |
| `TameTire.<pos>.TempCoreAvg` | `-` | °C | Average core temperature of the compound at `<pos>` |
| `TameTire.<pos>.TempSurf` | `-` | °C | Surface temperature of the compound at `<pos>` |
| `TameTire.<pos>.IntAirTemp` | `-` | °C | Internal air temperature at `<pos>` |
| `TameTire.<pos>.TempRim` | `-` | °C | Rim temperature at `<pos>` |
| `TameTire.<pos>.TempTrack` | `-` | °C | Track temperature at `<pos>` |
| `TameTire.<pos>.Wear` | `-` | - | Wear at `<pos>` |
| `TameTire.<pos>.Deg` | `-` | - | Degradation at `<pos>` |

### 26.10.2 Tire Model Magic Formula 5.2 and 6.1

| UAQ Name | C-Code | Unit | Info (data type, if not integer) |
|---|---|---|---|
| `MFTire.<pos>.Dx` | `-` | N | Peak value of pure longitudinal force at `<pos>` |
| `MFTire.<pos>.Dy` | `-` | N | Peak value of pure lateral force at `<pos>` |
| `MFTire.<pos>.Press` | `-` | bar | Tire inflation pressure at `<pos>` (MF 6.1 only) |

Note: `<pos> := FL, FR, RL, RR or FL.Twin, FR.Twin, RL.Twin, RR.Twin`

### 26.10.3 Tire Model MF-Tyre/MF-Swift

Note: `<pre> := MFSwift.<pos>` where `<pos> := FL, FR, RL, RR or FL.Twin, FR.Twin, RL.Twin, RR.Twin`

| UAQ Name | C-Code | Unit | Info (data type, if not integer) |
|---|---|---|---|
| `<pre>.contact_point_force_longitudinal` | `-` | N | Longitudinal force |
| `<pre>.contact_point_force_lateral` | `-` | N | Lateral force |
| `<pre>.contact_point_force_vertical` | `-` | N | Vertical force |
| `<pre>.contact_point_moment_roll` | `-` | Nm | Overturning force |
| `<pre>.contact_point_moment_pitch` | `-` | Nm | Rolling resistance moment |
| `<pre>.contact_point_moment_yaw` | `-` | Nm | Self-aligning moment |
| `<pre>.slip_ratio_longitudinal` | `-` | - | Longitudinal slip |
| `<pre>.slip_angle_lateral` | `-` | rad | Side slip angle |
| `<pre>.inclination_angle` | `-` | rad | Inclination angle |
| `<pre>.turn_slip` | `-` | 1/m | Turn slip |
| `<pre>.contact_point_velocity_longitudinal` | `-` | m/s | Wheel contact centre forward velocity |
| `<pre>.loaded_radius` | `-` | m | Loaded radius |
| `<pre>.effective_rolling_radius` | `-` | m | Effective rolling radius |
| `<pre>.deflection_vertical` | `-` | m | Tyre deflection |
| `<pre>.contact_patch_length` | `-` | m | Tyre contact length |
| `<pre>.pneumatic_trail` | `-` | m | Pneumatic trail |
| `<pre>.peak_friction_longitudinal` | `-` | - | Longitudinal friction coefficient |
| `<pre>.peak_friction_lateral` | `-` | - | Lateral friction coefficient |
| `<pre>.relaxation_length_longitudinal` | `-` | m | Longitudinal relaxation length |
| `<pre>.relaxation_length_lateral` | `-` | m | Lateral relaxation length |
| `<pre>.slip_velocity_longitudinal` | `-` | m/s | Longitudinal wheel slip velocity |
| `<pre>.slip_velocity_lateral` | `-` | m/s | Lateral wheel slip velocity |
| `<pre>.compression_velocity_vertical` | `-` | m/s | Tyre compression velocity |
| `<pre>.angular_velocity_yaw` | `-` | m/s | Tyre yaw velocity |
| `<pre>.contact_point_coordinate_x` | `-` | m | Global x coordinate contact point |
| `<pre>.contact_point_coordinate_y` | `-` | m | Global y coordinate contact point |
| `<pre>.contact_point_coordinate_z` | `-` | m | Global z coordinate contact point |
| `<pre>.road_normal_component_x` | `-` | - | Global x component road normal |
| `<pre>.road_normal_component_y` | `-` | - | Global y component road normal |
| `<pre>.road_normal_component_z` | `-` | - | Global z component road normal |
| `<pre>.effective_road_height` | `-` | m | Effective road height |
| `<pre>.effective_road_slope` | `-` | rad | Effective forward slope |
| `<pre>.effective_road_curvature` | `-` | 1/m | Effective road curvature |
| `<pre>.effective_road_banking` | `-` | rad | Effective road banking/road camber angle |
| `<pre>.tread_surface_temperature` | `-` | K | Tread surface temperature |
| `<pre>.bulk_temperature` | `-` | K | Tread bulk temperature |
| `<pre>.liner_temperature` | `-` | K | Liner temperature |
| `<pre>.core_air_temperature` | `-` | K | Core air temperature |
| `<pre>.inflation_pressure` | `-` | N/m² | Inflation pressure |

### 26.10.4 Tire Model FTire

Note: `<pre> := FTire.<pos>` where `<pos> := FL, FR, RL, RR or FL.Twin, FR.Twin, RL.Twin, RR.Twin`

| UAQ Name | C-Code | Unit | Info (data type, if not integer) |
|---|---|---|---|
| `<pre>.Param.<OverrideParam>_override` | `-` | - | Current value of the override parameter, which internally overrides its corresponding .tir file parameter with `<OverrideParam>` = LMUX, LMUY, LKX, LKY, LKYZ, LKZC, LTR, INFLPRES |
| `<pre>.RoadTemp` | `-` | K | Road surface temperature |
| `<pre>.PressureSetFromExt` | `-` | bar | Current 'cold' inflation pressure from extern (-99999: no change in pressure) |
| `<pre>.P_x` | `-` | m | Geometrical center of contact patch in global coordinates |
| `<pre>.P_y` | `-` | m | Geometrical center of contact patch in global coordinates |
| `<pre>.P_z` | `-` | m | Geometrical center of contact patch in global coordinates |
| `<pre>.tire_deflection` | `-` | m | Tire deflection |
| `<pre>.C_v_y` | `-` | m/s | Vertical rim center velocity |
| `<pre>.C_v_x` | `-` | m/s | Longitudinal rim center velocity |
| `<pre>.P_v_longslip` | `-` | m/s | Longitudinal slip velocity at contact point |
| `<pre>.P_v_latslip` | `-` | m/s | Lateral slip velocity at contact point |
| `<pre>.belt_rmax_inflation` | `-` | m | Maximum belt radius after inflation |
| `<pre>.rim_rotv_2WC` | `-` | rad/s | Rim angular velocity relative to wheel carrier (ABS signal) |
| `<pre>.friction` | `-` | - | Mean road friction factor in contact patch |
| `<pre>.Frc_C` | `-` | N | Tire forces expressed in TYDEX C-axis |
| `<pre>.Trq_C` | `-` | Nm | Tire torques expressed in TYDEX C-axis |
| `<pre>.rollingloss` | `-` | N | Rolling loss |
| `<pre>.belt2rim_intrusion` | `-` | m | Maximum belt-to-rim contact intrusion |
| `<pre>.dynradius` | `-` | m | Dynamic rolling radius |
| `<pre>.Frc_ISO` | `-` | N | Tire forces expressed in ISO axis |
| `<pre>.Trq_ISO` | `-` | Nm | Tire torques expressed in ISO axis |

## 26.11 Brake

### 26.11.1 Brake – General

| UAQ Name | C-Code | Unit | Info (data type, if not double) |
|---|---|---|---|
| `Brake.Park` | `<preIF>.Park` | - | Park brake actuation (0..1) |
| `Brake.Pedal` | `<preIF>.Pedal` | - | Brake pedal actuation (0..1) |

### 26.11.2 Brake – Hydraulic

#### Hydraulic Brake Control – General

Note: `<preIF> := Brake.IF`

| UAQ Name | C-Code | Unit | Info (data type, if not double) |
|---|---|---|---|
| `Brake.Trq_DriveSrc_trg_<ds>` | `<preIF>.Trq_DriveSrc_trg[ds]` | Nm | Optional target torque at drive source `<ds>` (e.g. by ESP ECU) |
| `Brake.Trq_Reg_trg_FL` / `Brake.Trq_Reg_trg_FR` / `Brake.Trq_Reg_trg_RL` / `Brake.Trq_Reg_trg_RR` | `<preIF>.Trq_Reg_trg[0]` / `[1]` / `[2]` / `[3]` | Nm | Target regenerative brake torque front left / front right / rear left / rear right |
| `Brake.Trq_FL_ext` / `Brake.Trq_FR_ext` / `Brake.Trq_RL_ext` / `Brake.Trq_RR_ext` | `Brake.Trq_ext[0]` / `[1]` / `[2]` / `[3]` | Nm | Additional external brake torque front left / front right / rear left / rear right |
| `Brake.Trq_FL_tot` / `Brake.Trq_FR_tot` / `Brake.Trq_RL_tot` / `Brake.Trq_RR_tot` | `Brake.Trq_tot[0]` / `[1]` / `[2]` / `[3]` | Nm | Total brake torque (Trq_WB + Trq_PB + Trq_ext) front left / front right / rear left / rear right |
| `Brake.Trq_PB_FL` / `Brake.Trq_PB_FR` / `Brake.Trq_PB_RL` / `Brake.Trq_PB_RR` | `<preIF>.Trq_PB[0]` / `[1]` / `[2]` / `[3]` | Nm | Brake torque of park brake front left / front right / rear left / rear right |
| `Brake.Trq_WB_FL` / `Brake.Trq_WB_FR` / `Brake.Trq_WB_RL` / `Brake.Trq_WB_RR` | `<preIF>.Trq_WB[0]` / `[1]` / `[2]` / `[3]` | Nm | Brake torque at wheel brake front left / front right / rear left / rear right |

#### Hydraulic Brake Control Unit

| UAQ Name | C-Code | Unit | Info (data type, if not double) |
|---|---|---|---|
| `Brake.Hyd.CU.BooSignal` | `Brake.HydBrakeCU_IF.BooSignal` | - | Booster activation signal (0..1) |
| `Brake.Hyd.CU.Park` | `Brake.HydBrakeCU_IF.Park` | - | Park brake actuation (0..1) |
| `Brake.Hyd.CU.Pedal` | `Brake.HydBrakeCU_IF.Pedal` | - | Brake pedal actuation (0..1) |
| `Brake.Hyd.CU.PumpCtrl` | `Brake.HydBrakeCU_IF.PumpCtrl` | - | Hydraulic pump activated (boolean) |
| `Brake.Hyd.CU.Valve_<i>` | `Brake.HydBrakeCU_IF.V[<i>]` | - | Valve activity for valves, `<i>` = 0..15; For HydESP & HydIPB model: Valve activity for inlet valve front left / front right / rear left / rear right for i=0..3; Valve activity for outlet valve front left / front right / rear left / rear right for i=4..7; For HydESP: Valve activity for pilot valve 0 & 1 for i=8,9; Valve activity for suction valve 0 & 1 for i=10, 11; For HydIPB model: Valve activity for chamber valve 0 & 1 for i=8,9; Valve activity for booster valve 0 & 1 for i=10, 11; Valve activity for emulator valve for i=12; Valve activity for reservoir valve for i=13 |
| `Brake.Hyd.CU.CtrlOut_<i>` | `Brake.HydBrakeCU_IF.CtrlOut[<i>]` | - | Generic control signals to Hydraulic Brake System, `<i>` = 0..10 |
| `Brake.Hyd.CU.p_trg` | `Brake.HydBrakeCU_IF.p_trg` | bar | Target pressure for Hydraulic Brake System |
| `Brake.Hyd.CU.Trq_trg` | `Brake.HydBrakeCU_IF.Trq_trg` | Nm | Target torque for Hydraulic Brake System |

#### Hydraulic Brake Control – HydBasic

| UAQ Name | C-Code | Unit | Info (data type, if not double) |
|---|---|---|---|
| `Brake.Hyd.CU.Basic.desiredTrq_<pos>` | `-` | Nm | Desired total (regenerative and conventional) static brake torque for the wheel `<pos>` |
| `Brake.Hyd.CU.Basic.dTrq_<pos>` | `-` | Nm | Torque difference between the desired and current total brake torque |
| `Brake.Hyd.CU.Basic.regCover_<pos>` | `-` | % | The coverage ratio of the regenerative brake torque to the total brake torque |

#### Hydraulic Brake System – General

| UAQ Name | C-Code | Unit | Info (data type, if not double) |
|---|---|---|---|
| `Brake.Hyd.Sys.DiaphTravel` | `Brake.HydBrakeIF.DiaphTravel` | m | Travel of the booster diaphragm |
| `Brake.Hyd.Sys.PedFrc` | `Brake.HydBrakeIF.PedFrc` | N | Force applied on brake pedal |
| `Brake.Hyd.Sys.PedTravel` | `Brake.HydBrakeIF.PedTravel` | m | Brake pedal travel |
| `Brake.Hyd.Sys.PistTravel` | `Brake.HydBrakeIF.PistTravel` | m | Travel of master cylinder brake piston |
| `Brake.Hyd.Sys.pMC` | `Brake.HydBrakeIF.pMC` | bar | Master cylinder first chamber pressure |
| `Brake.Hyd.Sys.pMC_in` | `Brake.HydBrakeIF.pMC_in` | bar | Master cylinder pressure to hydraulic model for input mode 'Use_pMCInput' (input from file) |
| `Brake.Hyd.Sys.PuRetVolt` | `Brake.HydBrakeIF.PuRetVolt` | V | Hydraulic pump return voltage |
| `Brake.Hyd.Sys.rot` | `Brake.HydBrakeIF.rot` | rad | Hydraulic System Motor rotation angle |
| `Brake.Hyd.Sys.rotv` | `Brake.HydBrakeIF.rotv` | rad/s | Hydraulic System Motor rotation speed |
| `Brake.Hyd.Sys.pWB_FL` / `Brake.Hyd.Sys.pWB_FR` / `Brake.Hyd.Sys.pWB_RL` / `Brake.Hyd.Sys.pWB_RR` | `Brake.HydBrakeIF.pWB[0-3]` | bar | Brake pressure at wheel base front left / front right / rear left / rear right |
| `Brake.Hyd.Sys.Rel_SW` | `Brake.HydBrakeIF.Rel_SW` | - | Brake booster release switch actuated (boolean) |
| `Brake.Hyd.Sys.CtrlOut_<i>` | `Brake.HydBrakeIF.CtrlOut[<i>]` | - | Generic signals to Hydraulic Brake Control Unit, `<i>` = 0..10 |
| `Brake.Hyd.Sys.Use_pMCInput` | `Brake.HydBrakeIF.Use_pMCInput` | - | Flag indicating whether Brake.pMC_in (pressure in master cylinder) is taken into account instead of pedal position for input from file (boolean) |

#### Hydraulic Brake System – HydESP

| UAQ Name | C-Code | Unit | Info (data type, if not integer) |
|---|---|---|---|
| `Brake.Hyd.Sys.ESP.Att_0.p` | `-` | bar | Pressure of attenuator 0 |
| `Brake.Hyd.Sys.ESP.Att_0.v` | `-` | m³ | Volume of attenuator 0 |
| `Brake.Hyd.Sys.ESP.Att_1.p` | `-` | bar | Pressure of attenuator 1 |
| `Brake.Hyd.Sys.ESP.Att_1.v` | `-` | m³ | Volume of attenuator 1 |
| `Brake.Hyd.Sys.ESP.Booster.F` | `-` | N | Booster output force (input to master cylinder piston) |
| `Brake.Hyd.Sys.ESP.Cyl_FL.p` / `Brake.Hyd.Sys.ESP.Cyl_FR.p` / `Brake.Hyd.Sys.ESP.Cyl_RL.p` / `Brake.Hyd.Sys.ESP.Cyl_RR.p` | `-` | bar | Pressure of brake cylinder: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.ESP.Cyl_FL.v` / `Brake.Hyd.Sys.ESP.Cyl_FR.v` / `Brake.Hyd.Sys.ESP.Cyl_RL.v` / `Brake.Hyd.Sys.ESP.Cyl_RR.v` | `-` | m³ | Volume of brake cylinder: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.ESP.In_FL.alpha` / `Brake.Hyd.Sys.ESP.In_FR.alpha` / `Brake.Hyd.Sys.ESP.In_RL.alpha` / `Brake.Hyd.Sys.ESP.In_RR.alpha` | `-` | - | Normalized opening of inlet valve: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.ESP.IN_FL.dp` / `Brake.Hyd.Sys.ESP.IN_FR.dp` / `Brake.Hyd.Sys.ESP.IN_RL.dp` / `Brake.Hyd.Sys.ESP.IN_RR.dp` | `-` | bar | Pressure difference of inlet valve: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.ESP.IN_FL.q` / `Brake.Hyd.Sys.ESP.IN_FR.q` / `Brake.Hyd.Sys.ESP.IN_RL.q` / `Brake.Hyd.Sys.ESP.IN_RR.q` | `-` | m³/s | Volume flow through inlet valve: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.ESP.In_FL.state` / `Brake.Hyd.Sys.ESP.In_FR.state` / `Brake.Hyd.Sys.ESP.In_RL.state` / `Brake.Hyd.Sys.ESP.In_RR.state` | `-` | - | State of inlet valve (integer): Front left / Front right / Rear left / Rear right; 0=not switchable, 1=switched to great, 2=switched to small |
| `Brake.Hyd.Sys.ESP.LPA_0.p` | `-` | bar | Pressure of low pressure accumulator 0 |
| `Brake.Hyd.Sys.ESP.LPA_0.v` | `-` | m³ | Volume of low pressure accumulator 0 |
| `Brake.Hyd.Sys.ESP.LPA_1.p` | `-` | bar | Pressure of low pressure accumulator 1 |
| `Brake.Hyd.Sys.ESP.LPA_1.v` | `-` | m³ | Volume of low pressure accumulator 1 |
| `Brake.Hyd.Sys.ESP.nPump` | `-` | 1/s | Rotation speed of hydraulic pump |
| `Brake.Hyd.Sys.ESP.Out_FL.alpha` / `Brake.Hyd.Sys.ESP.Out_FR.alpha` / `Brake.Hyd.Sys.ESP.Out_RL.alpha` / `Brake.Hyd.Sys.ESP.Out_RR.alpha` | `-` | - | Normalized opening of outlet valve: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.ESP.OUT_FL.dp` / `Brake.Hyd.Sys.ESP.OUT_FR.dp` / `Brake.Hyd.Sys.ESP.OUT_RL.dp` / `Brake.Hyd.Sys.ESP.OUT_RR.dp` | `-` | bar | Pressure difference of outlet valve: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.ESP.OUT_FL.q` / `Brake.Hyd.Sys.ESP.OUT_FR.q` / `Brake.Hyd.Sys.ESP.OUT_RL.q` / `Brake.Hyd.Sys.ESP.OUT_RR.q` | `-` | m³/s | Volume flow through outlet valve: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.ESP.Out_FL.state` / `Brake.Hyd.Sys.ESP.Out_FR.state` / `Brake.Hyd.Sys.ESP.Out_RL.state` / `Brake.Hyd.Sys.ESP.Out_RR.state` | `-` | - | State of outlet valve (integer): Front left / Front right / Rear left / Rear right; 0=not switchable, 1=switched to great, 2=switched to small |
| `Brake.Hyd.Sys.ESP.Pu_0.dp` | `-` | bar | Pressure difference of hydraulic pump 0 |
| `Brake.Hyd.Sys.ESP.Pu_0.q` | `-` | m³/s | Volume flow through hydraulic pump 0 |
| `Brake.Hyd.Sys.ESP.Pu_1.dp` | `-` | bar | Pressure difference of hydraulic pump 1 |
| `Brake.Hyd.Sys.ESP.Pu_1.q` | `-` | m³/s | Volume flow through hydraulic pump 1 |
| `Brake.Hyd.Sys.ESP.Pump.dp` | `-` | bar | Pressure difference of hydraulic pump |
| `Brake.Hyd.Sys.ESP.PV_0.alpha` | `-` | - | Normalized opening of pilot valve 0 |
| `Brake.Hyd.Sys.ESP.PV_0.dp` | `-` | bar | Pressure difference of pilot valve 0 |
| `Brake.Hyd.Sys.ESP.PV_0.q` | `-` | m³/s | Volume flow through pilot valve 0 |
| `Brake.Hyd.Sys.ESP.PV_0.state` | `-` | - | State of pilot valve 0 (integer): 0=not switchable, 1=switched to great, 2=switched to small |
| `Brake.Hyd.Sys.ESP.PV_1.alpha` | `-` | - | Normalized opening of pilot valve 1 |
| `Brake.Hyd.Sys.ESP.PV_1.dp` | `-` | bar | Pressure difference of pilot valve 1 |
| `Brake.Hyd.Sys.ESP.PV_1.q` | `-` | m³/s | Volume flow through pilot valve 1 |
| `Brake.Hyd.Sys.ESP.PV_1.state` | `-` | - | State of pilot valve 1 (integer): 0=not switchable, 1=switched to great, 2=switched to small |
| `Brake.Hyd.Sys.ESP.SuppL_0.p` | `-` | bar | Pressure of supply line 0 |
| `Brake.Hyd.Sys.ESP.SuppL_0.v` | `-` | m³ | Volume of supply line 0 |
| `Brake.Hyd.Sys.ESP.SuppL_1.p` | `-` | bar | Pressure of supply line 1 |
| `Brake.Hyd.Sys.ESP.SuppL_1.v` | `-` | m³ | Volume of supply line 1 |
| `Brake.Hyd.Sys.ESP.SV_0.alpha` | `-` | - | Normalized opening of suction valve 0 |
| `Brake.Hyd.Sys.ESP.SV_0.dp` | `-` | bar | Pressure difference of suction valve 0 |
| `Brake.Hyd.Sys.ESP.SV_0.q` | `-` | m³/s | Volume flow through suction valve 0 |
| `Brake.Hyd.Sys.ESP.SV_0.state` | `-` | - | State of suction valve 0 (integer): 0=not switchable, 1=switched to great, 2=switched to small |
| `Brake.Hyd.Sys.ESP.SV_1.alpha` | `-` | - | Normalized opening of suction valve 1 |
| `Brake.Hyd.Sys.ESP.SV_1.dp` | `-` | bar | Pressure difference of suction valve 1 |
| `Brake.Hyd.Sys.ESP.SV_1.q` | `-` | m³/s | Volume flow through suction valve 1 |
| `Brake.Hyd.Sys.ESP.SV_1.state` | `-` | - | State of suction valve 1 (integer): 0=not switchable, 1=switched to great, 2=switched to small |

#### Hydraulic Brake System – HydIPB

| UAQ Name | C-Code | Unit | Info (data type, if not integer) |
|---|---|---|---|
| `Brake.Hyd.Sys.IPB.Cyl_FL.p` / `Brake.Hyd.Sys.IPB.Cyl_FR.p` / `Brake.Hyd.Sys.IPB.Cyl_RL.p` / `Brake.Hyd.Sys.IPB.Cyl_RR.p` | `-` | bar | Pressure of brake cylinder: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.IPB.Cyl_FL.v` / `Brake.Hyd.Sys.IPB.Cyl_FR.v` / `Brake.Hyd.Sys.IPB.Cyl_RL.v` / `Brake.Hyd.Sys.IPB.Cyl_RR.v` | `-` | m³ | Volume of brake cylinder: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.IPB.CylInV_FL.alpha` / `Brake.Hyd.Sys.IPB.CylInV_FR.alpha` / `Brake.Hyd.Sys.IPB.CylInV_RL.alpha` / `Brake.Hyd.Sys.IPB.CylInV_RR.alpha` | `-` | - | Normalized opening of inlet valve: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.IPB.CylInV_FL.dp` / `Brake.Hyd.Sys.IPB.CylInV_FR.dp` / `Brake.Hyd.Sys.IPB.CylInV_RL.dp` / `Brake.Hyd.Sys.IPB.CylInV_RR.dp` | `-` | bar | Pressure difference of inlet valve: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.IPB.CylInV_FL.q` / `Brake.Hyd.Sys.IPB.CylInV_FR.q` / `Brake.Hyd.Sys.IPB.CylInV_RL.q` / `Brake.Hyd.Sys.IPB.CylInV_RR.q` | `-` | m³/s | Volume flow through inlet valve: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.IPB.CylInV_FL.state` / `Brake.Hyd.Sys.IPB.CylInV_FR.state` / `Brake.Hyd.Sys.IPB.CylInV_RL.state` / `Brake.Hyd.Sys.IPB.CylInV_RR.state` | `-` | - | State of inlet valve (integer): Front left / Front right / Rear left / Rear right; 0=not switchable, 1=switched to great, 2=switched to small |
| `Brake.Hyd.Sys.IPB.Emul.p` | `-` | bar | Pressure of Pedal Force Feedback Emulator |
| `Brake.Hyd.Sys.IPB.Emul.v` | `-` | m³ | Volume of Pedal Force Feedback Emulator |
| `Brake.Hyd.Sys.IPB.DampChamber_0.p` | `-` | bar | Pressure of first Damper Chamber |
| `Brake.Hyd.Sys.IPB.DampChamber_0.v` | `-` | m³ | Volume of first Damper Chamber |
| `Brake.Hyd.Sys.IPB.DampChamber_1.p` | `-` | bar | Pressure of second Damper Chamber |
| `Brake.Hyd.Sys.IPB.DampChamber_1.v` | `-` | m³ | Volume of second Damper Chamber |
| `Brake.Hyd.Sys.IPB.PresBooster.Motor.rota` | `-` | rad/s² | Rotatory acceleration of Motor |
| `Brake.Hyd.Sys.IPB.PresBooster.Motor.iA` | `-` | A | Motor current |
| `Brake.Hyd.Sys.IPB.PresBooster.Motor.TrqLoad_Demand` | `-` | Nm | Demanded load torque of Motor |
| `Brake.Hyd.Sys.IPB.PresBooster.Motor.TrqE_Demand` | `-` | Nm | Demanded electrical source torque of Motor |
| `Brake.Hyd.Sys.IPB.PresBooster.Motor.TrqE` | `-` | Nm | Actual electrical source torque of Motor |
| `Brake.Hyd.Sys.IPB.PresBooster.Motor.Trq` | `-` | Nm | Actual load torque of the motor acting on the Pressure Booster volume. Can be set via DVA |
| `Brake.Hyd.Sys.IPB.PresBooster.p` | `-` | bar | Actual pressure in the Pressure Booster volume. Can be set via DVA |
| `Brake.Hyd.Sys.IPB.CylOutV_FL.alpha` / `Brake.Hyd.Sys.IPB.CylOutV_FR.alpha` / `Brake.Hyd.Sys.IPB.CylOutV_RL.alpha` / `Brake.Hyd.Sys.IPB.CylOutV_RR.alpha` | `-` | - | Normalized opening of outlet valve: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.IPB.CylOutV_FL.dp` / `Brake.Hyd.Sys.IPB.CylOutV_FR.dp` / `Brake.Hyd.Sys.IPB.CylOutV_RL.dp` / `Brake.Hyd.Sys.IPB.CylOutV_RR.dp` | `-` | bar | Pressure difference of outlet valve: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.IPB.CylOutV_FL.q` / `Brake.Hyd.Sys.IPB.CylOutV_FR.q` / `Brake.Hyd.Sys.IPB.CylOutV_RL.q` / `Brake.Hyd.Sys.IPB.CylOutV_RR.q` | `-` | m³/s | Volume flow through outlet valve: Front left / Front right / Rear left / Rear right |
| `Brake.Hyd.Sys.IPB.CylOutV_FL.state` / `Brake.Hyd.Sys.IPB.CylOutV_FR.state` / `Brake.Hyd.Sys.IPB.CylOutV_RL.state` / `Brake.Hyd.Sys.IPB.CylOutV_RR.state` | `-` | - | State of outlet valve (integer): Front left / Front right / Rear left / Rear right; 0=not switchable, 1=switched to great, 2=switched to small |
| `Brake.Hyd.Sys.IPB.EmulV.alpha` | `-` | - | Normalized opening of Pedal Force Feedback Emulator valve |
| `Brake.Hyd.Sys.IPB.EmulV.dp` | `-` | bar | Pressure difference of Pedal Force Feedback Emulator valve |
| `Brake.Hyd.Sys.IPB.EmulV.q` | `-` | m³/s | Volume flow through Pedal Force Feedback Emulator valve |
| `Brake.Hyd.Sys.IPB.EmulV.state` | `-` | - | State of Pedal Force Feedback Emulator valve (integer): 0=not switchable, 1=switched to great, 2=switched to small |
| `Brake.Hyd.Sys.IPB.ResV.alpha` | `-` | - | Normalized opening of Reservoir valve |
| `Brake.Hyd.Sys.IPB.ResV.dp` | `-` | bar | Pressure difference of Reservoir valve |
| `Brake.Hyd.Sys.IPB.ResV.q` | `-` | m³/s | Volume flow through Reservoir valve |
| `Brake.Hyd.Sys.IPB.ResV.state` | `-` | - | State of Reservoir valve (integer): 0=not switchable, 1=switched to great, 2=switched to small |
| `Brake.Hyd.Sys.IPB.ChamberV_0.alpha` | `-` | - | Normalized opening of first Chamber valve |
| `Brake.Hyd.Sys.IPB.ChamberV_0.dp` | `-` | bar | Pressure difference of first Chamber valve |
| `Brake.Hyd.Sys.IPB.ChamberV_0.q` | `-` | m³/s | Volume flow through first Chamber valve |
| `Brake.Hyd.Sys.IPB.ChamberV_0.state` | `-` | - | State of first Chamber valve (integer): 0=not switchable, 1=switched to great, 2=switched to small |
| `Brake.Hyd.Sys.IPB.ChamberV_1.alpha` | `-` | - | Normalized opening of second Chamber valve |
| `Brake.Hyd.Sys.IPB.ChamberV_1.dp` | `-` | bar | Pressure difference of second Chamber valve |
| `Brake.Hyd.Sys.IPB.ChamberV_1.q` | `-` | m³/s | Volume flow through second Chamber valve |
| `Brake.Hyd.Sys.IPB.ChamberV_1.state` | `-` | - | State of second Chamber valve (integer): 0=not switchable, 1=switched to great, 2=switched to small |
| `Brake.Hyd.Sys.IPB.PresBoosterCheckV.q` | `-` | m³/s | Volume flow through Pressure Booster Check valve |
| `Brake.Hyd.Sys.IPB.PresBoosterV_0.alpha` | `-` | - | Normalized opening of first Pressure Booster valve |
| `Brake.Hyd.Sys.IPB.PresBoosterV_0.dp` | `-` | bar | Pressure difference of first Pressure Booster valve |
| `Brake.Hyd.Sys.IPB.PresBoosterV_0.q` | `-` | m³/s | Volume flow through first Pressure Booster valve |
| `Brake.Hyd.Sys.IPB.PresBoosterV_0.state` | `-` | - | State of first Pressure Booster valve (integer): 0=not switchable, 1=switched to great, 2=switched to small |
| `Brake.Hyd.Sys.IPB.PresBoosterV_1.alpha` | `-` | - | Normalized opening of second Pressure Booster valve |
| `Brake.Hyd.Sys.IPB.PresBoosterV_1.dp` | `-` | bar | Pressure difference of second Pressure Booster valve |
| `Brake.Hyd.Sys.IPB.PresBoosterV_1.q` | `-` | m³/s | Volume flow through second Pressure Booster valve |
| `Brake.Hyd.Sys.IPB.PresBoosterV_1.state` | `-` | - | State of second Pressure Booster valve (integer): 0=not switchable, 1=switched to great, 2=switched to small |
# User Accessible Quantities: Powertrain

## 26.12 Powertrain

### 26.12.1 General

#### Template Variables
- `<pos>` := FL, FR, RL, RR
- `<pre>` := PowerTrain
- `<Nb>` := 0, ..., n (number)
- `<preW>` := PowerTrain.IF.WheelOut[Nb]

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `PT.OSRate` | `<pre>.OSRate` | - | Oversampling rate (integration substeps) |
| `PT.Trq_Supp2Bdy1B.y` | `<pre>.Trq_Supp2Bdy1B[0]`<br/>`<pre>.Trq_Supp2Bdy1B[1]`<br/>`<pre>.Trq_Supp2Bdy1B[2]` | Nm | Support torque to vehicle frame Fr1B (x/y/z components) |
| `PT.Trq_Supp2Bdy1.y` | `<pre>.Trq_Supp2Bdy1[0]`<br/>`<pre>.Trq_Supp2Bdy1[1]`<br/>`<pre>.Trq_Supp2Bdy1[2]` | Nm | Support torque to vehicle frame Fr1/Fr1A (x/y/z components) |
| `PT.Trq_Supp2BdyEng.x/y` | `<pre>.Trq_Supp2BdyEng[0]`<br/>`<pre>.Trq_Supp2BdyEng[1]` | Nm | Support torque to engine frame FrEng (x/y components) |
| `PT.W<pos>.rot` | `<preW>.rot` | rad | Rotation angle of wheel `<pos>` |
| `PT.W<pos>.rotv` | `<preW>.rotv` | rad/s | Rotation speed of wheel `<pos>` |
| `PT.W<pos>.Trq_B2W` | `<preW>.Trq_B2W` | Nm | Torque acting from brake to wheel `<pos>` |
| `PT.W<pos>.Trq_BrakeReg` | `<preW>.Trq_BrakeReg` | Nm | Estimated current regenerative brake torque at wheel `<pos>` (absolute value) |
| `PT.W<pos>.Trq_BrakeReg_max` | `<preW>.Trq_BrakeReg_max` | Nm | Estimated maximum possible regenerative brake torque at wheel `<pos>` (absolute value) |
| `PT.W<pos>.Trq_Drive` | `<preW>.Trq_Drive` | Nm | Drive torque of wheel `<pos>` |
| `PT.W<pos>.Trq_Supp2WC` | `<preW>.Trq_Supp2WC` | Nm | Drive torque support on wheel carrier `<pos>` |

### 26.12.2 Powertrain Control (PTControl)

#### Template Variables
- `<pre>` := PT.Control
- `<preIF>` := PowerTrain.ControlIF
- `<preIFGB>` := PowerTrain.ControlIF.GearBoxOut[i]

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.Clutch.<i>.Pos` | `<preIF>.ClutchOut[i].Pos` | - | Clutch target position |
| `<pre>.Clutch.<i>.rotv_out_trg` | `<preIF>.ClutchOut[i].rotv_out_trg` | rad/s | Clutch output shaft target rotation speed |
| `<pre>.Clutch.<i>.Trq_out_trg` | `<preIF>.ClutchOut[i].Trq_out_trg` | Nm | Clutch output shaft target torque |
| `<pre>.Clutch.<i>.Phase` | - | - | For Parallel P3 model. Current clutch phase of the decoupling clutch: 0:=Closed, 1:=Open, 2:=Clutch opening, 3:=Wait for ramp down of electric motor torque, 4:=Synchronize motor speed, 5:=Close Clutch |
| `<pre>.Clutch.Phase_trg` | - | - | For Parallel P3 model. Target clutch phase of the decoupling clutch: 0:=Closed, 1:=Open |
| `<pre>.Clutch.Phase_trg.SetManual` | - | - | For Parallel P3 model. Activate manual setting of the Clutch.Phase_trg: 0:=Off, 1:=On |
| `<pre>.Coasting.EngineOn` | - | - | Allows changing the Coasting mode during simulation: 0:=Engine Off Coasting, 1:=Engine On Coasting |
| `<pre>.Consump.Comb_E.Abs`<br/>`<pre>.Consump.Comb_E.Act`<br/>`<pre>.Consump.Comb_E.Avg` | - | kWh/100km | Combined consumption (fuel, low and high voltage battery) expressed as electric energy consumption: absolute, actual, average |
| `<pre>.Consump.Comb_F.Abs`<br/>`<pre>.Consump.Comb_F.Act`<br/>`<pre>.Consump.Comb_F.Avg` | - | l/100km | Combined consumption (fuel, low and high voltage battery) expressed as fuel consumption: absolute, actual, average |
| `<pre>.Consump.Elec.Abs`<br/>`<pre>.Consump.Elec.Act`<br/>`<pre>.Consump.Elec.Avg` | - | kWh/100km | Electric energy consumption (low and high voltage battery): absolute, actual, average |
| `<pre>.Consump.Fuel.Abs`<br/>`<pre>.Consump.Fuel.Act`<br/>`<pre>.Consump.Fuel.Avg` | - | l/100km | Fuel consumption: absolute, actual, average |
| `<pre>.Consump.Reset` | - | - | Reset the absolute and average consumption values (boolean) |
| `<pre>.Engine.FuelCutOff` | `<preIF>.EngineOut.FuelCutOff` | - | Flag if fuel is cut-off (boolean) |
| `<pre>.Engine.Load` | `<preIF>.EngineOut.Load` | - | Engine target load |
| `<pre>.Engine.rotv_trg` | `<preIF>.EngineOut.rotv_trg` | rad/s | Engine target rotation speed |
| `<pre>.Engine.set_ISC` | `<preIF>.EngineOut.set_ISC` | - | Idle speed controller activated (boolean) |
| `<pre>.Engine.Trq_trg` | `<preIF>.EngineOut.Trq_trg` | Nm | Engine target torque |
| `<pre>.GasInterpret.Trq_trg` | - | Nm | Target drive torque from gas pedal interpreter module |
| `<pre>.GB.<i>.Clutch.Pos` | `<preIFGB>.Clutch.Pos` | - | Gearbox internal clutch target position |
| `<pre>.GB.<i>.Clutch_dis.Pos` | `<preIFGB>.Clutch_dis.Pos` | - | Gearbox internal clutch target position for disengaged shaft of DCT gearbox |
| `<pre>.GB.<i>.Clutch.rotv_out_trg` | `<preIFGB>.Clutch.rotv_out_trg` | rad/s | Gearbox internal clutch output shaft target rotation speed |
| `<pre>.GB.<i>.Clutch_dis.rotv_out_trg` | `<preIFGB>.Clutch_dis.rotv_out_trg` | rad/s | Gearbox internal clutch output shaft target rotation speed for disengaged shaft of DCT gearbox |
| `<pre>.GB.<i>.Clutch.Trq_out_trg` | `<preIFGB>.Clutch.Trq_out_trg` | Nm | Gearbox internal clutch output shaft target torque |
| `<pre>.GB.<i>.Clutch_dis.Trq_out_trg` | `<preIFGB>.Clutch_dis.Trq_out_trg` | Nm | Gearbox internal clutch output shaft target torque for disengaged shaft of DCT gearbox |
| `<pre>.GB.<i>.GearNoTrg` | `<preIFGB>.GearNoTrg` | - | Gearbox target gear (integer) |
| `<pre>.GB.<i>.GearNoTrg_dis` | `<preIFGB>.GearNoTrg_dis` | - | Gearbox target gear (integer) for disengaged shaft of DCT gearbox |
| `<pre>.GB.<i>.rotv_in_trg` | `<preIFGB>.rotv_in_trg` | rad/s | Gearbox input shaft target rotation speed |
| `<pre>.GB.<i>.Trq_out_trg` | `<preIFGB>.Trq_out_trg` | Nm | Gearbox output shaft target torque |
| `<pre>.Ignition` | `<preIF>.Ignition` | - | Powertrain ignition (boolean) |
| `<pre>.ISG.Load`<br/>`<pre>.Motor<iM>.Load` | `<preIF>.ISGOut.Load`<br/>`<preIF>.MotorOut[iM].Load` | - | Integrated starter generator / electric motor `<iM>` target load |
| `<pre>.ISG.rotv_trg`<br/>`<pre>.Motor<iM>.rotv_trg` | `<preIF>.ISGOut.rotv_trg`<br/>`<preIF>.MotorOut[iM].rotv_trg` | rad/s | Integrated starter generator / electric motor `<iM>` target rotation speed |
| `<pre>.ISG.Trq_trg`<br/>`<pre>.Motor<iM>.Trq_trg` | `<preIF>.ISGOut.Trq_trg`<br/>`<preIF>.MotorOut[iM].Trq_trg` | Nm | Integrated starter generator / electric motor `<iM>` target torque |
| `<pre>.Motor.Trq_trg_AtPOI` | - | - | For Parallel P3 model. Target torque of the motor at the POI/reference point of the GasInterpreter |
| `<pre>.OperationError` | `<preIF>.OperationError` | - | Current operation error (integer) |
| `<pre>.OperationState` | `<preIF>.OperationState` | - | Current operation state (integer): 0:Absent, 1:Power off, 2:Power accessory, 3:Power on, 4:Driving |
| `<pre>.PwrExploited` | - | % | Ratio of exploited power (for visualization in IPGInstruments) |
| `<pre>.Battery.<LV/HV>.Temp_trg` | `<preIF>.Batt<LV/HV>Out.Temp_trg` | K | Battery target temperature |
| `<pre>.Battery.<LV/HV>.MassFlowCool_trg` | `<preIF>.Batt<LV/HV>Out.MassFlowCool_trg` | kg/s | Battery coolant target mass flow rate |
| `<pre>.PwrSupply.Pwr_HV1toLV_trg` | `<preIF>.PwrSupplyOut.Pwr_HV1toLV_trg` | W | Target transferred electric power from high voltage 1 electric circuit to low voltage electric circuit |
| `<pre>.StrategyMode` | `<preIF>.StrategyMode` | - | Current strategy mode (integer): 0:Start/Stop, 1:Regenerative brake, 2:Regenerative drag torque, 3:Coasting, 4:Electric drive, 5:LoadShift, 6:Assist, 7:Boost, 8:Engine drive, 9:Engine start, 10:Engine synchronization, 11:Engine stop |
| `<pre>.StrategyMode_trg` | - | - | Target strategy mode (integer) |
| `<pre>.StrategyMode_trg.SetManual` | - | - | Flag if target strategy mode can be set by DVA (boolean): 1=target strategy mode is set manually by DVA and not by PTControl |
| `<pre>.TrqRatio.Front2Rear` | - | - | For electrical and serial powertrain the ratio for torque distribution between the front and rear drive axle (0=all at rear axle....1=all at front axle) |

### 26.12.3 Engine Control Unit (ECU)

#### Template Variables
- `<pre>` := PowerTrain.EngineCU_IF

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `PT.ECU.Engine_on` | `<pre>.Engine_on` | - | Flag if engine is on (boolean) |
| `PT.ECU.FuelCutOff` | `<pre>.FuelCutOff` | - | Flag if fuel is cut-off (boolean) |
| `PT.ECU.Load` | `<pre>.Load` | - | Load/throttle signal for engine |
| `PT.ECU.Status` | `<pre>.Status` | - | ECU status (integer) |
| `PT.ECU.TrqDrag` | `<pre>.TrqDrag` | Nm | Engine drag torque at current rotation speed |
| `PT.ECU.TrqFull` | `<pre>.TrqFull` | Nm | Engine full torque at current rotation speed |
| `PT.ECU.TrqOpt` | `<pre>.TrqOpt` | Nm | Engine torque with optimum consumption at current rotation speed |
| `PT.ECU.Load_lim_min`<br/>`PT.ECU.Load_lim_max` | - | - | Output engine load for lower and upper limitation (only for model Basic). PT.ECU.Load_lim_min must be smaller than PT.ECU.Load_lim_max |
| `PT.ECU.Trq_lim_min`<br/>`PT.ECU.Trq_lim_max` | - | Nm | Target engine torque limitation (only for model Basic). PT.ECU.Trq_lim_min must be smaller than PT.ECU.Trq_lim_max |

### 26.12.4 Motor Control Unit (MCU) - Basic FOC

#### Template Variables
- `<pre>` := PowerTrain.MotorCU_IF
- `<preM>` := PT.MCU.Motor<iM>

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `PT.MCU.ISG.Load`<br/>`<preM>.Load` | `<pre>.ISGOut.Load`<br/>`<pre>.MotorOut[iM].Load` | - | Load signal for integrated starter generator / electric motor `<iM>` |
| `PT.MCU.ISG.TrqGen_max`<br/>`<preM>.TrqGen_max` | `<pre>.ISGOut.TrqGen_max`<br/>`<pre>.MotorOut[iM].TrqGen_max` | Nm | Integrated starter generator / electric motor `<iM>` maximum generator torque at current rotation speed |
| `PT.MCU.ISG.TrqMot_max`<br/>`<preM>.TrqMot_max` | `<pre>.ISGOut.TrqMot_max`<br/>`<pre>.MotorOut[iM].TrqMot_max` | Nm | Integrated starter generator / electric motor `<iM>` maximum motor torque at current rotation speed |
| `PT.MCU.Status` | `<pre>.Status` | - | MCU status (integer) |

#### Permanent Magnet Synchronous Motor (PMSM)

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `PT.MCU.ISG.Current_d_ref`<br/>`<preM>.Current_d_ref` | - | A | d coordinate of target rotary current vector |
| `PT.MCU.ISG.Current_q_ref`<br/>`<preM>.Current_q_ref` | - | A | q coordinate of target rotary current vector |
| `PT.MCU.ISG.Load_Volt_d`<br/>`<preM>.Load_Volt_d` | - | V | d coordinate of applied rotary voltage vector |
| `PT.MCU.ISG.Load_Volt_q`<br/>`<preM>.Load_Volt_q` | - | V | q coordinate of applied rotary voltage vector |
| `PT.MCU.ISG.PhiVolt`<br/>`<preM>.PhiVolt` | - | rad | Angle of applied rotary voltage vector |
| `PT.MCU.ISG.MagVolt`<br/>`<preM>.MagVolt` | - | V | Magnitude of applied rotary voltage vector |

### 26.12.5 Transmission Control Unit (TCU)

#### Template Variables
- `<pre>` := PowerTrain.TransmCU_IF
- `<preGB>` := PT.TCU.GB.<i>

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `PT.TCU.Clutch.Pos` | `<pre>.ClutchOut.Pos` | - | Separated clutch target position |
| `<preGB>.Clutch.Pos` | `<pre>.GearBoxOut[i].Clutch.Pos` | - | Internal clutch target position of gearbox and electric motor gearbox `<i>` (0=clutch closed, 1=clutch open) |
| `<preGB>.Clutch_dis.Pos` | `<pre>.GearBoxOut[i].Clutch_dis.Pos` | - | Internal clutch target position of gearbox for disengaged shaft of DCT |
| `<preGB>.GearNoTrg` | `<pre>.GearBoxOut[i].GearNoTrg` | - | Target gear of gearbox and electric motor gearbox `<i>` |
| `<preGB>.GearNoTrg_dis` | `<pre>.GearBoxOut[i].GearNoTrg_dis` | - | Target gear of gearbox for disengaged shaft of DCT gearbox |
| `<preGB>.i_trg` | `<pre>.GearBoxOut[i].i_trg` | - | Target gear ratio for CVT gearbox |
| `<preGB>.set_ParkBrake` | `<pre>.GearBoxOut[i].set_ParkBrake` | - | Set gearbox park brake of gearbox and electric motor gearbox `<iM>` |
| `<preGB>.Trq_DriveSrc_trg` | `<pre>.GearBoxOut[i].Trq_DriveSrc_trg` | Nm | Optional drive source target torque from TCU to PTControl (e.g. while shifting) |
| `PT.TCU.ShiftCtrl.<i>.ShiftAvoid_active` | - | - | Flag if shift avoidance is active separate for every gearbox |
| `PT.TCU.LockUp` | - | - | Lock-up clutch position of gearbox converter clutch with TCU "Automatic" or "Automatic with Converter": 0=no lockup, 1=lockup clutch closed |
| `PT.TCU.LockUp.PosFinal` | - | - | Specifies the position of the lockup clutch at the end of the synchronization process |
| `PT.TCU.LockUp.SynchronisationTime` | - | - | Specifies the time to close the lockup clutch |
| `PT.TCU.Status` | `<pre>.Status` | - | TCU status (integer) |
| `PT.TCU.DCT.PwrOnUp.RotvGradientTrg`<br/>`PT.TCU.DCT.PwrOnDown.RotvGradientTrg`<br/>`PT.TCU.DCT.PwrOffUp.RotvGradientTrg`<br/>`PT.TCU.DCT.PwrOffDown.RotvGradientTrg` | - | - | Specifies the desired engine rotational speed gradient during clutch synchronization |
| `PT.TCU.DCT.PwrOnUp.SyncTime`<br/>`PT.TCU.DCT.PwrOnDown.SyncTime`<br/>`PT.TCU.DCT.PwrOffUp.SyncTime`<br/>`PT.TCU.DCT.PwrOffDown.SyncTime` | - | s | Specifies the desired clutch synchronization time |

### 26.12.6 Battery Control Unit (BCU)

#### Template Variables
- `<pre>` := PowerTrain.BatteryCU_IF

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `PT.BCU.Batt<LV/HV>.SOC` | `<pre>.Batt<LV/HV>.SOC` | % | Low / high voltage battery state of charge |
| `PT.BCU.Batt<LV/HV>.SOH` | `<pre>.Batt<LV/HV>.SOH` | % | Low / high voltage battery state of health |
| `PT.BCU.Batt<LV/HV>.Temp_trg` | `<pre>.Batt<LV/HV>.Temp_trg` | K | Low / high voltage battery target temperature (only in case BCU PI temperature control is activated) |
| `PT.BCU.Batt<LV/HV>.TempCool_in` | `<pre>.Batt<LV/HV>.TempCool_in` | K | Low / high voltage battery coolant inlet temperature |
| `PT.BCU.Batt<LV/HV>.TempCool_out` | `<pre>.Batt<LV/HV>.TempCool_out` | K | Low / high voltage battery coolant outlet temperature |
| `PT.BCU.Batt<LV/HV>.MassFlowCool` | `<pre>.Batt<LV/HV>.MassFlowCool` | kg/s | Low / high voltage battery coolant mass flow rate |
| `PT.BCU.Status` | `<pre>.Status` | - | BCU status (integer) |

### 26.12.7 Engine

#### General

#### Template Variables
- `<pre>` := PowerTrain.Engine
- `<preIF>` := PowerTrain.EngineIF

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `PT.Engine.Control_Trq` | `<preIF>.Engine_Trq` | Nm | Engine control torque |
| `PT.Engine.be` | - | g/kWh | Specific fuel consumption of the engine |
| `PT.Engine.FuelFlow` | `<preIF>.FuelFlow` | l/s | Current fuel flow |
| `PT.Engine.FuelFlow_ext` | `<pre>.Fuel.Flow_ext` | l/s | External fuel flow (negative for fill up the fuel tank) |
| `PT.Engine.FuelLevel` | `<pre>.Fuel.Level` | % | Current fuel tank level |
| `PT.Engine.DVA.Trq`<br/>`PT.Engine.Sherpa.Trq` | - | Nm | Effective engine torque at output shaft used for engine model 'DVA' respectively 'Sherpa' |
| `PT.Engine.PwrO` | - | W | Engine output power |
| `PT.Engine.rot` | `<preIF>.rot` | rad | Rotation angle of engine output shaft |
| `PT.Engine.rotv` | `<preIF>.rotv` | rad/s | Rotational speed of engine output shaft |
| `PT.Engine.Trq` | `<preIF>.Trq` | Nm | Effective engine torque at output shaft |
| `PT.Engine.Trq_Ext2E` | `<pre>.Trq_Ext2E` | Nm | External torque to engine output shaft |
| `PT.Engine.Mapping.PwrCorr.Fac` | - | - | Engine power/torque correction factor depending on environment conditions |

#### Intake Manifold Pressure

#### Template Variables
- `<pre>` := PowerTrain.Engine.Mapping.IMP

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.dm_cyl` | - | kg/s | Air mass flow in the engine cylinders |
| `<pre>.dm_thr` | - | kg/s | Air mass flow after throttle |
| `<pre>.dpres_im` | - | Pa/s | Intake manifold pressure derivation |
| `<pre>.alpha` | - | - | Throttle loss coefficient |
| `<pre>.lambda` | - | - | Intake manifold relative filling |
| `<pre>.psi` | - | - | Flow coefficient |
| `<pre>.pres_im` | - | Pa | Intake manifold pressure |
| `<pre>.relrho_im` | - | - | Intake manifold relative pressure (used for Linear2D) |

### 26.12.8 Integrated Starter Generator / Electric Motor - Permanent Magnet Synchronous Motor (PMSM)

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `PT.MotorISG.PwrElec`<br/>`PT.Motor<iM>.PwrElec` | `PowerTrain.ISG_IF.PwrElec`<br/>`PowerTrain.MotorIF[iM].PwrElec` | W | Actual electric power of integrated starter generator / electric motor `<iM>` |
| `PT.MotorISG.Ratio`<br/>`PT.Motor<iM>.Ratio` | `PowerTrain.ISG_IF.CfgIF->Ratio`<br/>`PowerTrain.MotorIF[iM].CfgIF->Ratio` | - | Transmission ratio of the integrated starter generator / electric motor `<iM>` between the motor output shaft and the powertrain shaft that it is connected to |
| `PT.MotorISG.rot`<br/>`PT.Motor<iM>.rot` | `PowerTrain.ISG_IF.rot`<br/>`PowerTrain.MotorIF[iM].rot` | rad | Actual output shaft rotation angle of integrated starter generator / electric motor `<iM>` |
| `PT.MotorISG.rotv`<br/>`PT.Motor<iM>.rotv` | `PowerTrain.ISG_IF.rotv`<br/>`PowerTrain.MotorIF[iM].rotv` | rad/s | Actual output shaft rotation speed of integrated starter generator / electric motor `<iM>` |
| `PT.MotorISG.Trq`<br/>`PT.Motor<iM>.Trq` | `PowerTrain.ISG_IF.Trq`<br/>`PowerTrain.MotorIF[iM].Trq` | Nm | Actual torque on driven shaft of integrated starter generator / electric motor `<iM>` |
| `PT.MotorISG.VoltBatt`<br/>`PT.Motor<iM>.VoltBatt` | `PowerTrain.ISG_IF.VoltBatt`<br/>`PowerTrain.MotorIF[iM].VoltBatt` | V | Electric grid voltage at integrated starter generator / electric motor `<iM>` |
| `PT.MotorISG.Voltage_d`<br/>`PT.Motor<iM>.Voltage_d` | `PowerTrain.ISG_IF.Voltage_dq[0]`<br/>`PowerTrain.MotorIF[iM].Voltage_dq[0]` | V | d coordinate of applied voltage |
| `PT.MotorISG.Voltage_q`<br/>`PT.Motor<iM>.Voltage_q` | `PowerTrain.ISG_IF.Voltage_dq[1]`<br/>`PowerTrain.MotorIF[iM].Voltage_dq[1]` | V | q coordinate of applied voltage |
| `PT.MotorISG.Voltage_u/v/w`<br/>`PT.Motor<iM>.Voltage_u/v/w` | `PowerTrain.ISG_IF.Voltage_uvw[0/1/2]`<br/>`PowerTrain.MotorIF[iM].Voltage_uvw[0/1/2]` | V | u/v/w coordinates of applied voltage |
| `PT.MotorISG.Current_d`<br/>`PT.Motor<iM>.Current_d` | `PowerTrain.ISG_IF.Current_dq[0]`<br/>`PowerTrain.MotorIF[iM].Current_dq[0]` | A | d coordinate of motor current |
| `PT.MotorISG.Current_q`<br/>`PT.Motor<iM>.Current_q` | `PowerTrain.ISG_IF.Current_dq[1]`<br/>`PowerTrain.MotorIF[iM].Current_dq[1]` | A | q coordinate of motor current |
| `PT.MotorISG.Current_u/v/w`<br/>`PT.Motor<iM>.Current_u/v/w` | `PowerTrain.ISG_IF.Current_uvw[0/1/2]`<br/>`PowerTrain.MotorIF[iM].Current_uvw[0/1/2]` | A | u/v/w coordinates of motor current |
| `PT.MotorISG.rotv_el`<br/>`PT.Motor<iM>.rotv_el` | - | rad/s | Rotational speed of the electric rotary vector |
| `PT.MotorISG.PwrMech`<br/>`PT.Motor<iM>.PwrMech` | - | W | Mechanical motor output power |

### 26.12.9 Clutch

#### Template Variables
- `<preIF>` := PowerTrain.ClutchIF[i]
- `<pre>` := PT.Clutch.<i>

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.i_TrqIn2Out` | `<pre>.i_TrqIn2Out` | - | Current ratio clutch input shaft torque to output shaft torque (estimated) |
| `<pre>.DVA.Trq_A2B` | - | Nm | Torque transferred from clutch input to output side used for clutch model 'DVA' |
| `<pre>.PwrI` | - | W | Clutch input power |
| `<pre>.PwrO` | - | W | Clutch output power |
| `<pre>.rot_in` | `<preIF>.rot_in` | rad | Rotation angle of clutch input shaft |
| `<pre>.rot_out` | `<preIF>.rot_out` | rad | Rotation angle of clutch output shaft |
| `<pre>.rotv_in` | `<preIF>.rotv_in` | rad/s | Rotational speed of clutch input shaft |
| `<pre>.rotv_out` | `<preIF>.rotv_out` | rad/s | Rotational speed of clutch output shaft |
| `<pre>.Trq_in` | `<preIF>.Trq_in` | Nm | Clutch input shaft torque |
| `<pre>.Trq_out` | `<preIF>.Trq_out` | Nm | Clutch output shaft torque |

### 26.12.10 GearBox

#### Template Variables
- `<pre>` := PT.Gearbox.<i>
- `<preIF>` := PowerTrain.GearBoxIF[i]
- `<preGB>` := PowerTrain.GearBox[i]

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.DVA.i` | - | - | Current user defined transmission ratio used for gearbox model 'DVA' |
| `<pre>.Clutch.i_TrqIn2Out` | `<preIF>.ClutchOut.i_TrqIn2Out` | - | Ratio between gearbox clutch input shaft and output shaft (estimated) |
| `<pre>.Clutch_dis.i_TrqIn2Out` | `<preIF>.Clutch_dis_Out.i_TrqIn2Out` | - | Ratio between gearbox clutch input shaft and output shaft (estimated) for disengaged shaft of DCT gearbox |
| `<pre>.Clutch.rotv_in` | `<preIF>.ClutchOut.rotv_in` | rad/s | Current gearbox clutch input shaft rotation speed |
| `<pre>.Clutch_dis.rotv_in` | `<preIF>.Clutch_dis_Out.rotv_in` | rad/s | Current gearbox clutch input shaft rotation angle for disengaged shaft of DCT gearbox |
| `<pre>.Clutch.rotv_out` | `<preIF>.ClutchOut.rotv_out` | rad/s | Current gearbox clutch output shaft rotation speed |
| `<pre>.Clutch_dis.rotv_out` | `<preIF>.Clutch_dis_Out.rotv_out` | rad/s | Current gearbox clutch output shaft rotation speed for disengaged shaft of DCT gearbox |
| `<pre>.Clutch.Trq_in` | `<preIF>.ClutchOut.Trq_in` | Nm | Current gearbox clutch input shaft torque |
| `<pre>.Clutch_dis.Trq_in` | `<preIF>.Clutch_dis_Out.Trq_in` | Nm | Current gearbox clutch input shaft torque for disengaged shaft of DCT gearbox |
| `<pre>.Clutch.Trq_out` | `<preIF>.ClutchOut.Trq_out` | Nm | Current gearbox clutch output shaft torque |
| `<pre>.Clutch_dis.Trq_out` | `<preIF>.Clutch_dis_Out.Trq_out` | Nm | Current gearbox clutch output shaft torque for disengaged shaft of DCT gearbox |
| `<pre>.Auto_AMT.SyncTime` | - | ms | Gearbox synchronization time for the AMT gearbox |
| `<pre>.Auto_Conv.SyncTime` | - | ms | Gearbox synchronization time for the Automatic with Converter gearbox |
| `<pre>.CVT.didt` | - | 1/s | Current gearbox ratio change rate for gearbox model CVT |
| `<pre>.CVT.efficiency` | - | - | Current gearbox efficiency for gearbox model CVT |
| `<pre>.GearNo` | `PowerTrain.IF.GearNo` | - | Current gear (integer) |
| `<pre>.GearNo_dis` | `<preIF>.GearNo_dis` | - | Current gear of disengaged shaft (integer) for DCT |
| `<pre>.i` | `<preIF>.i` | - | Current transmission ratio |
| `<pre>.i_Ext` | `<preGB>.i_Ext` | - | Additional user defined external transmission ratio |
| `<pre>.i_TrqIn2Out` | `<preIF>.i_TrqIn2Out` | - | Current gearbox transmission ratio considering loss |
| `<pre>.Inert_ExtIn` | `<preGB>.Inert_ExtIn` | kgm2 | Additional external inertia to gearbox input shaft |
| `<pre>.Inert_ExtOut` | `<preGB>.Inert_ExtOut` | kgm2 | Additional external inertia to gearbox output shaft |
| `<pre>.Inert_out` | `<preIF>.Inert_out` | kgm2 | Gearbox output shaft inertia |
| `<pre>.PwrI` | - | W | Gearbox input power |
| `<pre>.PwrO` | - | W | Gearbox output power |
| `<pre>.rot_in` | `<preIF>.rot_in` | rad | Rotation angle of gearbox input shaft |
| `<pre>.rot_out` | `<preIF>.rot_out` | rad | Rotation angle of gearbox output shaft |
| `<pre>.rotv_in` | `<preIF>.rotv_in` | rad/s | Rotational speed of gearbox input shaft |
| `<pre>.rotv_out` | `<preIF>.rotv_out` | rad/s | Rotational speed of gearbox output shaft |
| `<pre>.Trq_Ext2GB_In` | `<preGB>.Trq_Ext2GB_In` | Nm | External torque to gearbox input shaft (in front of the internal clutch) |
| `<pre>.Trq_Ext2GB_Out` | `<preGB>.Trq_Ext2GB_Out` | Nm | External torque to gearbox output shaft |
| `<pre>.Trq_in` | `<preIF>.Trq_in` | Nm | Current gearbox input shaft torque |
| `<pre>.Trq_out` | `<preIF>.Trq_out` | Nm | Current gearbox output shaft torque |

### 26.12.11 Free End

#### Template Variables
- `<pre>` := PT.FreeEnd.<Id>
- `<preIF>` := PowerTrain.FreeEnd_IF[Id]

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.Trq_in` | `<preIF>.Trq_in` | Nm | Input torque to the free end model |
| `<pre>.rotv` | `<preIF>.rotv` | rad/s | Free end shaft rotation speed |
| `<pre>.rot` | `<preIF>.rot` | rad | Free end shaft rotation angle |
| `<pre>.Trq_ext` | `<preIF>.Trq_ext` | Nm | Additional external torque that can be applied to the free spinning shaft |

### 26.12.12 Driveline

#### General

#### Template Variables
- `<pre>` := PowerTrain.DriveLine
- `<preIF>` := PowerTrain.DriveLineIF
- `<preDS>` := PT.DL.DriveSrc.<ds>
- `<pos>` := FL, FR, RL, RR

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preDS>.i_D2W<pos>` | `<preIF>.DriveOut[ds].i_D2W[pos]` | - | Drive source `<ds>` current ratio: drive source to wheel `<pos>` (estimated) |
| `<preDS>.rot_in` | `<preIF>.DriveOut[ds].rot_in` | rad | Drive source `<ds>` input rotation angle |
| `<preDS>.rotv_in` | `<preIF>.DriveOut[ds].rotv_in` | rad/s | Drive source `<ds>` input rotation speed |
| `<preDS>.Trq_in` | `<preIF>.DriveIn[ds].Trq_in` | Nm | Drive source `<ds>` input torque |
| `<preDS>.Trq_ext` | `<pre>.Trq_Ext2DriveSrc[ds]` | Nm | Additional external input torque at outshaft of drive source `<ds>` |
| `PT.DL.iDiff_mean` | `PowerTrain.IF.DL_iDiff_mean` | - | Driveline mean differential ratio (overrides the value from the initialization if non zero) |

#### Generic Models

##### Template Variables
- `<Diff>` := FDiff, RDiff, CDiff

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `PT.Gen.DL.<Diff>.DVA.Trq_A2B` | - | Nm | Torque transferred from A to B at differential (for coupling model 'DVA') |
| `PT.Gen.DL.<Diff>.PwrI` | - | W | Differential input power |
| `PT.Gen.DL.<Diff>.PwrO` | - | W | Differential output power |
| `PT.Gen.DL.<Diff>.rotv_in` | - | rad/s | Rotation speed of differential input shaft |
| `PT.Gen.DL.<Diff>.Trq_Cpl2B` | - | Nm | Torque from differential coupling model to shaft B |
| `PT.Gen.DL.<Diff>.Trq_Input` | - | Nm | Torque to differential input shaft (without external torque) |
| `PT.Gen.DL.<Diff>.Trq_in_ext` | - | Nm | External torque to differential input shaft |
| `PT.Gen.DL.<Diff>.TrqRatio` | - | - | Torque ratio at differential used for coupling mode 'TrqVec' |
| `PT.Gen.DL.CDiff.GearNo` | - | - | Current gear number of center differential if there exists more than one gears (integer) |
| `PT.Gen.DL.HangOn.drotv_Diff2o` | - | rad/s | Delta rotation speed between input and output shaft |
| `PT.Gen.DL.HangOn.DVA.Trq_A2B` | - | Nm | Torque transferred from A to B at hangon clutch (for coupling model 'DVA') |
| `PT.Gen.DL.HangOn.PwrI` | - | W | Hangon clutch input power |
| `PT.Gen.DL.HangOn.PwrO` | - | W | Hangon clutch output power |
| `PT.Gen.DL.HangOn.Trq_Cpl2B` | - | Nm | Torque from hangon clutch coupling model to shaft B (output) |

##### Template Variables (Flexible Shafts)
- `<Diff>` := FDiff, RDiff, CDiff
- `<Shaft>` := HalfShaftR, HalfShaftL, DriveShaft

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `PT.Gen.DL.<Diff>.<Shaft>.q` | - | rad | Torsion angle of the flexible shaft |
| `PT.Gen.DL.<Diff>.<Shaft>.qp` | - | rad/s | Angular velocity of the flexible shaft |
| `PT.Gen.DL.<Diff>.<Shaft>.qpp` | - | rad/s2 | Angular acceleration of the flexible shaft |
| `PT.Gen.DL.<Diff>.<Shaft>.Trq_sd` | - | Nm | Torque output of the flexible shaft |

### 26.12.13 Power Supply

#### General

#### Template Variables
- `<pre>` := PowerTrain.PowerSupplyIF

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `PT.BattLV.AOC`<br/>`PT.BattHV.AOC` | `<pre>.BattLV.AOC`<br/>`<pre>.BattHV.AOC` | Ah | Low / high voltage battery actual amount of charge |
| `PT.BattLV.Current`<br/>`PT.BattHV.Current` | `<pre>.BattLV.Current`<br/>`<pre>.BattHV.Current` | A | Low / high voltage battery electric current |
| `PT.BattLV.Energy`<br/>`PT.BattHV.Energy` | `<pre>.BattLV.Energy`<br/>`<pre>.BattHV.Energy` | kWh | Low / high voltage battery remaining energy capacity |
| `PT.BattLV.Pwr_max`<br/>`PT.BattHV.Pwr_max` | `<pre>.BattLV.Pwr_max`<br/>`<pre>.BattHV.Pwr_max` | W | Low / high voltage battery maximum charge/discharge power |
| `PT.BattLV.Temp`<br/>`PT.BattHV.Temp` | `<pre>.BattLV.Temp`<br/>`<pre>.BattHV.Temp` | K | Low / high voltage battery temperature |
| `PT.BattLV.Volt_oc`<br/>`PT.BattHV.Volt_oc` | - | V | Low / high voltage battery open circuit voltage (with the model 'Chen') |

#### Additional Quantities for BattECM

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `PT.Batt<LV/HV>.Volt_oc` | - | V | Low / high voltage battery open circuit voltage |
| `PT.Batt<LV/HV>.SOC` | - | - | Low / high voltage battery state of charge |
| `PT.Batt<LV/HV>.BattAOC` | - | Ah | Low / high voltage battery unscaled (sub-pack level) amount of charge |
| `PT.Batt<LV/HV>.BattVolt` | - | V | Low / high voltage battery unscaled (sub-pack level) voltage |
| `PT.Batt<LV/HV>.BattCurrent` | - | A | Low / high voltage battery unscaled (sub-pack level) current |
| `PT.Batt<LV/HV>.BattEnergy` | - | Wh | Low / high voltage battery unscaled (sub-pack level) remaining load of energy |
| `PT.Batt<LV/HV>.BattPwr` | - | W | Low / high voltage battery unscaled (sub-pack level) power |
| `PT.Batt<LV/HV>.PackChargeConsump` | - | Ah | Low / high voltage battery scaled (pack level) charge consumption |
| `PT.Batt<LV/HV>.PackEnergyConsump` | - | kWh | Low / high voltage battery scaled (pack level) energy consumption |
| `PT.Batt<LV/HV>.Pwr_ohmic` | - | W | Low / high voltage battery scaled (pack level) ohmic power loss (if thermal model is set) |
| `PT.Batt<LV/HV>.R0` | - | Ohm | Low / high voltage battery ECM electric resistance (if R0 is set) |
| `PT.Batt<LV/HV>.RC<i>.R` | - | Ohm | Low / high voltage battery electric resistance of RC elements (if RC<i> element is set) |
| `PT.Batt<LV/HV>.RC<i>.C` | - | F | Low / high voltage battery electric capacity of RC elements (if RC<i> element is set) |
| `PT.Batt<LV/HV>.RC<i>.Voltage` | - | V | Low / high voltage battery voltage of RC elements (if RC<i> element is set) |

#### Power Supply

#### Template Variables
- `<pre>` := PowerTrain.PowerSupply
- `<preIF>` := PowerTrain.PowerSupplyIF
- `<prePS>` := PT.PwrSupply

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<prePS>.Eta_HV1toHV2` | `<preIF>.Eta_HV1toHV2` | - | DC/DC efficiency from high voltage 1 electric circuit to high voltage 2 electric circuit |
| `<prePS>.Eta_HV1toLV` | `<preIF>.Eta_HV1toLV` | - | DC/DC efficiency from high voltage 1 electric circuit to low voltage electric circuit |
| `<prePS>.HV1.Pwr`<br/>`<prePS>.HV2.Pwr` | `<preIF>.Pwr_HV1`<br/>`<preIF>.Pwr_HV2` | W | Total electric power (generators and consumers) on high voltage 1 / 2 electric circuit |
| `<prePS>.LV.Pwr` | `<preIF>.Pwr_LV` | W | Total electric power (generators and consumers) on low voltage electric circuit |
| `<prePS>.HV1.Pwr_aux`<br/>`<prePS>.HV2.Pwr_aux` | `<pre>.Pwr_HV1_aux`<br/>`<pre>.Pwr_HV2_aux` | W | Additional external electric power (generators and consumers) on high voltage 1 / 2 electric circuit |
| `<prePS>.LV.Pwr_aux` | `<pre>.Pwr_LV_aux` | W | Additional external electric power (generators and consumers) on low voltage electric circuit |
| `<prePS>.HV1.Voltage`<br/>`<prePS>.HV2.Voltage` | `<preIF>.Voltage_HV1`<br/>`<preIF>.Voltage_HV2` | V | High voltage 1 / 2 electric circuit actual voltage |
| `<prePS>.LV.Voltage` | `<preIF>.Voltage_LV` | V | Low voltage electric circuit actual voltage |
| `<prePS>.Pwr_HV1toHV2` | `<preIF>.Pwr_HV1toHV2` | W | Actual transferred electric power from high voltage 1 circuit to high voltage 2 circuit |
| `<prePS>.Pwr_HV1toHV2_max` | `<preIF>.Pwr_HV1toHV2_max` | W | Maximum possible transferred electric power from high voltage 1 electric circuit to high voltage 2 electric circuit |
| `<prePS>.Pwr_HV1toLV` | `<preIF>.Pwr_HV1toLV` | W | Actual transferred electric power from high voltage 1 circuit to low voltage circuit |
| `<prePS>.Pwr_HV1toLV_max` | `<preIF>.Pwr_HV1toLV_max` | W | Maximum possible transferred electric power from high voltage 1 electric circuit to low voltage electric circuit |

## 26.13 Power Flow Calculation

### 26.13.1 PowerDelta

#### Template Variables
- `<pos>` := FL, FR, RL, RR

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `PwrD.Aero.Drag` | `PowerDelta.Aero.Drag` | W | PowerDelta due to aerodynamic drag force |
| `PwrD.Aero.Lift` | `PowerDelta.Aero.Lift` | W | PowerDelta due to aerodynamic lift force |
| `PwrD.Aero.Pitch` | `PowerDelta.Aero.Pitch` | W | PowerDelta due to aerodynamic pitch moment |
| `PwrD.Aero.Roll` | `PowerDelta.Aero.Roll` | W | PowerDelta due to aerodynamic roll moment |
| `PwrD.Aero.Side` | `PowerDelta.Aero.Side` | W | PowerDelta due to aerodynamic side force |
| `PwrD.Aero.Total` | `PowerDelta.Aero.Total` | W | Total aerodynamic PowerDelta |
| `PwrD.Aero.Yaw` | `PowerDelta.Aero.Yaw` | W | PowerDelta due to aerodynamic yaw moment |
| `PwrD.Brake.Total` | `PowerDelta.Brake_Total` | W | Total brake PowerDelta |
| `PwrD.Brake.Total<pos>` | `PowerDelta.Brake[i].Total` | W | PowerDelta due to brake at wheel `<pos>` |
| `PwrD.Grvt` | `PowerDelta.Grvt` | W | PowerDelta due to road inclination (gravity) |
| `PwrD.Hitch.Frc_x/y/z` | `PowerDelta.Hitch.Frc_x/y/z` | W | PowerDelta due to hitch forces |
| `PwrD.Hitch.Total` | `PowerDelta.Hitch.Total` | W | Total trailer hitch PowerDelta |
| `PwrD.Hitch.Trq_x/y/z` | `PowerDelta.Hitch.Trq_x/y/z` | W | PowerDelta due to hitch torques |
| `PwrD.Inert_Chassis` | `PowerDelta.Inert_Chassis` | W | PowerDelta due to inertia of the vehicle body |
| `PwrD.PT.Battery_LV` | `PowerDelta.PT.Battery_LV` | W | PowerDelta for the low voltage battery |
| `PwrD.PT.Battery_HV` | `PowerDelta.PT.Battery_HV` | W | PowerDelta for the high voltage battery |
| `PwrD.PT.CDiff` | `PowerDelta.PT.CDiff` | W | PowerDelta for the central differential |
| `PwrD.PT.Clutch.<i>` | `PowerDelta.PT.Clutch[i]` | W | PowerDelta for the clutch |
| `PwrD.PT.DriveLine` | `PowerDelta.PT.DriveLine` | W | PowerDelta for the total driveline (all differentials + hang-on clutch + shafts) |
| `PwrD.PT.Engine` | `PowerDelta.PT.Engine` | W | PowerDelta for the engine |
| `PwrD.PT.FDiff` | `PowerDelta.PT.FDiff` | W | PowerDelta for the front differential |
| `PwrD.PT.Gearbox<i>` | `PowerDelta.PT.GearBox[i]` | W | PowerDelta for the gearbox |
| `PwrD.PT.HangOn` | `PowerDelta.PT.HangOn` | W | PowerDelta for the hang-on clutch |
| `PwrD.PT.Inert` | `PowerDelta.PT.Inert` | W | PowerDelta due to inertia of the powertrain components (engine, clutch) not passed to driveline |
| `PwrD.PT.Inert_DL` | `PowerDelta.PT.Inert_DL` | W | PowerDelta due to inertia of the driveline |
| `PwrD.PT.ISG` | `PowerDelta.PT.ISG` | W | PowerDelta for the starter generator ISG |
| `PwrD.PT.Motor`<br/>`PwrD.PT.Motor<iM>` | `PowerDelta.PT.Motor[iM]` | W | PowerDelta for the electric motor iM |
| `PwrD.PT.PlanetGear` | `PowerDelta.PT.PlanetGear` | W | PowerDelta for the planet gearbox (only in PowerSplit powertrain) |
| `PwrD.PT.PowerSupply` | `PowerDelta.PT.PowerSupply` | W | PowerDelta for the power supply |
| `PwrD.PT.RDiff` | `PowerDelta.PT.RDiff` | W | PowerDelta for the rear differential |
| `PwrD.PT.Shafts` | `PowerDelta.PT.Shafts` | W | PowerDelta for all shafts torques |
| `PwrD.PT.Spring_DL` | `PowerDelta.PT.Spring_DL` | W | PowerDelta due to shaft spring torque in the flexible driveline |
| `PwrD.PT.Total` | `PowerDelta.PT.Total` | W | Total powertrain PowerDelta |
| `PwrD.Susp.Buffer<pos>` | `PowerDelta.Susp[i].Buffer` | W | PowerDelta due to the buffer of suspension `<pos>` |
| `PwrD.Susp.Damper<pos>` | `PowerDelta.Susp[i].Damper` | W | PowerDelta due to damper of suspension `<pos>` |
| `PwrD.Susp.Spring<pos>` | `PowerDelta.Susp[i].Spring` | W | PowerDelta due to the spring of suspension `<pos>` |
| `PwrD.Susp.Stabi<pos>` | `PowerDelta.Susp[i].Stabi` | W | PowerDelta due to the stabi of suspension `<pos>` |
| `PwrD.Susp.Total` | `PowerDelta.Susp_Total` | W | Total suspension PowerDelta |
| `PwrD.Susp.Total<pos>` | `PowerDelta.Susp[i].Total` | W | Total suspension PowerDelta of suspension `<pos>` |
| `PwrD.Tire.CambDefl<pos>` | `PowerDelta.Tire[i].CambDefl` | W | PowerDelta due to camber deflection of tire `<pos>` |
| `PwrD.Tire.LatSlip<pos>` | `PowerDelta.Tire[i].LatSlip` | W | PowerDelta due to lateral slip of tire `<pos>` |
| `PwrD.Tire.LongSlip<pos>` | `PowerDelta.Tire[i].LongSlip` | W | PowerDelta due to longitudinal slip of tire `<pos>` |
| `PwrD.Tire.RollResist<pos>` | `PowerDelta.Tire[i].RollResist` | W | PowerDelta due to rolling resistance of tire `<pos>` |
| `PwrD.Tire.ToeSlip<pos>` | `PowerDelta.Tire[i].ToeSlip` | W | PowerDelta due to toe slip of tire `<pos>` |
| `PwrD.Tire.Total` | `PowerDelta.Tire_Total` | W | Total tire PowerDelta |
| `PwrD.Tire.Total<pos>` | `PowerDelta.Tire[i].Total` | W | Total tire PowerDelta of tire `<pos>` |
| `PwrD.Tire.VertDefl<pos>` | `PowerDelta.Tire[i].VertDefl` | W | PowerDelta due to vertical deflection of tire `<pos>` |
| `PwrD.Total` | `PowerDelta.Total` | W | Total PowerDelta (power loss/gain) |

### 26.13.2 PowerLoss

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `PwrL.Aero` | `PowerLoss.Aero` | W | Total power loss due to aerodynamics |
| `PwrL.Brake` | `PowerLoss.Brake` | W | Total power loss in the brakes |
| `PwrL.Grvt` | `PowerLoss.Grvt` | W | Total power loss due to road inclination |
| `PwrL.Hitch` | `PowerLoss.Hitch` | W | Total power loss due to trailer hitch forces |
| `PwrL.Inert_Chassis` | `PowerLoss.Inert_Chassis` | W | Total power loss due to inertia of vehicle body |
| `PwrL.PT` | `PowerLoss.PT` | W | Total power loss in the powertrain |
| `PwrL.Susp` | `PowerLoss.Susp` | W | Total power loss in the suspensions |
| `PwrL.Tire` | `PowerLoss.Tire` | W | Total power loss in the tires |
| `PwrL.Total` | `PowerLoss.Total` | W | Total power loss |

### 26.13.3 PowerStore

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `PwrS.Aero` | `PowerStore.Aero` | W | Total power store due to aerodynamics |
| `PwrS.Brake` | `PowerStore.Brake` | W | Total power store in the brakes |
| `PwrS.Grvt` | `PowerStore.Grvt` | W | Total power store due to road inclination |
| `PwrS.Hitch` | `PowerStore.Hitch` | W | Total power store due to trailer hitch forces |
| `PwrS.Inert_Chassis` | `PowerStore.Inert_Chassis` | W | Total power store due to inertia of vehicle body |
| `PwrS.PT` | `PowerStore.PT` | W | Total power store in the powertrain |
| `PwrS.Susp` | `PowerStore.Susp` | W | Total power store in the suspensions |
| `PwrS.Tire` | `PowerStore.Tire` | W | Total power store in the tires |
| `PwrS.Total` | `PowerStore.Total` | W | Total power store |
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
# User Accessible Quantities: Trailer

## 26.15 Trailer

### 26.15.1 General

#### Template Variables and Notation
- `<pos>` := FL, FR, RL, RR (wheel positions)
- `<part>` := Buf, Damp, Spring, Stabi (component types)
- `<preSC>` := `Tr.SuspControl<j>`
- `<j>` = 0, 1, 2, 3, 4 (control unit number)
- `<preParaFric>` := `Tr.Parasitic.Friction`
- `<preParaStiff>` := `Tr.Parasitic.Stiffness`
- `<i>` := 0, 1
- Twin := used by the quantities for a twin wheel (describes the inner tire)

#### Aerodynamic Quantities

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Aero.Frc_1.x/y/z` | `Fr1` | N | Aerodynamic force acting on trailer |
| `Tr.Aero.tau_1` | `Fr1` | rad | Angle of incidence |
| `Tr.Aero.tau2_1` | `Fr1` | rad | Angle of incidence (shifted by 2π) |
| `Tr.Aero.Trq_1.x/y/z` | `Fr1` | Nm | Aerodynamic torque acting on trailer |
| `Tr.Aero.vres_1.x/y/z` | `Fr1` | m/s | Relative wind velocity |

#### Acceleration and Translation

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.alHori` | `Trailer.ConBdy1.alHori` | m/s² | Horizontal lateral acceleration |
| `Tr.atHori` | `Trailer.ConBdy1.atHori` | m/s² | Horizontal tangential acceleration |
| `Tr.ax/y/z` | `Trailer.ConBdy1.a_0[0]`/`[1]`/`[2]` | m/s² | Trailer acceleration (Fr1) |

#### Brake Torques

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Brake.Trq_<pos>_ext` | `TrBrake.Trq_ext[i]` | Nm | External brake torque |
| `Tr.Brake.Trq_<pos>_tot` | `TrBrake.Trq_tot[i]` | Nm | Total brake torque |
| `Tr.Brake.Trq_PB_<pos>` | `TrBrake.IF.Trq_PB[i]` | Nm | Parking brake torque |
| `Tr.Brake.Trq_Reg_trg_<pos>` | `TrBrake.IF.Trq_Reg_trg[i]` | Nm | Regenerative brake target torque |
| `Tr.Brake.Trq_WB_<pos>` | `TrBrake.IF.Trq_WB[i]` | Nm | Wheel brake torque |

#### Buffer Forces

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Buffer<pos>.Frc.q<i>` | - | N | Buffer force due to generalized coordinate `<i>` |
| `Tr.Buffer<pos>.Frc_tot` | - | N | Total buffer force |
| `Tr.Buffer<pos>.l` | - | m | Buffer length at `<pos>` (total) |
| `Tr.Buffer<pos>.l_com` | - | m | Buffer length at `<pos>` (by compliance) |
| `Tr.Buffer<pos>.l_ext` | - | m | Buffer length at `<pos>` (external, offset) |
| `Tr.Buffer<pos>.l_kin` | - | m | Buffer length at `<pos>` (by kinematics) |

#### Camber Angle

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Camber<pos>` | `Trailer.Tire[i].Camber` | rad | Camber angle (ISO 8855:2011, 7.1.17) |
| `Tr.CamberTwin<pos>` | `Trailer.TwinTire[i].Camber` | rad | Camber angle (Twin wheel) |

#### Control Body Acceleration

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Con.ax_1/y_1/z_1` | `Trailer.ConBdy1.a_1[0]`/`[1]`/`[2]` | m/s² | Translational acceleration of center of mass in vehicle frame (Fr1) |
| `Tr.Con.ax/y/z` | `Trailer.ConBdy1.a_0[0]`/`[1]`/`[2]` | m/s² | Translational acceleration of center of mass in global frame (Fr0) |

#### Control Body Translation

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Con.tx/y/z` | `Trailer.ConBdy1.t_0[0]`/`[1]`/`[2]` | m | Translation of center of mass in global frame (Fr0) |
| `Tr.Con.v` | `Trailer.ConBdy1.v` | m/s | Velocity of center of mass |
| `Tr.Con.vHori` | `Trailer.ConBdy1.vHori` | m/s | Horizontal trailer velocity (ISO 8855:2011, 5.1.5) |

#### Control Body Velocity

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Con.vx_1/y_1/z_1` | `Trailer.ConBdy1.v_1[0]`/`[1]`/`[2]` | m/s | Translational velocity of center of mass in vehicle frame (Fr1) |
| `Tr.Con.vx/y/z` | `Trailer.ConBdy1.v_0[0]`/`[1]`/`[2]` | m/s | Translational velocity of center of mass in global frame (Fr0) |

#### Wheel Carrier Center Point

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.C.a_0.x/y/z` | `Tr.SuspMod[i].WC_a_0[0]`/`[1]`/`[2]` | m/s² | Acceleration of carrier center point in Fr0 |
| `Tr.C<pos>.AxleFrc` | - | N | Total vertical force on axle `<pos>` |
| `Tr.C<pos>.C.t_0.x/y/z` | - | m | Translation of carrier center point at `<pos>` in Fr0 |
| `Tr.C<pos>.C.v_0.x/y/z` | - | m/s | Velocity of carrier center point at `<pos>` in Fr0 |

#### Wheel Carrier Forces

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.Frc2C_1.x/y/z` | - | N | Total force to wheel carrier at `<pos>` in vehicle frame (Fr1) |
| `Tr.C<pos>.Frc2C_2.x/y/z` | - | N | Total force to wheel carrier at `<pos>` in wheel frame (Fr2) |
| `Tr.C<pos>.Frc2CExt_0.x/y/z` | - | N | External forces to wheel carrier at `<pos>` in global frame (Fr0) |
| `Tr.C<pos>.Frc2CExt_1.x/y/z` | - | N | External forces to wheel carrier at `<pos>` in vehicle frame (Fr1) |
| `Tr.C<pos>.Frc2CExt_2.x/y/z` | - | N | External forces to wheel carrier at `<pos>` in wheel frame (Fr2) |

#### Generalized Coordinates

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.GenFrc0` | - | N | Generalized force at coordinate `<i>` = 0 |
| `Tr.C<pos>.GenFrc1` | - | N | Generalized force at coordinate `<i>` = 1 |
| `Tr.C<pos>.GenInert0` | - | kg | Generalized inertia at coordinate `<i>` = 0 |
| `Tr.C<pos>.GenInert1` | - | kg | Generalized inertia at coordinate `<i>` = 1 |

#### Component Length Changes

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.l<part>_dq<i>` | - | m | Change of length of `<part>` at `<pos>` in direction of generalized coordinate `<i>` (Fr1) |

#### Maggi-Matrix Elements

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.Maggi0.x/y/z` | - | - | Elements of "Maggi-Matrix": describes relation between coordinate q0 and wheel carrier rotation (Fr1) |
| `Tr.C<pos>.Maggi1.x/y/z` | - | - | Elements of "Maggi-Matrix": describes relation between coordinate q1 and wheel carrier rotation (Fr1) |

#### Wheel Contact Point

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.P.t_0.x/y/z` | - | m | Coordinates of wheel road contact point P (Fr0) |
| `Tr.C<pos>.Twin.P.t_0.x/y/z` | - | m | Coordinates of wheel road contact point P for twin wheel (Fr0) |
| `Car.C<pos>.P.v01_W.x/y/z` | - | m/s | Velocity of tire contact point in FrW |
| `Car.C<pos>.Twin.P.v01_W.x/y/z` | - | m/s | Velocity of tire contact point for twin wheel in FrW |

#### Generalized Coordinates q

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.q<i>` | - | m | Generalized coordinate `q<i>` (displacement) |
| `Tr.C<pos>.q<i>p` | - | m/s | Generalized coordinate `q<i>` (velocity) |
| `Tr.C<pos>.q<i>pp` | - | m/s² | Generalized coordinate `q<i>` (acceleration) |

#### Carrier Rotation by Compliance

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.rx_com/y_com/z_com` | - | rad | Rotation of carrier `<pos>` at reference point by compliance (Fr1, rotation sequence ZYX) |

#### Carrier Rotation Change

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.rx_dq<i>/y_dq<i>/z_dq<i>` | - | rad/m | Rotation of wheel carrier at `<pos>` in direction of generalized coordinate `<i>` |

#### External Carrier Rotation

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.rx_ext/y_ext/z_ext` | - | rad | Rotation of carrier `<pos>` at reference point external, offset (Fr1, rotation sequence ZYX) |

#### Carrier Rotation by Kinematics

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.rx_kin/y_kin/z_kin` | - | rad | Rotation of carrier `<pos>` at reference point by kinematics (Fr1, rotation sequence ZYX) |

#### Total Carrier Rotation

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.rx/y/rz` | `Trailer.SuspMod[i].r_zxy[0]`/`[1]`/`[2]` | rad | Total rotation of carrier `<pos>` at reference point (Fr1, rotation sequence ZXY) |

#### External Rotational Velocity

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.rxv_ext/ryv_ext/rzv_ext` | - | rad/s | External rotational velocity of carrier reference point (Fr1, rotation sequence ZXY) |

#### Rotational Velocity by Kinematics

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.rxv/ryv/rzv` | - | rad/s | Rotational velocity of carrier reference point by kinematics (Fr1, rotation sequence ZXY) |

#### Tire Forces and Torques

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.Tire.FrcC.x/y/z` | - | N | Tire force to wheel carrier (Fr2) |
| `Tr.C<pos>.Tire.TrqC.x/y/z` | - | Nm | Tire torque to wheel carrier (Fr2) |

#### Torques to Wheel Carrier

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.Trq2C_1.x/y/z` | - | Nm | Total torque to wheel carrier at `<pos>` in vehicle frame (Fr1) |
| `Tr.C<pos>.Trq2C_2.x/y/z` | - | Nm | Total torque to wheel carrier at `<pos>` in wheel frame (Fr2) |
| `Tr.C<pos>.Trq2CExt_1.x/y/z` | - | Nm | External torques to wheel carrier at `<pos>` defined in Fr1 |
| `Tr.C<pos>.Trq2CExt_2.x/y/z` | - | Nm | External torques to wheel carrier at `<pos>` defined in Fr2 |

#### Brake and Gyroscopic Torques

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.Trq_B2C` | - | Nm | Brake torque at wheel carrier `<pos>` after reduction |
| `Tr.C<pos>.TrqGyro_2.x/z` | - | Nm | Gyroscopic torque to carrier at `<pos>` defined in Fr2 |
| `Tr.C<pos>.Trq_T2W` | - | Nm | Tire torque around wheel spin axis at `<pos>` |
| `Tr.C<pos>.Twin.Trq_T2W` | - | Nm | Tire torque around wheel spin axis at `<pos>` (Twin wheel) |

#### Carrier Translation by Compliance

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.tx_com/y_com/z_com` | - | m | Translation of carrier reference point at `<pos>` by compliance (Fr1) |

#### Carrier Translation Change

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.tx_dq<i>/y_dq<i>/z_dq<i>` | - | m | Translation of wheel carrier at `<pos>` in direction of generalized coordinate `<i>` (Fr1) |

#### External Carrier Translation

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.tx_ext/y_ext/z_ext` | - | m | Translation of carrier reference point at `<pos>` external, offset (Fr1) |

#### Carrier Translation by Kinematics

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.tx_kin/y_kin/z_kin` | - | m | Translation of carrier reference point at `<pos>` by kinematics (Fr1) |

#### Total Carrier Translation

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.tx/y/tz` | `Trailer.SuspMod[i].t[0]`/`[1]`/`[2]` | m | Total translation of carrier reference point at `<pos>` (Fr1) |

#### External Velocity of Carrier

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.txv_ext/tyv_ext/tzv_ext` | - | m/s | External velocity of carrier reference point (Fr1) |

#### Velocity of Carrier by Kinematics

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.C<pos>.txv/tyv/tzv` | - | m/s | Velocity of carrier reference point by kinematics (Fr1) |

#### Damper Forces

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Damp<pos>.Frc_tot.q<i>` | - | N | Damper force due to generalized coordinate `<i>` |
| `Tr.Damp<pos>.Frc` | - | N | Damper force (internal) |
| `Tr.Damp<pos>.Frc_ext` | - | N | Damper force (external) |
| `Tr.Damp<pos>.Frc_tot` | - | N | Damper force (total) |

#### Damper Length

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Damp<pos>.l` | - | m | Damper length (total) |
| `Tr.Damp<pos>.l_com` | - | m | Damper length (by compliance) |
| `Tr.Damp<pos>.l_ext` | - | m | Damper length (external, offset) |
| `Tr.Damp<pos>.l_kin` | - | m | Damper length (by kinematics) |
| `Tr.Damp<pos>.v` | - | m/s | Damper velocity |

#### Fr1 Frame Acceleration

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Fr1.ax/y/z` | `Trailer.Fr1_a_0[0]`/`[1]`/`[2]` | m/s² | Translational acceleration of Fr1 in global frame (Fr0) |

#### Fr1 Frame Rotation Speed

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Fr1.rvx/vy/vz` | `Trailer.Fr1_rv_zyx[0]`/`[1]`/`[2]` | rad | Trailer rotation speed (Cardan angles: rz=Yaw, ry=Pitch, rx=Roll per ISO 8855:2011) |

#### Fr1 Frame Rotation Angles

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Fr1.rx/y/z` | `Trailer.Fr1_r_zyx[0]`/`[1]`/`[2]` | rad | Trailer rotation angles (Cardan angles per ISO 8855:2011, 5.2.1, 5.2.2, 5.2.3) |

#### Fr1 Frame Position

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Fr1.tx/y/z` | `Trailer.Fr1_t_0[0]`/`[1]`/`[2]` | m | Position of Fr1 in global frame |

#### Fr1 Frame Velocity

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Fr1.vx/y/z` | `Trailer.Fr1_v_0[0]`/`[1]`/`[2]` | m/s | Velocity of Fr1 in global frame |

#### Tire Forces in Wheel Frame

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Fx<pos>/Fy<pos>/Fz<pos>` | `Trailer.Tire[i].Frc_W[0]`/`[1]`/`[2]` | N | Longitudinal, lateral and vertical ground reaction force at wheel/road contact point (FrW) |
| `Tr.FxTwin<pos>/FyTwin<pos>/FzTwin<pos>` | `Trailer.TwinTire[i].Frc_W[0]`/`[1]`/`[2]` | N | Longitudinal, lateral and vertical ground reaction force at twin wheel/road contact point (FrW) |

#### Hitch Rotation

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Hitch.dr_0.x/y/z` | - | rad | Rotational angle difference between vehicle and trailer in hitch point (Fr0) |

#### Hitch Translation

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Hitch.dt_0.x/y/z` | - | m | Position difference between vehicle and trailer in hitch point (Fr0) |

#### Hitch Force to Trailer in Hitch Frame

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Hitch.Frc2Tr.x_1/y_1/z_1` | - | N | Hitch force from car to trailer (Fr1 for semi-trailer or FrDrw for drawbar trailer) |

#### External Hitch Force

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Hitch.Frc2TrExt.x_1/y_1/z_1` | `Trailer.Hitch.Frc2TrExt_1[0]`/`[1]`/`[2]` | N | External, user-defined hitch force to trailer (Fr1 for semi-trailer or FrDrw for drawbar trailer) |

#### Hitch Force in Global Frame

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Hitch.Frc2Tr.x/y/z` | `Trailer.Hitch.Frc2Tr_0[0]`/`[1]`/`[2]` | N | Total hitch force from car to trailer in global frame (Fr0) |

#### Hitch Torque to Trailer in Hitch Frame

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Hitch.Trq2Tr.x_1/y_1/z_1` | - | Nm | Hitch torque from car to trailer (Fr1 for semi-trailer or FrDrw for drawbar trailer) |

#### External Hitch Torque

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Hitch.Trq2TrExt.x_1/y_1/z_1` | `Trailer.Hitch.Trq2TrExt_1[0]`/`[1]`/`[2]` | Nm | External, user-defined hitch torque to trailer (Fr1 for semi-trailer or FrDrw for drawbar trailer) |

#### Hitch Torque in Global Frame

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Hitch.Trq2Tr.x/y/z` | `Trailer.Hitch.Trq2Tr_0[0]`/`[1]`/`[2]` | Nm | Total hitch torque from car to trailer in global frame (Fr0) |

#### Hitch Position and Velocity

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Hitch.tx/y/z` | `Trailer.Hitch.t_0[0]`/`[1]`/`[2]` | m | Hitch position in global frame (Fr0) |
| `Tr.Hitch.vx/y/z` | `Trailer.Hitch.v_0[0]`/`[1]`/`[2]` | m/s | Hitch velocity in global frame (Fr0) |

#### Inclination Angle

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.InclinAngle<pos>` | `Trailer.Tire[i].InclinAngle` | rad | Inclination angle of wheel at `<pos>` (ISO 8855:2011, 7.1.16) |
| `Tr.InclinAngleTwin<pos>` | `Trailer.TwinTire[i].InclinAngle` | rad | Inclination angle of twin wheel at `<pos>` (ISO 8855:2011, 7.1.16) |

#### Longitudinal Slip

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.LongSlip<pos>` | `Trailer.Tire[i].LongSlip` | - | Longitudinal slip of wheel `<pos>` |
| `Tr.LongSlipTwin<pos>` | `Trailer.TwinTire[i].LongSlip` | - | Longitudinal slip of twin wheel `<pos>` |

#### Road Friction Coefficient

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.muRoad<pos>` | `Tr.Tire[i].muRoad` | - | Road friction coefficient at tire `<pos>` |
| `Tr.muRoadTwin<pos>` | `Tr.TwinTire[i].muRoad` | - | Road friction coefficient at twin tire `<pos>` |

#### Parasitic Friction Force

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preParaFric><pos>.Frc_tot` | - | N | Parasitic friction force |
| `<preParaFric><pos>.Frc_tot.q<i>` | - | N | Generalized force for coordinate q0 due to parasitic friction force |

#### Parasitic Stiffness Force

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preParaStiff><pos>.Frc_tot` | - | N | Parasitic stiffness force |
| `<preParaStiff><pos>.Frc_tot.q<i>` | - | N | Generalized force for coordinate q0 due to parasitic stiffness force |

#### Pitch Angle

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Pitch` | `Trailer.Pitch` | rad | Pitch angle of the trailer (ISO 8855:2011, 5.2.2). Positive if front goes down and rear comes up |
| `Tr.PitchAcc` | `Trailer.PitchAcc` | rad/s² | Pitch angle acceleration (ISO 8855:2011, 5.2.2) |
| `Tr.PitchVel` | `Trailer.PitchVel` | rad/s | Pitch angle velocity (ISO 8855:2011, 5.2.2) |

#### Roll Angle

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Roll` | `Trailer.Roll` | rad | Roll angle of the trailer (ISO 8855:2011, 5.2.3). Positive if right side goes down and left comes up |
| `Tr.RollAcc` | `Trailer.RollAcc` | rad/s² | Roll angle acceleration (ISO 8855:2011, 5.2.3) |
| `Tr.RollVel` | `Trailer.RollVel` | rad/s | Roll angle velocity (ISO 8855:2011, 5.2.3) |

#### Sideslip Angle

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.SideSlipAngle` | `Trailer.ConBdy1.SideSlipAngle` | rad | Sideslip angle (ISO 8855:2011, 5.2.9) |
| `Tr.SideSlipAngle2` | `Trailer.ConBdy1.SideSlipAngle2` | rad | Sideslip angle with offset of 2π |
| `Tr.SideSlipAngleVel` | `Trailer.ConBdy1.SideSlipAngleVel` | rad/s | Sideslip angle velocity (ISO 8855:2011, 5.2.9) |

#### Simulation Phase

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.SimPhase` | - | - | Simulation phase (integer) |

#### Slip Angle

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.SlipAngle<pos>` | `Trailer.Tire[i].SlipAngle` | rad | Slip angle at `<pos>` |
| `Tr.SlipAngleTwin<pos>` | `Trailer.TwinTire[i].SlipAngle` | rad | Slip angle at twin wheel `<pos>` |

#### Spring Forces

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Spring<pos>.Frc_tot.q<i>` | - | N | Spring force due to generalized coordinate `<i>` |
| `Tr.Spring<pos>.Frc` | - | N | Spring force (internal) |
| `Tr.Spring<pos>.Frc_ext` | - | N | Spring force (external) |
| `Tr.Spring<pos>.Frc_tot` | - | N | Spring force (total) |

#### Spring Length

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Spring<pos>.l` | - | m | Spring length (total) |
| `Tr.Spring<pos>.l_com` | - | m | Spring length (by compliance) |
| `Tr.Spring<pos>.l_ext` | - | m | Spring length (external, offset) |
| `Tr.Spring<pos>.l_kin` | - | m | Spring length (by kinematics) |

#### Stabilizer Forces

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Stabi<pos>.Frc_tot.q<i>` | - | N | Stabilizer force due to generalized coordinate `<i>` |
| `Tr.Stabi<pos>.Frc` | - | N | Stabilizer force (internal) |
| `Tr.Stabi<pos>.Frc_ext` | - | N | Stabilizer force (external) |
| `Tr.Stabi<pos>.Frc_tot` | - | N | Stabilizer force (total) |

#### Stabilizer Length

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Stabi<pos>.l` | - | m | Stabilizer length (total) |
| `Tr.Stabi<pos>.l_com` | - | m | Stabilizer length (by compliance) |
| `Tr.Stabi<pos>.l_ext` | - | m | Stabilizer length (external, offset) |
| `Tr.Stabi<pos>.l_kin` | - | m | Stabilizer length (by kinematics) |

#### Suspension Control Unit Output

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<preSC>.Buffer<pos>.CtrlOut` | - | - | Trailer suspension control unit output signal for buffer component at wheel carrier `<pos>`. Value NOTSET = -99999 means no buffer control signal |
| `<preSC>.BufferCtrlOutOpt.<i>` | - | - | Optional output signal number `<i>` for buffer component (NOTSET = -99999 means not available, not available for FMU) |
| `<preSC>.BufferCtrlInOpt.<i>` | - | - | Optional input signal number `<i>` for buffer component (NOTSET = -99999 means not available, not available for FMU) |
| `<preSC>.Damper<pos>.CtrlOut` | - | - | Trailer suspension control unit output signal for damper component at wheel carrier `<pos>` (NOTSET = -99999 means no signal) |
| `<preSC>.DamperCtrlOutOpt.<i>` | - | - | Optional output signal number `<i>` for damper component (NOTSET = -99999 means not available, not available for FMU) |
| `<preSC>.DamperCtrlInOpt.<i>` | - | - | Optional input signal number `<i>` for damper component (NOTSET = -99999 means not available, not available for FMU) |
| `<preSC>.Spring<pos>.CtrlOut` | - | - | Trailer suspension control unit output signal for spring force component at wheel carrier `<pos>` (NOTSET = -99999 means no signal) |
| `<preSC>.SpringCtrlOutOpt.<i>` | - | - | Optional output signal number `<i>` for spring component (NOTSET = -99999 means not available, not available for FMU) |
| `<preSC>.SpringCtrlInOpt.<i>` | - | - | Optional input signal number `<i>` for spring component (NOTSET = -99999 means not available, not available for FMU) |
| `<preSC>.Stabi<pos>.CtrlOut` | - | - | Trailer suspension control unit output signal for stabi component at wheel carrier `<pos>` (NOTSET = -99999 means no signal) |
| `<preSC>.StabiCtrlOutOpt.<i>` | - | - | Optional output signal number `<i>` for stabi component (NOTSET = -99999 means not available, not available for FMU) |
| `<preSC>.StabiCtrlInOpt.<i>` | - | - | Optional input signal number `<i>` for stabi component (NOTSET = -99999 means not available, not available for FMU) |
| `<preSC>.SystemCtrlOutOpt.<i>` | - | - | Optional additional output signal number `<i>` for force system (NOTSET = -99999 means not available, not available for FMU) |
| `<preSC>.SystemCtrlInOpt.<i>` | - | - | Optional additional input signal number `<i>` for force system (NOTSET = -99999 means not available, not available for FMU) |

#### Toe Angle

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Toe<pos>` | `Tr.SuspMod[i].Toe` | rad | Toe angle (ISO 8855:2011, 7.1.6). Positive if front section turned toward vehicle's longitudinal center plane |
| `Tr.ToeTwin<pos>` | `Tr.SuspMod[i].Toe` | rad | Toe angle for twin wheel (ISO 8855:2011, 7.1.6) |

#### Tire Torques

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.TrqAlign<pos>` | `Trailer.Tire[i].Trq_W[2]` | Nm | Aligning torque in tire road contact point (FrW) |
| `Tr.TrqAlignTwin<pos>` | `Trailer.TwinTire[i].Trq_W[2]` | Nm | Aligning torque in tire road contact point for twin wheel (FrW) |
| `Tr.Trq_Ext2Whl<pos>` | `Trailer.Tire[i].Trq_Ext2W` | Nm | External torque around wheel spin axis. Used as: `Wheel_rota = (Trq_Brake2Wheel + Trq_Ext2Wheel + Trq_Tire2W) / lyy` |
| `Tr.TrqOvert<pos>` | `Trailer.Tire[i].Trq_W[0]` | Nm | Overturning torque in tire road contact point (FrW) |
| `Tr.TrqOvertTwin<pos>` | `Trailer.TwinTire[i].Trq_W[0]` | Nm | Overturning torque in tire road contact point for twin wheel (FrW) |
| `Tr.TrqRoll<pos>` | `Trailer.Tire[i].Trq_W[1]` | Nm | Rolling torque in tire road contact point (FrW) |
| `Tr.TrqRollTwin<pos>` | `Trailer.TwinTire[i].Trq_W[1]` | Nm | Rolling torque in tire road contact point for twin wheel (FrW) |

#### Turn Slip

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.TurnSlip<pos>` | `Trailer.Tire[i].TurnSlip` | 1/m | Turn slip at `<pos>` |
| `Tr.TurnSlipTwin<pos>` | `Trailer.TwinTire[i].TurnSlip` | 1/m | Turn slip at twin wheel `<pos>` |

#### Trailer Position and Velocity

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.tx/y/z` | `Trailer.ConBdy1.t_0[0]`/`[1]`/`[2]` | m | Trailer translation in global frame (Fr0) |
| `Tr.v` | `Trailer.ConBdy1.v` | m/s | Trailer velocity |
| `Tr.vx/y/z` | `Trailer.ConBdy1.v_0[0]`/`[1]`/`[2]` | m/s | Trailer velocity in vehicle frame (Fr1) |

#### Virtual Forces

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Virtual.Frc_0.x/y/z` | `Trailer.Virtual.Frc_0[0]`/`[1]`/`[2]` | N | External virtual force acting to trailer body in global frame (Fr0) |
| `Tr.Virtual.Frc_1.x/y/z` | `Trailer.Virtual.Frc_1[0]`/`[1]`/`[2]` | N | External virtual force acting to trailer body in vehicle frame (Fr1) |

#### Virtual Torques

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Virtual.Trq_0.x/y/z` | `Trailer.Virtual.Trq_0[0]`/`[1]`/`[2]` | Nm | External virtual torque acting to trailer body in global frame (Fr0) |
| `Tr.Virtual.Trq_1.x/y/z` | `Trailer.Virtual.Trq_1[0]`/`[1]`/`[2]` | Nm | External virtual torque acting to trailer body in vehicle frame (Fr1) |

#### Wheel Velocity

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.v<pos>` | `Trailer.Tire[i].v` | m/s | Wheel velocity (based on wheel rotation and wheel radius) |
| `Tr.vTwin<pos>` | `Trailer.TwinTire[i].v` | m/s | Twin wheel velocity (based on wheel rotation and wheel radius) |

#### Tire Contact Point Velocity

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.vx<pos>` | `Trailer.Tire[i].P_vel_W[0]` | m/s | Longitudinal velocity of tire contact point (FrW) |
| `Tr.vxTwin<pos>` | `Trailer.TwinTire[i].P_vel_W[0]` | m/s | Longitudinal velocity of twin tire contact point (FrW) |
| `Tr.vy<pos>` | `Trailer.Tire[i].P_vel_W[1]` | m/s | Lateral velocity of tire contact point (FrW) |
| `Tr.vyTwin<pos>` | `Trailer.TwinTire[i].P_vel_W[1]` | m/s | Lateral velocity of twin tire contact point (FrW) |
| `Tr.vz<pos>` | `Trailer.Tire[i].P_vel_W[2]` | m/s | Vertical velocity of tire contact point (FrW) |
| `Tr.vzTwin<pos>` | `Trailer.TwinTire[i].P_vel_W[2]` | m/s | Vertical velocity of twin tire contact point (FrW) |

#### Wheel Speed

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.WheelSpd_<pos>` | `Trailer.Tire[i].WheelSpd` | rad/s | Wheel rotation speed at `<pos>` |
| `Tr.WheelSpd_Twin<pos>` | `Trailer.TwinTire[i].WheelSpd` | rad/s | Wheel rotation speed at twin wheel `<pos>` |
| `Tr.WheelTurnSpd_<pos>` | `Trailer.Tire[i].WheelTurnSpd` | rad/s | Wheel turning speed at `<pos>` |

#### Wheel Radius

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.W<pos>.Radius` | `Trailer.Tire[i].WRadius` | m | Wheel radius at `<pos>` |
| `Tr.W<pos>.Twin.Radius` | `Trailer.TwinTire[i].WRadius` | m | Twin wheel radius at `<pos>` |

#### Wheel Rotation

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.W<pos>.rot` | `Trailer.Tire[i].rot` | rad | Wheel rotation around wheel spin axis at `<pos>` |

#### Yaw Angle

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Yaw` | `Trailer.Yaw` | rad | Yaw angle (ISO 8855:2011, 5.2.1). Angle between X-axis of trailer and X-axis of earth fixed system. Positive for positive rotation around Z-axis |
| `Tr.YawAcc` | `Trailer.YawAcc` | rad/s² | Yaw angle acceleration (ISO 8855:2011, 5.2.1) |
| `Tr.YawVel` | `Trailer.YawVel` | rad/s | Yaw angle velocity (ISO 8855:2011, 5.2.1) |

---

### 26.15.2 Trailer Load

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Load.<i>.mass` | `Trailer.Load[i].mass` | kg | Mass of load number `<i>` |
| `Tr.Load.<i>.tx` | `Trailer.Load[i].tx` | m | Position of i-th load in vehicle frame (x-coordinate, Fr1) |
| `Tr.Load.<i>.ty` | `Trailer.Load[i].ty` | m | Position of i-th load in vehicle frame (y-coordinate, Fr1) |
| `Tr.Load.<i>.tz` | `Trailer.Load[i].tz` | m | Position of i-th load in vehicle frame (z-coordinate, Fr1) |

---

### 26.15.3 Trailer Uncoupling

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `Tr.Hitch.Virtual.Active` | `Trailer.HitchVirt.Active` | - | Activate virtual hitch (boolean) |
| `Tr.Hitch.Virtual.Amplify` | `Trailer.HitchVirt.Amplify` | - | Amplification factor for virtual hitch forces |
| `Tr.Hitch.Virtual.tx/ty/tz` | `Trailer.HitchVirt.Vhcl.t_0` | m | Position of virtual hitch (Fr0) |
| `Tr.Hitch.Virtual.vx/vy/vz` | `Trailer.HitchVirt.Vhcl.v_0` | m/s | Velocity of virtual hitch (Fr0) |
| `Tr.Hitch.Virtual.rx/ry/rz` | `Trailer.HitchVirt.Vhcl.r_zyx` | rad | Orientation of virtual hitch (Fr0) |
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
