"""Build the final 5-slide deck plus backup from the submitted ideation deck.
Keeps the NYUAD template, team title, SDG icons and photo; numbers come from
results/judges_response.json so the slides cannot drift from the simulation."""
import json
from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Pt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'presentation/Team_7_Submitted.pptx'
OUT = ROOT / 'presentation/Team_7_Final.pptx'
r = json.loads((ROOT / 'results/judges_response.json').read_text(encoding='utf-8'))
gates = {row['candidate'][0]: row for row in json.loads((ROOT / 'results/advantage_path.json').read_text(encoding='utf-8'))['candidates']}
s = json.loads((ROOT / 'results/summary.json').read_text())

PURPLE, GREY, BLACK, LIGHT = RGBColor(0x57, 0x06, 0x8C), RGBColor(0x55, 0x55, 0x55), RGBColor(0x22, 0x22, 0x22), RGBColor(0xEE, 0xEA, 0xF3)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# Headline numbers used on several slides.
power = r['power']
matched_nw = power['coherent_power_matching_quantum_w'] * 1e9
regional_gain = s['regional64']['coherent_optimized']['controlled_rmse'] / s['regional64']['entangled']['controlled_rmse']
h2h = {(row['sensor'], row['scenario']): row for row in r['head_to_head']}
quantum_ctrl = h2h[('Quantum 10 nW', 'controlled (50 µK)')]
cond1_ctrl = h2h[('Conductivity ×1', 'controlled (50 µK)')]
cond16_ctrl = h2h[('Conductivity ×16', 'controlled (50 µK)')]
quantum_field = h2h[('Quantum 10 nW', 'field (10 mK)')]
cond16_field = h2h[('Conductivity ×16', 'field (10 mK)')]
need = r['squeezing_needed']['pilot']


def text(slide, x, y, w, h, content, size=14, color=BLACK, bold=False, align=PP_ALIGN.LEFT):
    """content is a string or a list of (string, bold) runs per paragraph."""
    box = slide.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h))
    frame = box.text_frame
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
    paragraphs = content if isinstance(content, list) else [content]
    for i, para in enumerate(paragraphs):
        p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        p.alignment = align
        p.space_after = Pt(size * 0.35)
        for run_text, run_bold in (para if isinstance(para, list) else [(para, bold)]):
            run = p.add_run()
            run.text = run_text
            run.font.name, run.font.size, run.font.bold, run.font.color.rgb = 'Arial', Pt(size), run_bold, color
    return box


def header(slide, title, subtitle, page):
    text(slide, 40, 30, 600, 34, title, 26, BLACK, True)
    text(slide, 41, 66, 600, 22, subtitle, 13, GREY)
    text(slide, 600, 386, 82, 12, page, 9, GREY, align=PP_ALIGN.RIGHT)


def box(slide, x, y, w, h, title, body, fill=LIGHT, color=BLACK):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Pt(x), Pt(y), Pt(w), Pt(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    shape.adjustments[0] = 0.08
    frame = shape.text_frame
    frame.word_wrap = True
    frame.vertical_anchor = MSO_ANCHOR.TOP
    frame.margin_left = frame.margin_right = Pt(6)
    frame.margin_top = Pt(6)
    for i, (line, size, bold) in enumerate([(title, 12, True), (body, 10, False)]):
        p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = line
        run.font.name, run.font.size, run.font.bold, run.font.color.rgb = 'Arial', Pt(size), bold, color


def arrow(slide, x1, y, x2):
    line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Pt(x1), Pt(y), Pt(x2), Pt(y))
    line.line.color.rgb = PURPLE
    line.line.width = Pt(2)
    line.line._get_or_add_ln().append(line.line._get_or_add_ln().makeelement(
        '{http://schemas.openxmlformats.org/drawingml/2006/main}tailEnd', {'type': 'triangle'}))


def picture(slide, name, x, y, w):
    return slide.shapes.add_picture(str(ROOT / 'figures' / name), Pt(x), Pt(y), width=Pt(w))


def notes(slide, content):
    slide.notes_slide.notes_text_frame.text = content


