import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
process.chdir(path.dirname(root));
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const page=await browser.newPage({viewport:{width:1280,height:720}});let errors=[];page.on('pageerror',e=>errors.push(String(e)));
await page.goto(pathToFileURL(path.join(root,'presentation/Presentation.html')).href);
await fs.mkdir(path.join(root,'.build/html-rendered'),{recursive:true});
const slideCount=await page.locator(".slide").count();
let overflows=[];
for(let i=0;i<slideCount;i++){await page.evaluate(i=>show(i),i);await page.screenshot({path:path.join(root,`.build/html-rendered/slide-${i+1}.png`)});let bad=await page.evaluate(()=>[...document.querySelector('.slide.active').querySelectorAll('header,.body,.chart')].map(e=>({tag:e.className||e.tagName,bottom:e.getBoundingClientRect().bottom})).filter(e=>e.bottom>675));if(bad.length)overflows.push({slide:i+1,bad});}
await page.evaluate(()=>show(0));await page.keyboard.press('ArrowRight');let nav=await page.evaluate(()=>document.querySelector('.slide.active').id);await page.keyboard.press('n');let notes=await page.evaluate(()=>getComputedStyle(document.querySelector('.slide.active .notes')).display);await page.keyboard.press('n');
await page.pdf({path:path.join(root,'presentation/Continuous_Water_Sensing.pdf'),preferCSSPageSize:true,printBackground:true});
const report={errors,overflows,keyboard_navigation:nav==='s2',notes_toggle:notes==='block',slides:slideCount};await fs.writeFile(path.join(root,'.build/html-validation.json'),JSON.stringify(report,null,2));console.log(report);await browser.close();if(errors.length||overflows.length||!report.keyboard_navigation||!report.notes_toggle)process.exitCode=1;
