"""Analyses requested by the judges: loss budget, probe-power cap, conductivity
baseline, loss-limited gain and an operational false-alarm rate.
Writes results/judges_response.json and figures/11-14 (light theme for slides)."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.stats import norm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import efficiency, noise_budget, ou_average_factor

ROOT = Path(__file__).resolve().parents[1]
p = json.loads((ROOT / 'config/default.json').read_text())
j = json.loads((ROOT / 'config/judges_response.json').read_text())
M = p['pilot_nodes']
ETA = float(efficiency(M, p['pilot_fiber_length_km'], p)[0])
DELTA = p['test_event_delta_mg_kg']
ALPHA_PILOT = p['false_alarm_probability_per_decision']
ALPHA_WEEK = j['operational_false_alarm_per_week'] / (7 * 24 * 3600)  # one 1 s decision per second

GREY, PURPLE, TEAL, RED = '#595959', '#57068C', '#16877B', '#B8424C'
plt.rcParams.update({'font.family': 'Arial', 'font.size': 12, 'axes.spines.top': False,
                     'axes.spines.right': False, 'lines.linewidth': 2.4, 'legend.frameon': False})


def db(transmission):
    return -10 * np.log10(transmission)


def rmse(strategy, params=p, eta=ETA, temperature=None):
    return float(np.sqrt(noise_budget(M, eta, params, strategy, temperature=temperature)['total']))


def gain(params=p, eta=ETA, temperature=None):
    return rmse('coherent', params, eta, temperature) / rmse('entangled', params, eta, temperature)


def with_input_squeezing(squeezing_db):
    # The model budgets squeezing as photons in the one shared mode; convert from dB.
    photons = np.sinh(squeezing_db * np.log(10) / 20) ** 2
    return dict(p, squeezing_cap_db=99., squeezing_photons_per_node_mode=photons / M)


def p_detect(sigma, alpha):
    return float(norm.sf(norm.isf(alpha) - DELTA / sigma))


def save(fig, name):
    fig.savefig(ROOT / 'figures' / f'{name}.png', dpi=200, bbox_inches='tight')
    plt.close(fig)


# A. Loss budget in dB and the squeezing needed to keep the pilot gain.
stages = int(np.ceil(np.log2(M)))
losses = {
    f'Splitter excess ({stages} stages)': p['splitter_excess_db_per_stage'] * stages,
    f'Fibre ({p["pilot_fiber_length_km"] * 1000:.0f} m)': p['fiber_loss_db_km'] * p['pilot_fiber_length_km'],
    'Fibre-to-cell coupling': db(p['coupling_transmission']),
    'Sample cell': db(p['sample_transmission']),
    'Homodyne detector': db(p['detector_efficiency']),
}
total_loss_db = sum(losses.values())

pilot_input_db = db(1 / (np.sqrt(1.6 + 1) + np.sqrt(1.6)) ** 2)  # 1.6 squeezed photons, as in summary.json
pilot_gain = gain()
# Phase-lock jitter mixes in anti-squeezing, so the gain peaks and then falls.
sweep_db = np.linspace(0.1, 30, 300)
sweep_gain = [gain(with_input_squeezing(x)) for x in sweep_db]
best_db, max_gain = sweep_db[np.argmax(sweep_gain)], max(sweep_gain)


def input_db_for(target):
    return brentq(lambda x: gain(with_input_squeezing(x)) - target, 0.01, best_db)


def generated_db(input_db, escape):
    # Squeezer escape/coupling loss before the network: v_in = escape * v_gen + (1 - escape).
    v_gen = (10 ** (-input_db / 10) - (1 - escape)) / escape
    return db(v_gen) if v_gen > 0 else None


targets = {'pilot': pilot_gain, '1.2x': 1.2, '1.1x': 1.1}
squeezing_needed = {}
for name, target in targets.items():
    needed = input_db_for(target)
    squeezing_needed[name] = {'target_gain': target, 'network_input_db': needed,
                              'generated_db': {str(e): generated_db(needed, e) for e in j['squeezer_escape_efficiencies']}}

v_in = 10 ** (-pilot_input_db / 10)
detected_db = db(ETA * v_in + 1 - ETA)
extra_loss_for_1p1 = brentq(lambda x: gain(eta=ETA * 10 ** (-x / 10)) - 1.1, 0, 30)

fig, (left, right) = plt.subplots(1, 2, figsize=(12, 4.3), layout='constrained')
names = list(losses) + ['Total']
values = list(losses.values()) + [total_loss_db]
left.barh(names[::-1], values[::-1], color=[PURPLE] + [GREY] * len(losses))
for y, v in enumerate(values[::-1]):
    left.text(v + 0.02, y, f'{v:.2f} dB', va='center')
left.set(xlabel='Loss (dB)', title=f'Source → detector: {total_loss_db:.2f} dB (η = {ETA:.3f})', xlim=(0, total_loss_db * 1.25))
right.plot(sweep_db, sweep_gain, color=PURPLE)
right.axhline(1.1, color=GREY, ls=':')
right.plot(pilot_input_db, pilot_gain, 'o', color=RED, ms=9)
right.annotate(f'Pilot: {pilot_input_db:.1f} dB → {pilot_gain:.2f}×', (pilot_input_db, pilot_gain),
               xytext=(10, -25), textcoords='offset points')
right.set(xlabel='Squeezing entering the network (dB)', ylabel='Classical / quantum total RMSE',
          title=f'Gain peaks at {max_gain:.2f}× ({best_db:.0f} dB): loss, drift, lock jitter')
save(fig, '11_loss_budget')

# B. Is there a physical reason to cap probe power near 10 nW?
quantum_10nw = rmse('entangled')
matched_power = brentq(lambda w: rmse('coherent', dict(p, power_per_node_w=w)) - quantum_10nw, 1e-9, 1e-5)
budget = noise_budget(M, ETA, p, 'coherent')
floor = float(np.sqrt(budget['temperature'] + budget['calibration']))

# Water absorbs ~10/cm at 1550 nm; treat the heated spot as a point source in water.
absorbed = 1 - np.exp(-j['water_absorption_per_m_1550nm'] * p['effective_interaction_length_m'])
kelvin_per_watt = absorbed / (4 * np.pi * j['water_thermal_conductivity_w_mk'] * j['beam_radius_m'])
photothermal_cap = p['controlled_temperature_rms_K'] / (kelvin_per_watt * j['laser_relative_power_noise_rms'])
sbs_per_tap = j['sbs_trunk_power_w'] / M
eye_safe_per_tap = j['eye_safety_class1_w_1550nm'] / M
taps_for_real_cap = j['sbs_trunk_power_w'] / matched_power

powers = np.geomspace(1e-9, 1e-2, 200)
coherent_curve = [rmse('coherent', dict(p, power_per_node_w=w)) for w in powers]
quantum_curve = [rmse('entangled', dict(p, power_per_node_w=w)) for w in powers]
fig, ax = plt.subplots(figsize=(7.2, 5.2), layout='constrained')
ax.loglog(powers, coherent_curve, color=GREY, label='Coherent')
ax.loglog(powers, quantum_curve, color=PURPLE, label='Squeezed')
ax.axhline(floor, color=GREY, ls=':', label=f'Drift floor {floor:.3f}')
for w, label, color, side in [(p['power_per_node_w'], '10 nW pitch', RED, 1.2), (matched_power, f'{matched_power * 1e9:.0f} nW matches', RED, 1.2),
                              (sbs_per_tap, 'SBS ÷ 16 taps', TEAL, 0.62), (photothermal_cap, 'Photothermal', TEAL, 1.2),
                              (eye_safe_per_tap, 'Class 1 ÷ 16', TEAL, 1.2)]:
    ax.axvline(w, color=color, ls='--', lw=1.2)
    ax.text(w * side, 0.14, label, rotation=90, va='bottom', color=color, fontsize=10)
ax.set(xlabel='Probe power per tap (W)', ylabel='Total 1 s RMSE (mg/kg NaCl)', ylim=(0.035, 0.6),
       title=f'Real limits sit ≥{min(sbs_per_tap, photothermal_cap) / matched_power:,.0f}× above the {matched_power * 1e9:.0f} nW crossover')
ax.legend(loc='upper left', bbox_to_anchor=(0.36, 0.99), fontsize=10)
save(fig, '12_power_cap')

# C. Head-to-head with a temperature-compensated conductivity probe (spec-derived).
ec = j['conductivity_ms_cm_per_mg_kg'] * p['baseline_nacl_mg_kg']
conductivity_mg_kg_per_K = j['conductivity_temperature_coefficient_per_K'] * ec / j['conductivity_ms_cm_per_mg_kg']
optical_mg_kg_per_K = budget['temperature'] ** 0.5 / p['controlled_temperature_rms_K'] / ou_average_factor(1, p['common_temperature_correlation_s']) ** 0.5


def conductivity_rmse(probes, temperature):
    resolution = j['conductivity_resolution_ms_cm'] / np.sqrt(12) / j['conductivity_ms_cm_per_mg_kg']
    thermal = conductivity_mg_kg_per_K * temperature * np.sqrt(ou_average_factor(1, p['common_temperature_correlation_s']))
    calibration = p['independent_calibration_rms_mg_kg']
    return float(np.sqrt((resolution ** 2 + calibration ** 2) / probes + thermal ** 2))


scenarios = {'controlled (50 µK)': p['controlled_temperature_rms_K'], 'field (10 mK)': p['field_temperature_rms_K']}
sensors = {
    'Coherent 10 nW': lambda t: rmse('coherent', temperature=t),
    f'Coherent {matched_power * 1e9:.0f} nW': lambda t: rmse('coherent', dict(p, power_per_node_w=matched_power), temperature=t),
    'Coherent 1 µW': lambda t: rmse('coherent', dict(p, power_per_node_w=1e-6), temperature=t),
    'Quantum 10 nW': lambda t: rmse('entangled', temperature=t),
    'Conductivity ×1': lambda t: conductivity_rmse(1, t),
    'Conductivity ×16': lambda t: conductivity_rmse(16, t),
}
comparison = []
for sensor, f in sensors.items():
    for scenario, temperature in scenarios.items():
        sigma = f(temperature)
        comparison.append({'sensor': sensor, 'scenario': scenario, 'rmse_mg_kg': sigma,
                           'p_detect_1pct': p_detect(sigma, ALPHA_PILOT), 'p_detect_1_per_week': p_detect(sigma, ALPHA_WEEK)})
comparison = pd.DataFrame(comparison)
comparison.to_csv(ROOT / 'results/head_to_head.csv', index=False)

rng = np.random.default_rng(p['seed'])
sigma = conductivity_rmse(1, p['controlled_temperature_rms_K'])
cut = norm.isf(ALPHA_PILOT) * sigma
monte_carlo = {'sigma': sigma, 'p_detect': p_detect(sigma, ALPHA_PILOT), 'trials': p['monte_carlo_trials'],
               'mc_false_alarm': float((rng.normal(0, sigma, p['monte_carlo_trials']) > cut).mean()),
               'mc_detection': float((rng.normal(DELTA, sigma, p['monte_carlo_trials']) > cut).mean())}

fig, (left, right) = plt.subplots(1, 2, figsize=(12, 4.4), layout='constrained')
colors = [GREY, GREY, GREY, PURPLE, TEAL, TEAL]
for ax, scenario in zip((left, right), scenarios):
    rows = comparison[comparison.scenario == scenario]
    ax.barh(rows.sensor[::-1], rows.rmse_mg_kg[::-1], color=colors[::-1])
    for y, (v, pd_) in enumerate(zip(rows.rmse_mg_kg[::-1], rows.p_detect_1pct[::-1])):
        ax.text(v * 1.1, y, f'{v:.3g} mg/kg · P(detect) {pd_:.0%}', va='center', fontsize=10)
    ax.set_xscale('log')
    ax.set_xlim(rows.rmse_mg_kg.min() / 2, rows.rmse_mg_kg.max() * 60)
    ax.set(xlabel='Total 1 s RMSE (mg/kg NaCl)', title=f'Temperature residual: {scenario}')
fig.suptitle(f'Detect a {DELTA} mg/kg step on 500 mg/kg, 16 taps, 1 s, 1% false alarm', fontsize=13)
save(fig, '13_head_to_head')

# D. Realised gain is a loss-limited constant, not sqrt(N).
scaling = pd.read_csv(ROOT / 'results/scaling.csv')
fig, ax = plt.subplots(figsize=(11, 4.4), layout='constrained')
nodes = np.arange(1, 65)
ax.plot(nodes, np.sqrt(nodes), color=GREY, ls=':', label='"√N" claim on the ideation deck')
loss_limited = {}
for geometry, color in [('pilot', PURPLE), ('regional', TEAL)]:
    rows = scaling[scaling.geometry == geometry].pivot(index='nodes', columns='strategy')
    ratio = rows.optical_rmse.coherent / rows.optical_rmse.entangled
    bound = 1 / np.sqrt(1 - rows.eta_mean.entangled)
    ax.plot(rows.index, ratio, color=color, label=f'{geometry.title()}: simulated optical gain')
    ax.plot(rows.index, bound, color=color, ls='--', lw=1.4, label=f'{geometry.title()}: loss bound 1/√(1−η)')
    loss_limited[geometry] = {'optical_gain_at_max': float(ratio.iloc[-1] if geometry == 'regional' else ratio.loc[M]),
                              'bound_at_max': float(bound.iloc[-1] if geometry == 'regional' else bound.loc[M])}
ax.set(xlabel='Number of taps', ylabel='Classical / quantum optical RMSE', ylim=(0.9, 4),
       title='With realistic loss the quantum gain is a constant factor (Demkowicz-Dobrzański 2012)')
ax.legend(fontsize=10, ncol=2)
save(fig, '14_loss_limited_gain')

summary = {
    'loss_budget_db': losses, 'total_loss_db': total_loss_db, 'eta': ETA,
    'pilot_input_squeezing_db': pilot_input_db, 'pilot_detected_squeezing_db': detected_db,
    'pilot_total_gain': pilot_gain, 'max_total_gain': max_gain, 'max_gain_input_db': best_db,
    'squeezing_needed': squeezing_needed, 'extra_loss_db_until_gain_1p1': extra_loss_for_1p1,
    'power': {'quantum_rmse_10nw': quantum_10nw, 'coherent_power_matching_quantum_w': matched_power,
              'floor_rmse': floor, 'gain_at_1uw': gain(dict(p, power_per_node_w=1e-6)),
              'absorbed_fraction': absorbed, 'heating_K_per_W': kelvin_per_watt,
              'heating_at_10nw_K': kelvin_per_watt * p['power_per_node_w'],
              'photothermal_cap_w': photothermal_cap, 'sbs_per_tap_w': sbs_per_tap,
              'eye_safe_per_tap_w': eye_safe_per_tap, 'taps_where_sbs_forces_matched_power': taps_for_real_cap},
    'temperature_sensitivity_mg_kg_per_K': {'optical': optical_mg_kg_per_K, 'conductivity': conductivity_mg_kg_per_K},
    'head_to_head': comparison.to_dict('records'), 'conductivity_monte_carlo': monte_carlo,
    'operational_false_alarm_per_decision': ALPHA_WEEK, 'loss_limited_gain': loss_limited,
}
(ROOT / 'results/judges_response.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps({k: v for k, v in summary.items() if k != 'head_to_head'}, indent=2, ensure_ascii=False))
print(comparison.to_string(index=False))
