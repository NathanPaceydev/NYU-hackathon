from __future__ import annotations
import argparse, json, sys, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import *
ROOT=Path(__file__).resolve().parents[1]
COL={'coherent':'#38bdf8','coherent_optimized':'#94a3b8','separable':'#fbbf24','entangled':'#2dd4bf','ideal':'#c084fc','field':'#f87171'}
LABEL={'coherent':'Coherent','coherent_optimized':'Coherent: optimized power','separable':'Independent squeezed','entangled':'Distributed squeezed'}
plt.rcParams.update({'figure.facecolor':'#0b1520','axes.facecolor':'#0b1520','savefig.facecolor':'#0b1520','text.color':'#e8edf2','axes.labelcolor':'#e8edf2','xtick.color':'#b5c4d2','ytick.color':'#b5c4d2','axes.edgecolor':'#456070','grid.color':'#294253','font.size':11,'axes.titleweight':'bold','axes.titlesize':14,'legend.frameon':False,'lines.linewidth':2.4,'svg.fonttype':'none'})

def save(fig, name):
    fig.savefig(ROOT/'figures'/f'{name}.png',dpi=190,bbox_inches='tight')
    fig.savefig(ROOT/'figures'/f'{name}.svg',bbox_inches='tight')
    plt.close(fig)

