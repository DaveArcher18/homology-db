/* Static textbook/review QA; never submits a public review. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
const fs=require('node:fs');
(async()=>{
  const target=process.argv[2]||'dist/atlas.html';
  const base=/^https?:/.test(target)?target:pathToFileURL(path.resolve(target)).href;
  const output=process.argv[3];if(output)fs.mkdirSync(output,{recursive:true});
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const errors=[];
  try{
    const page=await browser.newPage({viewport:{width:1100,height:900},reducedMotion:'reduce',permissions:['clipboard-read','clipboard-write']});
    page.on('pageerror',e=>errors.push(e.message));
    await page.goto(base);
    await page.getByRole('link',{name:'Textbook map & comparisons'}).click();
    await page.locator('.teaching-example').first().waitFor();
    assert.match(page.url(),/#textbook$/);
    assert.equal(await page.locator('.teaching-example').count(),42);
    assert.match(await page.locator('main').innerText(),/not an exhaustive/);
    assert.equal(await page.locator('.teaching-comparison-link').count(),3);
    const atlas=await page.evaluate(()=>window.HomologyAtlasDataStore.loadAtlas());
    async function go(route){
      await page.goto(base+route);
      if(route==='#textbook')await page.locator('.teaching-inventory').waitFor();
      else if(route.startsWith('#comparison='))await page.getByRole('heading',{name:atlas.teaching.comparisons.find(c=>c.id===route.slice(12)).title,exact:true}).waitFor();
      else {
        const space=route.startsWith('#space=')?atlas.conceptual_spaces.find(s=>s.slug===route.slice(7)):null;
        const family=space?.id.match(/^(sphere|real_projective_space|complex_projective_space):(\d+)$/);
        if(space&&!family)await page.locator(`.space-page[data-space-id="${space.id}"]`).waitFor();
        else {const p=new URLSearchParams(route.replace(/^#workbench\?/,''));const f=family?.[1]||p.get('family'),n=family?.[2]||p.get('n');await page.waitForFunction(({f,n})=>document.querySelector('.workbench-view')?.dataset.family===f&&document.querySelectorAll('.wb-controls input')[0]?.value===n,{f,n});}
      }
    }
    assert.equal(atlas.classical.record_count,75);
    await page.getByLabel('Find a textbook example').fill('quaternionic');
    assert.ok(await page.locator('.teaching-example').count()>=2);
    await page.getByLabel('Find a textbook example').fill('no-matching-space-zzzz');
    assert.equal(await page.locator('.teaching-example').count(),0);
    assert.match(await page.locator('.teaching-inventory').innerText(),/No examples match/);
    await page.getByLabel('Find a textbook example').fill('');
    await page.getByLabel('Chapter or topic').selectOption('3.2 / 4.B · Projective planes');
    assert.equal(await page.locator('.teaching-example').count(),3);
    await page.getByLabel('Chapter or topic').selectOption('');
    await page.locator('.teaching-source summary').first().click();
    assert.ok(await page.locator('.teaching-source[open] a[href^="https://"]').count());
    for(const comparison of atlas.teaching.comparisons){
      await go('#textbook');
      await page.getByRole('link',{name:comparison.title,exact:true}).click();
      await page.getByRole('heading',{name:comparison.title,exact:true}).waitFor();
      assert.equal(await page.locator('main h1').innerText(),comparison.title);
      assert.equal(await page.locator('.teaching-steps li').count(),comparison.steps.length);
      assert.equal(await page.locator('main .math-fallback').count(),0);
      const links=await page.locator('.teaching-steps a').evaluateAll(ns=>ns.map(n=>n.getAttribute('href')));
      for(const href of links){await go(href);assert.equal(await page.locator('.not-found').count(),0);assert.equal(await page.locator('.space-page,.workbench-view').count(),1);}
    }
    for(const entry of atlas.teaching.entries){
      await go('#space='+entry.space_slug);
      assert.equal(await page.locator('.space-teaching-note').count(),1,entry.space_id);
      assert.equal(await page.locator('main .math-fallback').count(),0,entry.space_id);
    }
    await go('#workbench?family=real_projective_space&n=2&start=0&reduced=1');
    await page.getByRole('button',{name:'Review this result',exact:true}).click();
    const review=page.locator('.wb-review-panel');
    assert.equal(await review.getAttribute('open'),'');
    assert.match(await review.innerText(),/ordinary unreduced/);
    const focused=await review.locator('summary').boundingBox(),header=await page.locator('.site-header').boundingBox();
    assert.ok(focused.y>=header.y+header.height-1,'review focus under sticky header');
    await review.getByLabel('Last reviewed degree (blank = all above)').fill('2');
    for(const value of ['Z','Q','F3','F5','F7','F11','homology'])await review.locator(`input[type=checkbox][value="${value}"]`).uncheck();
    const formLink=review.locator('.review-scope-form > a');
    const url=new URL(await formLink.getAttribute('href'));
    const scope=JSON.parse(url.searchParams.get('scope'));
    assert.deepEqual(scope,{parameters:{n:{min:'2',max:'2'}},coefficients:['F2'],degrees:{min:'0',max:'2'},components:['cohomology','multiplication']});
    assert.match(url.searchParams.get('rule-hash'),/^[a-f0-9]{64}$/);
    assert.match(url.searchParams.get('references'),/hatcher/);
    await review.getByRole('button',{name:'Copy review packet'}).click();
    const packet=await page.evaluate(()=>navigator.clipboard.readText());
    assert.ok(packet.includes(JSON.stringify(scope)));
    assert.match(packet,/ordinary unreduced/);assert.match(packet,/Not a published review/);
    await review.getByLabel('First reviewed degree').fill('4');
    assert.equal(await review.getByRole('button',{name:/Copy review packet|Copied/}).isDisabled(),true);
    assert.equal(await formLink.getAttribute('href'),null);
    await review.getByLabel('Review scope',{exact:true}).selectOption('whole');
    assert.equal(new URL(await formLink.getAttribute('href')).searchParams.get('scope'),'entire_rule');
    assert.equal(await review.locator('.review-narrow-scope').isVisible(),false);
    const widths=[320,390,640,641,700,768,900,960,961,1024,1440];
    for(const width of widths){
      await page.setViewportSize({width,height:900});
      for(const route of ['#textbook','#comparison=three-projective-planes','#workbench?family=real_projective_space&n=2&start=0']){
        await go(route);if(route.startsWith('#workbench'))await page.getByRole('button',{name:'Review this result',exact:true}).click();
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,`${route}/${width}`);
        if(output&&[390,1100,1440].includes(width))await page.screenshot({path:path.join(output,`${route.slice(1).split(/[=?]/)[0]}-${width}.png`),fullPage:false});
      }
    }
    // Render fixture metadata in this isolated browser only; never publish it.
    await page.evaluate(async()=>{
      const atlas=await window.HomologyAtlasDataStore.loadAtlas();
      const rule=atlas.family_rules.rules.find(r=>r.family==='real_projective_space');
      rule.human_review_state='human_reviewed';rule.scoped_review_state='scoped_human_concern';
      rule.scoped_human_reviews=[{reviewer:'Fixture reviewer',verdict:'reject',scope:{parameters:{n:{min:'2',max:'2'}},coefficients:['F2'],degrees:{min:'0',max:'2'},components:['cohomology']},rationale:'Fixture concern',source_url:'https://github.com/DaveArcher18/homology-db/issues/1'}];
      const context={atlas,renderTex:tex=>{const s=document.createElement('span');s.textContent=tex;return s;},copyText:()=>{}};
      document.querySelector('main').replaceChildren(window.HomologyWorkbench.create(context,{family:'real_projective_space',n:'99',start:'0'}));
    });
    assert.match(await page.locator('.wb-title-row').innerText(),/Human reviewed[\s\S]*Concern recorded in a narrower scope/);
    await page.locator('.wb-provenance > summary').click();
    assert.match(await page.locator('.wb-scoped-reviews').innerText(),/n 2–2/);
    assert.match(await page.locator('.wb-scoped-reviews').innerText(),/not the entire family/);
    const fixture=structuredClone(atlas);
    const fixtureRule=fixture.family_rules.rules.find(r=>r.family==='real_projective_space');
    fixtureRule.human_review_state='human_reviewed';fixtureRule.scoped_review_state='scoped_human_concern';
    fixtureRule.scoped_human_reviews=[{scope,verdict:'reject',reviewer:'Fixture reviewer',rationale:'Fixture concern'}];
    const html=/^https?:/.test(target)?await (await fetch(base)).text():fs.readFileSync(target,'utf8');
    const fixtureHtml=html.replace(/(<script\b[^>]*id="atlas-data"[^>]*>)[\s\S]*?(<\/script>)/,(_,open,close)=>open+JSON.stringify(fixture)+close);
    assert.notEqual(fixtureHtml,html);
    const about=await browser.newPage();about.on('pageerror',e=>errors.push(e.message));
    await about.route('https://atlas-qa.invalid/**',route=>route.fulfill({contentType:'text/html',body:fixtureHtml}));
    await about.goto('https://atlas-qa.invalid/#about');
    assert.match(await about.locator('.about-review-list').innerText(),/Human reviewed · Concern recorded in a narrower scope/);
    assert.match(await about.locator('.about-view').innerText(),/Review this result/);
    await about.getByRole('link',{name:'— inspect exact review scopes'}).click();
    await about.locator('.workbench-view').waitFor();
    assert.match(await about.locator('.wb-title-row').innerText(),/Concern recorded in a narrower scope/);
    await about.close();
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({ok:true,inventory:42,comparisons:3,recordCount:75,widths,scopedPacket:true,invalidScope:true,partialConcernFixture:true,errors}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
