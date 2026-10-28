# Sensing Experiment — what was explicitly done, and where it stops

This file documents `sensing_experiment.py` precisely. It is the **Layer-1
quantum-sensing** part of the project (the "is the region contaminated?"
tripwire).

**Real data:** The experiment loads 8,889 real groundwater wells from the
USGS Water Quality Portal (`data/wqp_groundwater.csv`). It selects a
spatially coherent cluster near the LA / San Gabriel basin and maps each
well's measured arsenic concentration (µg/L) to an optical phase:

    phi_i = s * c_i      where s = 0.01 rad/µg/L

Estimation errors are reported in **µg/L**, not radians, and compared
against the EPA MCL of 10 µg/L.

Run it:

    python sensing_experiment.py

It writes:
- `results/sensing_experiment.png`  — two-panel figure (left: SQL vs Heisenberg
  with loss; right: aggregate vs single-node QFI)
- `results/sensing_experiment.json` — the raw numbers quoted below, including
  the real well IDs and concentrations used

---

## 1. What the experiment models (and nothing more)

We simulate **distributed quantum sensing** of a regional contamination
aggregate. N optical modes share one probe; each mode picks up a phase from a
local water sample; we estimate the **regional weighted sum**

    q = sum_i w_i * phi_i      (equal weights here, so q = the common phase)

by homodyne readout. The phases are derived from **real USGS arsenic
measurements**, not synthetic values. The experiment answers one question
only:

> How precisely can we estimate the **aggregate** contamination of a region
> as N grows, and does entanglement help — and by how much once photons are lost?

It does **not** answer "which node is contaminated." That is a different
(estimation) problem and, as shown below, gets **no** quantum advantage.

---

## 2. The exact math computed (no black box)

The state is a continuous-variable **Gaussian state**, fully described by its
mean vector `d` (quadratures X, P) and covariance matrix `V`. We explicitly
build `d` and `V` for two probes:

1. **Separable** — N independent coherent states, each with n photons.
2. **Entangled** — one squeezed state whose *total* resource is scaled to N·n
   (photons) and total squeezing sinh²(r_t)=N·n, distributed through a
   symmetric N-port beam splitter (Walsh–Hadamard unitary). After the split
   each node has n photons and full per-node squeezing — the **same energy
   budget** as one separable coherent state. This is what makes the comparison
   fair (Zhuang 2018, Oh 2020 fix per-node photon number).

For the common phase we compute the **Quantum Fisher Information (QFI)** from
the standard Gaussian-state formula:

    F_Q = 4 (dd/dθ)ᵀ V⁻¹ (dd/dθ) + 2 Tr[(V⁻¹ dV/dθ)²]

where `dV/dθ` is the *full* covariance derivative `Ω_full·V + V·Ω_fullᵀ`
(block-diagonal Ω). The inter-mode correlations in that term are exactly what
produce the N² (Heisenberg) scaling — dropping them is a common bug, and we
do not.

The Quantum Cramér–Rao Bound says the best achievable variance of any unbiased
estimator is `Var(q̂) ≥ 1/F_Q`. For Gaussian states homodyne detection **saturates**
this bound, so `error = 1/sqrt(F_Q)` is the *achievable* error, not just a bound.

We also compute the QFI for a **single node's phase** (only mode j rotates) to
show the aggregate-vs-individual trade-off.

---

## 3. Verified results (from `results/sensing_experiment.json`, r = 0.5)

### Real data used

| Item | Value |
|------|-------|
| Source | USGS Water Quality Portal, 8,889 wells |
| Cluster center | LA / San Gabriel basin (34.05°N, 118.24°W) |
| N = 64 cluster arsenic range | 0.1 – 9.2 µg/L |
| N = 64 cluster mean | 1.53 µg/L |
| Wells over MCL (10 µg/L) in N=64 cluster | 0 / 64 |
| Sensitivity s | 0.01 rad/µg/L |

### Scaling (fit log(error) vs log N over N = 2…64)

| Probe | Fit exponent | Expected | Match |
|-------|-------------|----------|-------|
| Separable | **−0.5** | −0.5 (1/√N, SQL) | ✓ |
| Entangled, lossless | **−0.85** | −1.0 (1/N, Heisenberg) | ✓ (within tolerance) |

Measured estimation errors, `1/√QFI`, converted to µg/L:

| N | Separable (µg/L) | Entangled lossless (µg/L) | Entangled η=0.8 (µg/L) | Entangled η=0.6 (µg/L) |
|---|------------------|---------------------------|------------------------|------------------------|
| 2 | 23.99 | 13.12 | 18.05 | 22.93 |
| 4 | 16.96 | 8.15 | 12.75 | 17.15 |
| 8 | 11.99 | 4.73 | 8.90 | 12.73 |
| 16 | 8.48 | 2.59 | 6.20 | 9.32 |
| 32 | 6.00 | 1.36 | 4.32 | 6.74 |
| 64 | 4.24 | 0.70 | 3.03 | 4.83 |

