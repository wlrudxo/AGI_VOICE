function params = decode_slalom_mpc_theta(x)
% Decode normalized BO vector x in [0, 1]^5 into MPC tuning parameters.
%
% Order:
%   [q_y, q_psi, q_r, r_delta, r_d_delta]

if numel(x) ~= 5
    error('Expected x to have 5 elements, got %d.', numel(x));
end

x = double(x(:)');
if any(~isfinite(x))
    error('Normalized theta contains NaN or Inf.');
end
if any(x < 0) || any(x > 1)
    error('Normalized theta must be in [0, 1].');
end

params = struct();
params.q_y = decode_log(x(1), 0.1, 100.0);
params.q_psi = decode_log(x(2), 0.1, 100.0);
params.q_r = decode_log(x(3), 0.01, 30.0);
params.r_delta = decode_log(x(4), 0.01, 10.0);
params.r_d_delta = decode_log(x(5), 0.01, 10.0);
params.normalized_x = x;
end

function value = decode_log(x, lb, ub)
value = 10 ^ (log10(lb) + x * (log10(ub) - log10(lb)));
end
