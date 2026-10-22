import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

const source=await readFile(new URL('../site/workspace.js',import.meta.url),'utf8');
const loader=await readFile(new URL('../site/home-entry.js',import.meta.url),'utf8');
const token='synthetic_reset_token_for_browser_tests_123456789';
function element(tag,attrs={},...children){
  return {tag,attrs,children,listeners:{},value:attrs.value||'',dataset:{},
    append(...items){this.children.push(...items);},
    replaceChildren(...items){this.children=items;},
    addEventListener(name,fn){this.listeners[name]=fn;},
    reset(){for(const control of descendants(this))if(control.tag==='input')control.value='';},
    querySelector(selector){return descendants(this).find(node=>selector.startsWith('[name=')
      ?node.attrs?.name===selector.slice(6,-1):node.tag===selector)||null;},
    setAttribute(name,value){this.attrs[name]=value;}};
}
function descendants(node){return (node.children||[]).flat(Infinity).flatMap(child=>
  child&&typeof child==='object'?[child,...descendants(child)]:[]);}
function renderContext(search='?view=login',home=true){
  const calls={api:[],feedback:[],titles:[],pending:[],navigations:[],gates:0};
  const main=element('main');
  const visitorNotice={hidden:true},guestActions={hidden:true},memberActions={hidden:false};
  const state={calls,main,isHomeAccount:home,params:new URLSearchParams(search),
    visitorNotice,guestActions,memberActions,
    document:{querySelectorAll:()=>[visitorNotice],getElementById:id=>id==='contributor-guest-actions'?guestActions:memberActions},
    passwordResetToken:token,session:{user:null,email_registration:{enabled:true,research_domains:[]}},
    el:element,p:(text,cls)=>element('p',{class:cls},text),
    button:(text,fn)=>element('button',{type:'button'},text),
    link:(text,href,cls)=>element('a',{href,class:cls},text),
    field:(name,label,type='text',value='',hint='',required=false)=>element('field',{},element('input',{name,type,value,required})),
    title:(text,description)=>{calls.titles.push(text);main.append(element('h2',{},text),description||'');},
    href:query=>'/?'+query+'#contributor-access',authHref:mode=>'/?view='+mode+'#contributor-access',
    formData:form=>Object.fromEntries(descendants(form).filter(node=>node.tag==='input').map(node=>[node.attrs.name,node.value])),
    act:fn=>{const pending=fn();calls.pending.push(pending);return pending;},
    api:async(...args)=>{calls.api.push(args);return {reset:true};},
    feedback:(...args)=>calls.feedback.push(args),navigate:url=>calls.navigations.push(url),
    guestReadOnlyPage:()=>{calls.gates++;},policyAcknowledgement:()=>element('policy'),
    googleSignIn:()=>element('google-signin')};
  vm.createContext(state);
  const guidanceStart=source.indexOf('function mailDeliveryGuidance(');
  const guidanceEnd=source.indexOf('function feedback(',guidanceStart);
  assert.ok(guidanceStart>=0&&guidanceEnd>guidanceStart);
  vm.runInContext(source.slice(guidanceStart,guidanceEnd),state);
  const start=source.indexOf('function loginPage(');
  const end=source.indexOf('function policyAcknowledgement(');
  assert.ok(start>=0&&end>start);
  vm.runInContext(source.slice(start,end),state);
  return state;
}

test('Forgot password link appears only on the homepage sign-in form',()=>{
  for(const [home,register,expected] of [[true,false,1],[true,true,0],[false,false,0]]){
    const state=renderContext('?view=login',home);
    vm.runInContext('loginPage('+register+');',state);
    const links=descendants(state.main).filter(node=>node.tag==='a'&&node.children.includes('Forgot your password?'));
    assert.equal(links.length,expected);
    if(expected)assert.equal(new URL(links[0].attrs.href,'http://127.0.0.1:8797').pathname,'/');
  }
});

test('Both recovery renderers refuse forms outside the homepage',()=>{
  for(const name of ['requestPasswordResetPage','completePasswordResetPage']){
    const state=renderContext('',false);
    assert.equal(typeof state[name],'function',name+' exists');
    vm.runInContext(name+'();',state);
    assert.equal(state.calls.gates,1);
    assert.equal(descendants(state.main).filter(node=>node.tag==='form').length,0);
  }
});

test('Recovery request uses the same-origin endpoint and always presents generic confirmation',async()=>{
  const state=renderContext('?view=forgot-password');
  assert.equal(typeof state.requestPasswordResetPage,'function');
  vm.runInContext('requestPasswordResetPage();',state);
  const form=descendants(state.main).find(node=>node.tag==='form');
  form.querySelector('[name=email]').value='synthetic@example.edu';
  form.listeners.submit({preventDefault(){}});
  await Promise.all(state.calls.pending);
  assert.equal(JSON.stringify(state.calls.api),JSON.stringify([
    ['/auth/password-reset/request','POST',{email:'synthetic@example.edu'}]]));
  assert.match(JSON.stringify(state.calls.feedback),/If an eligible account exists/);
  assert.ok(!JSON.stringify(state.main).includes('synthetic@example.edu'));
});

