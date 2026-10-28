import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const skill='/Users/nathanpacey/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations';
const {finalizePresentation,resolvePresentationFont,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const family=resolvePresentationFont({fontFamily:'Arial'});
const template=path.join(root,'..','Slides Templates  and Judging','NYUAD Hackathon Presentation Template.pptx');
const p=await PresentationFile.importPptx(await FileBlob.load(path.join(root,'.build/ideation-template.pptx')));
const old=JSON.parse(await fs.readFile(path.join(root,'presentation/slides.json'),'utf8'));
const notes=JSON.parse(await fs.readFile(path.join(root,'presentation/Team_7_Ideation.json'),'utf8'));
const layout=p.layouts.items[0];
for(const s of p.slides.items){s.setLayout(layout);s.background.fill='#FFFFFF';for(const sh of s.shapes.items){sh.text='';sh.fill='none';sh.line={fill:'none',width:0};sh.position={left:0,top:0,width:1,height:1};}}
const PURPLE='#57068C',GRAY='#555555';
function text(s,str,x,y,w,h,size=19,color='#222222',bold=false){const sh=s.shapes.add({geometry:'textbox',name:str.slice(0,55),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});sh.text=str;sh.text.style={typeface:family,fontSize:size,color,bold,autoFit:'none'};return sh;}
function header(s,title,subtitle,i){text(s,title,54,64,858,44,32,'#000000',true);text(s,subtitle,55,114,850,46,19,GRAY);text(s,'TEAM 7  •  IDEATION  •  SIMULATED RESULTS',55,514,730,15,10,GRAY);text(s,`${i} / 5`,857,514,52,15,10,GRAY);}
function chart(s,index,x,y,w,h,opts={}){
 const c=structuredClone(old[index].chart);if(opts.categories)c.categories=opts.categories;if(opts.ylabel)c.ylabel=opts.ylabel;
 const colors=index===12?['#222222','#16877B','#999999','#660099']:['#595959','#16877B','#660099','#B8424C'];
 const series=c.series.map((v,j)=>({name:opts.names?.[j]??v.name,values:v.y.map(v=>Number(v.toPrecision(10))),...(c.kind==='scatter'?{xValues:v.x.map(v=>Number(v.toPrecision(10)))}:{}),fill:colors[j%4],line:{fill:colors[j%4],width:2.4},marker:{symbol:'none'}}));
 const ch=s.charts.add(c.kind,{position:{left:x,top:y,width:w,height:h},series,...(c.categories?{categories:c.categories}:{}),hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{typeface:family,fontSize:11,fill:'#333333'}},chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF',chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},scatterOptions:{style:'line'},barOptions:{direction:'column',grouping:'clustered'},xAxis:{title:{text:opts.xlabel??c.xlabel,textStyle:{typeface:family,fontSize:12,fill:'#333333'}},textStyle:{typeface:family,fontSize:11,fill:GRAY},line:{fill:'#999999',width:1},numberFormatCode:'0.##'},yAxis:{title:{text:c.ylabel,textStyle:{typeface:family,fontSize:12,fill:'#333333'}},textStyle:{typeface:family,fontSize:11,fill:GRAY},line:{fill:'#999999',width:1},majorGridlines:{fill:'#DDDDDD',width:1},numberFormatCode:'0.##'},dataLabels:{showValue:false}});
 applyPresentationChartFont(ch,{fontFamily:family});return ch;
}
async function photo(s,name,x,y,w,h,alt){s.images.add({blob:new Uint8Array(await fs.readFile(path.join(root,'presentation/assets',name))),contentType:'image/jpeg',alt,fit:'cover',position:{left:x,top:y,width:w,height:h}});}
// 1 — A concrete problem and actual contextual photographs.
{
 const s=p.slides.items[0];header(s,'Small changes need trustworthy detection','Water-quality monitoring for treatment and reuse operators • SDG 6',1);
 text(s,'A documented monitoring gap',55,172,465,28,22,PURPLE,true);
 text(s,'UN 2025: poorest regions supplied only 60,000 of about two million water-quality reporting measurements. EPA describes online monitoring for investigation.',55,208,465,105,20);
 text(s,'Our target',55,323,465,27,21,PURPLE,true);
 text(s,'Test a water-proxy mean using published CV sensing, adding loss, drift and decision analysis.',55,356,465,63,20);
 text(s,'Sources: UN SDG Report 2025; EPA OWQM.\nOur operator use case is assumed. Water saved remains unmeasured.',55,436,465,65,18);
 await photo(s,'blue_plains.jpg',558,167,344,139,'Blue Plains wastewater treatment plant, Washington DC; contextual photograph, not our deployment');
 text(s,'Treatment context: Blue Plains, Washington, DC',558,307,344,23,12,GRAY);
 await photo(s,'usgs_sampling.jpg',558,344,344,130,'USGS staff collecting a water sample in high water at Lincoln Creek, Milwaukee; not a project trial');
 text(s,'USGS field sampling: real-world monitoring demands',558,475,344,20,12,GRAY);
 text(s,'Photos: Duane Lempke / CC0; Barbara Mahler / USGS, public domain',558,495,344,15,9,GRAY);
 s.speakerNotes.textFrame.setText(notes[0].notes+'\nPHOTO SOURCES: Blue Plains aerial by Duane Lempke,2022,CC0: https://commons.wikimedia.org/wiki/File:BluePlainsWaste-4126-022022.jpg . USGS Lincoln Creek sampling by Barbara J Mahler,2013,public domain: https://www.usgs.gov/media/images/collecting-a-water-quality-sample-usgs-regional-stream-quality . Photographs illustrate context; neither location is our pilot or a measured salt incident. They are not proof that our salt proxy detects all visible contamination. SDG definitions: https://sdgs.un.org/goals/goal6 .');
}
// 2 — Explain the transducer and continuous experiment next to the actual trace.
{
 const s=p.slides.items[1];header(s,'Proposed sensor and continuous readout','1550 nm light → water-induced phase shift → homodyne → mean estimate',2);
 text(s,'A calibrated optical proxy',55,170,299,28,21,PURPLE,true);
 text(s,'NaCl index slope: 1.62 × 10⁻⁷ RIU per mg/kg. A proposed 10 µm interaction converts salt changes into phase.',55,208,294,87,19);
 text(s,'Why shared squeezing?',55,308,299,28,21,PURPLE,true);
 text(s,'Distribute one squeezed mode across taps. Negative readout correlations reduce noise in q̂ = Σ yᵢ / M.',55,345,294,86,19);
 text(s,'Synthetic event at 16 different taps',379,170,523,27,19,PURPLE,true);
 chart(s,12,374,205,533,225,{names:['Water mean','Sensor response','Coherent','Distributed']});
 text(s,'Arrivals: 90–135 s; response lag: 10 s. Both strategies share the same drift. Squeezing reduces noise, not lag.',380,438,520,60,17);
 text(s,'Classical Python simulator • Proposed quantum sensing hardware • No pollutant-specific identification',55,490,850,24,14,GRAY);
 s.speakerNotes.textFrame.setText(notes[1].notes+'\n'+old[12].notes+'\nSource NaCl slope Saunders2016 https://doi.org/10.1364/AO.55.000947 . Mean event.35mg/kg,±25%spatial variation,25s rise,1s sampling. The stationary RMSE does not include transient lag bias. Full trace results/time_trace.csv. Scalar estimator is classical; this does not show quantum computational speedup. Source mode rate1MHz and10dB cap are assumptions.');
}
// 3 — Visible simulation stack, input/output contract and development method.
{
 const s=p.slides.items[2];header(s,'How the simulation runs','Classical Python on a CPU models a proposed quantum optical sensor',3);
 text(s,'1  Inputs and assumptions',55,173,410,28,21,PURPLE,true);
 text(s,'default.json: optical budget, loss and drift.\nsite_geometry.csv: 64 distinct locations.\nSalt-change signals are synthetic.',55,212,410,92,19);
 text(s,'2  Scientific implementation',495,173,410,28,21,PURPLE,true);
 text(s,'Python 3.12, NumPy and SciPy compute phase sensitivity, optical covariance, mean RMSE and detection probability.',495,212,405,92,19);
 text(s,'3  Outputs and reproducibility',55,326,410,28,21,PURPLE,true);
 text(s,'pandas handles CSV result tables.\nMatplotlib creates ten PNG/SVG figures.\nRun: bash src/reproduce.sh',55,366,410,93,19);
 text(s,'4  Verification and limits',495,326,410,28,21,PURPLE,true);
 text(s,'13 model checks. Seed 2601006.\n100,000 null/event draws per strategy.\nNo quantum hardware or ML training.',495,366,405,93,19);
 text(s,'Analytic error curves, Monte Carlo checks and a separate synthetic time trace. Full method: docs/SIMULATION.md',55,484,850,26,14,GRAY);
 s.speakerNotes.textFrame.setText(notes[2].notes+' Code structure: model.py implements equations; run.py sweeps assumptions; validate.py checks identities. Native PPTX uses JavaScript and artifact-tool, separate from the science. Analytic curves compute w^T Sigma w, with OU temperature and independent calibration added. Monte Carlo checks Gaussian marginal decisions. A seeded trace does not establish field reliability.');
}
// 4 — Matched estimation and decision experiments.
{
 const s=p.slides.items[3];header(s,'Controlled pilot: lower error, more detected changes','16 taps • 100 m links • 10 nW/tap • 1 s • Assumed 50 µK common temperature residual',4);
 text(s,'Estimation: 28% lower total RMSE',55,174,422,27,20,PURPLE,true);
 text(s,'Detection: 24% → 47% probability',492,174,413,27,20,PURPLE,true);
 const categories=['Coherent','Local squeezed','Distributed'];
 chart(s,6,48,208,427,210,{categories,xlabel:'Probe strategy',names:['Optical noise','Total error']});
 chart(s,11,484,208,427,210,{categories,xlabel:'Probe strategy',names:['Gaussian prediction','Monte Carlo']});
 text(s,'0.0921 → 0.0664 mg/kg total RMSE. Distributed squeezing also beats independent squeezing by 16.6%.',55,430,416,60,17);
 text(s,'A 0.15 mg/kg mean step, at 1% false alarm per decision. 100,000 null and event trials per strategy.',492,430,412,60,17);
 text(s,'All results simulated. 1% at 1 Hz means 36 expected flagged windows/hour; an operational alarm rule is still needed.',55,495,850,18,12,GRAY);
 s.speakerNotes.textFrame.setText(notes[3].notes+'\n'+old[11].notes+'\nAnalytic Pdetect .2426817/.3293999/.4733113;MC .24311/.3316/.47512. Marginal Gaussian tests, not temporally independent field seconds. No regulatory or chemical safety threshold.13internal checks validate model properties; no hardware trial. Pilot optical RMSE .079619 vs .047583mg/kg gives1.673×gain;total1.387×. Technical targets are essential. Raw summary results/summary.json.');
}
// 5 — Failure boundary, sustainability and a concrete experimental next step.
{
 const s=p.slides.items[4];header(s,'The next test: does the gain survive real water?','Loss, temperature drift and higher classical power determine whether quantum optics is useful',5);
 text(s,'Common temperature drift erases gain',55,175,422,27,19,PURPLE,true);
 chart(s,8,48,211,427,210,{ylabel:'Classical / quantum total RMSE',xlabel:'log₁₀ temperature residual (mK)',names:['16-tap pilot']});
 text(s,'At 10 mK: both errors ≈9.137 mg/kg. At low drift, ~28 nW coherent matches 10 nW distributed performance.',55,430,416,62,17);
 text(s,'A scoped laboratory pilot',510,175,390,28,21,PURPLE,true);
 text(s,'1  Calibrate one water cell: salt response, transmission, temperature and bias.',510,214,389,61,18);
 text(s,'2  Blind-test four taps against coherent probes and conventional conductivity.',510,281,389,61,18);
 text(s,'3  Measure detection delay, false alarms and full electrical energy before scaling.',510,348,389,61,18);
 text(s,'Resource KPI: 160 nJ probe/window for both. Pump, readout and control energy are unmeasured; no net saving claimed.',510,423,389,72,17,PURPLE,true);
 text(s,'Path to impact: operator + optics-lab pilot → validated monitoring module; water saved and commercial viability remain open.',55,496,850,18,12,GRAY);
 s.speakerNotes.textFrame.setText(notes[4].notes+'\n'+old[8].notes+'\nThe50µK residual is a demanding target, not demonstrated water performance;10mK is a stress scenario, not statistical interpretation of YSI accuracy. CommonOUdrift tau60s.1mK≈.916mg/kg apparent NaCl change using Kim thermo-optic anchor https://opg.optica.org/abstract.cfm?uri=sensors-2012-STu1F.3 . Higher-power coherent sweep1nW–70µW in Figure10. Stop or redesign if a cheaper/lower-energy conventional alternative achieves the operational goal. Three KPIs: estimator RMSE/sl4,monitoring detection/sl4,energy accounting/sl5. Literature is conditionally consistent, not independently experimentally validated. Team7 has no confirmed partner, customer, price or installed device.');
}
const render=path.join(root,'.build/ideation-visual-rendered');await fs.mkdir(render,{recursive:true});
const candidate=path.join(root,'.build/ideation-visual-candidate.pptx');await(await PresentationFile.exportPptx(p)).save(candidate);
for(let i=0;i<5;i++){const b=await p.export({slide:p.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(render,`slide-${i+1}.png`),new Uint8Array(await b.arrayBuffer()));}
const finalPath=path.join(root,'presentation/Team_7_Ideation_Visual.pptx');
for(const [a,b]of[[finalPath,path.join(root,'.build/ideation-visual-previous.pptx')],[path.join(root,'.build/ideation-visual.validation.json'),path.join(root,'.build/ideation-visual.previous-validation.json')]]){try{await fs.rename(a,b);}catch(e){if(e.code!=='ENOENT')throw e;}}
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath,pythonExecutable:'/Users/nathanpacey/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','9144000,5143500','--validate-heading-fit'],fontPolicy:{basis:'reference',families:[family],referencePath:template,referenceSha256:createHash('sha256').update(await fs.readFile(template)).digest('hex')},requiredNativeChartOwnerSlides:[2,4,5],requiredNativeTableOwnerSlides:[],materializeLiteralChartWorkbooks:true,verifyArtifactToolImport:true,receiptPath:path.join(root,'.build/ideation-visual.validation.json')});console.log(JSON.stringify(result));
