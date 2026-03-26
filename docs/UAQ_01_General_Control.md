
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
| `LatCtrl.Lines.<LineId>.exists` | - | - | Flag if priority/standard line (<LineId>=PrioL, PrioR, StdL, StdR) exists |