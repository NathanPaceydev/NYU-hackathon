# Model and resource accounting

## Task and scope

Estimate changes in the arithmetic mean q = sum(c_i)/M across the installed sampling taps. c_i is dissolved NaCl concentration change in mg/kg around 500 mg/kg. All local changes may differ; there is no assumption that every sensor sees an identical unknown phase. A pure-water/salt refractive-index calibration does not identify arsenic, nitrate, microbes or other pollutants. An alarm is a change-screening signal needing chemical follow-up, not a declaration of safe drinking water.

The implementation is continuous-variable Gaussian optics and a continuously sampled time-domain example. It contains no discrete qubit simulation, fabricated QFI calculation or imposed error=1/M rule.

## Chemical-to-optical model

Empirical S7 polynomial n(W), W=c/1e6, gives local derivative k_n=1.6207394e-7 RIU/(mg/kg) at c0=500 mg/kg. Phase slope k=(2 pi L_eff/lambda) k_n=6.5699393e-6 rad/(mg/kg), with proposed L_eff=10 µm and lambda=1550 nm. This effective length is a design assumption; all concentration errors scale inversely with it. For the synthetic sub-mg/kg perturbations, the polynomial's nonlinearity is negligible relative to the modeled noise. We assume a reference calibration removes static phase and the sensor is locked near its linear operating point. At other backgrounds or large signals use the full polynomial and nonlinear readout.

## Optical Gaussian state and measurement

Quadratures satisfy [X,P]=2i and vacuum covariance I. Splitting one squeezed mode evenly among M paths gives u=(1,...,1)/sqrt(M), Vx=I+(v-1)uuᵀ and Vp=I+(1/v-1)uuᵀ, v=exp(-2r)=(sqrt(Ns+1)+sqrt(Ns))^-2, Ns=sinh²(r). Attenuation D=diag(sqrt(eta_i)) adds vacuum: Vout=D Vin D+I-D² separately on X/P. The unused splitter ports are vacuum, not an additional 1/M photon-erasure loss. Bright carrier power per node is explicitly budgeted after the split.

Small phase signals produce readout mean x_i=2 sqrt(eta_i F_c T) k c_i. Calibrating each local homodyne readout back to concentration gives

Σ_ent = [diag(1/eta_i)+(v_eff-1)uuᵀ] / (4 F_c T k²).

A global zero-mean Gaussian squeeze-angle jitter with RMS s contributes v_eff = v(1+e^-2s²)/2 + v^-1(1-e^-2s²)/2. This is a covariance/moment approximation to phase jitter; actual random rotations need not yield exactly Gaussian tails. The detection ROC adopts the Gaussian approximation explicitly. For independent squeezers substitute diag(1/eta_i-1+v_eff(Ns/M)). For coherent light use diag(1/eta_i)/(4 F T k²).

The actual estimator qhat=wᵀy, w_i=1/M, is unbiased for arbitrary local c_i, with variance wᵀΣw. We compute this achievable homodyne-estimator variance directly, not a pure-state QFI formula used outside its domain. For this linear Gaussian location model with independent local parameters as nuisance parameters, it is also the estimator covariance implied by the classical Fisher information. This does not prove optimality among all quantum strategies or nonlinear phase measurements.

The unequal-loss calibration penalizes distant nodes. We do not discard noisy nodes or change their weights, which would change the target mean. We also include an optimistic coherent comparator with the same total launched photon budget redistributed as F_i proportional to 1/sqrt(eta_i); this relaxes the individual-node power cap and is a stronger classical comparison.

## Fair resources and scalings

M is sensor count; Ns is TOTAL squeezed photon number per effective temporal mode; T is integration time. They are never used interchangeably. F=P/(hc/lambda)=7.8029e10 photons/s per node at 10 nW. With mode rate B=1 MHz, quantum squeezed flux is B Ns TOTAL, and carrier flux per node is F_c=F-B Ns/M. Thus total launched carrier plus squeezed light remains M F for every strategy. At M=16, Ns=1.6 and 9.18 dB source squeezing; its 1.6e6 photons/s is deducted from the total, small compared with bright carriers. Independent squeezers share exactly the same total Ns. Source pump energy, locking infrastructure and strong local oscillator power are not included in probe-photon accounting. No economic or wall-plug energy advantage is claimed.

For equal eta and no jitter, Var(qhat)=[1/eta-1+v]/(4 M F_c T k²). If Ns=M n_s grows without cap and eta=1, v approximately 1/(4 M n_s), giving RMS approximately M^-1. Independent squeezers with fixed Ns/M have M^-1/2 behavior. This is the finite-resource asymptote of the explicit covariance, not a hardcoded line. With any fixed eta<1, the 1/eta-1 term dominates at large M, returning optical RMS to M^-1/2. With a fixed source squeezing cap, that exponent returns even without loss. Regional geometry can make eta itself decrease with M. A fixed total carrier AND squeezing budget removes the claim that simply adding sensors guarantees precision growth. Figure 05 demonstrates both budget schedules.

