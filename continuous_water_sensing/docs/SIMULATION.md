# How the simulation was developed and runs

Updated 7 October 2026. This is a **classical numerical simulation of proposed quantum optical sensing**. It runs locally on a CPU. The quantum resource is squeezed light in the physical model; no quantum computer or optical device executed these experiments. The report and slide decks distinguish the implemented software from the proposed hardware.

The supplied NYUAD template's slide 2 requests the hack stack, algorithms, frameworks and hardware/software status. This document provides that implementation account. Code references are the primary evidence for software behavior; literature supplies physical anchors, not a claim that the proposed water device has been built.

## Languages and libraries

| Component | Implementation | Role |
|---|---|---|
| Scientific model and experiments | Python 3.12; [requirements.txt](../requirements.txt) pins NumPy 2.3.5, SciPy 1.18.1, pandas 2.2.3, Matplotlib 3.11.2 | CPU numerical calculations and deterministic regeneration |
| NumPy | Arrays, linear algebra, polynomial operations, seeded random generator | Covariance propagation, estimator variance and synthetic Gaussian noise |
| SciPy | SI constants, normal distribution; root solving in the comparison helper | Photon conversion, analytic detection probabilities and classical-power matching |
| pandas | CSV input/output and tabular filtering | Geometry, scenario tables and plotted series |
| Matplotlib with Agg backend | Static plots | Ten PNG/SVG figures; no graphical desktop needed |
| Python standard library | argparse, json, pathlib, hashlib, unittest | Configuration, paths, hashes and 13 model checks |
| Presentation authoring | JavaScript ES modules in Node.js with bundled `@oai/artifact-tool` | Editable PPTX export and validation; separate from the science |
| Offline presentation | Python-generated HTML/CSS/JavaScript | Browser slideshow with embedded charts and notes |
| PDF export | Node.js, Playwright and Chrome | Prints the HTML slide deck; does not run quantum calculations |

There is no Qiskit/PennyLane dependency, quantum circuit, GPU requirement, trained neural network or optimization over a learned model. No API key or cloud account is required for scientific reproduction. Presentation export uses the separately supplied artifact runtime; see [BUILD_PRESENTATION.md](BUILD_PRESENTATION.md).

## Development approach

