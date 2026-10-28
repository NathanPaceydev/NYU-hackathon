from pathlib import Path
import zipfile,hashlib,json
R=Path(__file__).resolve().parents[1];dest=R/'Continuous_Water_Sensing_Project.zip';excluded={'.venv','.build','__pycache__','.git'}
files=[f for f in R.rglob('*') if f.is_file() and not any(x in excluded or x.startswith('.chart-data-') for x in f.relative_to(R).parts) and f.name not in {dest.name,'.DS_Store','delivery_manifest.json'}]
manifest={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(files)}
(R/'delivery_manifest.json').write_text(json.dumps(manifest,indent=2));files.append(R/'delivery_manifest.json')
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(files):z.write(f,Path(R.name)/f.relative_to(R))
with zipfile.ZipFile(dest) as z:assert z.testzip() is None
print(f'{len(files)} files; {dest.stat().st_size/1e6:.2f} MB; archive checked')
