from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];s=json.loads((R/'results/summary.json').read_text());p=s['pilot16'];r=s['regional64'];d=s['detection']
text=f'''# Simulation results

All concentration errors are RMS for **differential NaCl-equivalent mass concentration (mg/kg)**. Default configuration, seed {s['seed']}. These are computed predictions for a proposed sensor; only the separate literature benchmark contains reported experimental values.

## What the experiments establish

**Conclusion:** a classical simulation predicts a conditional quantum sensing precision advantage. No physical water sensor or field trial was run. The 16-tap choice, 10 nW/tap budget, 100 m links, 1 s windows and 50 µK common temperature residual are assumptions, explained in [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md).

| Finding | Interpretation |
|---|---|
| Pilot total RMSE falls 27.92% versus coherent and 16.58% versus independent squeezing | Shared correlations improve the specified mean at matched launched probe photons under the default assumptions |
| Detection rises 24.27% to 47.33% | Better statistical power, but most specified events are still missed; 1% false alarm applies per window |
| Regional gain is 1.11× and thermal stress removes useful advantage | Loss and technical noise constrain the laboratory opportunity |
| Coherent power of about 28 nW/tap matches the 10 nW/tap distributed result | The practical reason for constraining probe power must be demonstrated |
| Ideal RMS exponent is −0.953 | Conditional consistency with existing theory, not discovery or hardware validation of a new law |

Published theory: [Zhuang, S4](https://arxiv.org/abs/1711.10459). NaCl optical calibration: [Saunders, S7](https://doi.org/10.1364/AO.55.000947). Assumptions and outputs are distinct from those published measurements. See [SIMULATION.md](SIMULATION.md) for the Python implementation, input/output contract and reproduction steps.

## Main comparison

| Strategy | 16-node optical RMSE | 16-node total RMSE | 64-node regional total RMSE |
|---|---:|---:|---:|
'''
for st in ['coherent','separable','entangled']:text+=f"| {st} | {p[st]['optical_rmse']:.6f} | {p[st]['controlled_rmse']:.6f} | {r[st]['controlled_rmse']:.6f} |\n"
text+=f'''
Pilot: distributed squeezing yields {p['coherent']['optical_rmse']/p['entangled']['optical_rmse']:.3f}× optical precision and {p['coherent']['controlled_rmse']/p['entangled']['controlled_rmse']:.3f}× total precision versus coherent. Total RMSE reduction is {100*(1-p['entangled']['controlled_rmse']/p['coherent']['controlled_rmse']):.2f}%. Relative to independent squeezers, total RMSE decreases {100*(1-p['entangled']['controlled_rmse']/p['separable']['controlled_rmse']):.2f}%. Pilot transmission is {p['entangled']['eta_mean']:.4f}.

Regional: at 64 distinct locations, mean transmission {r['entangled']['eta_mean']:.4f}, range {r['entangled']['eta_min']:.4f}–{r['entangled']['eta_max']:.4f}. Optimized classical power allocation gives {r['coherent_optimized']['controlled_rmse']:.6f} mg/kg total RMSE. Quantum gain against that stronger comparator is {r['coherent_optimized']['controlled_rmse']/r['entangled']['controlled_rmse']:.3f}×. The routing assumption is 1.3 times straight-line distance, not surveyed installed fiber.

The 10 mK common residual produces approximately {p['entangled']['field_rmse']:.3f} mg/kg error in the pilot for either strategy. Thus the model predicts essentially no field-like thermal-limited quantum advantage. The 50 µK residual used for the useful pilot result is an ambitious controlled target, not a demonstrated water-probe capability.

## Scaling

Fitted log-log exponent over M=33–64 (theory panel only): coherent {s['ideal_slopes_M33_64']['coherent']:.3f}, independent squeezed {s['ideal_slopes_M33_64']['separable']:.3f}, distributed squeezed {s['ideal_slopes_M33_64']['entangled']:.3f}. Source energy Ns=0.1 M photons/mode grows with M. This panel is lossless, without jitter or the practical 10 dB cap. It establishes the ideal mechanism, not a deployable exponent claim.

At 10 dB, source Ns is capped at {s['source_cap_photons']:.3f} photons/mode. At the default 10 nW/node, launched flux is {s['photon_flux_per_node_s']:.5g} photons/s per node. All strategy comparisons deduct the squeezed photon flux from carrier flux. Pump/LO/stabilization electrical resources are not in that budget.

## Detection comparison

0.15 mg/kg increase, 1 s windows, 16 taps, 1% false alarm per decision:

| Strategy | Theory P(detect) | Monte Carlo P(detect) | Monte Carlo false alarm |
|---|---:|---:|---:|
'''
for z in d:text+=f"| {z['strategy']} | {z['p_detect']:.5f} | {z['mc_detection']:.5f} | {z['mc_false_alarm']:.5f} |\n"
text+='''
100,000 null and 100,000 alternative draws per strategy. Bernoulli Monte Carlo errors are checked within five sampling standard errors. These trials validate the Gaussian marginal decision calculation; they do not prove a deployed alarm's sequential false-alarm rate. At 1 Hz, a 1% marginal rate means 36 expected flagged windows/hour. A deployed decision rule needs a separate temporal study.

## Figure guide

1. `01_scaling`: ideal log-log exponent and controlled pilot error including loss and drift.
2. `02_network_geometry`: 64 distinct coordinates and transmission range as the network expands.
3. `03_regional_limits`: optimized coherent comparison and the 10 mK thermal failure regime.
4. `04_averaging_temperature`: integration-time limits and thermal-control sensitivity.
5. `05_resource_accounting`: fixed-total versus fixed-per-node resources and source squeezing requirements.
6. `06_detection_correlations`: ROC at a fixed change and the negative readout correlations.
7. `07_continuous_monitoring`: unequal synthetic arrivals, sensor lag, aggregate versus local information.
8. `08_feasibility_map`: optical transmission versus common temperature residual, showing where gain survives.
9. `09_measured_benchmarks`: reported Dowran optical sensitivities and YSI manufacturer accuracy context.
10. `10_power_sensitivity`: benefit of increasing classical optical power; technical floor at high powers.

Every figure has PNG and SVG output. Raw series are in the named CSV files; the feasibility surface is in `feasibility.npz`. `summary.json` contains exact headline values and the configuration hash. Parameter uncertainty, missing physics and incomplete field-data provenance remain the limits described in MODEL.md and SOURCES.md.
'''
c=json.loads((R/'results/practical_comparisons.json').read_text())
text+=f'''
## Practical interpretation of the default model

All calculations retain the same transducer, 1 s integration and technical noise. These are additional model comparisons, not new water experiments.

- Raising coherent power to **{c['coherent_matching_power_W_per_tap']*1e9:.3f} nW/tap** matches the 10 nW distributed total RMSE. This relaxes the equal-dose constraint.
- At 95% detection and 1% false alarm per window, required settled mean steps are **{c['mean_step_for_95_percent_detection_mg_kg']['coherent']:.3f} mg/kg coherent** and **{c['mean_step_for_95_percent_detection_mg_kg']['entangled']:.3f} mg/kg distributed**.
- A 0.15 mg/kg event at only one of 16 taps changes the mean by {c['single_tap_event_mean_mg_kg']:.6f} mg/kg. Detection is just **{100*c['single_tap_event_detection_probability']['coherent']:.2f}% / {100*c['single_tap_event_detection_probability']['entangled']:.2f}%**. The mean is a poor localized-event alarm.
- A 10 s first-order response constant implies **{c['assumed_response_T95_seconds']:.2f} s to 95% response**, despite 1 s readout windows. This lag is assumed.
- At 70 µW/tap, both total errors approach **0.0463 mg/kg**, the modeled technical floor.

Reproduction: `src/practical_comparisons.py`; exact values in [practical_comparisons.json](../results/practical_comparisons.json). A commercial EXO salinity accuracy bound and a NitraLED nitrate accuracy/response specification concern different measurands and error definitions. They provide real-instrument context, not evidence of superiority. [YSI EXO](https://www.ysi.com/product/id-599870/exo-conductivity--temperature-smart-sensor); [NitraLED](https://www.ysi.com/exo/nitraled).

The next experiment should establish the water-cell calibration, residual drift and practical dose constraint before expanding to 16 taps. Computational validation supports implementation consistency; only a controlled physical comparison can establish instrument performance.
'''
(R/'docs/RESULTS.md').write_text(text)