def grid(ax): ax.grid(True,alpha=.4)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',default=str(ROOT/'config/default.json'));args=ap.parse_args()
    p=json.loads(Path(args.config).read_text());rng=np.random.default_rng(p['seed'])
    for d in ['results','figures']: (ROOT/d).mkdir(exist_ok=True)
    sites=pd.read_csv(ROOT/'data/site_geometry.csv'); nmax=min(p['maximum_nodes'],len(sites)); ms=np.arange(1,nmax+1)
    records=[]
    for m in ms:
        for geometry in ['pilot','regional']:
            dist=p['pilot_fiber_length_km'] if geometry=='pilot' else sites.distance_km.to_numpy()[:m]*p['route_stretch']
            eta=efficiency(m,dist,p)
            for strat in ['coherent','coherent_optimized','separable','entangled']:
                b=noise_budget(m,eta,p,strat);bf=noise_budget(m,eta,p,strat,temperature=p['field_temperature_rms_K'])
                records.append(dict(nodes=int(m),geometry=geometry,strategy=strat,eta_min=eta.min(),eta_mean=eta.mean(),eta_max=eta.max(),squeezing_photons_total=(0. if strat.startswith('coherent') else squeezing_budget(m,p)),squeezing_db=(0. if strat.startswith('coherent') else -10*np.log10(sq_variance(squeezing_budget(m,p)/(m if strat=='separable' else 1)))),optical_rmse=np.sqrt(b['optical']),controlled_rmse=np.sqrt(b['total']),field_rmse=np.sqrt(bf['total']),mean_route_km=np.mean(np.broadcast_to(dist,(m,)))))
    scaling=pd.DataFrame(records);scaling.to_csv(ROOT/'results/scaling.csv',index=False)
    # 1. Resource-explicit ideal displacement limit versus achievable noise.
    fig,axs=plt.subplots(1,2,figsize=(12.3,4.3),layout='constrained')
    ideal=[]
    for strategy in ['coherent','separable','entangled']:
        vals=np.array([np.sqrt(mean_variance(covariance(int(m),1.,p,strategy,capped=False,jitter=False))) for m in ms]);ideal.append(vals)
        axs[0].loglog(ms,vals,label=LABEL[strategy],color=COL[strategy])
    axs[0].set(title='Ideal scaling: squeezing grows with node count',xlabel='Number of sensors M',ylabel='Optical RMSE (mg/kg NaCl change)')
    axs[0].legend(fontsize=9);grid(axs[0])
    for strategy in ['coherent','separable','entangled']:
        s=scaling[(scaling.geometry=='pilot')&(scaling.strategy==strategy)]
        axs[1].loglog(s.nodes,s.optical_rmse,color=COL[strategy],ls='--',alpha=.7)
        axs[1].loglog(s.nodes,s.controlled_rmse,color=COL[strategy],label=LABEL[strategy])
    axs[1].set(title='100 m pilot: loss, 10 dB cap and drift',xlabel='Number of sensors M',ylabel='RMSE (mg/kg NaCl change)')
    axs[1].text(.04,.04,'Solid: total error   Dashed: optical only\n1 s integration; 0.05 mK common residual',transform=axs[1].transAxes,fontsize=9)
    grid(axs[1]);axs[1].legend(fontsize=9);save(fig,'01_scaling')
    # 2. Geometry from unique coordinates, not fabricated node growth.
    fig,axs=plt.subplots(1,2,figsize=(12.3,4.3),layout='constrained')
    x=(sites.lon-p['hub_lon'])*111.2*np.cos(np.deg2rad(p['hub_lat']));y=(sites.lat-p['hub_lat'])*111.2
    for xx,yy in zip(x,y): axs[0].plot([0,xx],[0,yy],color='#294253',lw=.7)
    sc=axs[0].scatter(x,y,c=np.arange(1,65),cmap='viridis',s=30);axs[0].scatter([0],[0],marker='*',color=COL['separable'],s=150,label='Assumed hub')
    axs[0].set(xlabel='East of hub (km)',ylabel='North of hub (km)',title='64 distinct locations from supplied well file',aspect='equal');axs[0].legend(fontsize=9);fig.colorbar(sc,ax=axs[0],label='Order by distance')
    reg=scaling[(scaling.geometry=='regional')&(scaling.strategy=='entangled')]
    axs[1].plot(reg.nodes,reg.eta_mean,color=COL['entangled'],label='Mean transmission');axs[1].fill_between(reg.nodes,reg.eta_min,reg.eta_max,color=COL['entangled'],alpha=.2,label='Node range')
    axs[1].set(xlabel='Sensors, nearest first',ylabel='End-to-end transmission',title='Longer routes consume quantum advantage',ylim=(0,1));axs[1].legend();grid(axs[1]);save(fig,'02_network_geometry')
    # 3. Real geography comparison / field failure.
    fig,axs=plt.subplots(1,2,figsize=(12.3,4.3),layout='constrained')
    for strategy in ['coherent','coherent_optimized','separable','entangled']:
        s=scaling[(scaling.geometry=='regional')&(scaling.strategy==strategy)]
        axs[0].loglog(s.nodes,s.optical_rmse,color=COL[strategy],label=LABEL[strategy])
    axs[0].set(title='Regional routes: optical precision',xlabel='Number of sensors M',ylabel='1 s optical RMSE (mg/kg)');axs[0].legend(fontsize=9);grid(axs[0])
    for temp,ls,label in [(p['controlled_temperature_rms_K'],'-','0.05 mK residual'),(p['field_temperature_rms_K'],'--','10 mK residual')]:
        for strat in ['coherent','entangled']:
            v=[np.sqrt(noise_budget(int(m),efficiency(int(m),sites.distance_km.to_numpy()[:m]*p['route_stretch'],p),p,strat,temperature=temp)['total']) for m in ms]
            axs[1].loglog(ms,v,ls=ls,color=COL[strat],label=LABEL[strat]+': '+label)
    axs[1].set(title='Shared temperature error does not average away',xlabel='Number of sensors M',ylabel='1 s total RMSE (mg/kg)');axs[1].legend(fontsize=8);grid(axs[1]);save(fig,'03_regional_limits')
    # 4. Time averaging with correlated drift, exact OU integral.
    m=p['pilot_nodes'];eta=efficiency(m,p['pilot_fiber_length_km'],p);ts=np.geomspace(.1,3600,180);timerecs=[]
    fig,axs=plt.subplots(1,2,figsize=(12.3,4.3),layout='constrained')
    for strat in ['coherent','separable','entangled']:
        vals=[]
        for t in ts:
            b=noise_budget(m,eta,p,strat,t);vals.append(np.sqrt(b['total']));timerecs.append(dict(seconds=t,strategy=strat,**b))
        axs[0].loglog(ts,vals,label=LABEL[strat],color=COL[strat])
    axs[0].set(title='16-node pilot: averaging encounters slow drift',xlabel='Integration time (s)',ylabel='RMSE (mg/kg)');axs[0].legend();grid(axs[0])
    tempgrid=np.geomspace(.01,10,130)
    gains=[]
    for temp in tempgrid:
        a=noise_budget(m,eta,p,'coherent',temperature=temp/1000)['total'];b=noise_budget(m,eta,p,'entangled',temperature=temp/1000)['total'];gains.append(np.sqrt(a/b))
    axs[1].semilogx(tempgrid,gains,color=COL['entangled']);axs[1].axvline(.05,color='#94a3b8',ls='--');axs[1].set(title='Temperature compensation sets the useful gain',xlabel='Common temperature residual RMS (mK)',ylabel='Classical / quantum total RMSE',ylim=(.99,max(gains)*1.07));grid(axs[1]);save(fig,'04_averaging_temperature');pd.DataFrame(timerecs).to_csv(ROOT/'results/averaging.csv',index=False)
    # 5. Fixed total photon resource versus per-node budget.
    fig,axs=plt.subplots(1,2,figsize=(12.3,4.3),layout='constrained');resource=[]
    for strat in ['coherent','entangled']:
        for fixed,ls in [(False,'-'),(True,'--')]:
            vals=[]
            for mm in ms:
                q=dict(p);q['power_per_node_w']=p['power_per_node_w']*(m/mm if fixed else 1)
                # Same total squeezing resource fixed too: capped 16-node resource.
                if fixed:q['squeezing_photons_per_node_mode']=squeezing_budget(m,p)/mm
                v=np.sqrt(mean_variance(covariance(int(mm),efficiency(int(mm),p['pilot_fiber_length_km'],p),q,strat)));vals.append(v)
                resource.append(dict(nodes=int(mm),strategy=strat,fixed_total=fixed,optical_rmse=v,total_power_nw=mm*q['power_per_node_w']*1e9))
            axs[0].loglog(ms,vals,ls=ls,color=COL[strat],label=LABEL[strat]+(' / fixed total' if fixed else ' / 10 nW per node'))
    axs[0].set(title='Adding sensors also adds optical resources',xlabel='Number of sensors M',ylabel='Optical RMSE (mg/kg)');axs[0].legend(fontsize=8);grid(axs[0])
    req=-10*np.log10(sq_variance(ms*p['squeezing_photons_per_node_mode']));axs[1].plot(ms,req,color=COL['ideal'],label='Uncapped source requirement');axs[1].plot(ms,np.minimum(req,p['squeezing_cap_db']),color=COL['entangled'],label='Implemented source cap');axs[1].axhline(12.3,color=COL['separable'],ls=':',label='12.3 dB observed at 1550 nm / 5 MHz')
    axs[1].set(title='Heisenberg-like scaling spends more squeezing',xlabel='Number of sensors M',ylabel='Source squeezing (dB)');axs[1].legend(fontsize=9);grid(axs[1]);save(fig,'05_resource_accounting');pd.DataFrame(resource).to_csv(ROOT/'results/resources.csv',index=False)
    # 6. Detection ROC: explicitly per decision, matched local signals.
    fpr=np.geomspace(1e-4,.5,250);delta=p['test_event_delta_mg_kg'];alpha=p['false_alarm_probability_per_decision'];detection=[]
    fig,axs=plt.subplots(1,2,figsize=(12.3,4.3),layout='constrained')
    for strat in ['coherent','separable','entangled']:
        sigma=np.sqrt(noise_budget(m,eta,p,strat)['total']);tpr=norm.sf(norm.isf(fpr)-delta/sigma)
        axs[0].semilogx(fpr,tpr,color=COL[strat],label=LABEL[strat]);pdv=norm.sf(norm.isf(alpha)-delta/sigma)
        null=rng.normal(0,sigma,p['monte_carlo_trials']);alt=rng.normal(delta,sigma,p['monte_carlo_trials']);cut=norm.isf(alpha)*sigma
        detection.append(dict(strategy=strat,rmse=sigma,threshold=cut,p_false_alarm=alpha,p_detect=pdv,mc_false_alarm=float((null>cut).mean()),mc_detection=float((alt>cut).mean()),mc_trials=p['monte_carlo_trials']))
    axs[0].axvline(alpha,color='#94a3b8',ls=':');axs[0].set(title=f'{delta:g} mg/kg regional change, 1 s decisions',xlabel='False-alarm probability per decision',ylabel='Detection probability',ylim=(0,1));axs[0].legend();grid(axs[0])
    cov=covariance(m,eta,p,'entangled');corr=cov/np.sqrt(np.outer(np.diag(cov),np.diag(cov)))
    im=axs[1].imshow(corr,vmin=-.15,vmax=.15,cmap='RdBu_r');fig.colorbar(im,ax=axs[1],label='Readout correlation (diagonal clipped)');axs[1].set(title='Negative correlations suppress the average',xlabel='Sensor',ylabel='Sensor');save(fig,'06_detection_correlations');pd.DataFrame(detection).to_csv(ROOT/'results/detection.csv',index=False)
    # 7. Continuous trace: different local signals; sum estimator, no all-equal assumption.
    t=np.arange(0,360,dtype=float);arrivals=90+np.linspace(0,45,m);amp=.35*(1+.25*np.sin(np.arange(m)));truth_nodes=np.maximum(0,1-np.exp(-(t[:,None]-arrivals)/25))*amp;truth=truth_nodes.mean(axis=1)
    sensed=np.zeros_like(truth_nodes)
    for j in range(1,len(t)):sensed[j]=sensed[j-1]+(1-np.exp(-1/p['sensor_response_tau_s']))*(truth_nodes[j]-sensed[j-1])
    sensed_mean=sensed.mean(axis=1);rho=np.exp(-1/p['common_temperature_correlation_s']);common=np.zeros(len(t));common[0]=rng.normal();
    for j in range(1,len(t)):common[j]=rho*common[j-1]+np.sqrt(1-rho*rho)*rng.normal()
    common*=abs(p['dn_dT_RIU_K'])/index_slope(p)*p['controlled_temperature_rms_K']
    bias=rng.normal(0,p['independent_calibration_rms_mg_kg'],m);trace={'seconds':t,'true_aggregate':truth,'filtered_aggregate':sensed_mean,'common_temperature_error':common}
    fig,axs=plt.subplots(1,2,figsize=(12.3,4.3),layout='constrained')
    for strat in ['coherent','entangled']:
        mat=covariance(m,eta,p,strat);z=rng.multivariate_normal(np.zeros(m),mat,len(t));read=(sensed+z+bias).mean(axis=1)+common;trace[strat]=read
        axs[0].plot(t,read,color=COL[strat],alpha=.55,lw=.9,label=LABEL[strat])
    axs[0].plot(t,truth,color='white',lw=2,label='True aggregate');axs[0].plot(t,sensed_mean,color=COL['separable'],ls='--',label='10 s sensor response');axs[0].set(title='Continuous monitoring of a synthetic salt pulse',xlabel='Time (s)',ylabel='NaCl change (mg/kg)');axs[0].legend(fontsize=8);grid(axs[0])
    for strat in ['coherent','separable','entangled']:
        mat=covariance(m,eta,p,strat);w=np.ones(m)/m;v=np.zeros(m);v[:2]=[1/np.sqrt(2),-1/np.sqrt(2)]
        vals=[np.sqrt(w@mat@w),np.sqrt(mat[0,0]),np.sqrt(v@mat@v)];ix=np.arange(3)+(['coherent','separable','entangled'].index(strat)-1)*.24;axs[1].bar(ix,vals,width=.23,color=COL[strat],label=LABEL[strat])
    axs[1].set_xticks(range(3),['Regional mean','One location','Local contrast']);axs[1].set(title='An aggregate gain does not locate the source',ylabel='Optical RMSE (mg/kg)');axs[1].legend(fontsize=8);grid(axs[1]);save(fig,'07_continuous_monitoring');pd.DataFrame(trace).to_csv(ROOT/'results/time_trace.csv',index=False)
    # 8. Feasibility map on optical efficiency and drift at the pilot size.
    efficiencies=np.linspace(.05,.99,100);temps=np.geomspace(.005,10,120);gain=np.empty((len(temps),len(efficiencies)))
    for i,tt in enumerate(temps):
        for j,ee in enumerate(efficiencies):gain[i,j]=np.sqrt(noise_budget(m,ee,p,'coherent',temperature=tt/1e3)['total']/noise_budget(m,ee,p,'entangled',temperature=tt/1e3)['total'])
    fig,ax=plt.subplots(figsize=(10.7,4.8),layout='constrained');im=ax.pcolormesh(efficiencies,temps,gain,shading='auto',cmap='viridis',vmin=1,vmax=2.5);ax.set_yscale('log');cs=ax.contour(efficiencies,temps,gain,levels=[1.05,1.2,1.5,2],colors='white',linewidths=.8);ax.clabel(cs,fmt='%.2fx',fontsize=9);ax.scatter([eta.mean()],[.05],marker='*',color='#fbbf24',s=200,label='Controlled pilot scenario');ax.set(xlabel='End-to-end optical transmission',ylabel='Common temperature residual RMS (mK)',title='Useful quantum gain requires low loss and tight thermal control');ax.legend(loc='upper left');fig.colorbar(im,ax=ax,label='Classical / quantum total RMSE');save(fig,'08_feasibility_map');np.savez_compressed(ROOT/'results/feasibility.npz',efficiencies=efficiencies,temperature_mK=temps,gain=gain)
    # 9. Literature benchmark: reported sensitivities, never transferred to field DC.
    fig,axs=plt.subplots(1,2,figsize=(12.3,4.3),layout='constrained');sens=[8.6,6.8,5.5];axs[0].bar(['Matched classical','Best classical*','Twin beams'],sens,color=[COL['coherent'],COL['separable'],COL['entangled']]);axs[0].set(ylabel='Reported sensitivity (10⁻¹⁰ RIU/√Hz)',title='Dowran et al. (2018): measured optical benchmark');axs[0].text(.03,.95,'795 nm; air; 199 kHz ultrasound\n*Single-beam baseline estimated in paper',transform=axs[0].transAxes,va='top',fontsize=10);axs[0].set_ylim(0,11.5);grid(axs[0])
    axs[1].axis('off');axs[1].text(0,.96,'Commercial field reference: YSI EXO',weight='bold',fontsize=16,va='top');axs[1].text(0,.80,'Salinity accuracy:\n±1% of reading or 0.1 ppt, whichever is greater\n\nTemperature accuracy: ±0.01 °C (-5 to 35 °C)\n\nThese are accuracy specifications, not Gaussian\nstandard deviations or shot-noise floors.\n\nOur optical simulation estimates changes in NaCl;\nit is not a measured replacement for an EXO sonde.',fontsize=12,va='top',linespacing=1.6);save(fig,'09_measured_benchmarks')
    # 10. Power sensitivity: no suggestion that quantum always beats more classical light.
    powers=np.geomspace(1e-9,70e-6,140);powerrows=[]
    fig,ax=plt.subplots(figsize=(10.7,4.8),layout='constrained')
    for strat in ['coherent','separable','entangled']:
        vals=[]
        for power in powers:
            pp=dict(p,power_per_node_w=float(power));bb=noise_budget(m,eta,pp,strat);vv=np.sqrt(bb['total']);vals.append(vv);powerrows.append(dict(power_W=power,strategy=strat,total_rmse=vv))
        ax.loglog(powers*1e9,vals,color=COL[strat],label=LABEL[strat])
    ax.axvline(p['power_per_node_w']*1e9,color='#94a3b8',ls='--',label='Default 10 nW/node (assumption)')
    ax.set(title='More classical light also helps until technical noise dominates',xlabel='Launched optical power per node (nW)',ylabel='Total 1 s RMSE (mg/kg NaCl change)');ax.legend();grid(ax);save(fig,'10_power_sensitivity');pd.DataFrame(powerrows).to_csv(ROOT/'results/power_sensitivity.csv',index=False)
    slopes={s:float(np.polyfit(np.log(ms[-32:]),np.log(v[-32:]),1)[0]) for s,v in zip(['coherent','separable','entangled'],ideal)}
    def row(g,s,mm):return scaling[(scaling.geometry==g)&(scaling.strategy==s)&(scaling.nodes==mm)].iloc[0].to_dict()
    summary={'seed':p['seed'],'units':'mg/kg differential NaCl-equivalent, not pollutant-specific','phase_slope_rad_per_mg_kg':phase_slope(p),'dn_dc_RIU_per_mg_kg':index_slope(p),'photon_flux_per_node_s':photon_flux(p),'ideal_slopes_M33_64':slopes,'pilot16':{s:row('pilot',s,16) for s in ['coherent','separable','entangled']},'regional64':{s:row('regional',s,64) for s in ['coherent','coherent_optimized','separable','entangled']},'detection':detection,'site_min_km':float(sites.distance_km.min()),'site_max_km':float(sites.distance_km.max()),'source_cap_photons':float(np.sinh(p['squeezing_cap_db']*np.log(10)/20)**2),'measured_dowran_gain_vs_optimal_classical':6.8/5.5,'config_sha256':hashlib.sha256(Path(args.config).read_bytes()).hexdigest()}
    (ROOT/'results/summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