def new_slide(prs):
    slide = prs.slides.add_slide(prs.slides[1].slide_layout)
    for placeholder in list(slide.placeholders):
        placeholder._element.getparent().remove(placeholder._element)
    return slide


def remove(shape):
    shape._element.getparent().remove(shape._element)


def set_text(shape, value):
    run = shape.text_frame.paragraphs[0].runs[0]
    for extra in shape.text_frame.paragraphs[0].runs[1:]:
        extra._r.getparent().remove(extra._r)
    for extra in shape.text_frame.paragraphs[1:]:
        extra._p.getparent().remove(extra._p)
    run.text = value


prs = Presentation(SOURCE)
cover, sensor, pilot, layers, drift = list(prs.slides)

# 1. Problem, use case and SDG — reuse the team title, SDG icons and photo.
for shape in list(cover.shapes):
    if shape.shape_type != 13 and 'SensorFlow' not in shape.text_frame.text and 'Photos:' not in shape.text_frame.text \
            and 'USGS field' not in shape.text_frame.text:
        remove(shape)
text(cover, 40, 50, 460, 34, 'Catch salt creep before the tap', 24, BLACK, True)
text(cover, 41, 84, 460, 20, 'Use case: salinity alarms at water-reuse and desalination blending points', 12, GREY)
text(cover, 41, 116, 460, 18, 'The problem', 15, PURPLE, True)
text(cover, 41, 136, 460, 80, 'Brine carry-over or saline intrusion first appears as a tiny rise in dissolved salt. '
     'Today it is often caught at the next scheduled lab test, after the water has already moved on.', 13)
text(cover, 41, 196, 370, 18, 'Our target', 15, PURPLE, True)
text(cover, 41, 216, 370, 70, [[('Detect a ', False), ('0.15 mg/kg', True), (' rise on a ', False), ('500 mg/kg', True),
                                  (' NaCl background (0.03 %) in a ', False), ('1 s', True), (' window, so the operator pulls a confirmatory '
                                  'grab sample immediately.', False)]], 13)
text(cover, 41, 286, 370, 18, 'Why it matters: SDG 6', 15, PURPLE, True)
text(cover, 41, 306, 370, 60, '6.1 safe drinking water  ·  6.3 safe water reuse  ·  6.4 less water dumped because of late detection. '
     'Our question: does quantum sensing make that alarm better?', 12)
text(cover, 41, 362, 370, 22, 'Sources: UN SDG Report 2025; US EPA Online Water Quality Monitoring. The 0.15 mg/kg target is our design choice.', 8, GREY)
text(cover, 600, 386, 82, 12, '1 / 5', 9, GREY, align=PP_ALIGN.RIGHT)
notes(cover, 'Judges asked for one concrete analyte, the threshold, and the decision it improves. Analyte: dissolved salt (NaCl-equivalent), '
      'measured as a change on a 500 mg/kg background. Decision: trigger a grab sample. Impact framing: SDG 6.1/6.3/6.4. '
      'The rest of the deck answers one question honestly: is quantum light the right tool for this alarm?')

# 2. System flow and what is (not) quantum.
flow = new_slide(prs)
header(flow, 'Quantum sensing, classical decisions', 'End-to-end: water sample → squeezed phase sensing → classical estimator → action', '2 / 5')
steps = [('Water tap', '16 taps, sampled every 1 s', LIGHT, BLACK),
         ('Phase cell', '1550 nm, 10 µm path: salt shifts refractive index → optical phase', LIGHT, BLACK),
         ('Quantum probe', 'one squeezed beam shared across all taps; homodyne readout', PURPLE, WHITE),
         ('Estimator', 'classical weighted mean + drift model (Kalman-equivalent)', LIGHT, BLACK),
         ('Action', 'alarm → grab sample → lab confirms', LIGHT, BLACK)]
for i, (title, body, fill, color) in enumerate(steps):
    x = 40 + i * 130
    box(flow, x, 100, 110, 82, title, body, fill, color)
    if i < len(steps) - 1:
        arrow(flow, x + 111, 141, x + 129)
text(flow, 41, 200, 300, 18, 'What is quantum', 15, PURPLE, True)
text(flow, 41, 220, 300, 90, ['Only the sensing: distributed squeezed light lowers the shot noise on the average of all taps '
                              '(Zhuang, Zhang & Shapiro 2018; Guo et al. 2020).',
                              'Everything after the detector is classical signal processing.'], 12)
