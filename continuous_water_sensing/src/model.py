"""Continuous-variable Gaussian homodyne model. All concentration units: mg/kg NaCl.
Vacuum quadrature variance = 1. No Gaussian-QFI shortcut is used.
"""
from __future__ import annotations
import numpy as np
from scipy.constants import h, c

def index_nacl(concentration, p):
    return np.polyval(p['nacl_index_polynomial'], np.asarray(concentration)/1e6)

def index_slope(p):
    return np.polyval(np.polyder(p['nacl_index_polynomial']), p['baseline_nacl_mg_kg']/1e6)/1e6

def phase_slope(p):
    return 2*np.pi*p['effective_interaction_length_m']/p['wavelength_m']*index_slope(p)

def sq_variance(ns):
    # Stable form of (sqrt(ns+1)-sqrt(ns))**2.
    return 1/(np.sqrt(np.asarray(ns)+1)+np.sqrt(ns))**2

def squeezing_budget(m, p, capped=True):
    cap=np.sinh(p['squeezing_cap_db']*np.log(10)/20)**2
    return min(m*p['squeezing_photons_per_node_mode'],cap) if capped else m*p['squeezing_photons_per_node_mode']

def jitter_variance(ns, rms):
    v=sq_variance(ns)
    e=np.exp(-2*rms*rms)
    return (v*(1+e)+1/v*(1-e))/2

def efficiency(m, distances_km, p):
    # Local detection: one-way quantum fiber distribution, no fabricated round trip.
    d=np.broadcast_to(np.asarray(distances_km), (m,))
    stages=int(np.ceil(np.log2(m)))
    db=p['fiber_loss_db_km']*d+p['splitter_excess_db_per_stage']*stages
    return p['detector_efficiency']*p['sample_transmission']*p['coupling_transmission']*10**(-db/10)

def photon_flux(p):
    return p['power_per_node_w']/(h*c/p['wavelength_m'])

def covariance(m, eta, p, strategy='entangled', seconds=1., capped=True, jitter=True):
    """Covariance of calibrated local estimates for arbitrary local signals.
    Carrier plus squeezed photons have equal total launched energy in all strategies.
    Bright local oscillators and pump electrical power excluded, same readout convention.
    """
    eta=np.broadcast_to(np.asarray(eta,dtype=float),(m,))
    if np.any(eta<=0) or np.any(eta>1) or seconds<=0:
        raise ValueError('eta must be in (0,1], seconds positive')
    f=photon_flux(p); ns=squeezing_budget(m,p,capped)
    if strategy in ('coherent','coherent_optimized'):
        ns=0.
    fc=f-p['squeezing_mode_rate_hz']*ns/m
    if fc<=0: raise ValueError('Squeezing exceeds launched photon budget')
    k=phase_slope(p)
    if strategy=='coherent_optimized':
        # Unconstrained total-power optimum for equal weights; exceeds per-node cap.
        fi=(m*f)*(1/np.sqrt(eta))/np.sum(1/np.sqrt(eta))
        return np.diag(1/(4*seconds*fi*k*k*eta))
    v=jitter_variance(ns,p['phase_lock_rms_rad'] if jitter else 0.)
    if strategy=='entangled':
        mat=np.diag(1/eta)+(v-1)*np.ones((m,m))/m
    elif strategy=='separable':
        vs=jitter_variance(ns/m,p['phase_lock_rms_rad'] if jitter else 0.)
        mat=np.diag(1/eta-1+vs)
    elif strategy=='coherent': mat=np.diag(1/eta)
    else: raise ValueError(strategy)
    return mat/(4*seconds*fc*k*k)

def quadrature_covariance(m, eta, ns):
    """Physical 2M covariance, [X_1..X_M,P_1..P_M], [X,P]=2i."""
    eta=np.broadcast_to(eta,(m,)); u=np.sqrt(eta/m); v=sq_variance(ns)
    vx=np.eye(m)+(v-1)*np.outer(u,u)
    vp=np.eye(m)+(1/v-1)*np.outer(u,u)
    z=np.zeros((m,m))
    return np.block([[vx,z],[z,vp]])

def mean_variance(cov, weights=None):
    w=np.ones(len(cov))/len(cov) if weights is None else np.asarray(weights)
    return float(w@cov@w)

def ou_average_factor(seconds, tau):
    # Variance of continuous-time rectangular average of stationary OU process.
    x=np.asarray(seconds,dtype=float)/tau
    return 2*(x+np.expm1(-x))/(x*x)

def noise_budget(m, eta, p, strategy='entangled', seconds=1., temperature=None):
    optical=mean_variance(covariance(m,eta,p,strategy,seconds))
    t=p['controlled_temperature_rms_K'] if temperature is None else temperature
    thermal=(abs(p['dn_dT_RIU_K'])/index_slope(p)*t)**2*ou_average_factor(seconds,p['common_temperature_correlation_s'])
    independent=p['independent_calibration_rms_mg_kg']**2/m
    return {'optical':optical,'temperature':float(thermal),'calibration':independent,'total':optical+thermal+independent}
