# User Accessible Quantities: Car

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