text(flow, 370, 200, 310, 18, 'What is not', 15, PURPLE, True)
text(flow, 370, 220, 310, 90, ['No quantum computing advantage is claimed.',
                               'QAOA was tested for choosing tap locations: a classical greedy algorithm is near-optimal and '
                               'scales to thousands of nodes, so placement moved to backup (B1).'], 12)
callout = flow.shapes.add_shape(MSO_SHAPE.RECTANGLE, Pt(40), Pt(318), Pt(642), Pt(46))
callout.fill.solid()
callout.fill.fore_color.rgb = LIGHT
callout.line.fill.background()
text(flow, 52, 324, 620, 50, [[('Measured gain is a constant factor, not √N. ', True),
                               (f'{r["pilot_total_gain"]:.2f}× lower error for the 16-tap pilot ({r["total_loss_db"]:.2f} dB loss), '
                                f'{regional_gain:.2f}× across 64 regional taps. With loss η the ceiling is 1/√(1−η) = '
                                f'{r["loss_limited_gain"]["pilot"]["bound_at_max"]:.2f}× (Demkowicz-Dobrzański et al. 2012). See B3.', False)]], 12)
notes(flow, 'Answers: "what is the quantum technique" and "why QAOA". It is CV distributed quantum sensing; processing is a '
      'classical linear estimator, which is optimal for this Gaussian model (a Kalman filter gives the same answer for slow drift). '
      'QAOA is not needed: placement is a solved classical problem. The previous "classical needs N sensors, quantum needs √N" line was '
      'wrong with loss; replaced by the measured constant factor, as judge 4 asked.')

# 3. Head-to-head with classical baselines.
h2h_slide = new_slide(prs)
header(h2h_slide, 'Is quantum light necessary? Not for salt', 'Same 500 mg/kg background, 16 taps, 1 s window, 1 % false alarm per decision', '3 / 5')
picture(h2h_slide, '13_head_to_head.png', 50, 92, 620)
text(h2h_slide, 41, 352, 640, 34, [[(f'{matched_nw:.0f} nW of ordinary light matches 10 nW of squeezing. ', True),
                                    (f'A temperature-compensated conductivity probe is {quantum_ctrl["rmse_mg_kg"] / cond1_ctrl["rmse_mg_kg"]:.0f}× better (controlled) '
                                     f'and {quantum_field["rmse_mg_kg"] / cond16_field["rmse_mg_kg"]:.0f}× better in field drift: 1 mK looks like '
                                     f'{r["temperature_sensitivity_mg_kg_per_K"]["optical"] / 1000:.2f} mg/kg of salt optically, '
                                     f'{r["temperature_sensitivity_mg_kg_per_K"]["conductivity"] / 1000:.2f} mg/kg to conductivity.', False)]], 11)
notes(h2h_slide, 'Judges 1, 4 and 5 asked for a head-to-head with classical baselines and a commercial conductivity probe at the same '
      'background, window and false-alarm rate. Conductivity model is spec-derived (YSI EXO-class: 0.1 µS/cm resolution, ±0.01 °C '
      'temperature sensor, ~2 %/°C compensation), not a measurement. Refractive index is non-specific and very temperature sensitive; '
      'conductivity is ~90× less so. Honest result: for salinity, conductivity wins.')

# 4. Power cap and loss budget.
budget = new_slide(prs)
header(budget, 'What would it take? Power cap and loss budget', 'Quantum only pays if probe power is genuinely capped — and the squeezing survives the network', '4 / 5')
picture(budget, '12_power_cap.png', 36, 92, 330)
text(budget, 41, 335, 330, 50, f'No physical cap near 10 nW: fibre SBS ÷ 16 taps allows {power["sbs_per_tap_w"] * 1e6:.0f} µW, photothermal noise '
     f'{power["photothermal_cap_w"] * 1e6:.0f} µW. A real cap needs ~{round(power["taps_where_sbs_forces_matched_power"], -4):,.0f} taps per source.', 10)
