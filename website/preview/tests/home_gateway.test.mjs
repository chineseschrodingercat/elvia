import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

const source=await readFile(new URL('../site/workspace.js',import.meta.url),'utf8');
const shell=await readFile(new URL('../site/contribute.html',import.meta.url),'utf8');
const routingStart=source.indexOf('function safeWorkspaceNext(');
const routingEnd=source.indexOf('const itemLink');

function routingContext(search='',pathname='/contribute.html') {
  assert.ok(routingStart>=0,'A shared safe homepage-auth route is required.');
  const location={origin:'http://127.0.0.1:8797',pathname,search,hash:'',href:'http://127.0.0.1:8797'+pathname+search,replace(value){this.replaced=value;}};
  const context={URL,URLSearchParams,params:new URLSearchParams(search),location,isHomeAccount:pathname==='/',view:new URLSearchParams(search).get('view')||'home',caseRoute:null,addCaseContext:query=>query};
  vm.createContext(context);
  vm.runInContext(source.slice(routingStart,routingEnd)+'\nthis.routes={safeWorkspaceNext,authHref,redirectLegacyAuth,href};',context);
  return context;
}

test('Return links preserve only the exact same-origin contribution workspace',()=>{
  const {routes}=routingContext();
  for(const value of ['/contribute.html?review=example#section-2','http://127.0.0.1:8797/contribute.html?view=my-work'])assert.ok(routes.safeWorkspaceNext(value).startsWith('/contribute.html'));
  for(const value of ['',null,'https://other.example/contribute.html','//other.example/contribute.html','/other/contribute.html','/contribute.html/','javascript:alert(1)','/contribute.html?view=login','/contribute.html?view=register'])assert.equal(routes.safeWorkspaceNext(value),'',String(value));
});

test('Every generated auth entry uses the homepage and keeps a safe return link',()=>{
  const {routes}=routingContext('?review=example');
  for(const mode of ['login','register']) {
    const url=new URL(routes.href('view='+mode),'http://127.0.0.1:8797');
    assert.equal(url.pathname,'/');assert.equal(url.searchParams.get('view'),mode);assert.equal(url.hash,'#contributor-access');
    assert.equal(url.searchParams.get('next'),'/contribute.html?review=example');
  }
  const bad=new URL(routes.authHref('login',{next:'https://other.example/contribute.html'}),'http://127.0.0.1:8797');
  assert.equal(bad.searchParams.has('next'),false);
});

test('Old login and register bookmarks redirect before off-home forms can render',()=>{
  for(const mode of ['login','register']) {
    const context=routingContext('?view='+mode+'&maintainer=1&next='+encodeURIComponent('/contribute.html?review=example'));
    assert.equal(context.routes.redirectLegacyAuth(),true);
    const url=new URL(context.location.replaced,'http://127.0.0.1:8797');
    assert.equal(url.pathname,'/');assert.equal(url.searchParams.get('view'),mode);assert.equal(url.hash,'#contributor-access');
    assert.equal(url.searchParams.get('next'),'/contribute.html?review=example');
  }
  assert.equal(routingContext('?view=login','/').routes.redirectLegacyAuth(),false);
  assert.equal(routingContext('?view=my-work').routes.redirectLegacyAuth(),false);
});

test('Guest and signed-in workspace navigation has no sign-in or registration entry',()=>{
  const nav=source.slice(source.indexOf('function nav()'),source.indexOf('function loginPage('));
  for(const role of [null,'contributor','admin','maintainer']) {
    let rendered;
    vm.runInNewContext(nav+'\nnav();',{
      session:{user:role?{role}:null},isStaff:()=>['admin','maintainer'].includes(role),
      href:query=>'/contribute.html'+(query?'?'+query:''),link:(text,href)=>({text,href}),
      document:{querySelector:()=>({replaceChildren(...items){rendered=items;}})},
    });
    assert.ok(rendered.some(item=>item.text==='Home'&&item.href==='/'));
    assert.ok(rendered.some(item=>item.text==='Atlas'&&item.href==='/atlas/'));
    assert.ok(!rendered.some(item=>/sign in|register/i.test(item.text)));
  }
});

test('An unauthenticated edit route renders the visitor gate, never an inline login form',()=>{
  const gate=source.match(/function gate\(\) \{[\s\S]*?\n\}/)?.[0];
  let rendered=false;
  const context={session:{user:null},guestReadOnlyPage(){rendered=true;},loginPage(){assert.fail('A guest edit route must not render a login form off the homepage.');}};
  assert.equal(vm.runInNewContext(gate+'\ngate();',context),true);
  assert.equal(rendered,true);
  context.session.user={role:'contributor'};rendered=false;
  assert.equal(vm.runInNewContext(gate+'\ngate();',context),false);assert.equal(rendered,false);
});

test('The auth renderer itself refuses to display forms outside the homepage',()=>{
  const login=source.slice(source.indexOf('function loginPage('),source.indexOf('function policyAcknowledgement('));
  let gated=false;
  vm.runInNewContext(login+'\nloginPage();',{isHomeAccount:false,guestReadOnlyPage(){gated=true;}});
  assert.equal(gated,true);
});

test('Fallback workspace shell only offers a homepage visitor link',()=>{
  assert.ok(shell.includes('data-visitor-notice'));
  assert.ok(shell.includes('visitor-access.js'));
  assert.ok(shell.includes('Back to main page'));
  for(const [,href] of shell.matchAll(/<a\b[^>]*href="([^"]+)"/g))assert.ok(!/[?&](view=login|view=register|maintainer=1)/.test(href),href);
});

test('Public task details stop before any guest claim or revision controls',()=>{
  const task=source.slice(source.indexOf('async function taskPage('),source.indexOf('function myWorkPage('));
  const guard=task.indexOf('if(!session.user)');
  assert.ok(guard>=0);
  for(const label of ['Continue your review','Review or revise the current work','Claim this review'])assert.ok(guard<task.indexOf(label));
  assert.ok(source.includes("if(isHomeAccount){homeAccountPage();}"));
});
