"""Independent physics, estimator, unit and Monte Carlo checks; exits nonzero on failure."""
import json, hashlib, unittest
from pathlib import Path
import numpy as np
from scipy.linalg import block_diag
from model import *
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'config/default.json').read_text())
class Physics(unittest.TestCase):
 def test_vacuum_and_zero_squeezing(self):
  self.assertEqual(float(sq_variance(0)),1.)
  p=dict(P,squeezing_photons_per_node_mode=0.)
  for m in [1,3,16]: np.testing.assert_allclose(covariance(m,.7,p,'entangled'),covariance(m,.7,p,'coherent'))
 def test_one_mode_equals_separable(self):
  np.testing.assert_allclose(covariance(1,.63,P,'entangled'),covariance(1,.63,P,'separable'))
 def test_gaussian_uncertainty(self):
  for m in [1,3,16]:
   v=quadrature_covariance(m,np.linspace(.2,.9,m),squeezing_budget(m,P));i=np.eye(m);z=np.zeros((m,m));omega=np.block([[z,i],[-i,z]])
   self.assertGreater(np.linalg.eigvalsh(v+1j*omega).min(),-1e-10)
 def test_homodyne_covariance_from_full_state(self):
  m=7;eta=np.linspace(.3,.9,m);p=dict(P,phase_lock_rms_rad=0.);ns=squeezing_budget(m,p);v=quadrature_covariance(m,eta,ns);fc=photon_flux(p)-p['squeezing_mode_rate_hz']*ns/m
  d=np.diag(1/(2*np.sqrt(eta*fc)*phase_slope(p)))
  np.testing.assert_allclose(d@v[:m,:m]@d,covariance(m,eta,p))
 def test_equal_loss_analytic(self):
  m=12;eta=.7;ns=squeezing_budget(m,P);fc=photon_flux(P)-P['squeezing_mode_rate_hz']*ns/m
  expected=(1/eta-1+jitter_variance(ns,P['phase_lock_rms_rad']))/(4*fc*phase_slope(P)**2*m)
  self.assertAlmostEqual(mean_variance(covariance(m,eta,P)),expected,places=13)
 def test_high_loss_erases_optical_gain(self):
  a=mean_variance(covariance(16,1e-5,P,'coherent'));b=mean_variance(covariance(16,1e-5,P,'entangled'))
  self.assertAlmostEqual(a/b,1.,delta=.0001)
 def test_actual_classical_power_optimum(self):
  eta=np.linspace(.1,.9,16)
  self.assertLess(mean_variance(covariance(16,eta,P,'coherent_optimized')),mean_variance(covariance(16,eta,P,'coherent')))
 def test_index_derivative_units(self):
  d=(index_nacl(P['baseline_nacl_mg_kg']+.1,P)-index_nacl(P['baseline_nacl_mg_kg']-.1,P))/.2
  self.assertAlmostEqual(d/index_slope(P),1.,places=7)
 def test_ou_averaging_limits(self):
  self.assertAlmostEqual(float(ou_average_factor(.001,60)),1.,places=4)
  self.assertAlmostEqual(float(ou_average_factor(6e6,60)),2e-5,places=8)
 def test_monte_carlo_heterogeneous_local_parameters(self):
  rng=np.random.default_rng(1006);m=7;eta=np.linspace(.3,.9,m);cov=covariance(m,eta,P);truth=np.linspace(-.2,.5,m);draw=rng.multivariate_normal(truth,cov,100000);err=draw.mean(axis=1)-truth.mean();theory=mean_variance(cov)
  self.assertLess(abs(err.mean()),5*np.sqrt(theory/len(err)))
  self.assertLess(abs(np.mean(err**2)/theory-1),.02)
 def test_roc_monte_carlo(self):
  d=json.loads((ROOT/'results/summary.json').read_text())['detection']
  for row in d:
   for exact,mc in [('p_false_alarm','mc_false_alarm'),('p_detect','mc_detection')]:
    se=np.sqrt(row[exact]*(1-row[exact])/row['mc_trials']); self.assertLess(abs(row[exact]-row[mc]),5*se)
 def test_original_folder_unchanged(self):
  for name,digest in json.loads((ROOT/'data/draft_sha256.json').read_text()).items():
   self.assertEqual(hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest(),digest,name)
 def test_real_geometry_unique(self):
  import pandas as pd
  p=pd.read_csv(ROOT/'data/site_geometry.csv');self.assertEqual(len(p),64);self.assertEqual(len(p.drop_duplicates(['lat','lon'])),64)
if __name__=='__main__': unittest.main(verbosity=2)
