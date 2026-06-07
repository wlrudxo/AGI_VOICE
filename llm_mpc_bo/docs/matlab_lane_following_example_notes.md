# MATLAB Lane Following MPC Example Notes

## Local Example

Source inspected:

```text
C:\Users\user\OneDrive\문서\MATLAB\Examples\R2025a\mpc\LaneFollowingUsingNMPCExample
```

Important files:

```text
LaneFollowingUsingNMPCExample.m
LaneFollowingUsingNMPCData.m
LaneFollowingStateFcn.m
LaneFollowingStateJacFcn.m
LaneFollowingGetCurvature.m
LaneFollowingNMPC.slx
```

## What Is Useful for This Research

The example is a nonlinear MPC lane-following controller. Its most useful part
for the CarMaker slalom work is not the NLMPC solver itself, but the vehicle
state convention and bicycle lateral model:

```text
states:
  Vy          lateral velocity
  yaw_rate    yaw rate
  Vx          longitudinal velocity
  Vx_dot      longitudinal acceleration
  e1          lateral deviation
  e2          relative yaw angle
  xOD         output disturbance

inputs:
  acceleration
  steering angle
  road curvature * Vx
  unmeasured disturbance
```

For the current CarMaker slalom setup, the longitudinal controller remains
CarMaker/UserSteer, so the first MPC Controller block trial only uses the
steering part:

```text
x = [Vy; yaw_rate; lateral_deviation; heading_error]
u = steering angle
y = [lateral_deviation; heading_error; yaw_rate]
```

This is now reflected in:

```text
llm_mpc_bo/simulink/init_slalom_mpc.m
```

## Why Not Copy the Whole Example

The MathWorks example files are installed toolbox/example material, so copying
the full implementation into this repository is unnecessary and creates
licensing/noise issues. The research code instead uses the same standard
vehicle-model structure in a compact project-specific initialization script.

## LQR vs MPC

LQR and LQR-like controllers are common for lane keeping when constraints are
not the main concern. They are useful as a fallback or sanity baseline.

For this study, MPC is preferable because the research objective includes
automatic tuning under low-friction slalom conditions, where explicit steering
angle and steering-rate constraints are part of the tuning/unsafe-trial story.

Recommended hierarchy:

```text
1. Standard MPC Controller block with bicycle lateral model
2. Adaptive/gain-scheduled MPC if speed dependence becomes a problem
3. Finite-horizon LQR as fallback/baseline
4. Direct CasADi/NLMPC implementation only if the standard block fails
```
