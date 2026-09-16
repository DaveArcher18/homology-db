/* Production-bundle provenance contract for the computed-only atlas. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
  const base=process.argv[2];
  if(!/^https?:\/\//.test(base||''))throw Error('Provide the HTTP URL of a built sharded site');
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const errors=[];
  try{
    const page=await browser.newPage({viewport:{width:1100,height:900},reducedMotion:'reduce'});
    page.on('pageerror',error=>errors.push(error.message));
    page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
    await page.goto(base);
    const contract=await page.evaluate(async()=>{
      const atlas=await window.HomologyAtlasDataStore.loadAtlas();
      await Promise.all(atlas.conceptual_spaces.map(space=>window.HomologyAtlasDataStore.loadSpace(space)));
      const computedIds=new Set(atlas.computed_rings.space_ids);
      return {
        spaces:atlas.conceptual_spaces.length,
        computedSpaces:computedIds.size,
        withheld:atlas.conceptual_spaces.filter(space=>!computedIds.has(space.id)).map(space=>space.id),
        records:atlas.computed_rings.record_count,
        models:atlas.computed_rings.models.length,
        sources:atlas.computed_rings.sources,
        legacy:atlas.conceptual_spaces.some(space=>space.id==='cayley_plane:2'),
      };
    });
    assert.equal(contract.spaces,194);
    assert.equal(contract.computedSpaces,187);
    assert.equal(contract.withheld.length,7);
    assert.equal(contract.records,1309);
    assert.equal(contract.models,11);
    assert.equal(contract.legacy,false);
    assert.match(contract.sources['cohomology-tables'].title,/cohomology rings/);
    assert.match(contract.sources.oscar.title,/OSCAR/);
    assert.match(contract.sources['lutz-sulanke-swartz-3manifolds'].title,/f-vectors of 3-manifolds/);

    await page.goto(base+'#space=flat-g2');
    const g2=page.getByRole('heading',{name:'Supporting cohomology sources'}).locator('..');
    assert.equal(await g2.getByText('Untitled source',{exact:true}).count(),0);
    for(const title of [
      'cohomology-tables: cohomology rings and cup product tables for simplicial complexes',
      'OSCAR: Open Source Computer Algebra Research system',
      'Frank H. Lutz, The Manifold Page: geometric 3-manifold catalogues',
      'f-vectors of 3-manifolds',
    ])assert.equal(await g2.getByText(title,{exact:false}).count(),1,title);
    assert.equal(await g2.locator('a[href^="https://"]').count(),4);

    await page.goto(base+'#space=torus-2');
    await page.getByText('Technical model and evidence records',{exact:true}).click();
    assert.equal(await page.getByRole('heading',{name:'Simplicial models used for computed rings'}).count(),1);
    assert.equal(await page.getByText('Untitled source',{exact:true}).count(),0);
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({ok:true,...contract,g2Sources:4,errors}));
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
