# Response to judges: Team 7 SensorFlow

Final deck: `Team_7_Final.pptx` / `Team_7_Final.pdf` (5 main slides, backup B1–B8).
Numbers come from `results/judges_response.json`, produced by `src/judges_response.py`. All results are simulated; no hardware was measured.

## Our conclusion in one sentence
For salinity, quantum sensing is not needed. Coherent light at 28 nW matches the 10 nW squeezed array, no physical limit caps probe power anywhere near that level, and a temperature-compensated conductivity probe is 2× (controlled) to 91× (field) better. We show the exact conditions under which squeezing would pay off.

| Judge point | Where it is answered | Answer |
|---|---|---|
| Narrow to one analyte and threshold (J1, J2) | Slide 1 | Dissolved salt (NaCl-equivalent): a 0.15 mg/kg rise on 500 mg/kg in 1 s, triggering a grab sample at reuse or desalination blending points |
| End-to-end system flow (J1) | Slide 2 | Tap → 1550 nm phase cell → squeezed probe and homodyne → classical estimator → alarm and lab confirmation |
| Which quantum technique; why QAOA (J1, J2) | Slide 2, B1 | CV distributed quantum sensing only. Processing is a classical linear estimator (Kalman-equivalent). QAOA is not needed because greedy placement is near-optimal |
| Replace the "√N" claim (J4) | Slide 2, B3 | The measured gain is a constant factor: 1.39× (pilot) and 1.11× (64 regional taps), with a loss bound of 1/√(1−η) = 1.93× |
| Justify the power cap (J3, J4, J5 priority 1) | Slides 3–4 | Coherent at 28 nW matches the quantum result, and above ~1 µW both hit the same drift floor. Per-tap limits are SBS 125 µW, photothermal 189 µW and Class 1 eye safety 625 µW. A real cap would need ~70,000 taps per source |
| dB loss budget and source squeezing (J4, J5 priority 2) | Slide 4, B2 | 1.36 dB in total. Keeping 1.39× needs 9.2 dB entering the network: 11.3 dB generated at 95 % escape, 16.4 dB at 90 %. The gain falls below 1.1× after 5.3 dB of extra loss |
| Conductivity head-to-head (J4, J5 priority 3) | Slide 3 | Same background, 1 s window and false-alarm rate. Conductivity reaches 0.033 mg/kg (1 probe), against 0.066 mg/kg for the quantum array (controlled). In the field it reaches 0.10 mg/kg, against 9.14 mg/kg |
| Thermal drift (J3, J5) | Slides 3–5 | 1 mK of drift looks like 0.92 mg/kg of salt optically, but 0.01 mg/kg to conductivity. The quantum gain needs ≲0.1 mK |
| False alarms, impact, scale (J2) | B7 | At 1 false alarm per week, 16 conductivity probes detect the step 100 % of the time and the quantum array 0.8 %. Covers cost, calibration and maintenance, a stop rule, and a lab pilot |
| SDG and impact (J2) | Slide 1, B7 | SDG 6.1, 6.3 and 6.4. The deliverable is a feasibility map that tells a utility whether quantum sensing would pay off |
| Does quantum sensing fit the competition scope? (J3) | Slide 2, notes | It is a quantum technology. We are explicit that no quantum-computing speed-up is claimed |
| Placement and GNN distract (J4) | B1 | Moved to backup |

| Where would quantum really win? | Slide 5, B8 | A four-gate screen. Salt, a salt reference arm and a plasmonic microcystin chip all fail, because drift is 35–12,800× the shot noise at the real power cap. Dose-limited live-cell measurement gets closest (1.16× lower error, i.e. the 35 % power-SNR gain Casacio et al. measured), but its 56 % loss caps it at 1.34×, and no routine water decision needs it yet |

## New assumptions (spec- or literature-derived, `config/judges_response.json`)
- **Water absorption:** ≈10 cm⁻¹ at 1550 nm (Hale & Querry 1973). The 5 µm beam radius and 1e-3 laser intensity noise are assumptions.
- **Conductivity probe:** 2 µS/cm per mg/kg, 2 %/°C compensation, 0.1 µS/cm resolution, ±0.01 °C sensor (YSI EXO-class). Resolution is treated as quantisation noise.
- **Fibre and eye safety:** SBS limit of 2 mW per shared trunk; Class 1 eye-safe ≈10 mW at 1550 nm.
- **Squeezer escape efficiency:** 1.0, 0.95 or 0.9. The original model did not include it.

## Reproduce
```
.venv-win\Scripts\python src\run.py
.venv-win\Scripts\python src\judges_response.py
.venv-win\Scripts\python src\advantage_path.py
.venv-win\Scripts\python src\validate.py
.venv-win\Scripts\python src\build_final_deck.py
```
`validate.py` reports one pre-existing error: it looks for Nathan's original draft folder, which is not in this copy.
