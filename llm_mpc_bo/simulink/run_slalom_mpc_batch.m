% Batch entry point for running the current Slalom MPC Simulink workflow.
%
% Windows command:
%   E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink\run_slalom_mpc_batch.bat

clc;

cd('E:\CarMakerProject\AGI\src_cm4sl');
cmenv;

run('E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink\init_slalom_mpc.m');
open_system('UserSteer');

run('E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink\run_slalom_mpc_and_export.m');
