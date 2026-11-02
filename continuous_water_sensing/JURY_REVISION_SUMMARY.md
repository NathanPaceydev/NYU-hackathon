# Jury revision: what we changed and why

The jury's main message was that our quantum advantage was only claimed, not proven. We checked it properly. For salt, quantum sensing loses to ordinary sensors. So the revised deck says that plainly and adds a test for where quantum sensing would win.

Everything is still simulation; no hardware was measured.

## What the jury asked for, and what we did

| Jury comment | What we did | Where |
|---|---|---|
| Pick one analyte and threshold | Dissolved salt: catch a 0.15 mg/kg rise on 500 mg/kg within 1 s, then pull a grab sample | Slide 1 |
| Show the whole system | Flow diagram: tap → phase cell → squeezed light + homodyne → classical estimator → alarm | Slide 2 |
| Which quantum technique? Why QAOA? | Quantum *sensing* only (distributed squeezed light). Processing is classical. QAOA dropped because greedy placement is as good | Slide 2, B1 |
| "√N" claim is wrong with loss | Replaced by the measured constant factor, 1.39× (pilot) and 1.11× (64 taps), with the loss ceiling 1/√(1−η) | Slide 2, B3 |
| Justify the 10 nW power cap | We computed it. Ordinary light at 28 nW matches us, and the real limits (fibre SBS, water heating, eye safety) are 125–625 µW. There is no real cap | Slides 3–4 |
| dB loss budget and squeezing needed | 1.36 dB in total; 11.3 dB must be generated at the source to keep 1.39× | Slide 4, B2 |
| Compare with a conductivity probe | Same background, window and false-alarm rate. Conductivity is 2× better in the lab and 91× better in the field, because temperature fools the optical sensor ~90× more | Slide 3 |
| False alarms, impact, scale, SDG | At 1 false alarm per week: conductivity catches the step 100 %, quantum 0.8 %. SDG 6.1/6.3/6.4. Cost and stop rule | Slide 1, B7 |
| Placement/GNN distract | Moved to backup | B1 |

## What we added beyond the comments

**A test for real quantum advantage** (slide 5, B8). We screened four targets against four gates:
1. classical sensors fall short;
2. a real power or dose limit binds while photon noise still dominates;
3. loss is low enough for at least 1.5×;
4. classical can't simply measure for longer.

| Target | Result |
|---|---|
| Salt | Fails: temperature drift swamps photon noise, and conductivity wins |
| Salt + thermal reference arm | Fails: matches conductivity, but squeezing adds nothing |
| Plasmonic microcystin chip | Fails: classical SPR already reaches 73 ng/L, under the WHO 1 µg/L limit |
| Live-cell Raman (light damages the cells) | Closest: 1.16× measured by Casacio et al. 2021, but 56 % loss caps it at 1.34× |

No water target passes yet. The path forward is a water decision that needs a measurement limited by light damage, built with lower loss.

**Why:** the jury asked whether quantum is *necessary*. An honest "not for salt, and here is when it would be" answers that better than defending a weak claim.

## How

- `src/judges_response.py`: loss budget, power cap, conductivity comparison, loss-limited gain. It reuses `src/model.py` unchanged, so the original pilot results reproduce exactly.
- `src/advantage_path.py`: the four-gate screen.
- `src/build_final_deck.py`: rebuilds the deck from the submitted template, pulling every number from `results/*.json`.
- `src/validate.py`: 6 new checks, including that the loss budget matches the model, the 28 nW power matches, and no gain exceeds the loss ceiling. 18/19 pass; the one error is a check for Nathan's original folder, which isn't in this copy.
- Every new parameter is cited in `docs/SOURCES.md`; source files are in `docs/references/`.

Reproduce (Windows):
```
.venv-win\Scripts\python src\run.py
.venv-win\Scripts\python src\judges_response.py
.venv-win\Scripts\python src\advantage_path.py
.venv-win\Scripts\python src\validate.py
.venv-win\Scripts\python src\build_final_deck.py
```
Output: `presentation/Team_7_Final.pptx` and `.pdf` (5 slides + backup B1–B8).
