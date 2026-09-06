/* Screenshot every retained space; read-only audit of an exact static artifact. */
const {chromium}=require('playwright');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
(async()=>{
  const target=process.argv[2]||'dist/atlas.html',out=process.argv[3];
  if(!out)throw Error('Provide an existing audit output directory');
  const base=/^https?:/.test(target)?target:pathToFileURL(path.resolve(target)).href;
  const browser=await chromium.launch({channel:'chrome',headless:true});
  try{
    const page=await browser.newPage({viewport:{width:1100,height:1000},reducedMotion:'reduce'});
    await page.goto(base);
    const spaces=await page.locator('#atlas-data').evaluate(n=>JSON.parse(n.textContent).conceptual_spaces);
    const records=[];
    for(const [index,space] of spaces.entries()){
      await page.goto(base+'#space='+space.slug);
      await page.locator('.space-page,.workbench-view').waitFor();
      const record={index,slug:space.slug,name:space.name.plain};
      for(const width of [1100,390]){
        await page.setViewportSize({width,height:1000});
        record[width]=await page.evaluate(()=>({height:document.documentElement.scrollHeight,overflow:document.documentElement.scrollWidth>innerWidth+1,headings:[...document.querySelectorAll('main h1,main h2,main h3')].map(n=>({text:n.textContent,top:Math.round(n.getBoundingClientRect().top+scrollY)})),text:document.querySelector('main').innerText}));
        await page.screenshot({path:path.join(out,`${index}-${width}.png`)});
      }
      records.push(record);
    }
    fs.writeFileSync(path.join(out,'audit.json'),JSON.stringify(records,null,2));
    const sheet=await browser.newPage({viewport:{width:1100,height:1680}});
    for(let start=0;start<records.length;start+=6){
      const tiles=records.slice(start,start+6).map(r=>`<section><b>${r.index+1}. ${r.name}</b><img src="data:image/png;base64,${fs.readFileSync(path.join(out,`${r.index}-1100.png`)).toString('base64')}"></section>`).join('');
      await sheet.setContent(`<style>body{margin:0;font:16px sans-serif;display:grid;grid-template-columns:1fr 1fr;gap:10px;background:#bbb}section{min-width:0;background:white}b{display:block;padding:8px}img{width:100%;display:block}</style>${tiles}`);
      await sheet.screenshot({path:path.join(out,`sheet-${start/6}.png`),fullPage:true});
    }
    console.log(JSON.stringify(records.map(r=>({slug:r.slug,desktopHeight:r[1100].height,mobileHeight:r[390].height,overflow:r[390].overflow})),null,2));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
