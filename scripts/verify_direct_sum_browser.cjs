/* Direct-sum script rendering regression, including the reported K3 case. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const path=require('node:path');

(async()=>{
  const target=process.argv[2]||'dist/atlas.html';
  const base=/^https?:/.test(target)?target:pathToFileURL(path.resolve(target)).href;
  const output=process.argv[3]||'/tmp';
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const errors=[];
  const checked=[];
  try {
    for(const width of [1440,390]){
      const page=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});
      page.on('pageerror',error=>errors.push(error.message));
      page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
      await page.goto(base);
      const slug=await page.evaluate(async()=>{
        const atlas=await window.HomologyAtlasDataStore.loadAtlas();
        return atlas.conceptual_spaces.find(space=>space.id==='four_manifold:k3').slug;
      });
      for(const coefficient of ['F2','F3','F5','F7','F11','Z']){
        await page.goto(`${base}#space=${slug}?coefficient=${coefficient}`);
        await page.locator('.space-page[data-space-id="four_manifold:k3"]').waitFor();
        const expected=coefficient==='Z'
          ? String.raw`\mathbb{Z}^{\oplus 22}`
          : String.raw`\mathbb{F}_{${coefficient.slice(1)}}^{\oplus 22}`;
        const expression=page.locator(`[data-tex="${expected.replaceAll('\\','\\\\')}"]`).first();
        assert.equal(await expression.count(),1,`${coefficient} dimension 22 expression`);
        const script=expression.locator('sup');
        assert.equal(await script.textContent(),'⊕ 22');
        const layout=await script.evaluate(node=>({
          display:getComputedStyle(node).display,
          whiteSpace:getComputedStyle(node).whiteSpace,
          rects:[...node.getClientRects()].map(rect=>({width:rect.width,height:rect.height})),
        }));
        assert.equal(layout.display,'inline-block');
        assert.equal(layout.whiteSpace,'nowrap');
        assert.equal(layout.rects.length,1);
        assert.ok(layout.rects[0].width>0&&layout.rects[0].height>0);
        checked.push({width,coefficient,tex:expected});
      }

      const torsion=await page.evaluate(()=>{
        const host=document.createElement('div');
        host.style.width='7rem';
        host.append(window.HomologyAtlasMath.renderTex(
          String.raw`(\mathbb{Z}/2\mathbb{Z})^{\oplus 168}`,
          '168 copies of the integers modulo 2',
          'group-math',
        ));
        document.body.append(host);
        const sup=host.querySelector('sup');
        const result={
          text:sup.textContent,
          display:getComputedStyle(sup).display,
          whiteSpace:getComputedStyle(sup).whiteSpace,
          rects:[...sup.getClientRects()].length,
        };
        host.remove();
        return result;
      });
      assert.deepEqual(torsion,{text:'⊕ 168',display:'inline-block',whiteSpace:'nowrap',rects:1});

      await page.goto(`${base}#space=${slug}?coefficient=F7`);
      await page.locator('.space-page').waitFor();
      await page.screenshot({
        path:path.join(output,`homology-atlas-k3-f7-${width}.png`),
        fullPage:true,
        animations:'disabled',
      });
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
      await page.close();
    }
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({ok:true,checked,torsion:true,widths:[1440,390],errors},null,2));
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
