# Design decisions and assumption register

Updated 7 October 2026. This register explains the default model, not a purchased or built instrument. **Published anchor** means a source supports that particular quantity; **assumption** means the project selected it to test a hypothesis. A plausible value is not a measured capability. Source identifiers resolve in [SOURCES.md](SOURCES.md), also reproduced in the report's Appendix A.

The proposed system estimates the mean change across water taps from a refractive-index signal. Its intended role is to flag changes for investigation, following the general online-monitoring use case described by [EPA, S15](https://www.epa.gov/waterresilience/online-water-quality-monitoring-resources). A facility's need for the particular sensitivity, count and dose used here has not been established.

## Why these scientific choices?

| Choice | Evidence and reasoning | Limitation / validation required |
|---|---|---|
| NaCl-equivalent differential concentration | [Saunders, S7](https://doi.org/10.1364/AO.55.000947) supplies a measured index–concentration fit at the chosen wavelength; gives interpretable units rather than arbitrary phase | Calibrate mixtures, temperature and the real cell; index alone cannot identify a contaminant |
| Shared squeezed mode and local homodyne | [Zhuang, S4](https://arxiv.org/abs/1711.10459) supplies aggregate sensing theory; [Guo, S6](https://arxiv.org/abs/1905.09408) supplies a four-node optical precedent | Water application, bandwidth and network operation remain proposed; no universal optimality claim |
| Arithmetic mean, equal tap weights | Assumption matching the aggregate that distributed sensing improves; keeps all local signals as parameters | Not a flow-weighted or health-risk measure; a local change is diluted by 1/M |
| Coherent and independent-squeezer baselines | Separate the effect of squeezing from the benefit of sharing it; match total launched probe photons | Does not match purchase cost, electronics, pump or local-oscillator electricity |
| Optimized coherent regional baseline | Derived within our model: allocate flux proportional to 1/√η while keeping the arithmetic mean | Relaxes per-tap dose; it is an optimistic total-power comparator |
| Gaussian readout, independent calibration and common OU temperature drift | Modeling assumptions that permit explicit covariance and decision calculations | Validate measured tails, biases, correlations, excess noise and outages; simulation agreement cannot establish these assumptions |

## Every configuration setting

Values refer to [default.json](../config/default.json). Rows covering more than one field give the values in the same order. Test ranges are explorations, not confidence intervals.

| Configuration field(s) | Value | Status and rationale | What must be checked |
|---|---|---|---|
| `wavelength_m` | 1.55e-6 m | Published anchors S7–S9 align chemical calibration, squeezing and fiber loss | Real cell transmission and readout at this wavelength |
| `nacl_index_polynomial` | −0.0800, 0.0740, 0.1620, 1.3162 | Published anchor: S7 Table 2, NaCl mass fraction at 298 K | Local slope and calibration uncertainty in the actual water matrix |
| `dn_dT_RIU_K` | −1.485e-4 RIU/K | Published anchor: [Kim, S10](https://opg.optica.org/abstract.cfm?uri=sensors-2012-STu1F.3), water at 1550 nm | Composition/temperature dependence; not a universal coefficient |
| `fiber_loss_db_km` | 0.18 dB/km | Manufacturer anchor: [Corning, S9](https://www.corning.com/media/worldwide/coc/documents/Fiber/application-notes/AN2008.pdf) | Installed routes, splices and connectors separately |
| `effective_interaction_length_m` | 1e-5 m | Assumed short effective path for the concentration-to-phase conversion; a test geometry, not an optimized cell | Measure effective slope and loss jointly; no absorption-based optimization was performed |
| `baseline_nacl_mg_kg` | 500 mg/kg | Assumed dilute reference within S7's fit range; defines linearization point | Partner water composition; not a regulatory target or measured well concentration |
| `power_per_node_w` | 1e-8 W | Assumed low-dose constraint exposes the quantum hypothesis; sweep checks its importance | Establish an operational reason for it; ~28 nW coherent matches default quantum RMSE |
| `squeezing_photons_per_node_mode` | 0.1 | Assumed allocation schedule; source Nₛ grows with M before the cap | Measure actual source flux and compare fixed-total resources |
| `squeezing_cap_db` | 10 dB | Engineering assumption informed by 12.3 dB telecom squeezing in [Mehmet, S8](https://arxiv.org/abs/1110.3737) | S8 is not a guarantee for this instrument's band and optical losses |
| `squeezing_mode_rate_hz` | 1e6 s⁻¹ | Assumed flat effective mode rate for photon accounting | Measure spectral squeezing and modulation/demodulation efficiency; not a 1 MHz water sample rate |
| `phase_lock_rms_rad` | 0.01 rad | Assumed small jitter for squeezed/antisqueezed mixing | Measure phase-lock spectrum and non-Gaussian excursions |
| `detector_efficiency`, `sample_transmission`, `coupling_transmission` | 0.95, 0.90, 0.90 | Assumed component budget, chosen to explore an efficient bench system | Measure end-to-end efficiency; no selected components validate the combined budget |
| `splitter_excess_db_per_stage` | 0.05 dB | Assumed modest excess loss per ceil(log₂M) stage | Measure real distribution loss; ideal splitting is already in state construction |
| `pilot_nodes` | 16 | Assumed illustrative count: four binary stages, Nₛ=1.6 below the 2.025 cap; neither optimal nor deployment-derived | Start at one/four nodes (S6 precedent); choose count from coverage and loss requirements |
| `pilot_fiber_length_km` | 0.10 km | Assumed compact-facility links to separate bench feasibility from regional loss | Survey an actual facility; no route is verified |
| `maximum_nodes` | 64 | Assumed sweep limit large enough to expose source saturation and distance penalties | Not a demonstrated hardware count; changing regional M changes the sampled population |
| `route_stretch` | 1.3 | Assumed overhead over straight-line distance | Survey real fiber routes; geometry does not establish connectivity |
| `hub_lat`, `hub_lon` | 34.05, −118.24 | Assumed geographic reference to make the supplied-coordinate stress test reproducible | Not a partner facility or proposed installation permission |
| `controlled_temperature_rms_K` | 0.00005 K | Ambitious assumed compensated residual chosen to expose optical noise | Measure residual drift; cannot infer this capability from a thermometer accuracy bound |
| `field_temperature_rms_K` | 0.01 K | Assumed adverse scenario at the numerical scale of EXO's ±0.01°C specification (S11) | Not a conversion of manufacturer accuracy into stochastic RMS and not measured field noise |
| `common_temperature_correlation_s` | 60 s | Assumed slow drift so that longer integration is not given a free white-noise benefit | Fit autocovariance from a real instrument |
| `independent_calibration_rms_mg_kg` | 0.03 mg/kg | Assumed fixed session offsets, independent across taps; prevents claiming unlimited temporal averaging | Measure spatial dependence and common bias; common bias does not average out |
| `sensor_response_tau_s` | 10 s | Assumed first-order sample/readout lag; T95≈30 s by calculation | Measure fluidics and transducer response; not imported from RF optical experiments |
| `test_event_delta_mg_kg` | 0.15 mg/kg | Assumed settled mean step to compare power of tests; selected illustrative signal | Obtain event requirements from an operator; neither safety limit nor pollutant-specific threshold |
| `false_alarm_probability_per_decision` | 0.01 | Assumed matched statistical operating point; easy to inspect a detection/false-alarm tradeoff | Too many null flags for direct use at 1 Hz; design a time-based operational policy |
| `monte_carlo_trials` | 100,000 per hypothesis/strategy | Numerical choice to check analytic Gaussian probabilities with sampling error | Does not simulate 100,000 independent seconds of slow thermal drift |
| `seed` | 2601006 | Reproducibility choice | A single trace is illustrative; multiple measured events are still required |

## Settings in the experiment code

The 1 s headline window, M=33–64 ideal-slope fit, 1 nW–70 µW power sweep, transmission range 0.05–0.99 and thermal range 0.005–10 mK are numerical study choices in [run.py](../src/run.py). They do not come from a field study. The 360 s example, 90–135 s staggered arrivals, 0.35 mg/kg mean event amplitude, ±25% spatial variation and 25 s rise are synthetic scenario settings. They illustrate nonuniform changes rather than estimate real event statistics. The synthetic trace amplitude differs intentionally from the settled 0.15 mg/kg ROC test.

The great-circle radius of 6371 km and coordinate deduplication are geometry conventions; the route multiplier remains assumed. Exact SI h and c are used through SciPy. The 95% detection target and single-tap comparison in [practical_comparisons.py](../src/practical_comparisons.py) are additional interpretive calculations, not achieved operational requirements.

## Decision implied by the evidence

Proceed first with transducer and noise-budget measurements, then a one/four-tap comparison. A 16-tap deployment is justified only if useful coverage and measured optical/thermal performance warrant it. If a higher-power coherent probe or conventional conductivity sensor meets the actual requirement more simply, this model provides no basis to prefer quantum hardware. Performance, cost and sustainability require measurements at matched useful outcomes.