rows = list(r['loss_budget_db'].items()) + [('Total, source → detector', r['total_loss_db'])]
table = budget.shapes.add_table(len(rows) + 1, 2, Pt(390), Pt(96), Pt(290), Pt(16 * (len(rows) + 1))).table
table.columns[0].width, table.columns[1].width = Pt(210), Pt(80)
for i, (name, value) in enumerate([('Element (16-tap pilot)', 'Loss')] + [(n, f'{v:.2f} dB') for n, v in rows]):
    for j, content in enumerate((name, value)):
        cell = table.cell(i, j)
        cell.text = content
        cell.margin_top = cell.margin_bottom = Pt(2)
        font = cell.text_frame.paragraphs[0].runs[0].font
        font.name, font.size, font.bold = 'Arial', Pt(10), i in (0, len(rows))
        if i == 0:
            cell.fill.solid()
            cell.fill.fore_color.rgb = PURPLE
text(budget, 390, 230, 290, 150, [[('Squeezing needed to keep ', False), (f'{r["pilot_total_gain"]:.2f}×', True), (':', False)],
                                  f'{need["network_input_db"]:.1f} dB entering the network '
                                  f'({r["pilot_detected_squeezing_db"]:.1f} dB survives to the detectors)',
                                  f'{need["generated_db"]["0.95"]:.1f} dB at the source if 95 % escapes the squeezer; '
                                  f'{need["generated_db"]["0.9"]:.1f} dB if 90 %',
                                  f'Gain falls below 1.1× after {r["extra_loss_db_until_gain_1p1"]:.1f} dB of extra loss'], 11)
notes(budget, 'Judges 4 and 5 priorities 1 and 2. Power: coherent light matching the quantum error needs only '
      f'{matched_nw:.1f} nW; above ~1 µW both hit the same drift floor ({power["floor_rmse"]:.3f} mg/kg) and the gain vanishes '
      f'({power["gain_at_1uw"]:.3f}× at 1 µW). Photothermal cap: water absorbs ~10/cm at 1550 nm, '
      f'{power["absorbed_fraction"] * 100:.1f} % absorbed over 10 µm, {power["heating_K_per_W"]:.0f} K/W heating, 1e-3 RIN, '
      'set equal to the 50 µK thermal budget. SBS: 2 mW per shared trunk (assumed). Eye safety: Class 1 ~10 mW at 1550 nm. '
      'Loss budget from config; squeezer escape efficiency was not in the original model and is now stated explicitly. '
      'Full squeezing sweep in B2.')

# 5. Verdict: where quantum really wins (results/advantage_path.json).
verdict = new_slide(prs)
header(verdict, 'Verdict: where quantum light really wins', 'Squeezing must beat the best classical option at the power the sample allows', '5 / 5')
picture(verdict, '15_advantage_gates.png', 36, 96, 420)
text(verdict, 470, 96, 212, 230, [
    [('Salt fails. ', True), (f'At the real power cap, temperature drift is {gates["B"]["tech_to_shot_ratio"]:.0f}–'
                              f'{gates["A"]["tech_to_shot_ratio"]:,.0f}× the shot noise, so squeezing changes nothing.', False)],
    [('Real advantage needs a dose cap. ', True), (f'Live cells limit light by photodamage; squeezing gave '
                                                  f'{gates["D"]["gain_vs_best_classical"]:.2f}× lower error (Casacio et al. 2021), '
                                                  f'but {1 - gates["D"]["eta"]:.0%} optical loss caps it at '
                                                  f'{(1 - gates["D"]["eta"]) ** -0.5:.2f}×.', False)],
    [('Path: ', True), ('1 find a water decision only a dose-limited measurement can make (e.g. toxin state of live cyanobacteria); '
                        '2 tabletop squeezed vs coherent at the photodamage limit; 3 go only if ≥1.2× (today: 1.16×) and classical misses the target.', False)]], 11)
closing = verdict.shapes.add_shape(MSO_SHAPE.RECTANGLE, Pt(40), Pt(318), Pt(642), Pt(46))
closing.fill.solid()
closing.fill.fore_color.rgb = LIGHT
closing.line.fill.background()
text(verdict, 52, 324, 620, 40, [[('What we deliver: ', True), ('a validated simulator and four-gate test that tells a utility, before it buys a '
                                  'squeezed-light source, whether quantum sensing can beat the sensor it already has.', False)]], 12)
