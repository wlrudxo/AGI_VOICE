% Auto-generated slalom reference loader.
% Source: Base mu=1.0 successful Slalom18m trajectory.
T = readtable('E:\GitProject\AGI_VOICE\llm_mpc_bo\simulink\slalom18m_base_reference.csv');
slalom_s_ref = T.s_ref;
slalom_t_ref = T.t_ref;
slalom_psi_ref = T.psi_ref;
slalom_delta_ff = T.delta_ff;
clear T;