The ideal panel exceeds the implemented 10 dB source cap beyond 20 nodes; it is explicitly a theoretical reference. Fits use M=33..64; there is no assertion that 64-node hardware has been demonstrated. The smallest demonstrated CV network among the cited experimental anchors has four nodes (S6).

## Physical deployment model

Pilot: 16 proposed sampling taps on a plant-scale network with 100 m quantum links, extrapolated from M=1..64 for design studies. Regional: nearest M of 64 distinct supplied locations, one-way length=1.3×great-circle distance from assumed LA hub, local readout and classical communications. Transmission eta_i=0.95×0.90×0.90×10^[-(0.18 L_i+0.05 ceil(log2 M))/10]. Fiber term is sourced; the other factors are component targets.

Adding the 65th sensor is not simulated because no 65th candidate was selected. M is integer and is not restricted to powers of two; stage count is an engineering approximation to a balanced distribution tree. Spatial weights are equal only for the selected taps, not a population/exposure/flow-weighted regional mean. As M changes in the regional sweep, the sampled population changes. Those curves compare precision at each deployment, not the accuracy of estimating one fixed 64-site regional mean with fewer sites. Sampling coverage and missed unsampled hotspots cannot be repaired by squeezing.

## Technical error and continuous operation

Total MSE = optical variance + independent session-calibration variance/M + thermal variance. The common temperature residual maps to concentration through (dn/dT)/(dn/dc). A stationary Ornstein–Uhlenbeck process with correlation tau=60 s has rectangular-average variance multiplier f(T)=2[x+exp(-x)-1]/x², x=T/tau. It does not behave like white noise over short windows. Calibration offsets persist in time. Temperature and calibration parameters are assumed zero-mean ensembles; a fixed unknown common bias would remain bias and is outside this formula.

Figure 07 has 16 unequal synthetic arrivals (90–135 s), amplitudes with ±25% variation, a 25 s rise and a first-order 10 s sensor response. Exact exponential recursion at 1 s step models sample lag. A single shared OU realization and the same calibration realization are applied to both strategies, with independent Gaussian optical draws. No fitted field transport model is implied. The scalar precision calculations and ROC target the settled or window-averaged sampled concentration; the trace includes lag relative to instantaneous truth. For fast transients, lag bias must be added to the optical-plus-technical RMSE; the stationary RMSE is not the total transient tracking error. This is why true and filtered signals are shown separately.

Low-frequency optical readout requires modulation/demodulation into a squeezed sideband (S1/S8). The simulator assumes this works with losses included in the component budget. Slow fiber path drift, fouling, cross-sensitivity, ADC/electronic noise, excess laser noise, outages, resource multiplexing and non-Gaussian tails need measured budgets before deployment. Common temperature drift serves as a technical-noise stress test, not an exhaustive field-error model.

## Detection and statistical validation

For a one-sided single-window change test H0:q=0 versus H1:q=delta, threshold z_(1-alpha) sigma and Pdetect=1-Phi(z_(1-alpha)-delta/sigma). Default delta=0.15 mg/kg and alpha=0.01 are illustrative. Gaussian null and alternative simulations use 100,000 independent trials each. These are repeated hypothetical decisions/experiments, not 100,000 independent seconds from the OU trace.

At 1 Hz, 1% per-window false alarm means 36 expected flagged windows per hour under a calibrated null, even with correlated windows. That is not an operational alarm rate. A conservative policy bounding the probability of ANY false alarm in an hour by 5% could use alpha=0.05/3600 via the union bound, or a separately validated sequential detector. Temporal correlations and drift must be retained in an operational test. No regulatory threshold is inferred from an RMSE or LOD.

Validation checks physical Gaussian uncertainty, full-state to readout-covariance agreement, the closed-form equal-loss result, vacuum and high-loss limits, one-node equivalence, arbitrary local signals, unequal-loss classical power allocation, polynomial derivative units, OU limits, ROC Monte Carlo sampling error, unique coordinates, and unchanged draft hashes. Parameter uncertainty is not sampling uncertainty: sweeping power and thermal control exposes assumptions, but does not provide a certified uncertainty interval for a real sensor.

## Implementation and evidence boundary

The equations above run as classical Python array operations in [model.py](../src/model.py), with scenario construction in [run.py](../src/run.py). No quantum hardware, Qiskit circuit, learned model or machine-learning training is involved. The optical hardware is a proposed future realization of the modeled state and readout. See [SIMULATION.md](SIMULATION.md) for the exact stack, inputs, outputs and reproduction flow, and [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) for all parameter justifications.

The split-state mechanism and loss-aware Gaussian sensing are grounded in [S4](https://arxiv.org/abs/1711.10459) and [S5](https://doi.org/10.1103/PhysRevResearch.2.023030). The chemical slope uses [S7](https://doi.org/10.1364/AO.55.000947), and thermal cross-sensitivity uses [S10](https://opg.optica.org/abstract.cfm?uri=sensors-2012-STu1F.3). The OU process, calibration distribution, response dynamics and detection operating point are project assumptions. Their analytic formulas follow from those assumptions, rather than measurements in those papers.
