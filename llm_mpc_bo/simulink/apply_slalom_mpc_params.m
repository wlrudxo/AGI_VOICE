function mpcobj = apply_slalom_mpc_params(params, mpcobj)
% Apply Slalom MPC tuning parameters to an MPC Toolbox controller object.
%
% If mpcobj is omitted, this function reads and updates base workspace mpcobj.
% The updated object is assigned back to the base workspace so the Simulink
% MPC Controller block sees it on the next simulation.
%
% Main experiment variables are MPC weights only:
%   q_y, q_psi, q_r, r_delta, r_d_delta
%
% Steering-wheel command constraints are fixed to the physical command range
% used by VhclCtrl.Steering.Ang [rad].

if nargin < 1 || isempty(params)
    params = struct();
end

if nargin < 2 || isempty(mpcobj)
    if ~evalin('base', "exist('mpcobj', 'var')")
        error('Base workspace mpcobj does not exist. Run init_slalom_mpc.m first.');
    end
    mpcobj = evalin('base', 'mpcobj');
end

params = fill_defaults(params);

mpcobj.Weights.OutputVariables = [params.q_y, params.q_psi, params.q_r];
mpcobj.Weights.ManipulatedVariables = params.r_delta;
mpcobj.Weights.ManipulatedVariablesRate = params.r_d_delta;

deltaMax = 12.0;
mpcobj.MV.Min = -deltaMax;
mpcobj.MV.Max = deltaMax;

rateMax = 0.6;
mpcobj.MV.RateMin = -rateMax;
mpcobj.MV.RateMax = rateMax;

if isfield(params, 'PredictionHorizon')
    mpcobj.PredictionHorizon = params.PredictionHorizon;
end
if isfield(params, 'ControlHorizon')
    mpcobj.ControlHorizon = params.ControlHorizon;
end

assignin('base', 'mpcobj', mpcobj);
assignin('base', 'slalom_mpc_params', params);
end

function params = fill_defaults(params)
defaults = struct( ...
    'q_y', 5.0, ...
    'q_psi', 2.0, ...
    'q_r', 0.2, ...
    'r_delta', 0.2, ...
    'r_d_delta', 2.0 ...
);

names = fieldnames(defaults);
for i = 1:numel(names)
    name = names{i};
    if ~isfield(params, name) || isempty(params.(name))
        params.(name) = defaults.(name);
    end
    if ~isscalar(params.(name)) || ~isfinite(params.(name))
        error('Parameter %s must be a finite scalar.', name);
    end
end

end
