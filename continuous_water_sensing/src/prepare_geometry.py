"""Reproduce geometry selection; read-only access to the supplied draft."""
from pathlib import Path
import argparse,numpy as np,pandas as pd,json
R=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('csv',nargs='?',default=str(R.parent/'NYUAD-Hackathon-T7-main/poc/data/wqp_groundwater.csv'));args=a.parse_args()
p=json.loads((R/'config/default.json').read_text());d=pd.read_csv(args.csv).drop_duplicates(['lat','lon']).copy()
lat=np.deg2rad(d.lat);lon=np.deg2rad(d.lon);h=np.sin((lat-np.deg2rad(p['hub_lat']))/2)**2+np.cos(lat)*np.cos(np.deg2rad(p['hub_lat']))*np.sin((lon-np.deg2rad(p['hub_lon']))/2)**2
d['distance_km']=6371*2*np.arcsin(np.sqrt(np.clip(h,0,1)))
d=d.sort_values(['distance_km','siteid']).head(64)
d[['siteid','state','lat','lon','distance_km']].to_csv(R/'data/site_geometry.csv',index=False)
print('Selected',len(d),'distinct coordinates; no concentration measurements transferred.')
