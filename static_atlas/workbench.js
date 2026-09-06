/* A small, formula-driven workbench. Never expands an entire parameter family. */
(() => {
  "use strict";
  const families = [
    ["real_projective_space", "Real projective spaces · RPⁿ", "\\mathbb{RP}^{n}"],
    ["complex_projective_space", "Complex projective spaces · CPⁿ", "\\mathbb{CP}^{n}"],
    ["sphere", "Spheres · Sⁿ", "S^{n}"],
  ];
  const glossary = [
    ["integers", "Integers", "\\mathbb{Z}", "The ring of whole numbers, positive, negative, and zero. Integral homology retains torsion information that can disappear over a field.", "\\mathbb{Z}/2\\mathbb{Z}"],
    ["rationals", "Rational numbers", "\\mathbb{Q}", "The field of fractions of integers. Every nonzero rational number has a multiplicative inverse. Rational homology records the free part of integral homology.", "1/2"],
    ["finite-fields", "Finite fields", "\\mathbb{F}_{p}", "For a prime p, arithmetic is modulo p. There are p elements. The coefficient field can change both the groups and cup products.", "\\mathbb{F}_{2}=\\mathbb{Z}/2\\mathbb{Z}"],
    ["rings", "Rings and fields", "R", "A ring has addition, subtraction, and multiplication, with distributive laws. Here rings have a unit 1. A field is a commutative ring with 0 ≠ 1 in which each nonzero element has an inverse.", "\\mathbb{Z},\\mathbb{Q},\\mathbb{F}_{p}"],
    ["polynomial", "Polynomial rings", "R[x]", "Polynomials in a formal generator x with coefficients in R. In a graded ring, specifying the degree of x also specifies the degrees of its powers.", "|x^{2}|=2|x|"],
    ["quotients", "Quotient rings", "R[x]/(x^{3})", "Impose the indicated relations on a ring. Here x cubed is zero, so higher powers are zero too; 1, x, and x squared generate the underlying additive module.", "x^{3}=0"],
    ["exterior", "Exterior algebras", "\\Lambda_{R}(a,b)", "An algebra with generators whose squares are zero and whose distinct generators anticommute. These square-zero relations still apply in characteristic two. The symbol Λ here means exterior algebra, not a λ-ring with extra operations.", "a^{2}=b^{2}=0,\\quad ab=-ba"],
    ["generators", "Generators and relations", "R[x]/(x^{3})", "Generators build every element using addition and multiplication. Relations identify expressions or make them zero. Additive generators instead build elements by addition and scalar multiplication alone.", "1,x,x^{2}"],
    ["grading", "Grading", "H^{*}(X;R)", "A grading separates classes by integer degree. Multiplication adds degrees. Cohomology is graded-commutative: exchanging two classes introduces a sign determined by their degrees.", "ab=(-1)^{|a||b|}ba"],
    ["cup-products", "Cup products", "a\\smile b", "The multiplication of cohomology classes. A cup-product table says more than the additive groups: spaces with the same groups can have different rings.", "H^{i}(X;R)\\times H^{j}(X;R)\\to H^{i+j}(X;R)"],
    ["torsion", "Torsion", "\\mathbb{Z}/2\\mathbb{Z}", "A nonzero additive class is torsion when some positive integer multiple is zero. Its order is the smallest such integer. An integral additive generating set with torsion is not a vector-space basis.", "2a=0"],
    ["reduced", "Reduced groups", "\\widetilde{H}_{0}(X;R)", "For these nonempty spaces, reduced homology removes one copy of the coefficient ring in degree zero. Other nonnegative degrees are unchanged. The ring displayed here always uses ordinary unreduced cohomology.", "H_{0}(X;R)"],
  ];
  const e = (tag, cls = "", text) => { const node = document.createElement(tag); node.className = cls; if (text !== undefined) node.textContent = text; return node; };
  const link = (text, href) => { const node = e("a", "", text); node.href = href; return node; };
  function natural(value, fallback = "0") { return /^\d+$/.test(String(value)) ? BigInt(value).toString() : fallback; }
  function route(hash) {
    if (hash === "#glossary" || hash.startsWith("#glossary=")) { try { return {kind:"glossary",term:decodeURIComponent(hash.split("=")[1] || "")}; } catch { return {kind:"glossary",term:""}; } }
    if (!hash.startsWith("#workbench")) return null;
    const p = new URLSearchParams(hash.replace(/^#workbench\??/, ""));
    return {kind:"workbench",family:p.get("family") || "real_projective_space",n:p.get("n") || "4",start:p.get("start") || "0",reduced:p.get("reduced") === "1"};
  }
  function legacy(space) {
    const match = space.id.match(/^(sphere|real_projective_space|complex_projective_space):(\d+)$/);
    return match ? {kind:"workbench",family:match[1],n:match[2],start:"0",legacy:space} : null;
  }
  function hashFor(state) { return "#workbench?" + new URLSearchParams({family:state.family,n:state.n,start:state.start,...(state.reduced ? {reduced:"1"} : {})}); }
  function mathText(host, text, math) {
    String(text).split(/(\$[^$]+\$)/g).forEach(part => host.append(part.startsWith("$") && part.endsWith("$") ? math(part.slice(1,-1),part.slice(1,-1),"math-inline") : document.createTextNode(part)));
  }
  function knowl(id, math, labelTex) {
    const entry = glossary.find(item => item[0] === id);
    const details = e("details", "wb-knowl");
    const summary = e("summary"); summary.append(math(labelTex || entry[2],labelTex || entry[1],"math-inline"));
    const body = e("div", "wb-knowl-body", entry[3]); body.append(" ",math(entry[4],entry[4],"math-inline")," ",link("Read glossary entry →", "#glossary=" + id)); details.append(summary,body); return details;
  }
  function glossaryView({renderTex:math}, state) {
    const view=e("article","route-view glossary-view"); view.append(e("p","page-kicker","A little algebra, close at hand"),e("h1","page-title","Glossary"));
    const label=e("label","wb-field","Find a definition"); const search=e("input");search.type="search";search.placeholder="Try exterior, torsion, or cup product";label.append(search); view.append(label);
    const results=e("div","glossary-results");view.append(results);
    function draw(){results.replaceChildren();glossary.filter(item=>item.join(" ").toLowerCase().includes(search.value.toLowerCase())).forEach(item=>{const card=e("section","glossary-card");card.id="term-"+item[0];const h=e("h2");h.append(link(item[1],"#glossary="+item[0])," ",math(item[2],item[1],"math-inline"));card.append(h,e("p","",item[3]),math(item[4],item[4],"math-display"),e("small","wb-muted","Educational exposition · human review pending. See family sources for evidence supporting results."));results.append(card);}); if(!results.childNodes.length)results.append(e("p","","No matching definition."));}
    search.addEventListener("input",draw);draw();
    if(state.term)requestAnimationFrame(()=>{const target=document.getElementById("term-"+state.term);if(target){target.scrollIntoView();target.tabIndex=-1;target.focus({preventScroll:true});}});
    return view;
  }
  function create(context, input) {
    if(input.kind === "glossary")return glossaryView(context,input);
    const {atlas,renderTex:math}=context;
    if ((input.n !== undefined && !/^\d+$/.test(input.n)) || (input.start !== undefined && !/^\d+$/.test(input.start))) {
      const invalid=e("article","route-view");invalid.append(e("h1","page-title","Invalid family parameters"),e("p","","Dimension n and first degree must be nonnegative decimal integers."),link("Open the workbench","#home"));return invalid;
    }
    const state={family:input.family || "real_projective_space",n:natural(input.n,"4"),start:natural(input.start),reduced:Boolean(input.reduced)};
    const view=e("article","route-view workbench-view");view.dataset.family=state.family;
    const familyEntry=families.find(f=>f[0]===state.family);
    let first;
    try {if(familyEntry)first=window.AtlasFamilies.evaluate(state.family,state.n,"Z",{start:state.start,count:9});}catch(error){view.append(e("h1","page-title","Unable to display this family"),e("p","",String(error.message)));return view;}
    const metadata=atlas.family_rules;const records=Array.isArray(metadata)?metadata:metadata?.rules || [];const record=records.find(r=>r.id===first?.rule_id || r.family===state.family) || {};
    const reviewState=record.human_review_state || "human_review_pending";
    const reviewLabel=reviewState==="human_reviewed"?"Human reviewed":reviewState==="human_concern"?"Human concern recorded":"Human review pending";
    const intro=e("header","wb-intro");
    intro.append(e("p","page-kicker",familyEntry?`${familyEntry[1].split(" · ")[0]} · family workbench`:"Family workbench"));
    const title=e("h1","page-title");
    if(first)title.append(math(first.name_tex,`${familyEntry[1].split(" · ")[0]}, n = ${state.n}`,"math-display"));else title.textContent="Choose a recorded family";
    const titleRow=e("div","wb-title-row");titleRow.append(title,e("span","wb-review-state",reviewLabel));
    intro.append(titleRow);view.append(intro);
    const form=e("form","wb-controls");
    const familyLabel=e("label","wb-field wb-family-field","Family");const picker=e("select");picker.setAttribute("aria-label","Family");picker.id="wb-family";families.forEach(f=>{const option=e("option","",f[1]);option.value=f[0];picker.append(option);});picker.value=state.family;familyLabel.append(picker);
    const nLabel=e("label","wb-field","Dimension parameter n");const n=e("input");n.inputMode="numeric";n.pattern="[0-9]+";n.required=true;n.value=state.n;nLabel.append(n);
    const degreeLabel=e("label","wb-field","First displayed degree");const start=e("input");start.inputMode="numeric";start.pattern="[0-9]+";start.required=true;start.value=state.start;degreeLabel.append(start);
    const submit=e("button","wb-primary","Explore");submit.type="submit";form.append(familyLabel,nLabel,degreeLabel,submit);view.append(form);
    form.addEventListener("submit",event=>{event.preventDefault();if(!form.reportValidity())return;window.location.hash=hashFor({...state,family:picker.value,n:natural(n.value),start:natural(start.value)});});
    view.append(e("p","visually-hidden wb-control-note","Explore applies your choices. All spaces contains the wider catalogue."));
    const utilities=e("div","wb-utilities");
    const copy=e("button","text-button","Copy link");copy.type="button";copy.addEventListener("click",()=>context.copyText(new URL(hashFor(state),location.href).href,copy));utilities.append(copy);
    const reduced=e("label","wb-reduced");const check=e("input");check.type="checkbox";check.checked=state.reduced;check.addEventListener("change",()=>{window.location.hash=hashFor({...state,reduced:check.checked});});reduced.append(check," Reduced homology only");utilities.append(reduced);view.append(utilities);
    if(!families.some(f=>f[0]===state.family)){view.append(e("p","","This family is not recorded. Choose a listed family."));return view;}
    view.append(e("h2","wb-section-title","Compare coefficients"));
    const degreeBar=e("div","wb-degree-bar");degreeBar.append(e("p","wb-muted",`Displaying degrees ${state.start}–${BigInt(state.start)+8n}. The family rules cover all degrees.`));
    [["← Previous degrees",BigInt(state.start)>8n?BigInt(state.start)-9n:0n],["Next degrees →",BigInt(state.start)+9n]].forEach(([text,value])=>degreeBar.append(link(text,hashFor({...state,start:String(value)}))));view.append(degreeBar);
    const fields=e("div","wb-fields");view.append(fields);
    const finiteSection=e("section","wb-finite-section");finiteSection.append(e("h3","wb-section-title","Finite fields"),e("p","wb-muted","Compare the prime coefficients side by side. Scroll horizontally when needed; focus the row and use the arrow keys."));
    const finiteScroll=e("div","wb-finite-scroll");finiteScroll.tabIndex=0;finiteScroll.setAttribute("role","region");finiteScroll.setAttribute("aria-label","Finite-field comparisons, horizontally scrollable");
    const finiteGrid=e("div","wb-finite-grid");finiteScroll.append(finiteGrid);finiteSection.append(finiteScroll);
    const coefficients=["Z","Q","F2","F3","F5","F7","F11"];
    coefficients.forEach(coefficient=>{
      const result=coefficient==="Z"?first:window.AtlasFamilies.evaluate(state.family,state.n,coefficient,{start:state.start,count:9});
      const panel=e("section",`wb-coefficient ${coefficient==="Z"||coefficient==="Q"?"wb-wide":""}`);panel.dataset.coefficient=coefficient;
      const head=e("h3");head.append(knowl(coefficient==="Z"?"integers":coefficient==="Q"?"rationals":"finite-fields",math,result.coefficient_tex));panel.append(head);
      const layout=e("div","wb-panel-layout");const table=e("table","wb-groups");const caption=e("caption","visually-hidden",`Homology and cohomology over ${coefficient}`);const th=e("thead");const tr=e("tr");["Degree",state.reduced?"Reduced Hᵢ":"Hᵢ","Hⁱ"].forEach(label=>{const cell=e("th","",label);cell.scope="col";tr.append(cell);});th.append(tr);const body=e("tbody");
      result.rows.forEach(row=>{const r=e("tr");const degree=e("th","",row.degree);degree.scope="row";r.append(degree);let homology=row.homology.tex;if(state.reduced&&row.degree==="0"){const rank=BigInt(row.homology.free_rank)-1n;const ctex=coefficient==="Z"?"\\mathbb{Z}":coefficient==="Q"?"\\mathbb{Q}":`\\mathbb{F}_{${coefficient.slice(1)}}`;homology=rank===0n?"0":rank===1n?ctex:`${ctex}^{${rank}}`;}
        if(homology!==row.cohomology.tex)r.classList.add("wb-different-groups");
        [homology,row.cohomology.tex].forEach(tex=>{const td=e("td");td.append(math(tex,tex,"group-math"));r.append(td);});body.append(r);});table.append(caption,th,body);layout.append(table);
      const facts=e("div","wb-facts");facts.append(e("h4","","Cohomology ring"),math(result.formulas.ring,result.formulas.ring,"math-display"));
      const rules=e("details","wb-rules");rules.append(e("summary","","All-degree rules (unreduced)"));["homology","cohomology","multiplication"].forEach(key=>rules.append(e("strong","",key==="homology"?"Unreduced homology":key[0].toUpperCase()+key.slice(1)),key==="multiplication"?e("p","",result.formulas[key]):math(result.formulas[key],result.formulas[key],"math-display")));(Array.isArray(result.formulas.notes)?result.formulas.notes:[result.formulas.notes]).filter(Boolean).forEach(note=>rules.append(e("p","",note)));facts.append(rules);
      if(body.querySelector('.wb-different-groups'))facts.append(e("p","wb-difference-note","Shaded rows: the displayed homology and cohomology groups differ."));
      const coverage=e("div","wb-coverage");["homology","cohomology","multiplication"].forEach(key=>{const label=e("p","",`${key[0].toUpperCase()+key.slice(1)}: ${result.coverage[key]?.kind === "complete_all_degrees"?"complete in all degrees":result.coverage[key]?.text || "Not recorded"}`);label.title=result.coverage[key]?.text || "Not recorded";coverage.append(label);});facts.append(coverage);
      const products=e("details","wb-products");products.append(e("summary","","Cup-product table"));const productBody=e("div");products.append(productBody);
      function drawProducts(generatorStart="0"){
        const data=window.AtlasFamilies.evaluate(state.family,state.n,coefficient,{start:state.start,count:9,generatorStart,generatorCount:12});productBody.replaceChildren();
        productBody.append(e("p","wb-muted",data.display.multiplication_complete?"Complete multiplication table.":`Cropped display of ${data.generator_total} additive generators. The general multiplication rule is complete.`));
        if(BigInt(data.generator_total)>12n){const control=e("form","wb-generator-control");const label=e("label","wb-field","First generator index (0-based)");const index=e("input");index.inputMode="numeric";index.pattern="[0-9]+";index.value=data.generator_start;label.append(index);const go=e("button","text-button","Show generators");go.type="submit";control.append(label,go);control.addEventListener("submit",event=>{event.preventDefault();if(control.reportValidity())drawProducts(natural(index.value));});productBody.append(control);}
        const names=e("ul","wb-generator-list");data.generators.forEach(g=>{const li=e("li");li.append(math(g.tex,g.id,"math-inline"),` · degree ${g.degree} · ${g.order?`order ${g.order}`:coefficient==="Z"?"infinite order":"field generator"}`);names.append(li);});productBody.append(names);
        const wrap=e("div","wb-table-scroll");wrap.tabIndex=0;wrap.setAttribute("role","region");wrap.setAttribute("aria-label",`Cup-product table over ${coefficient}`);const t=e("table","wb-multiplication");const h=e("thead");const hr=e("tr");hr.append(e("th","","∪"));data.generators.forEach(g=>{const cell=e("th");cell.scope="col";cell.append(math(g.tex,g.id,"math-inline"));hr.append(cell);});h.append(hr);const b=e("tbody");data.generators.forEach((g,i)=>{const r=e("tr");const title=e("th");title.scope="row";title.append(math(g.tex,g.id,"math-inline"));r.append(title);data.multiplication[i].forEach(tex=>{const cell=e("td");cell.append(math(tex,tex,"math-inline"));r.append(cell);});b.append(r);});t.append(h,b);wrap.append(t);productBody.append(wrap,e("p","wb-muted",data.formulas.multiplication));
      }
      let productsBuilt=false;products.addEventListener("toggle",()=>{if(products.open&&!productsBuilt){drawProducts();productsBuilt=true;}});facts.append(products);layout.append(facts);panel.append(layout);(coefficient.startsWith("F")?finiteGrid:fields).append(panel);
    });
    fields.append(finiteSection);
    const source=e("details","wb-provenance");source.append(e("summary","","Sources, review, and downloads"));
    const digest=record.content_sha256 || record.rule_hash || record.sha256 || metadata?.content_sha256 || "Not recorded";
    source.append(e("p","",`${reviewLabel}. Mathematical completeness is a coverage claim, not a human sign-off. Automated checks and agent review are separate from human review.`));
    const identity=e("details","wb-rule-identity");identity.append(e("summary","","Exact rule identity"),e("p","",`Rule ${first.rule_id} · version ${first.rule_version} · ${digest}`));source.append(identity);
    if(record.derivation) source.append(e("h3","","Derivation"),e("p","",record.derivation));
    (record.human_reviews || []).forEach(review=>source.append(e("p","",`${review.reviewer}: ${review.verdict} · ${review.scope} · ${review.rationale}`),link("Review evidence",review.source_url)));
    const refs=record.sources || metadata?.sources || [];(Array.isArray(refs)?refs:Object.values(refs)).forEach(ref=>{const p=e("p");const url=ref.url || "https://pi.math.cornell.edu/~hatcher/AT/AT.pdf";if(/^https:\/\//.test(url)){const a=link(ref.title || ref.source_id || "Source",url);a.target="_blank";a.rel="noopener noreferrer";p.append(a);}p.append(" "+(ref.locator || ""));source.append(p);});
    const reviewBody=`Family: ${state.family}\nRule: ${first.rule_id}\nVersion: ${first.rule_version}\nRule hash: ${digest}\nScope: all finite n >= 0; all degrees; coefficients Z, Q, F2, F3, F5, F7, F11\nDisplayed n: ${state.n}\nSources: ${JSON.stringify(refs)}\n\nReviewer name:\nVerdict (accept / needs-evidence / reject):\nExact scope reviewed (parameters, degrees, coefficients, groups/products):\nEvidence and corrections:\n\nSubmission is pending maintainer validation, not automatic acceptance.`;
    const review=link("Review this family ↗","https://github.com/DaveArcher18/homology-db/issues/new?"+new URLSearchParams({template:"family-review.yml",title:`Family review: ${first.rule_id} v${first.rule_version}`,"rule-id":first.rule_id,"rule-version":first.rule_version,"rule-hash":digest,scope:`All finite n >= 0; all degrees; Z, Q, F2, F3, F5, F7, F11. Displayed n=${state.n}. State any narrower reviewed scope in your rationale.`,references:(Array.isArray(refs)?refs:Object.values(refs)).map(ref=>`${ref.url} ${ref.locator}`).join("; ").slice(0,650)+"\nView: https://davearcher18.github.io/homology-db/"+hashFor(state)}));review.target="_blank";review.rel="noopener noreferrer";source.append(review,e("p","wb-muted","Requires a GitHub account. Review submissions are public and checked by a maintainer before publication."));
    const download=e("button","text-button","Download family JSON");download.type="button";download.addEventListener("click",()=>{const payload={schema_version:"homology-db.family-view/1",parameters:state,result_convention:"ordinary_unreduced",displayed_homology_convention:state.reduced?"reduced":"unreduced",display_note:"results contains ordinary unreduced groups and rings. If displayed_homology_convention is reduced, the UI subtracts one free summand from homology in degree zero only; cohomology is unchanged.",rule:record,review_history:metadata?.review_history || [],rule_id:first.rule_id,rule_version:first.rule_version,rule_hash:digest,results:coefficients.map(c=>window.AtlasFamilies.evaluate(state.family,state.n,c,{start:state.start,count:9})),snapshot:atlas.snapshot};const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:"application/json"}));const a=link("",url);a.download=`${state.family}-${state.n}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});source.append(download);
    review.textContent="Review this family ↗";download.setAttribute("aria-label","Download family JSON");download.textContent="JSON ↓";
    const quickActions=e("div","wb-reading-actions");quickActions.append(review,download);utilities.insertAdjacentElement("afterend",quickActions);
    const sourceShortcut=e("button","text-button","Sources");sourceShortcut.setAttribute("aria-label","Sources & derivation");sourceShortcut.type="button";sourceShortcut.addEventListener("click",()=>{source.open=true;source.scrollIntoView({block:"start"});source.querySelector("summary").focus({preventScroll:true});});quickActions.prepend(sourceShortcut);
    if(input.legacy){const old=e("button","text-button","Download original space JSON");old.type="button";old.addEventListener("click",()=>context.downloadRecord(input.legacy));source.append(old);}view.append(source);return view;
  }
  window.HomologyWorkbench=Object.freeze({create,route,legacy,mathText});
})();
