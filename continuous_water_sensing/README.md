# Continuous water sensing

A new, self-contained simulation project for the NYUAD hackathon. The original `NYUAD-Hackathon-T7-main` folder is unchanged and is treated as a draft reference.

The experiment estimates **dissolved-salt concentration changes**, using a published 1550 nm NaCl refractive-index calibration and a continuous-variable Gaussian optical network. It demonstrates where distributed squeezing improves aggregate precision, and where optical loss or ordinary technical noise removes that improvement. The proposed quantum water sensor is not measured hardware.

## Start here

- **[Project report](docs/PROJECT_REPORT.md)** — sourced problem, project contribution, assumptions and experiment conclusions.
- **[How the simulation runs](docs/SIMULATION.md)** — languages, libraries, inputs, calculations, outputs and validation.
- **[Design decisions](docs/DESIGN_DECISIONS.md)** — evidence, rationale and validation requirements for every configuration field.

- **[Offline presentation](presentation/Presentation.html)** — double-click; arrows/space to navigate, F for fullscreen, N for source and speaker notes. No network required.
- **[Editable PowerPoint](presentation/Continuous_Water_Sensing.pptx)** — 20 slides, native editable charts with embedded chart data.
- **[Presentation PDF](presentation/Continuous_Water_Sensing.pdf)** — 20 printable slides.
- **[Results](docs/RESULTS.md)** — numerical findings and interpretation.
- **[Model](docs/MODEL.md)** — equations, resources, assumptions and limits.
- **[Sources](docs/SOURCES.md)** — paper review, real hardware specifications and complete parameter provenance.
- **[Figures](figures/)** — ten publication-style figures, each as PNG and editable vector SVG.

## Results at the default parameters

| Comparison | Coherent | Independent squeezed | Distributed squeezed |
|---|---:|---:|---:|
| 16-node pilot optical RMSE, mg/kg | 0.0796 | 0.0647 | 0.0476 |
| 16-node pilot total RMSE, mg/kg | 0.0921 | 0.0796 | 0.0664 |
| Detect 0.15 mg/kg increase at 1% per-decision false alarm | 24.3% | 32.9% | 47.3% |

The pilot quantum total RMSE is **28% lower (1.39× precision gain)** than coherent light at equal launched photon resources. It assumes 100 m fiber links, 10 nW/node, 1 s windows, and an ambitious 0.05 mK common compensated-temperature residual. At 10 mK residual, technical error dominates and the gain is negligible. A regional test using 64 distinct supplied well coordinates gives only **1.11×** total precision gain over optimally allocated coherent light. These are model predictions, not field measurements.

Ideal, lossless, uncapped squeezing produces a fitted error exponent of −0.953 over 33–64 nodes, versus −0.500 for coherent and independent squeezed probes. The realistic model does not promise indefinite 1/M scaling. Node count, optical power, squeezed photons, measurement time and geographic coverage are accounted for separately.

## Reproduce

Python 3.12 recommended. From this project directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/run.py
.venv/bin/python src/validate.py
.venv/bin/python src/presentation_data.py
.venv/bin/python src/build_html.py
```

The prepared local `.venv` already has the dependencies, so you can start at `src/run.py`. No quantum SDK or hardware account is required. `run.py` writes CSV/JSON/NPZ results and PNG/SVG figures. It uses seed 2601006. `presentation_data.py` and `build_html.py` regenerate the HTML presentation from those results. All mutable simulation parameters are in `config/default.json`; `python src/run.py --config PATH` accepts a scenario copy. The standard report/presentation assumes a 64-candidate sweep and 16-node pilot; use the model API for other deployment sizes. Outputs are overwritten inside this new project only.

PowerPoint source is `src/build_deck.mjs`. It requires the Codex bundled `@oai/artifact-tool`, presentation skill finalizer and Python runtime, not a public pip package. See `docs/BUILD_PRESENTATION.md`. PPTX charts round display/workbook coordinates to ten significant digits for Excel portability; full precision remains in the scientific result files.

## Project layout

```text
config/default.json        Numerical configuration
src/model.py               Chemical calibration, CV covariance, loss and technical noise
src/run.py                 Scenario sweeps, figures, continuous trace, Monte Carlo ROC
src/validate.py            Physics, statistics, units and preservation checks
src/presentation_data.py   Common slide content and chart values
src/build_html.py          Offline HTML authoring
src/build_deck.mjs         Editable PowerPoint authoring
src/export_pdf.mjs         Optional browser PDF export and HTML layout checks
src/prepare_geometry.py    Rebuild the selected geometry from the supplied draft CSV
src/report.py              Generate the numerical results report
src/figure_gallery.py      Build offline SVG figure gallery
src/package.py             Rebuild the shareable project ZIP
src/reproduce.sh           One-command scientific/HTML rebuild
presentation/             Finished HTML, PPTX, PDF and slide data
figures/                   Ten scientific figures in PNG/SVG; offline gallery
results/                   Raw CSV/JSON/NPZ results and validation log
data/                     Selected coordinates and original draft SHA-256 hashes
docs/                     Research, methods, results and build notes
```

## Important interpretation

- This is a **NaCl-equivalent change measurement**, not detection or identification of arsenic, nitrate or pathogens. A regional mean cannot certify all locations are safe.
- The empirical chemical slope is real; optical geometry, losses beyond the fiber anchor, thermal compensation and calibration floors are explicitly proposed design values.
- The supplied well file provides geometry only. It lacks dates, units metadata and quality flags, so its field-measurement provenance is not independently verified.
- YSI accuracy specifications are reported as real-world context, never treated as Gaussian shot-noise sigma or a directly comparable laboratory detection limit.
- No QML, QAOA, cost, total electrical-energy or deployment advantage is claimed.

## Detailed report and NYUAD pitch

- [Extensive project report](docs/PROJECT_REPORT.md): problem, proposed solution, equations, parameter provenance, all ten experiments with plots, literature interpretation, limitations, future work and judging criteria.
- [Team 7 NYUAD pitch](presentation/Team_7_NYUAD_Pitch.pptx): separate 15-slide deck using the supplied template and judging guidance, with editable charts and source notes.
- [Pitch content and notes](presentation/Team_7_Pitch.json) and [build instructions](docs/BUILD_PRESENTATION.md).

The pitch retains Team 7 as the working name. Confirmed roster, affiliations, team photo and logo remain to be added. It distinguishes quantum sensing from quantum computational advantage and separates simulated monitoring metrics from unmeasured sustainability outcomes.

- [Five-slide ideation deck](presentation/Team_7_Ideation.pptx): concise problem/SDG 6, proposed solution, simulation design, results and next steps using the supplied NYUAD template.
- [Expanded visual ideation deck](presentation/Team_7_Ideation_Visual.pptx): five slides with two sourced contextual photos, four editable result charts, detailed plot captions and source notes.

Documentation revised 7 October 2026. Practical comparison: ~28 nW/tap coherent power matches the default 10 nW/tap distributed result under the same technical-noise assumptions. Thus the low-dose constraint needs operational justification. All reported improvements remain simulated. Alternative-config runs overwrite results; use a separate copy and review default-specific report/deck text (see SIMULATION.md).

Revision of 7 October 2026: all decks include visible simulation implementation details. The general deck has 20 slides (implementation detail on slides 4, 19–20); the NYUAD pitch has 15 slides (implementation on slides 3–4); both ideation decks retain five slides (implementation on slide 3). Source citations and detailed reproduction notes accompany the slides.
