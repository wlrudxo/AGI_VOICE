# CarMaker-Simulink Slalom/MPC Connection Scan

Date: 2026-06-06

## Goal

Find the shortest practical path from the current CarMaker Slalom18m scenario to
a Simulink/MATLAB MPC steering controller.

## Local Install Searched

```text
C:\IPG\carmaker\win64-15.0.1
/mnt/c/IPG/carmaker/win64-15.0.1
```

Current CarMaker project:

```text
E:\CarMakerProject\AGI
/mnt/e/CarMakerProject/AGI
```

## Slalom Examples Found

Official handling examples:

```text
Data\TestRun\Examples\VehicleDynamics\Handling\Slalom18m
Data\TestRun\Examples\VehicleDynamics\Handling\Slalom18m_AMS
Data\TestRun\Examples\VehicleDynamics\Handling\Slalom36m
```

Other slalom-related examples:

```text
Data\TestRun\Examples\BasicFunctions\TestAutomation\TestManager\Runs\Slalom18m
Data\TestRun\Examples\BasicFunctions\TestAutomation\TestWare\DemoPackage\Runs\Slalom_18m
Data\TestRun\Examples\BasicFunctions\TestAutomation\TestWare\DemoPackage\Scripts\SlalomTest.tcl
Data\TestRun\Examples\BasicFunctions\VehicleModel\MBS\MBS_Slalom_36m
Data\TestRun\Examples\BasicFunctions\VehicleModel\Steering\Pfeffer_Slalom_18m
```

No direct `Slalom + Simulink MPC` ready-made TestRun was found in the local
CarMaker examples.

## Simulink Examples Found

Main folder:

```text
Data\TestRun\Examples\BasicFunctions\Simulink
```

Relevant TestRun candidates:

```text
Hockenheim_UserSteer
Hockenheim_UserSteer_RTW
LaneChange_ISO_ESP
Hockenheim_SingleTrack
Hockenheim_SingleTrack_RTW
Hockenheim_UserSteerTorque
Hockenheim_UserBrake
TractCtrl
```

Relevant model templates:

```text
Templates\Car4SL_Extras\src_cm4sl\UserSteer.mdl
Templates\Car4SL_Extras\src_cm4sl\UserSteerTorque.mdl
Templates\Car4SL_Extras\src_cm4sl\SingleTrack.mdl
Templates\Car4SL_Extras\src_cm4sl\HydBrakeCU_ESP.mdl
Templates\RTW\src\UserSteer_RTW.mdl
Templates\RTW\src\SingleTrack_RTW.mdl
Templates\RTW\src\ESP_RTW.mdl
```

## Best Candidate: UserSteer CM4SL

TestRun:

```text
Data\TestRun\Examples\BasicFunctions\Simulink\Hockenheim_UserSteer
```

Important lines from the TestRun:

```text
Description:
    To be used with the UserSteer_CM4SL Simulink model.
Vehicle = Examples/DemoCar_UserSteer_CM4SL
DrivMan.Man.0.LatStep.0.Dyn = Driver 0
```

Vehicle file:

```text
Data\Vehicle\Examples\DemoCar_UserSteer_CM4SL
```

Important vehicle keys:

```text
Steering.Kind = CM4SL
Steering.SInputKind = Angle
Steering.PrefByDriver = Angle
```

Interpretation:

- This is the cleanest official example for replacing the steering system with
  a Simulink-side steering-angle controller.
- It is more directly relevant to lateral MPC than the ESP, traction-control,
  or powertrain examples.
- The current Slalom18m TestRun can keep its road, pylon geometry, friction,
  driver task, and output quantities while switching the vehicle to a
  `DemoCar_UserSteer_CM4SL`-style vehicle.

## Other Candidate Roles

`LaneChange_ISO_ESP`:

- Useful as a Simulink vehicle-control example with ESP/brake control.
- Not the shortest route for steering MPC because it targets brake/ESP rather
  than steering-angle control.

`Hockenheim_SingleTrack`:

- Useful if the research switches to a simplified vehicle model.
- Not preferred for the first experiment because the current baseline uses the
  full `Examples/DemoCar` vehicle.

`Hockenheim_UserSteer_RTW`:

- Useful later if compiled RTW deployment is required.
- Not preferred for the first experiment; CM4SL is better for fast model
  iteration and MATLAB/MPC tuning.

## Current AGI Project State

AGI project has a CM4SL folder:

```text
E:\CarMakerProject\AGI\src_cm4sl
/mnt/e/CarMakerProject/AGI/src_cm4sl
```

Confirmed present after setup:

```text
src_cm4sl\generic.mdl
src_cm4sl\ACC.mdl
src_cm4sl\UserSteer.mdl
Data\Vehicle\Examples\DemoCar_UserSteer_CM4SL
```

Original research Slalom18m TestRun used:

```text
Vehicle = Examples/DemoCar
```

UserSteer variants now use:

```text
Vehicle = Examples/DemoCar_UserSteer_CM4SL
```

## Recommended Implementation Path

1. Copy the official `UserSteer.mdl` model into the AGI project `src_cm4sl`.
2. Copy `Data\Vehicle\Examples\DemoCar_UserSteer_CM4SL` into the AGI project.
3. Create a new TestRun variant, for example:

```text
LLM_MPC_BO/ICCAS_Slalom18m_UserSteer_CM4SL
```

4. Keep the Slalom18m road/friction/output quantities unchanged.
5. Change only the vehicle reference:

```text
Vehicle = Examples/DemoCar_UserSteer_CM4SL
```

6. Open MATLAB with working directory:

```text
E:\CarMakerProject\AGI\src_cm4sl
```

7. Open `UserSteer.mdl`, verify that `cmenv.m` initializes CarMaker for
   Simulink, and run the official Hockenheim UserSteer example first if needed.
8. Replace the effective steering-angle signal in `UserSteer.mdl` with a
   minimal pass-through or bounded controller smoke test.
9. Run `ICCAS_Slalom18m_UserSteer_CM4SL` and verify that the Simulink steering
   signal affects the vehicle.
10. Insert the MATLAB MPC block/controller after the smoke test works.

## MPC Integration Notes

Use available CarMaker quantities/signals already confirmed in ERG:

```text
Car.Road.Path.DevDist
Car.Road.Path.DevAng
Car.v
Car.YawRate
Vhcl.YawRate
DM.Steer.Ang
DM.Steer.AngVel
```

Initial MPC should output steering angle or steering command compatible with:

```text
Steering.SInputKind = Angle
Steering.PrefByDriver = Angle
```

Important implementation correction confirmed by smoke testing:

```text
VehicleControlUpd out3
  -> CreateBus VhclCtrl.Steering
  -> VhclCtrl Steering Ang
```

The effective first override point is downstream of `VehicleControlUpd`, inside
or immediately before `CreateBus VhclCtrl.Steering`. Setting only
`VhclCtrl Steering Ang` to zero makes the vehicle drive straight, confirming
that this is the practical steering command channel for the first MPC version.

The earlier idea of modifying the `CreateBus VhclCtrl` output before
`VehicleControlUpd` did not affect the final steering output in the current
model, even when `-disablevehiclecontrol` was set.

The BO-tuned parameters should remain MATLAB/Simulink workspace parameters so
the trial runner can edit them before each simulation.

## Decision

Proceed with the `UserSteer CM4SL` path first. It is the closest official
CarMaker-Simulink bridge for steering MPC on the existing Slalom18m scenario.
