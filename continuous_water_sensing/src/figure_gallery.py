from pathlib import Path
import html
R=Path(__file__).resolve().parents[1]
figures=sorted((R/'figures').glob('*.svg'))
items=''.join(f'<section><h2>{html.escape(f.stem.replace("_"," "))}</h2><img src="{f.name}" alt="{f.stem}"><p><a href="{f.name}" download>Vector SVG</a> · <a href="{f.with_suffix(".png").name}" download>PNG</a></p></section>' for f in figures)
(R/'figures/index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Continuous water sensing — figures</title><style>body{background:#0b1520;color:#e8edf2;font:18px system-ui;margin:40px auto;max-width:1400px;padding:0 24px}h1{font-size:40px}h2{font-size:25px}section{margin:48px 0}img{width:100%;height:auto}a{color:#38bdf8}p{color:#a5b7c7}</style><h1>Continuous water sensing</h1><p>Ten reproducible simulation figures. Concentration units are differential NaCl-equivalent mg/kg. Source measurements and proposed device assumptions are distinguished in the project documentation.</p><p><a href="../presentation/Presentation.html">Open presentation</a> · <a href="../docs/SOURCES.md">Sources</a></p>'+items)
