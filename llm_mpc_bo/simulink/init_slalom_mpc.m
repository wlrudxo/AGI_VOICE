% Initialize the Slalom18m reference tables and Simulink MPC Controller object.
%
% Usage from MATLAB:
%   cd('E:\CarMakerProject\AGI\src_cm4sl')
%   cmenv
%   run('E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink\init_slalom_mpc.m')
%   open_system('UserSteer')
%
% Simulink MPC Controller block:
%   Controller object: mpcobj
%   mo  = [Car.Road.Path.DevDist; Car.Road.Path.DevAng; Car.YawRate]
%   ref = [slalom_t_ref(Vhcl.sRoad); slalom_psi_ref(Vhcl.sRoad); 0]
%   mv  = VhclCtrl Steering Ang
%
% Model basis:
%   The lateral bicycle model follows the state convention used in the
%   MathWorks LaneFollowingUsingNMPCExample, reduced here to a linear
%   constant-speed steering-only model for the standard MPC Controller block.

agiVoiceRoot = 'E:\GitProject\AGI_VOICE';
slalomSimulinkDir = fullfile(agiVoiceRoot, 'llm_mpc_bo', 'simulink');

if ~exist(slalomSimulinkDir, 'dir')
    error('Slalom Simulink directory does not exist: %s', slalomSimulinkDir);
end

addpath(slalomSimulinkDir);

% Load slalom_s_ref, slalom_t_ref, slalom_psi_ref, slalom_delta_ff.
run(fullfile(slalomSimulinkDir, 'init_slalom_reference.m'));

% Fixed sample time for the first MPC block trial.
Ts = 0.02;

% Nominal forward speed used in the fixed lateral bicycle model [m/s].
Vx = 12.0;

% State/output convention:
%   x = [Vy; yaw_rate; lateral_deviation; heading_error]
%   y = [lateral_deviation; heading_error; yaw_rate]
%   u = VhclCtrl.Steering.Ang steering wheel angle command [rad]
%
% The formal experiment does not tune or apply steering ratio/input-scale
% factors. The MPC manipulated variable is the same steering-wheel command
% signal sent to VhclCtrl.Steering.Ang. The Simulink Gain after the MPC block
% should be 1.
m = 1575;
Iz = 2875;
lf = 1.2;
lr = 1.6;
Cf = 19000;
Cr = 33000;
steerSign = 1.0;

a1 = -(2*Cf + 2*Cr) / (m * Vx);
a2 = -(2*Cf*lf - 2*Cr*lr) / (m * Vx) - Vx;
a3 = -(2*Cf*lf - 2*Cr*lr) / (Iz * Vx);
a4 = -(2*Cf*lf^2 + 2*Cr*lr^2) / (Iz * Vx);
b1 = 2*Cf / m;
b2 = 2*Cf*lf / Iz;

Ac = [a1, a2, 0.0, 0.0;
      a3, a4, 0.0, 0.0;
      1.0, 0.0, 0.0, Vx;
      0.0, 1.0, 0.0, 0.0];

Bc = steerSign * [b1; b2; 0.0; 0.0];

C = [0.0, 0.0, 1.0, 0.0;
     0.0, 0.0, 0.0, 1.0;
     0.0, 1.0, 0.0, 0.0];
D = zeros(3, 1);

plant_c = ss(Ac, Bc, C, D);
plant = c2d(plant_c, Ts);

mpcVerbosityStatus = mpcverbosity('off');
mpcobj = mpc(plant, Ts);
mpcverbosity(mpcVerbosityStatus);

mpcobj.PredictionHorizon = 40;
mpcobj.ControlHorizon = 8;

% Steering-wheel angle and rate constraints [rad], [rad/s].
mpcobj.MV.Min = -12.0;
mpcobj.MV.Max =  12.0;
mpcobj.MV.RateMin = -10.0;
mpcobj.MV.RateMax =  10.0;

% Initial hand-tuned weights. These become BO variables after nominal closure.
mpcobj.Weights.OutputVariables = [5.0 2.0 0.2];
mpcobj.Weights.ManipulatedVariables = 0.2;
mpcobj.Weights.ManipulatedVariablesRate = 2.0;

clear Ac Bc C D Ts plant plant_c Vx m Iz lf lr Cf Cr steerSign;
clear a1 a2 a3 a4 b1 b2 agiVoiceRoot slalomSimulinkDir;
clear mpcVerbosityStatus;
