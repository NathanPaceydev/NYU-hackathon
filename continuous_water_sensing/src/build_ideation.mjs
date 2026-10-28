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
const d=JSON.parse(await fs.readFile(path.join(root,'presentation/Team_7_Ideation.json'),'utf8'));
// Retain the actual template master, theme and branded layout. Replace instruction copy.
const layout=p.layouts.items[0];
for(const s of p.slides.items){s.setLayout(layout);s.background.fill='#FFFFFF';for(const sh of s.shapes.items){sh.text='';sh.fill='none';sh.line={fill:'none',width:0};sh.position={left:0,top:0,width:1,height:1};}}
while(p.slides.items.length<d.length){const s=p.slides.items.at(-1).duplicate();s.setLayout(layout);}
function text(s,str,x,y,w,h,size=24,color='#111111',bold=false){let sh=s.shapes.add({geometry:'textbox',name:str.slice(0,45),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});sh.text=str;sh.text.style={typeface:family,fontSize:size,color,bold,autoFit:'none'};return sh;}
const owners=[];
for(let i=0;i<d.length;i++){
 const s=p.slides.items[i],a=d[i];
 text(s,a.title,64,67,826,48,36,'#000000',true);
 text(s,a.subtitle,64,123,826,55,21,'#565656',false);
 if(a.chart){
 const c=a.chart,colors=['#555555','#16877B','#660099','#BC3441'];
 const series=c.series.map((v,j)=>({name:v.name,values:v.y.map(v=>Number(v.toPrecision(10))),...(c.kind==='scatter'?{xValues:v.x.map(v=>Number(v.toPrecision(10)))}:{}),fill:colors[j%4],line:{fill:colors[j%4],width:2.5},marker:{symbol:'none'}}));
 const ch=s.charts.add(c.kind,{position:{left:65,top:181,width:828,height:255},series,...(c.categories?{categories:c.categories}:{}),hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{typeface:family,fontSize:13,fill:'#222222'}},chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF',chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},scatterOptions:{style:'line'},barOptions:{direction:'column',grouping:'clustered'},xAxis:{title:{text:c.xlabel,textStyle:{typeface:family,fontSize:14,fill:'#333333'}},textStyle:{typeface:family,fontSize:12,fill:'#555555'},line:{fill:'#999999',width:1},numberFormatCode:'0.##'},yAxis:{title:{text:c.ylabel,textStyle:{typeface:family,fontSize:14,fill:'#333333'}},textStyle:{typeface:family,fontSize:12,fill:'#555555'},line:{fill:'#999999',width:1},majorGridlines:{fill:'#DDDDDD',width:1},numberFormatCode:'0.##'},dataLabels:{showValue:false}});
 applyPresentationChartFont(ch,{fontFamily:family});owners.push(i+1);
 a.body.forEach((b,j)=>text(s,b,66,446+j*28,828,28,18,j===0?'#57068C':'#444444',j===0));
 }else if(false){
 a.body.forEach((b,j)=>text(s,b,65,283+j*61,826,56,j===0?26:24,j===1?'#57068C':'#333333',j===1));
 text(s,'Roster, affiliations, team photo and team logo to be added',65,487,825,25,15,'#666666');
 }else{
 a.body.forEach((b,j)=>text(s,b,66,196+j*73,825,66,24,j===3?'#555555':'#111111',false));
 }
 text(s,'TEAM 7  •  IDEATION / SIMULATION',64,512,740,16,11,'#666666');
 text(s,`${i+1} / ${d.length}`,846,512,60,16,11,'#666666');
 s.speakerNotes.textFrame.setText(a.notes);
}
const render=path.join(root,'.build/ideation-rendered');await fs.mkdir(render,{recursive:true});
const candidate=path.join(root,'.build/ideation-candidate.pptx');await(await PresentationFile.exportPptx(p)).save(candidate);
for(let i=0;i<d.length;i++){const b=await p.export({slide:p.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(render,`slide-${i+1}.png`),new Uint8Array(await b.arrayBuffer()));}
const finalPath=path.join(root,'presentation/Team_7_Ideation.pptx');
try{await fs.rename(finalPath,path.join(root,'.build/ideation-previous.pptx'));}catch(e){if(e.code!=='ENOENT')throw e;}
try{await fs.rename(path.join(root,'.build/ideation.validation.json'),path.join(root,'.build/ideation.previous-validation.json'));}catch(e){if(e.code!=='ENOENT')throw e;}
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath,pythonExecutable:'/Users/nathanpacey/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','9144000,5143500','--validate-heading-fit'],fontPolicy:{basis:'reference',families:[family],referencePath:template,referenceSha256:createHash('sha256').update(await fs.readFile(template)).digest('hex')},requiredNativeChartOwnerSlides:owners,requiredNativeTableOwnerSlides:[],materializeLiteralChartWorkbooks:true,verifyArtifactToolImport:true,receiptPath:path.join(root,'.build/ideation.validation.json')});console.log(JSON.stringify(result));
