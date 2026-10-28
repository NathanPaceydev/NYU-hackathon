import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const skill=process.env.SKILL_DIR || '/Users/nathanpacey/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations';
const {finalizePresentation,resolvePresentationFont,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const family=resolvePresentationFont({fontFamily:'Arial'});console.log('font',family);
const p=Presentation.create({slideSize:{width:1280,height:720}});
const data=JSON.parse(await fs.readFile(path.join(root,'presentation/slides.json'),'utf8'));
const BG='#0b1520',INK='#e8edf2',MUTED='#a5b7c7',ACC='#38bdf8';
function text(s,str,x,y,w,h,size=24,color=INK,bold=false){let sh=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});sh.text=str;sh.text.style={typeface:family,fontSize:size,color,bold,autoFit:'none'};return sh;}
let owners=[];
for(let i=0;i<data.length;i++){
 const d=data[i],s=p.slides.add();s.background.fill=BG;
 text(s,d.title,64,42,1152,78,i===0?48:36,INK,true);
 text(s,d.subtitle,64,120,1152,62,21,MUTED);
 if(d.chart){
  const ch=d.chart,ser=ch.series.map(a=>({name:a.name,values:a.y.map(v=>Number(v.toPrecision(10))),...(ch.kind==='scatter'?{xValues:a.x.map(v=>Number(v.toPrecision(10)))}:{}),fill:a.color,line:{fill:a.color,width:2.5},marker:{symbol:'none'}}));
  let chart=s.charts.add(ch.kind,{position:{left:70,top:197,width:1140,height:348},series:ser,...(ch.categories?{categories:ch.categories}:{}),hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{typeface:family,fontSize:15,fill:INK}},chartFill:BG,plotAreaFill:BG,chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},scatterOptions:{style:'line'},barOptions:{direction:'column',grouping:'clustered'},xAxis:{title:{text:ch.xlabel,textStyle:{typeface:family,fontSize:16,fill:INK}},textStyle:{typeface:family,fontSize:14,fill:MUTED},line:{fill:'#456070',width:1},numberFormatCode:'0.##'},yAxis:{title:{text:ch.ylabel,textStyle:{typeface:family,fontSize:16,fill:INK}},textStyle:{typeface:family,fontSize:14,fill:MUTED},line:{fill:'#456070',width:1},majorGridlines:{fill:'#294253',width:1},numberFormatCode:'0.##'},dataLabels:{showValue:false}});
  applyPresentationChartFont(chart,{fontFamily:family});owners.push(i+1);
  d.body.forEach((b,j)=>text(s,b,70,568+j*32,1130,33,19,j===0?'#2dd4bf':MUTED,j===0));
 }else{
  let start=i===0?230:214;let step=i===17?49:d.body.length>5?64:84;
  d.body.forEach((b,j)=>{text(s,b,78,start+j*step,1124,step-9,i===0?(j===0?32:26):(i===17?21:25),i===0&&j<2?'#2dd4bf':INK,i===0&&j<2);});
 }
 text(s,'CONTINUOUS WATER SENSING  •  SIMULATION',64,678,950,22,12,MUTED);
 text(s,`${i+1} / ${data.length}`,1120,678,100,22,12,MUTED);
 s.speakerNotes.textFrame.setText(d.notes);
}
await fs.mkdir(path.join(root,'.build/rendered'),{recursive:true});
const candidate=path.join(root,'.build/candidate.pptx');await(await PresentationFile.exportPptx(p)).save(candidate);
for(let i=0;i<p.slides.items.length;i++) {const b=await p.export({slide:p.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(root,`.build/rendered/slide-${i+1}.png`),new Uint8Array(await b.arrayBuffer()));}
const finalPath=path.join(root,'presentation/Continuous_Water_Sensing.pptx');
try { await fs.rename(finalPath,path.join(root,'.build/previous-export.pptx')); } catch(e) { if(e.code!=='ENOENT') throw e; }
try { await fs.rename(path.join(root,'.build/pptx.validation.json'),path.join(root,'.build/pptx.previous-validation.json')); } catch(e) { if(e.code!=='ENOENT') throw e; }
const out=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath,pythonExecutable:process.env.RUNTIME_PYTHON || '/Users/nathanpacey/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:[family]},requiredNativeChartOwnerSlides:owners,requiredNativeTableOwnerSlides:[],materializeLiteralChartWorkbooks:true,verifyArtifactToolImport:true,receiptPath:path.join(root,'.build/pptx.validation.json')});console.log(JSON.stringify(out));
