# Evidence and parameter register

Updated 7 October 2026. Team discussions and the original proposal motivate questions; they are not independent scientific evidence. Published papers support only the stated scope. Design choices without a measurement are explicitly assumptions. The original draft files are preserved as historical input.

## Papers discussed by the team

**S1. Dowran et al., Quantum-enhanced plasmonic sensing, Optica 5, 628–633 (2018).** [DOI](https://doi.org/10.1364/OPTICA.5.000628). Supplied as `quantum_photonic_sensing.pdf`, six pages. Actual experiment: refractive-index modulation of AIR by 199 kHz ultrasound, 795 nm twin beams, 70 µW detected probe power. Reports 9 dB source intensity-difference squeezing, 4 dB after sensor, approximately 66% sensor transmission and 27% other optical losses. Reported sensitivities: matched classical 8.6e-10, inferred best single-beam classical 6.8e-10, twin beams 5.5e-10 RIU/sqrt(Hz). Gains 1.56 and 1.24 respectively. Sensitivity is a bandwidth-normalized detection measure from its SNR/confidence procedure, not a manufacturer 1-s RMS accuracy. The single-beam baseline is estimated, not a separately achieved field detector. We reproduce these three reported numbers in Figure 09; we do NOT transfer this RF air sensitivity to slow water measurements or to 1550 nm. Page 5 proposes modulation to move DC signals into a squeezing band; that is an engineering requirement here.

**S2. Pooser & Lawrie, Supporting information: Plasmonic trace sensing below the photon shot noise limit.** Supplied `sensing_below_photonic_limit.pdf`, four pages. This attachment is supporting information, not the complete experimental paper. Equations 11–14 treat twin-beam difference noise and beam-splitter loss. Supports vacuum entering unused/loss ports and degradation with transmission. It is not the supplement to S1 and does not calibrate NaCl, nitrate or arsenic. We use the same Gaussian attenuation principle, not a claimed replication of its twin-beam apparatus.

**S3. Abraham-Mexicano et al., Quantum Machine Learning for Water Pollution Profiling in the Rio Santiago Basin, Quantum Reports 8, 60 (2026).** Supplied 20-page PDF. [DOI](https://doi.org/10.3390/quantum8030060). Studies 13 monitoring stations, 2009–2022, PCA/RBF/quantum kernels and small IBM hardware samples. Matched 650-row comparisons retain RBF as strongest nonlinear comparator; 24-row hardware checks show feasibility, not superiority. Cleaning changes results. Contribution here: explicit baselines, matched resources, and data lineage. This paper provides neither quantum sensor physics nor a chemical phase calibration. No QML advantage is claimed and QML is not implemented.

## Distributed sensing theory and experiment

**S4. Zhuang, Zhang & Shapiro, PRA 97, 032329 (2018).** [Paper](https://arxiv.org/abs/1711.10459). Distributed quadrature-displacement estimation using a split squeezed state. Ideal RMS scales as 1/M only while TOTAL squeezed energy grows with M; finite loss destroys the asymptotic exponent advantage. Our linearized bright-carrier phase-to-quadrature model uses an explicit homodyne covariance and estimator. It is not a general phase QFI implementation. Signal in our model is attenuated with the probe; displacement placement relative to loss must therefore be accounted for, rather than copying a formula across conventions.

**S5. Oh, Lee, Lie & Jeong, PR Research 2, 023030 (2020).** [Paper](https://doi.org/10.1103/PhysRevResearch.2.023030). Gaussian average-phase sensing. Homodyne reaches the optimum in the lossless case; under loss Gaussian readouts compete. The draft's blanket assertion that homodyne always saturates QFI is too strong. We make no universal optimality claim.

**S6. Guo et al., Distributed quantum sensing in a continuous variable entangled network, Nature Physics 16, 281 (2020).** [Preprint](https://arxiv.org/abs/1905.09408), [DOI](https://doi.org/10.1038/s41567-019-0743-x). Four-node experimental CV average-phase sensing. This establishes a laboratory precedent, not a 64-well deployment. The chat's [Nature Photonics link](https://doi.org/10.1038/s41566-020-00718-2) is a distinct entangled-photon phase experiment, not this CV experiment.

## Numerical anchors

**S7. Saunders et al., Refractive indices of common solvents and solutions at 1550 nm, Applied Optics 55, 947 (2016).** [Article and Table 2](https://opg.optica.org/ao/abstract.cfm?uri=ao-55-4-947), [DOI](https://doi.org/10.1364/AO.55.000947). 34 NaCl solutions. At 298 K, fit n(W) = -0.0800 W^3 + 0.0740 W^2 + 0.1620 W + 1.3162; W is NaCl mass fraction, range 0–0.25. In code W=c/1e6 with c in mg/kg. At 500 mg/kg, dn/dc = 1.6207394e-7 RIU/(mg/kg). The differential slope is an empirical calibration anchor; polynomial absolute accuracy does not establish sub-mg/kg absolute concentration accuracy. Temperature and mixture specificity require independent calibration. No conversion to mg/L without a density measurement.

**S8. Mehmet et al., Squeezed light at 1550 nm with a quantum noise reduction of 12.3 dB, Optics Express 19, 25763 (2011).** [Preprint](https://arxiv.org/abs/1110.3737), [DOI](https://doi.org/10.1364/OE.19.025763). 12.3 dB observed at 5 MHz, squeezing down to 2 kHz. Our 10 dB source cap is an engineering target consistent with the existence of strong telecom squeezing, NOT a broadband/low-frequency performance guarantee. The assumed flat 1 MHz effective mode rate and modulation/demodulation efficiency need testing.

**S9. Corning SMF-28 Ultra application note AN2008.** [Manufacturer PDF](https://www.corning.com/media/worldwide/coc/documents/Fiber/application-notes/AN2008.pdf). Uses 0.18 dB/km at 1550 nm as a fiber-loss numerical anchor. Our route stretch, connector/coupler losses, splitter excess, and detectors are separately specified; installed cable performance is not guaranteed by bare-fiber attenuation.

**S10. Kim et al., Double Cladding Fiber Interferometer Suitable for Measuring Thermo-Optic Coefficient of Liquid, Optical Sensors 2012, STu1F.3.** [Primary abstract](https://opg.optica.org/abstract.cfm?uri=sensors-2012-STu1F.3). Reports water dn/dT approximately -1.485e-4 RIU/°C at 1550 nm. Used as a thermal cross-sensitivity anchor. Not universal across temperature, composition or sensor geometries. At our NaCl slope, 1 mK produces about 0.916 mg/kg apparent change. Temperature residuals and correlation times are assumptions, not measured capabilities.

**S11. YSI EXO conductivity/temperature sensor.** [Manufacturer specification](https://www.ysi.com/product/id-599870/exo-conductivity--temperature-smart-sensor). Conductivity: ±0.5% or 0.001 mS/cm over 0–100 mS/cm. Temperature: ±0.01 °C over -5 to 35 °C, resolution 0.001 °C. Salinity: ±1% or 0.1 ppt, whichever greater. These are commercial accuracy bounds, NOT iid standard deviations, and are not used as shot noise. Practical salinity is not exactly NaCl mass fraction; the reference provides deployment context, not a fair numerical head-to-head with our differential laboratory model. A 10 mK stochastic residual scenario is motivated by the temperature scale only; it is not a statistical interpretation of YSI accuracy.

**S12. YSI EXO NitraLED, 2024 specification sheet.** [Manufacturer PDF](https://www.ysi.com/File%20Library/Documents/Specification%20Sheets/EXO-NitraLED-Specification-Sheet.pdf). For 0–10 mg/L-N, accuracy ±0.1 mg/L-N or 5%, whichever greater within 2°C; T95 <30 s; 10 mm optical path; UV LEDs 235/275 nm. Pure-water qualifications apply. Included as a second real sensor benchmark only; UV absorbance and nitrate-N units do not transfer to the telecom NaCl phase model. Older FAQ differs on range/detection limits; use dated sheet rather than mixing versions.

## Problem and monitoring context

**S13. World Health Organization, Drinking-water, 13 September 2023.** [Fact sheet](https://www.who.int/news-room/fact-sheets/detail/drinking-water). Reports at least 1.7 billion people using faecally contaminated drinking-water sources in 2022 and describes water-safety planning. Used to explain the public-health importance of monitoring; our NaCl proxy does not detect microbial contamination or establish a health benefit. The data year is retained rather than presented as a 2026 estimate.

**S14. United Nations, Sustainable Development Goals Report 2025, Goal 6.** [Official report](https://unstats.un.org/sdgs/report/2025/Goal-06/). Reports 120 countries contributing water-quality information in 2023 and about two million measurements, only 60,000 from the poorest regions. This supports the monitoring-gap problem statement. These are measurements used in SDG reporting, not a count of all sensors or all measurements worldwide. They do not establish a quantum-noise bottleneck, a paying market or a 16-sensor requirement.

**S15. US EPA, Online Water Quality Monitoring Resources.** [Official guidance collection](https://www.epa.gov/waterresilience/online-water-quality-monitoring-resources). Describes online monitoring for treatment optimization, distribution operations and detection of contamination incidents, with linked design and event-detection guidance. Supports the proposed monitoring-and-investigation role, not our optical architecture, detection threshold or claimed performance.

**S16. Supplied NYUAD presentation template and judging rubric.** [Template](../../Slides%20Templates%20%20and%20Judging/NYUAD%20Hackathon%20Presentation%20Template.pptx), slide 2 asks for “Hack Stack,” algorithms/frameworks and hardware/software status; slide 4 asks about technology, prior work and dataset integrity. [Rubric](../../Slides%20Templates%20%20and%20Judging/NYUAD%20Hackathons%20Virtual%20Ideation%20Judging%20Criteria.docx). These are project communication requirements, not scientific evidence for performance.

Source review: S7/S10 publisher pages, S4/S6/S8 arXiv records, S9 manufacturer note, S3 publisher/search record and S11/S12 manufacturer records were checked for this revision. S1/S2 also have extracted source text retained in the private build folder from the earlier review. Manufacturer specifications are context, not same-device independent performance trials. No literature search establishes research priority for the combined project.

## Explicit engineering assumptions, not measurements

| Config property | Default | Role / justification |
|---|---:|---|
| Probe wavelength | 1550 nm | Matches S7/S8/S9; not S1's 795 nm |
| Effective interaction length | 10 µm | Assumed short effective path; no absorption-based optimization or measured geometry |
| Launched power per node | 10 nW | Deliberately low-dose test budget; no evidence water mandates this limit. Sweep 1 nW–70 µW |
| Background NaCl | 500 mg/kg | Scenario around which the empirical response is linearized; not a sampled site value |
| Squeezed photons / node / temporal mode | 0.1 | Resource schedule; grows source energy with M until cap |
| Source cap / mode rate | 10 dB / 1 MHz | Plausible targets, not demonstrated together in this design |
| Phase-lock RMS | 10 mrad | Assumed; squeezed/antisqueezed mixing included |
| Detector / sample / coupling efficiencies | 0.95 / 0.90 / 0.90 | Proposed component budget, not vendor-certified device measurements |
| Splitter excess | 0.05 dB/stage | ceil(log2 M) depth approximation; actual mesh may be worse |
| Pilot fiber / node count | 100 m / 16 taps | Illustrative four-stage splitter scenario, not an optimum; Nₛ=1.6 stays below cap. S6 demonstrated four nodes. Sweep M=1..64 |
| Regional route length | 1.3 × great-circle distance | Assumed routing overhead; local homodyne detection, one-way link |
| Common temperature residual | 0.05 mK RMS | Ambitious compensated bench target; much better than S11 absolute accuracy |
| Field-like residual | 10 mK RMS | Stress scenario, not measured random error of S11 |
| Common drift correlation | 60 s | Stationary OU assumption; long averages use exact integrated covariance |
| Independent node calibration | 0.03 mg/kg RMS | Assumed fixed session offset; averages spatially, not temporally |
| Response time constant | 10 s | Assumed fluid/sample/readout lag; not imported from S1's RF response |
| Decision test | 0.15 mg/kg change, 1% false alarm | Statistical demonstration, not a safety standard or field alarm policy |

Every adjustable scalar is in `config/default.json`. Fundamental h and c use SI exact constants through scipy.constants. The model does not pretend all proposed device parameters are real-world measurements: that would require building and calibrating the hardware.

## Supplied geometry provenance

`data/site_geometry.csv` derives only identifiers and coordinates from the draft's `poc/data/wqp_groundwater.csv`. Original file: 8,889 records, 7,704 distinct coordinate pairs. Select nearest 64 DISTINCT coordinates to assumed hub (34.05, -118.24), first row per coordinate then distance/site-ID ordering. Hashes of every draft file are in `data/draft_sha256.json`; validation checks none changed. Great-circle radius 6371 km. Zero-distance duplicates cannot count as new geographic coverage. No arsenic measurements are used as NaCl values.

The draft labels its file USGS/WQP, but it lacks sampling dates, units metadata, censoring flags, query URL, site depths and laboratory methods. The new project therefore describes it as supplied USGS-labelled geometry, not independently verified field monitoring data. Site coordinates do not prove available fiber routes, site access or simultaneous water conditions. The proposed regional optical network and every contamination time series are synthetic.

For each configuration field, its reasoning and the measurement needed to validate it, see [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md). For software provenance, inputs and generated outputs, see [SIMULATION.md](SIMULATION.md).