test('Reset completion keeps token out of the form and clears memory/passwords after success',async()=>{
  const state=renderContext('?view=reset-password');
  state.session.user={role:'maintainer'};state.session.csrf='synthetic csrf';
  assert.equal(typeof state.completePasswordResetPage,'function');
  vm.runInContext('completePasswordResetPage();',state);
  assert.ok(!JSON.stringify(state.main).includes(token));
  const form=descendants(state.main).find(node=>node.tag==='form');
  form.querySelector('[name=newpassword]').value='Synthetic new password 42!';
  form.querySelector('[name=confirm_password]').value='Synthetic new password 42!';
  form.listeners.submit({preventDefault(){}});
  await Promise.all(state.calls.pending);
  assert.equal(JSON.stringify(state.calls.api),JSON.stringify([
    ['/auth/password-reset/complete','POST',{token,newpassword:'Synthetic new password 42!'}]]));
  assert.equal(state.passwordResetToken,'');
  assert.equal(state.session.user,null);assert.equal(state.session.csrf,'');
  assert.equal(state.visitorNotice.hidden,false);
  assert.equal(state.guestActions.hidden,false);assert.equal(state.memberActions.hidden,true);
  assert.equal(form.querySelector('[name=newpassword]').value,'');
  assert.equal(form.querySelector('[name=confirm_password]').value,'');
  assert.ok(!JSON.stringify(state.main).includes('Synthetic new password 42!'));
  assert.deepEqual(state.calls.navigations,['/password-reset-complete.html']);
  assert.ok(!state.calls.navigations[0].includes(token));
  assert.equal(state.calls.api.length,1,'Completing a reset must never sign in automatically.');
});

test('Missing token offers a fresh request; mismatched passwords never reach the endpoint',async()=>{
  const missing=renderContext('?view=reset-password');missing.passwordResetToken='';
  assert.equal(typeof missing.completePasswordResetPage,'function');
  vm.runInContext('completePasswordResetPage();',missing);
  assert.equal(descendants(missing.main).filter(node=>node.tag==='form').length,0);
  assert.ok(descendants(missing.main).some(node=>node.tag==='a'&&node.attrs.href.includes('forgot-password')));
  const state=renderContext('?view=reset-password');
  vm.runInContext('completePasswordResetPage();',state);
  const form=descendants(state.main).find(node=>node.tag==='form');
  form.querySelector('[name=newpassword]').value='Synthetic new password 42!';
  form.querySelector('[name=confirm_password]').value='A different synthetic password!';
  form.listeners.submit({preventDefault(){}});
  await Promise.all(state.calls.pending);
  assert.equal(state.calls.api.length,0);assert.equal(state.calls.feedback.length,1);
});

test('Homepage removes the fragment token before module loading or asynchronous work',async()=>{
  const order=[];
  const location={origin:'http://127.0.0.1:8797',pathname:'/',search:'?view=reset-password',
    hash:'#token='+token,href:'http://127.0.0.1:8797/?view=reset-password#token='+token};
  const panel={hidden:true,getBoundingClientRect:()=>({top:100}),querySelector:()=>null};
  const state={URL,URLSearchParams,location,
    document:{querySelector:selector=>selector==='#contributor-access'?panel:null,getElementById:()=>null,readyState:'complete'},
    history:{replaceState(...args){order.push(['clear',args[2]]);location.hash='#contributor-access';}},
    window:{scrollY:0,scrollTo(){},addEventListener(){}},requestAnimationFrame:fn=>fn(),
    loadWorkspace:async()=>{order.push(['import']);assert.ok(!location.hash.includes(token));return {
      initializeHomeAccount:async received=>{order.push(['initialize']);assert.equal(received,token);}};}};
  vm.createContext(state);
  const script=loader.replace("import('./workspace.js')",'loadWorkspace()');
  await vm.runInContext('(async()=>{'+script+'})()',state);
  assert.equal(order[0][0],'clear');assert.equal(order[1][0],'import');
  assert.equal(order[2][0],'initialize');
  assert.ok(!order[0][1].includes(token));
  assert.ok(!/localStorage|sessionStorage|console\.|document\.cookie/.test(script));
});

test('Homepage loader admits both recovery views and module initializes them without a login redirect',()=>{
  assert.match(loader,/forgot-password/);assert.match(loader,/reset-password/);
  assert.ok(source.includes("if(view==='forgot-password'){requestPasswordResetPage();return;}"));
  assert.ok(source.includes("if(view==='reset-password'){completePasswordResetPage();return;}"));
  assert.ok(source.includes('export async function initializeHomeAccount('));
});

test('Off-home recovery routes go to the homepage without forwarding a token or auth return loop',()=>{
  const routing=source.slice(source.indexOf('function safeWorkspaceNext('),source.indexOf('const itemLink'));
  for(const view of ['forgot-password','reset-password']){
    const location={origin:'http://127.0.0.1:8797',pathname:'/contribute.html',
      search:'?view='+view,hash:'#token='+token,replace(url){this.target=url;}};
    const state={URL,URLSearchParams,location,view,isHomeAccount:false,params:new URLSearchParams(location.search)};
    vm.createContext(state);
    vm.runInContext(routing+'\nredirectLegacyAuth();',state);
    const target=new URL(location.target,location.origin);
    assert.equal(target.pathname,'/');assert.equal(target.searchParams.get('view'),view);
    assert.ok(!location.target.includes(token));assert.equal(target.searchParams.has('token'),false);
    assert.equal(target.searchParams.has('next'),false);
    assert.equal(vm.runInContext("safeWorkspaceNext('/contribute.html?view=reset-password#token=invalid')",state),'');
  }
});
