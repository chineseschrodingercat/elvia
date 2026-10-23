import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
const source=await readFile(new URL('../site/workspace.js',import.meta.url),'utf8');
test('Registration without an explicit destination opens contribution choices',()=>{
  const code=source.slice(source.indexOf('function afterLogin('),source.indexOf('function mainPageHref('));
  const ctx={params:new URLSearchParams(),safeWorkspaceNext:()=>'',view:'register',isStaff:()=>false,href:q=>'/contribute.html'+(q?'?'+q:''),location:{href:'https://example.test/?view=register'}};
  assert.equal(vm.runInNewContext(code+';afterLogin()',ctx),'/contribute.html');
});
test('Registration keeps explicit report context',()=>{
  const code=source.slice(source.indexOf('function afterLogin('),source.indexOf('function mainPageHref('));
  const next='/contribute.html?view=compose&case=synthetic';
  assert.equal(vm.runInNewContext(code+';afterLogin()',{params:new URLSearchParams({next}),safeWorkspaceNext:x=>x}),next);
});
test('Pending applicants have clear progress rather than approval-like copy or redundant links',()=>{
  assert.ok(!source.includes('Your work, ready to continue.'));
  assert.ok(!source.includes('View reviewer application'));
  assert.ok(source.includes('applicationProgress('));
});
const progressSource=await readFile(new URL('../site/application-progress.js',import.meta.url),'utf8');
const {applicationProgress}=await import('data:text/javascript;base64,'+Buffer.from(progressSource).toString('base64'));
const fieldSource=await readFile(new URL('../site/profile-fields.js',import.meta.url),'utf8');
const {matchesExpertise}=await import('data:text/javascript;base64,'+Buffer.from(fieldSource).toString('base64'));
function node(tag,attrs={},...children){return {tag,attrs,children:children.flat(Infinity).filter(x=>x!=null),append(...items){this.children.push(...items);}};}
const text=n=>typeof n==='object'?n.children.map(text).join(' '):String(n);
const all=(n,predicate)=>(predicate(n)?[n]:[]).concat(...(n.children||[]).filter(x=>typeof x==='object').map(x=>all(x,predicate)));
const helpers={el:node,p:(s,cls)=>node('p',{class:cls},s),fmt:s=>s,link:(label,href)=>node('a',{href},label),href:q=>'/contribute.html?'+(q||'')};
test('Each stage has one current step and only approval grants a choose-review action',()=>{
  for(const state of ['pending','under_review','approved','needs_information','declined']){
    const result=applicationProgress({status:state,note:'Synthetic note'},helpers);
    const steps=all(result,n=>n.tag==='li');
    assert.equal(steps.length,3);
    assert.equal(steps.filter(x=>x.attrs['aria-current']==='step').length,1);
    assert.equal(all(result,n=>n.tag==='a').some(n=>text(n)==='Choose a review'),state==='approved');
    assert.equal(all(result,n=>n.tag==='a').some(n=>text(n)==='Update application'),['needs_information','declined'].includes(state));
    if(state==='pending'){assert.match(text(result),/1–3 days/);assert.equal(text(steps[2]),'3 Approved Awaiting this stage');}
    if(state==='under_review')assert.match(text(result),/awaiting a decision/);
    if(state==='declined')assert.ok(!text(steps[2]).includes('Approved'));
  }
});
test('Expertise search finds disciplines and methods with case and accent tolerance',()=>{
  assert.equal(matchesExpertise('Microscopy','Research methods','MICRO'),true);
  assert.equal(matchesExpertise('Algebra','Mathematics and statistics','mathematics'),true);
  assert.equal(matchesExpertise('Métrology','Physics','metrology'),true);
  assert.equal(matchesExpertise('Algebra','Mathematics','genetics'),false);
});
test('All public header shells expose Contact and the page uses the existing contact address',async()=>{
  for(const file of ['index.html','contribute.html','project.html','participate.html','privacy.html','terms.html']){
    const html=await readFile(new URL('../site/'+file,import.meta.url),'utf8');
    assert.match(html.split('</header>')[0],/href="\/contact.html"/);
  }
  const contact=await readFile(new URL('../site/contact.html',import.meta.url),'utf8');
  assert.match(contact,/mailto:contact@elvia-atlas.org/);
});