notes(verdict, 'Four gates for a real quantum advantage: (1) the best classical sensor falls short of the target; (2) a physical power or '
      'dose cap binds while shot noise still dominates; (3) loss is low enough that 1/sqrt(1-eta) is worth it; (4) classical cannot '
      'simply average longer. Salt fails 2 and 4 (and conductivity beats it, B7). A plasmonic microcystin chip fails 1 (classical SPR already '
      f'reaches 73 ng/L vs the WHO 1 ug/L limit) and 2 (Biacore-class noise is ~{gates["C"]["tech_to_shot_ratio"]:.0f}x Dowran\'s shot-noise level; it would need a '
      f'{gates["C"]["noise_cut_needed_for_1p2x"]:.0f}x quieter baseline for 1.2x). Dose-limited live-cell Raman passes 2 and 4 and has been '
      'demonstrated: Casacio reports 35 % better power SNR, which is 1.16x lower error. It fails 3: total efficiency is only 0.44, '
      'so even perfect squeezing gives at most 1.34x. No routine water decision needs '
      'it yet: that is the open research question. Cost, false alarms and stop rule in B7; loss ceiling curves in B8.')

# Backup B7: the salt verdict, impact and stop rule (was slide 5 before the advantage screen).
impact = new_slide(prs)
header(impact, 'Backup B7: salt verdict, impact and scale', 'Rigorous negative results are a deliverable: they tell operators what to buy', 'B7')
columns = [
    ('Verdict', [f'For salinity, a conductivity probe beats our quantum design ({quantum_ctrl["rmse_mg_kg"] / cond1_ctrl["rmse_mg_kg"]:.0f}× '
                 f'controlled, {quantum_field["rmse_mg_kg"] / cond16_field["rmse_mg_kg"]:.0f}× in the field).',
                 'Squeezing helps only if power per tap is capped below ~30 nW, extra loss stays under ~5 dB '
                 'and temperature is held to ~0.1 mK.']),
    ('Impact and scale', [f'At 1 false alarm per week, 16 conductivity probes catch the 0.15 mg/kg step '
                          f'{cond16_ctrl["p_detect_1_per_week"]:.0%} of the time in controlled conditions; the quantum array '
                          f'{quantum_ctrl["p_detect_1_per_week"]:.1%}.',
                          'Cost, calibration and maintenance favour commercial probes; squeezed sources need lab-grade stabilisation.']),
    ('Next steps', ['1  Point the optical sensor at targets conductivity cannot see (non-ionic organics), with a temperature reference arm.',
                    '2  Lab pilot: one cell, coherent vs squeezed vs conductivity side by side.',
                    '3  Stop rule: if classical meets the operator\'s alarm target, ship classical.']),
]
for i, (title, body) in enumerate(columns):
    x = 40 + i * 218
    text(impact, x, 100, 200, 20, title, 16, PURPLE, True)
    text(impact, x, 126, 200, 190, body, 12)
closing = impact.shapes.add_shape(MSO_SHAPE.RECTANGLE, Pt(40), Pt(318), Pt(642), Pt(46))
closing.fill.solid()
closing.fill.fore_color.rgb = LIGHT
closing.line.fill.background()
text(impact, 52, 324, 620, 40, [[('What we deliver: ', True), ('a validated simulator and feasibility map (power × loss × drift) that tells a '
                                  'utility, before it buys a squeezed-light source, whether quantum sensing will beat the probe it already has.', False)]], 12)
# Backup: reuse the submitted slides and add the supporting figures.
for shape in layers.shapes:
    if shape.has_text_frame and shape.text_frame.text.startswith('Classical layers'):
        set_text(shape, 'Backup B1: classical layers — placement and source ID')
    elif shape.has_text_frame and shape.text_frame.text.replace(' ', '') == '4/5':
        set_text(shape, 'B1')
for shape in list(pilot.shapes):
    if shape.has_text_frame and shape.text_frame.text.startswith('Controlled pilot'):
        set_text(shape, 'Backup B4: controlled pilot estimation and detection')
    elif shape.has_text_frame and shape.text_frame.text.replace(' ', '') == '3/5':
        set_text(shape, 'B4')
