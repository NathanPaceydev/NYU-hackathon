"""Screen candidate targets for a real quantum advantage: squeezed light must beat
the best classical option at the power (or dose) the sample actually allows.
Writes results/advantage_path.json, results/advantage_gates.csv and figures/15-16."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import efficiency, noise_budget, jitter_variance, squeezing_budget

ROOT = Path(__file__).resolve().parents[1]
p = json.loads((ROOT / 'config/default.json').read_text())
j = json.loads((ROOT / 'config/judges_response.json').read_text())
a = json.loads((ROOT / 'config/advantage_candidates.json').read_text(encoding='utf-8'))
r = json.loads((ROOT / 'results/judges_response.json').read_text(encoding='utf-8'))
M = p['pilot_nodes']
ETA = float(efficiency(M, p['pilot_fiber_length_km'], p)[0])
ESCAPE = a['squeezer_escape_efficiency']

GREY, PURPLE, TEAL, RED = '#595959', '#57068C', '#16877B', '#B8424C'
plt.rcParams.update({'font.family': 'Arial', 'font.size': 12, 'axes.spines.top': False,
                     'axes.spines.right': False, 'lines.linewidth': 2.4, 'legend.frameon': False})


def input_variance(generated_db):
    return ESCAPE * 10 ** (-generated_db / 10) + 1 - ESCAPE


def gain(eta, v, tech_ratio):
    # Variances in units of coherent shot noise at the cap: coherent 1/eta, squeezed 1/eta - 1 + v.
    # tech_ratio = technical noise / coherent shot noise (rms); it does not care about squeezing.
    tech = tech_ratio ** 2 / eta
    return float(np.sqrt((1 / eta + tech) / (1 / eta - 1 + v + tech)))


def tech_ratio_for(target, eta, v):
    # Largest technical/shot ratio that still leaves the target gain.
    tech = (1 / eta - target ** 2 * (1 / eta - 1 + v)) / (target ** 2 - 1)
    return float(np.sqrt(tech * eta)) if tech > 0 else 0.


# A and B: the salt pilot run at the real per-tap cap (SBS share, the lowest physical limit).
salt_cap = r['power']['sbs_per_tap_w']
salt_v = float(jitter_variance(squeezing_budget(M, p), p['phase_lock_rms_rad']))
conductivity_field = next(row['rmse_mg_kg'] for row in r['head_to_head']
                          if row['sensor'] == 'Conductivity ×16' and row['scenario'].startswith('field'))


def salt(name, temperature, need_note, cap_note):
    b = noise_budget(M, ETA, dict(p, power_per_node_w=salt_cap), 'coherent', temperature=temperature)
    ratio = np.sqrt((b['temperature'] + b['calibration']) / b['optical'])
    g = gain(ETA, salt_v, ratio)
    quantum = np.sqrt(b['total']) / g
    return {'name': name, 'eta': ETA, 'v': salt_v, 'tech_ratio': ratio, 'gain_vs_coherent': g,
            'gain_vs_best_classical': min(g, conductivity_field / quantum),
            'classical_meets_target': False, 'need_note': need_note,
            'time_escape': True, 'time_note': 'slow drift:\naverage longer',
            'cap_note': cap_note}


candidates = [
    salt('A. Salt pilot\n(field)', p['field_temperature_rms_K'],
         'nothing reaches\n0.15 mg/kg in field', f'SBS {salt_cap * 1e6:.0f} µW/tap'),
    salt('B. Salt + thermal\nreference arm', p['field_temperature_rms_K'] / a['salt_reference_rejection'],
         'nothing reaches\n0.15 mg/kg in field', f'SBS {salt_cap * 1e6:.0f} µW/tap'),
]
for c in a['candidates']:
    v = input_variance(c['generated_db'])
    ratio = c['technical_noise_riu_1s'] / c['shot_noise_riu_1s']
    g = gain(c['eta'], v, ratio)
    candidates.append({**c, 'v': v, 'tech_ratio': ratio, 'gain_vs_coherent': g, 'gain_vs_best_classical': g})

rows = []
for c in candidates:
    needed = tech_ratio_for(1.2, c['eta'], c['v'])
    rows.append({
        'candidate': c['name'], 'eta': c['eta'], 'tech_to_shot_ratio': c['tech_ratio'],
        'gate_need': not c['classical_meets_target'],
        'gate_cap_binds': c['tech_ratio'] < 1,
        'gate_low_loss': 1 / np.sqrt(1 - c['eta']) >= 1.5,
        'gate_no_time_escape': not c['time_escape'],
        'gain_vs_coherent_at_cap': c['gain_vs_coherent'],
        'gain_vs_best_classical': c['gain_vs_best_classical'],
        'noise_cut_needed_for_1p2x': c['tech_ratio'] / needed if needed else np.inf,
        'need_note': c['need_note'], 'cap_note': c['cap_note'], 'time_note': c['time_note'],
    })
gates = pd.DataFrame(rows)
gates['all_gates'] = gates[['gate_need', 'gate_cap_binds', 'gate_low_loss', 'gate_no_time_escape']].all(axis=1)
gates.to_csv(ROOT / 'results/advantage_gates.csv', index=False)


def save(fig, name):
    fig.savefig(ROOT / 'figures' / f'{name}.png', dpi=200, bbox_inches='tight')
    plt.close(fig)


# Figure 15: candidate x gate scorecard.
columns = [('gate_need', 'Classical\nfalls short'), ('gate_cap_binds', 'Power/dose\ncap binds'),
           ('gate_low_loss', 'Loss ceiling\n≥ 1.5×'), ('gate_no_time_escape', 'No time\nescape')]
fig, ax = plt.subplots(figsize=(12, 5), layout='constrained')
for y, row in gates.iterrows():
    notes = [row.need_note, f'{row.cap_note}\ndrift/shot noise = {row.tech_to_shot_ratio:.3g}',
             f'η = {row.eta:.2f} → ≤{1 / np.sqrt(1 - row.eta):.2f}×', row.time_note]
    for x, ((key, _), note) in enumerate(zip(columns, notes)):
        ax.add_patch(plt.Rectangle((x, y), 0.96, 0.92, color=TEAL if row[key] else RED, alpha=0.85))
        ax.text(x + 0.48, y + 0.46, note, ha='center', va='center', color='white', fontsize=10)
    good = row.gain_vs_best_classical > 1.05
    ax.add_patch(plt.Rectangle((4.1, y), 0.96, 0.92, color=PURPLE if good else GREY))
    ax.text(4.58, y + 0.46, f'{row.gain_vs_best_classical:.2f}×', ha='center', va='center', color='white',
            fontsize=13, weight='bold')
ax.set_xlim(0, 5.1)
ax.set_ylim(len(gates), -0.6)
ax.set_xticks([x + 0.48 for x in range(4)] + [4.58], [label for _, label in columns] + ['Gain vs best\nclassical'])
ax.set_yticks([y + 0.46 for y in range(len(gates))], gates.candidate)
ax.xaxis.tick_top()
ax.tick_params(length=0)
for side in ax.spines.values():
    side.set_visible(False)
save(fig, '15_advantage_gates')

# Figure 16: what any target needs from the loss budget.
etas = np.linspace(0.3, 0.99, 200)
fig, ax = plt.subplots(figsize=(7.2, 5.0), layout='constrained')
ax.plot(etas, 1 / np.sqrt(1 - etas), color=GREY, ls=':', label='Ideal squeezing, 1/√(1−η)')
for generated, shade in zip(a['universal_generated_db'], [0.35, 0.55, 0.8, 1.0]):
    ax.plot(etas, [gain(e, input_variance(generated), 0) for e in etas], color=PURPLE, alpha=shade,
            label=f'{generated} dB generated ({ESCAPE:.0%} escape)')
for c, row in zip(candidates, rows):
    ax.plot(c['eta'], row['gain_vs_best_classical'], 'o', color=RED, ms=8)
    ax.annotate(row['candidate'][0], (c['eta'], row['gain_vs_best_classical']), xytext=(6, 4),
                textcoords='offset points', color=RED)
ax.set(xlabel='Total efficiency η (source to detector)', ylabel='Gain over coherent light at the cap',
       ylim=(0.9, 3.2), title='No technical noise: the best any target can do (A is off-chart at 0.01×)')
ax.legend(fontsize=9, loc='upper left')
save(fig, '16_gain_vs_efficiency')

summary = {'candidates': gates.to_dict('records'),
           'salt_cap_w': salt_cap, 'squeezer_escape_efficiency': ESCAPE,
           'any_candidate_passes_all_gates': bool(gates.all_gates.any())}
(ROOT / 'results/advantage_path.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=float),
                                                 encoding='utf-8')
print(gates.drop(columns=['need_note', 'cap_note', 'time_note']).to_string(index=False))
