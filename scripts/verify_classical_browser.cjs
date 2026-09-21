/* Classical ring coverage in the shared recorded-space page. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const path=require('node:path');

(async()=>{
  const target=process.argv[2]||'dist/atlas.html';
  const base=/^https?:/.test(target)?target:pathToFileURL(path.resolve(target)).href;
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const errors=[];
  try {
    const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
    page.on('pageerror',error=>errors.push(error.message));
    page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
    await page.goto(base);
    const atlas=await page.locator('#atlas-data').evaluate(node=>JSON.parse(node.textContent));
    const classicalIds=new Set(atlas.classical.space_ids);
    const core=atlas.conceptual_spaces.filter(space=>classicalIds.has(space.id));
    assert.equal(core.length,13);
    let fieldViews=0;
    for(const space of core){
      await page.goto(`${base}#space=${space.slug}`);
      await page.locator('.canonical-space-page').waitFor();
      for(const coefficient of atlas.classical.coefficients){
        await page.locator('.canonical-select').first().selectOption(coefficient);
        const record=space.cohomology.find(item=>item.coefficient===coefficient);
        assert.ok(record,`${space.id}/${coefficient}`);
        assert.equal(await page.locator('.canonical-theory-table').last().locator('tbody tr').count(),record.groups.length);
        assert.equal(await page.locator('.canonical-theory-table').last().getByText('Not recorded').count(),0);
        fieldViews++;
      }
      await page.locator('.canonical-select').first().selectOption('Z');
      if(!space.cohomology.some(item=>item.coefficient==='Z'))
        assert.match(await page.locator('.canonical-theory-table').last().innerText(),/Not recorded/);
      assert.ok(await page.locator('.canonical-theory-table').first().locator('tbody tr').count()>0);
    }
    for(const width of [1440,390,320]){
      await page.setViewportSize({width,height:900});
      for(const hash of ['#home','#spaces','#space=complex-projective-space-2','#space=sphere-0','#space=klein-bottle']){
        await page.goto(base+hash);
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,`${width}px ${hash}`);
      }
    }
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({ok:true,classicalSpaces:core.length,fieldViews,responsiveCases:15,errors}));
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