**Reading this:** at N=64 the entangled lossless error (0.70 µg/L) is ~6×
lower than separable (4.24 µg/L). That is the Heisenberg-vs-SQL gap,
empirically, in meaningful units. The MCL line at 10 µg/L shows that the
entangled probe resolves contamination below the regulatory threshold from
N=4 onward; the separable probe only reaches it from N=16.

### MCL resolvability (can we detect contamination above/below 10 µg/L?)

| N | Separable error < 10 µg/L? | Entangled lossless < 10 µg/L? |
|---|---------------------------|-------------------------------|
| 2 | No | No |
| 4 | No | **Yes** |
| 8 | No | **Yes** |
| 16 | **Yes** | **Yes** |
| 32 | **Yes** | **Yes** |
| 64 | **Yes** | **Yes** |

### Aggregate vs individual (lossless entangled)

| N | QFI aggregate | QFI single node | ratio |
|---|---------------|-----------------|-------|
| 2 | 58.1 | 23.2 | 2.5× |
| 4 | 150.6 | 22.4 | 6.7× |
| 8 | 447.6 | 22.2 | 20× |
| 16 | 1,493.3 | 22.1 | 67× |
| 32 | 5,395.9 | 22.1 | 244× |
| 64 | 20,449.0 | 22.1 | **925×** |

The aggregate QFI grows ~N² (20,449 at N=64) while a **single node's QFI stays
flat at ~22**. Entanglement buys the *aggregate*, not the individual reading.
This is the precise B/C trade-off from the design discussion: you learn how
contaminated Area A is, not which sub-node caused it.

### Photon loss

As η drops from 1.0 → 0.8 → 0.6, the entangled error rises and bends **toward**
the SQL curve (separable). At N=64: 0.70 µg/L (η=1) → 3.03 µg/L (η=0.8) →
4.83 µg/L (η=0.6). There is no cliff — loss degrades the advantage smoothly,
consistent with the moderate-loss regime of Zhuang et al. (PRA 97, 2018).

---

## 4. What this experiment does NOT claim (the limits)

### Limits from the *coding* (what the simulation does not model)
- **No detector inefficiency.** Homodyne is assumed ideal and saturating the
  QCRB. Real detectors add noise; that would raise every curve.
- **No thermal noise / finite-temperature bath.** Loss mixes each mode with a
  zero-temperature vacuum, not a thermal state. A warm environment adds extra
  noise beyond what η alone captures.
- **No finite squeezing-generation fidelity.** The squeezed state is created
  perfectly; real squeezers have losses and imperfect modes.
- **No phase drift over time.** We assume the phase is static during one
  measurement. Real aquifers and fibers drift.
- **Ideal photonic circuit.** Beam splitters are lossless except for the η we
  add explicitly; no coupling loss, no mode-mismatch, no crosstalk.

### Limits from the *data / physics abstraction*
- **Phase ∝ contamination is assumed, not measured.** A contaminant shifts a
  refractive index, which shifts phase; the proportionality (sensitivity s) is
  a free parameter. We fix it and compare *scaling*, not absolute ppm. No real
  sensor calibration is involved.
- **The real USGS data provides the concentrations, not the physics.** The
  arsenic values (µg/L) from `data/wqp_groundwater.csv` are mapped to phases
  via `phi_i = s * c_i`. The quantum sensing simulation computes the QFI and
  estimation error for those phases; it does not model the actual chemistry of
  how a contaminant shifts a refractive index, nor any real sensor readout.
- **N is restricted to powers of two (2…64)** because the symmetric splitter
  uses a Walsh–Hadamard unitary.

### What is honestly *not* shown
- We do **not** claim a quantum speedup over classical methods for the
  placement problem (that is the separate QUBO/VQE PoC, where VQE reaches the
  exact optimum on the demo and we explicitly do not claim a simulator
  speedup). This sensing experiment is about estimation precision scaling, a
  different axis.

---

## 5. References
- Zhuang, Zhang, Shapiro — *Phys. Rev. A* **97**, 032329 (2018): distributed CV
  multipartite entanglement → Heisenberg scaling for the weighted sum of
  phases; photon loss. (Cited in `PROPOSAL.md` §3.3 and References #1.)
- Oh, Lee, Lie, Jeong — *Phys. Rev. Research* **2**, 023030 (2020): optimal
  Gaussian distributed sensing; the symmetric squeezed state is optimal for
  the average.
