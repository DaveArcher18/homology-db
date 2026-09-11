/* Interaction-first regression for family discovery, About and split windows. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
const widths=[320,390,640,641,700,768,900,960,961,1024,1440];

async function verifyZoom(base){
  // Real Chrome page zoom in a disposable profile, not CSS zoom or pinch scale.
  const context=await chromium.launchPersistentContext('',{channel:'chrome',headless:true,viewport:{width:1280,height:900}});
  const results=[];
  try{
    const settings=context.pages()[0],page=await context.newPage();
    await settings.goto('chrome://settings/appearance');
    for(const zoom of ['1.25','2']){
      await settings.locator('#zoomLevel').selectOption(zoom);
      await page.goto(base+'#home');
      await page.getByRole('combobox',{name:'Family',exact:true}).waitFor();
      const metrics=await page.evaluate(()=>({width:innerWidth,ratio:devicePixelRatio}));
      assert.ok(Math.abs(metrics.width-1280/Number(zoom))<2,'Chrome must actually apply page zoom');
      for(const route of ['workbench','about']){
        if(route==='about')await page.locator('#nav-about').click();
        assert.deepEqual(await page.evaluate(()=>{
          const nodes=[...document.querySelectorAll('.primary-nav a,.wb-controls input,.wb-controls select,.wb-primary')];
          return nodes.filter(n=>{const r=n.getBoundingClientRect();return r.left<0||r.right>innerWidth+1||!r.width||!r.height||getComputedStyle(n).visibility!=='visible';}).map(n=>n.textContent);
        }),[],`zoom ${zoom} ${route}`);
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
      }
      await page.locator('#nav-home').click();
      await page.getByRole('combobox',{name:'Family',exact:true}).waitFor();
      results.push({zoom:Number(zoom),...metrics});
    }
  }finally{await context.close();}
  return results;
}

async function main(){
  const target=process.argv[2]||'dist/atlas.html';
  const base=/^https?:/.test(target)?target:pathToFileURL(path.resolve(target)).href;
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const errors=[];
  let choices=0;
  try{
    const page=await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'reduce'});
    page.on('pageerror',e=>errors.push(e.message));
    page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
    async function layout(){
      const problems=await page.evaluate(()=>{
        const issues=[];
        if(document.documentElement.scrollWidth>innerWidth+1)issues.push('document overflow');
        document.querySelectorAll('.primary-nav a,.wb-controls input,.wb-controls select,.wb-primary').forEach(n=>{
          const r=n.getBoundingClientRect(),s=getComputedStyle(n);
          if(s.visibility!=='visible'||s.display==='none'||!r.width||!r.height)issues.push('hidden '+n.textContent);
          if(r.left < -1||r.right>innerWidth+1)issues.push('clipped '+n.textContent);
          if(n.matches('.primary-nav a') && n.scrollWidth>n.clientWidth+1)issues.push('overflowing navigation label '+n.textContent);
        });
        const main=document.querySelector('#atlas-document');
        if(main.getBoundingClientRect().top>250)issues.push('blank spacer before main');
        if(document.querySelector('[inert],#index-backdrop'))issues.push('obsolete drawer state');
        return issues;
      });
      assert.deepEqual(problems,[],`${page.viewportSize().width}px ${page.url()}`);
    }
    for(const width of widths){
      await page.setViewportSize({width,height:900});
      await page.goto(base+'#home');
      await page.getByRole('combobox',{name:'Family',exact:true}).waitFor();
      assert.deepEqual(await page.locator('#wb-family option').evaluateAll(ns=>ns.map(n=>n.value)),['real_projective_space','complex_projective_space','sphere']);
      await layout();
      for(const family of ['complex_projective_space','sphere','real_projective_space']){
        const beforeExplore=page.url();
        await page.getByRole('combobox',{name:'Family',exact:true}).selectOption(family);
        await page.getByLabel('Dimension parameter n').fill('7');
        await page.getByLabel('First displayed degree').fill('5');
        assert.equal(page.url(),beforeExplore,'Picker changes apply only with Explore');
        await page.getByRole('button',{name:'Explore',exact:true}).click();
        await page.waitForFunction(f=>document.querySelector('.workbench-view')?.dataset.family===f,family);
        assert.equal(await page.getByLabel('Dimension parameter n').inputValue(),'7');
        assert.equal(await page.getByLabel('First displayed degree').inputValue(),'5');
        choices++;
      }
      const saved=page.url();
      await page.locator('#nav-about').click();
      await page.locator('.about-view').waitFor();
      await page.waitForFunction(()=>document.activeElement===document.querySelector('.about-view h1'));
      assert.equal(await page.locator('#nav-about').getAttribute('aria-current'),'page');
      assert.match(await page.locator('.about-view').innerText(),/human review pending/i);
      await layout();
      await page.reload();
      await page.locator('.about-view').waitFor();
      await layout();
      assert.equal(await page.locator('.about-view').getByRole('link',{name:/Request a space/}).isVisible(),true);
      await page.locator('#nav-home').click();
      await page.getByRole('combobox',{name:'Family',exact:true}).waitFor();
      assert.equal(page.url(),saved,'About reload must preserve the workbench return destination');
      await page.locator('#nav-about').click();
      await page.locator('.about-view').waitFor();
      await page.goBack();
      await page.getByRole('combobox',{name:'Family',exact:true}).waitFor();
      assert.equal(page.url(),saved);
      assert.equal(await page.getByLabel('Dimension parameter n').inputValue(),'7');
      await page.goForward();
      await page.locator('.about-view').waitFor();
      await page.locator('#nav-home').click();
      await page.getByRole('combobox',{name:'Family',exact:true}).waitFor();
      assert.equal(page.url(),saved);
      await page.locator('#nav-glossary').click();
      await page.locator('.glossary-view').waitFor();
      assert.equal(await page.locator('#nav-glossary').getAttribute('aria-current'),'page');
      await page.locator('#nav-spaces').click();
      await page.locator('.spaces-view').waitFor();
      assert.equal(await page.locator('#nav-spaces').getAttribute('aria-current'),'page');
    }
    await page.goto(base+'#home');
    const picker=page.getByRole('combobox',{name:'Family',exact:true});
    await picker.focus();
    await picker.press('c');
    await picker.press('Tab');
    assert.equal(await picker.inputValue(),'complex_projective_space');
    for(const [key,family] of [['s','sphere'],['r','real_projective_space'],['c','complex_projective_space']]){
      await picker.focus();await picker.press(key);await picker.press('Tab');
      assert.equal(await picker.inputValue(),family);
    }
    await page.getByLabel('Dimension parameter n').fill('12');
    await page.getByLabel('First displayed degree').fill('18');
    await page.getByLabel('First displayed degree').press('Enter');
    await page.waitForURL(/family=complex_projective_space.*n=12.*start=18/);
    await page.reload();
    assert.equal(await page.getByLabel('Dimension parameter n').inputValue(),'12');
    await page.locator('#nav-about').click();
    for(const width of widths){await page.setViewportSize({width,height:900});await layout();}
    await page.screenshot({path:'/tmp/homology-navigation-about.png'});
    await page.locator('#nav-home').click();
    await page.screenshot({path:'/tmp/homology-navigation-workbench.png'});
    const failurePage=await browser.newPage({viewport:{width:390,height:900},reducedMotion:'reduce'});
    await failurePage.route('**/data/spaces/klein-bottle.json*',route=>route.abort());
    await failurePage.goto(base+'?failure-fixture=1#space=klein-bottle');
    await failurePage.locator('.loading-view,.load-error-view').first().waitFor();
    await failurePage.locator('.load-error-view').waitFor();
    assert.match(await failurePage.locator('main').innerText(),/could not be loaded[\s\S]*must not|could not be loaded[\s\S]*not.*zero/i);
    assert.equal(await failurePage.getByRole('button',{name:'Retry',exact:true}).isVisible(),true);
    assert.equal(await failurePage.getByRole('link',{name:'Return to all spaces',exact:true}).isVisible(),true);
    await failurePage.close();
    assert.deepEqual(errors,[]);
    const zoom=await verifyZoom(base);
    console.log(JSON.stringify({ok:true,widths,pickerSelections:choices,keyboard:true,aboutHistoryReloadResize:true,failureState:true,zoom,errors}));
  }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
