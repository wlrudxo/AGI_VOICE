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
