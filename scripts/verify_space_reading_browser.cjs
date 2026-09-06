/* Reading UX contract: every retained page, state, coverage and disclosures. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
(async()=>{
  const target=process.argv[2]||'dist/atlas.html';
  const base=/^https?:/.test(target)?target:pathToFileURL(path.resolve(target)).href;
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const errors=[];
  let legacy=0,coefficientViews=0,disclosures=0;
  try{
    const page=await browser.newPage({viewport:{width:1100,height:900},reducedMotion:'reduce',permissions:['clipboard-read','clipboard-write']});
    page.on('pageerror',e=>errors.push(e.message));
    await page.goto(base);
    const spaces=await page.locator('#atlas-data').evaluate(n=>JSON.parse(n.textContent).conceptual_spaces);
    for(const space of spaces){
      await page.goto(base+'#space='+space.slug);
      if(await page.locator('.space-page').count()){
        legacy++;
        assert.match(await page.locator('.space-title-facts').innerText(),/Dimension:[\s\S]*Human review pending/);
        assert.equal(await page.getByRole('button',{name:'Download space JSON',exact:true}).isVisible(),true);
        const choices=await page.locator('.space-coefficients input').evaluateAll(ns=>ns.map(n=>n.value));
        for(const coefficient of choices){
          const previous=await page.locator('.space-coefficients input:checked').inputValue();
          await page.locator(`.space-coefficients input[value="${coefficient}"]`).locator('..').click();
          if(previous!==coefficient)assert.match(page.url(),new RegExp('coefficient='+coefficient));
          const h=page.locator('.homology-section'),c=page.locator('.cohomology-section');
          assert.ok((await h.boundingBox()).y<=(await c.boundingBox()).y);
          const ring=space.cohomology?.find(r=>r.coefficient===coefficient&&r.knowledge_state==='exact');
          if(!ring)assert.match(await c.innerText(),/not recorded.*does not mean it is zero/);
          coefficientViews++;
        }
        await page.locator('.space-coefficients input').first().locator('..').click();
        const extra=page.getByRole('button',{name:'Show all recorded degrees',exact:true});
        if(await extra.count()){
          const rows=page.locator('.homology-section tbody tr');
          const total=await rows.count();
          assert.equal(await page.locator('.homology-section tbody tr:visible').count(),9);
          await extra.click();assert.equal(await page.locator('.homology-section tbody tr:visible').count(),total);
          await page.getByRole('button',{name:'Show first 9 recorded degrees'}).click();
          assert.equal(await page.locator('.homology-section tbody tr:visible').count(),9);
          await page.emulateMedia({media:'print'});
          assert.equal(await page.locator('.homology-section tbody tr:visible').count(),total);
          assert.equal(await page.locator('.degree-display-note').isVisible(),false);
          await page.emulateMedia({media:'screen'});disclosures++;
        }
        assert.equal(await page.locator('.space-page > .space-theory-results').count(),1);
      }else{
        assert.equal(await page.locator('.wb-rules[open]').count(),0);
        assert.equal(await page.locator('.wb-finite-grid > .wb-coefficient').count(),5);
        assert.ok(!(await page.locator('main h1').innerText()).includes('Choose a space'));
      }
      for(const width of [320,390,700,1100]){
        await page.setViewportSize({width,height:900});
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,`${space.slug}/${width}`);
      }
    }
    await page.goto(base+'#space=klein-bottle');
    await page.locator('input[name="coefficient-klein-bottle"][value="F2"]').locator('..').click();
    await page.locator('.space-convention input[value="true"]').locator('..').click();
    await page.getByRole('button',{name:'Copy link',exact:true}).click();
    const copied=await page.evaluate(()=>navigator.clipboard.readText());
    assert.match(copied,/#space=klein-bottle\?coefficient=F2&reduced=1$/);
    await page.reload();
    assert.equal(await page.locator('.space-coefficients input:checked').inputValue(),'F2');
    assert.equal(await page.locator('.space-convention input:checked').inputValue(),'true');
    assert.match(await page.locator('.homology-section tbody th [role="math"]').first().getAttribute('aria-label'),/Reduced homology/);
    await page.goto(base+'#home');await page.goBack();
    assert.equal(await page.locator('.space-convention input:checked').inputValue(),'true');
    await page.goto(base+'#home');
    await page.setViewportSize({width:390,height:900});
    const region=page.getByRole('region',{name:'Finite-field comparisons, horizontally scrollable'});
    await region.focus();await region.press('ArrowRight');
    await page.waitForFunction(()=>document.querySelector('.wb-finite-scroll').scrollLeft>0);
    await page.getByRole('button',{name:'Sources & derivation',exact:true}).click();
    assert.equal(await page.locator('.wb-provenance').getAttribute('open'),'');
    await page.waitForFunction(()=>{const n=document.querySelector('.wb-provenance summary'),h=document.querySelector('.site-header');return document.activeElement===n&&n.getBoundingClientRect().top>=h.getBoundingClientRect().bottom;});
    await page.locator('#theme-menu > summary').click();
    await page.locator('input[name="theme-preference"][value="dark"]').locator('..').click();
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({ok:true,spaces:spaces.length,legacy,coefficientViews,disclosures,widths:[320,390,700,1100],copyReloadHistory:true,keyboardScroll:true,sourceFocus:true,dark:true,errors}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