The implementation encodes the published split-squeezed-state mechanism from [Zhuang et al.](https://arxiv.org/abs/1711.10459), with a local homodyne estimator and a chemical slope from [Saunders et al.](https://doi.org/10.1364/AO.55.000947). Project code adds engineering assumptions for the transducer, losses, drift and lag, then compares baselines under explicit optical budgets. It computes covariance and error from the equations; it does not hardcode an error proportional to 1/M. The ideal exponent is fitted to generated values.

The existing [model.py](../src/model.py) is the numerical kernel; [run.py](../src/run.py) defines experiment sweeps and figures; [validate.py](../src/validate.py) checks model identities and statistical consistency. [prepare_geometry.py](../src/prepare_geometry.py) selects distinct coordinates from the historical input. This revision adds [practical_comparisons.py](../src/practical_comparisons.py) to reproduce the classical-power, localized-event and detection-target interpretations. The scientific equations and default parameters were not changed by the documentation revision.

Team discussions supplied candidate ideas. They did not calibrate component efficiencies or prove a sensor count. All parameter choices are classified in [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md). This account describes the code and reproducible calculation, not an independently audited development history.

## Inputs and their meaning

| Input | Contents | How it is used |
|---|---|---|
| [config/default.json](../config/default.json) | Wavelength, chemical fit, optical budget, efficiencies, thermal/calibration assumptions, seed and decision settings | Numerical specification of the default scenario |
| [data/site_geometry.csv](../data/site_geometry.csv) | 64 distinct supplied locations with distances to an assumed hub | Regional loss scenarios; not measured fiber routes or contamination concentrations |
| [data/draft_sha256.json](../data/draft_sha256.json) | Original draft file hashes | Preservation check, not validation of the original scientific claims |
| Synthetic events in `run.py` | Staggered local concentration rises, assumed response lag and noise | Illustrative continuous monitoring trace |
| Published constants | NaCl fit, water thermo-optic coefficient, fiber attenuation | Traceable anchors embedded in configuration; experiment code does not fetch papers at runtime |

The headline concentration unit is **mg/kg differential NaCl-equivalent**. The supplied arsenic-labelled measurements are not converted to NaCl or used to train a model. Coordinates provide a geometry stress test only. No live instrument feed enters this simulation.

## Calculation sequence

1. **Load the scenario.** Read configuration and geometry. Seed NumPy with 2601006. Select node counts M=1…64 and pilot or regional links.
2. **Convert chemistry into phase.** Differentiate the measured NaCl index polynomial at the assumed 500 mg/kg background. Multiply by 2πL/λ using the assumed 10 µm effective interaction length.
3. **Account for resources and transmission.** Convert launched power into photon flux. Deduct squeezed photons from carrier allocation. Calculate fiber and component losses; cap the source at 10 dB.
4. **Construct the readout covariance.** Propagate the squeezed state through loss, include phase-jitter mixing and calibrate each local output into concentration units. Coherent, independent squeezed and distributed states share the declared probe budget. A regional comparator optimizes coherent power allocation.
5. **Estimate the mean and its error.** Use q̂=Σyᵢ/M and optical variance wᵀΣw. Add independent calibration variance/M and common temperature variance, including the exact averaging factor of the assumed 60 s OU process. Take the square root for total RMSE.
6. **Run decisions and a time trace.** The settled Gaussian test uses a 0.15 mg/kg mean step and 1% false alarm per decision. Generate 100,000 null and 100,000 alternative draws per strategy to check the analytic probabilities. Separately generate a 360 s synthetic trace with unequal arrivals, shared drift and 10 s first-order response lag.
7. **Sweep and export.** Explore sensor count, resources, power, integration, loss and temperature. Save numeric series before plotting. Generate report tables and decks from saved results.

The main RMSE curves are analytic covariance calculations; the Monte Carlo draws check decision probabilities. The time trace is a third, distinct output. Its single seed cannot establish operational detection delay or false-alarm performance. Calibration offsets persist in time, while common drift does not disappear by adding taps.

## Outputs and what they establish

| Output | Contents and interpretation |
|---|---|
| [results/summary.json](../results/summary.json) | Exact headline errors, detection probabilities, ideal fitted exponents and configuration hash |
| `scaling.csv`, `resources.csv`, `averaging.csv`, `power_sensitivity.csv` | Scenario curves; each row describes modeled settings and outputs |
| [results/detection.csv](../results/detection.csv) | Analytic and Monte Carlo detection/null probabilities |
| [results/time_trace.csv](../results/time_trace.csv) | Synthetic truth, sensor response and noisy estimates; no field measurements |
| `results/feasibility.npz` | Numerical grid of loss/temperature sensitivity |
| [results/practical_comparisons.json](../results/practical_comparisons.json) | Derived power matching, 95% detection requirements and single-tap dilution |
| [results/validation.txt](../results/validation.txt) | Saved model-check log; validates implementation, not unmeasured physical assumptions |
| [figures/index.html](../figures/index.html) | Offline gallery of ten PNG/SVG figures |
| [docs/RESULTS.md](RESULTS.md) | Generated numerical results and interpretations |
| [presentation/Presentation.html](../presentation/Presentation.html) and PPTX/PDF files | Communication artifacts; presentation tools do not supply scientific results |

**Worked example:** default 16 taps, 100 m links, 10 nW/tap, 1 s and 50 µK common temperature residual produce η=0.731827. The resulting total RMSE is 0.092101 mg/kg coherent and 0.066389 mg/kg distributed. The model predicts a reduction of 27.92%. Those inputs are engineering assumptions except where the source register identifies measured anchors; the output is a prediction, not a measurement.

## Reproduction and verification

From the project directory, with Python 3.12 available:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
bash src/reproduce.sh
```

The prepared `.venv` can be reused. The script runs `run.py`, `validate.py`, `practical_comparisons.py`, `report.py`, `presentation_data.py`, `build_html.py` and `figure_gallery.py`. To capture a fresh validation log explicitly:

```sh
.venv/bin/python src/validate.py > results/validation.txt 2>&1
```

The 13 existing checks cover physical covariance, analytic/numerical agreement, zero-squeezing and high-loss limits, one-node equivalence, arbitrary local signals, coherent power allocation, chemical units, OU limits, Monte Carlo sampling uncertainty, distinct geometry and preserved draft hashes. They do not certify real transducer losses, chemical selectivity, drift or field alarms.

`run.py --config PATH` accepts a scenario file but overwrites the project result directory. For explorations, use a separate project copy; report and deck generators assume the default 16-tap/64-candidate study and must be reviewed if settings change. The comparison helper reads `default.json`. Do not mix alternative-scenario results with default report text. Python scientific reproduction does not rebuild PPTX/PDF; follow the presentation build guide for those artifacts.
