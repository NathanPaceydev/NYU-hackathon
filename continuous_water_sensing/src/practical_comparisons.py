"""Derived interpretation of the existing default model; no new measured data."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm
from model import efficiency, noise_budget

R = Path(__file__).resolve().parents[1]
p = json.loads((R / 'config/default.json').read_text())
m = p['pilot_nodes']
eta = efficiency(m, p['pilot_fiber_length_km'], p)
strategies = ('coherent', 'entangled')
budgets = {st: noise_budget(m, eta, p, st) for st in strategies}
sigma = {st: np.sqrt(budgets[st]['total']) for st in strategies}
# Solve for power with all other parameters and the integration window fixed.
match_log = brentq(lambda logp: noise_budget(
    m, eta, dict(p, power_per_node_w=10**logp), 'coherent')['total']
    - budgets['entangled']['total'], -9, -6)
alpha = p['false_alarm_probability_per_decision']
z = norm.ppf(1-alpha)
local_delta = p['test_event_delta_mg_kg']/m
out = {
    'status': 'Derived simulation comparisons, not experimental measurements',
    'conditions': {'nodes': m, 'seconds': 1, 'temperature_rms_K': p['controlled_temperature_rms_K'],
                   'quantum_power_W_per_tap': p['power_per_node_w'], 'false_alarm_per_window': alpha},
    'noise_variance_mg_kg_squared': budgets,
    'coherent_matching_power_W_per_tap': 10**match_log,
    'mean_step_for_95_percent_detection_mg_kg': {
        st: (z+norm.ppf(.95))*sigma[st] for st in strategies},
    'single_tap_event_mg_kg': p['test_event_delta_mg_kg'],
    'single_tap_event_mean_mg_kg': local_delta,
    'single_tap_event_detection_probability': {
        st: norm.sf(z-local_delta/sigma[st]) for st in strategies},
    'total_rmse_at_70_uW_per_tap': {
        st: np.sqrt(noise_budget(m, eta, dict(p, power_per_node_w=70e-6), st)['total'])
        for st in strategies},
    'assumed_response_T95_seconds': -np.log(.05)*p['sensor_response_tau_s'],
    'expected_null_flags_per_hour_at_1_Hz': 3600*alpha,
}
(R / 'results/practical_comparisons.json').write_text(json.dumps(out, indent=2)+'\n')
print('Wrote results/practical_comparisons.json')