for shape in list(sensor.shapes):
    if shape.has_text_frame and '√N' in shape.text_frame.text:
        remove(shape)
    elif shape.has_text_frame and shape.text_frame.text.startswith('Proposed sensor'):
        set_text(shape, 'Backup B5: sensor and continuous readout')
    elif shape.has_text_frame and shape.text_frame.text.replace(' ', '') == '2/5':
        set_text(shape, 'B5')

squeezing = new_slide(prs)
header(squeezing, 'Backup B2: loss budget and squeezing sweep', 'Gain peaks at '
       f'{r["max_total_gain"]:.2f}× near {r["max_gain_input_db"]:.0f} dB; phase-lock jitter then mixes in anti-squeezing', 'B2')
picture(squeezing, '11_loss_budget.png', 40, 100, 640)

scaling = new_slide(prs)
header(scaling, 'Backup B3: realised gain vs the √N claim', 'Loss-limited constant factor 1/√(1−η); Demkowicz-Dobrzański, Kołodyński & Guţă, Nat. Commun. 3, 1063 (2012)', 'B3')
picture(scaling, '14_loss_limited_gain.png', 40, 100, 640)

ceiling = new_slide(prs)
header(ceiling, 'Backup B8: loss ceiling for any target', 'Gain over coherent light at the cap with no technical noise; points are the screened candidates', 'B8')
picture(ceiling, '16_gain_vs_efficiency.png', 150, 96, 420)

assumptions = new_slide(prs)
header(assumptions, 'Backup B6: assumptions and references', 'Every number is a model prediction; no hardware was measured', 'B6')
text(assumptions, 41, 96, 310, 290, [
    'NaCl index slope 1.62×10⁻⁷ RIU per mg/kg (Saunders et al. 2016); dn/dT −1.49×10⁻⁴ /K.',
    '10 nW per tap, 10 µm path, 100 m fibre, 16 taps, 1 s window, 50 µK (controlled) or 10 mK (field) common temperature residual.',
    'Water absorption ≈10 cm⁻¹ at 1550 nm (Hale & Querry 1973); 5 µm beam radius; 1e-3 laser intensity noise.',
    'Conductivity: 2 µS/cm per mg/kg, 2 %/°C compensation, 0.1 µS/cm resolution, ±0.01 °C sensor (YSI EXO-class specs).',
    'Fibre SBS budget 2 mW per shared trunk; Class 1 eye-safe ~10 mW at 1550 nm.'], 10)
text(assumptions, 370, 96, 310, 290, [
    'Zhuang, Zhang & Shapiro, Phys. Rev. A 97, 032329 (2018).',
    'Guo et al., Nat. Phys. 16, 281 (2020).',
    'Demkowicz-Dobrzański, Kołodyński & Guţă, Nat. Commun. 3, 1063 (2012).',
    'Oh et al., Phys. Rev. Research 2, 023030 (2020).',
    'Saunders et al., Appl. Opt. 55, 947 (2016).',
    'Hale & Querry, Appl. Opt. 12, 555 (1973).',
    'YSI EXO sensor specifications; US EPA Online Water Quality Monitoring; UN SDG Report 2025.',
    'Dowran et al., Optica 5, 628 (2018); Casacio et al., Nature 594, 201 (2021).',
    'Code and data: src/judges_response.py, src/advantage_path.py and their results/*.json.'], 10)

# Order: 5 main slides, then backup. The old slide 5 is superseded by slides 3 and 4.
order = [cover, flow, h2h_slide, budget, verdict, layers, squeezing, scaling, pilot, sensor, assumptions, impact, ceiling]
ids = prs.slides._sldIdLst
by_slide = {slide.slide_id: element for slide, element in zip(prs.slides, list(ids))}
drift_element = by_slide[drift.slide_id]
prs.part.drop_rel(drift_element.rId)
ids.remove(drift_element)
for slide in order:
    element = by_slide[slide.slide_id]
    ids.remove(element)
    ids.append(element)

prs.save(OUT)
print('wrote', OUT)
