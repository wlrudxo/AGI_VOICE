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
