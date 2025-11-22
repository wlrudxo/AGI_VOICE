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
