import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

const source=await readFile(new URL('../site/workspace.js',import.meta.url),'utf8');
const passwordHelpers=source.slice(source.indexOf('function newPasswordHint('),source.indexOf('function requestPasswordResetPage('));
function element(tag,attrs={},...children){
  return {tag,attrs,children,append(...items){this.children.push(...items);},
    querySelector(){return {minLength:0,autocomplete:'',dataset:{}};},addEventListener(){}};
}
function context(role='reviewer',search=''){
  const calls={google:0,email:0,titles:[],nodes:[]};
  return {calls,isHomeAccount:true,params:new URLSearchParams(search),
    session:{user:{role,has_password:false,force_change:0,name:'Synthetic account',login:'synthetic@example.edu'}},
    main:{append(...nodes){calls.nodes.push(...nodes);}},el:element,
    title(value){calls.titles.push(value);},p:(text,cls)=>element('p',{class:cls},text),
    link:(text,href,cls)=>element('a',{href,class:cls},text),
    field:(name)=>element('field',{name}),href:q=>'/?'+q+'#contributor-access',
    gate:()=>false,isStaff:()=>['admin','maintainer'].includes(role),
    googleAccount:()=>{calls.google++;return element('google-account');},
    googleSignIn:()=>{calls.google++;return element('google-sign-in');},
    emailSettings:async()=>{calls.email++;},button:()=>element('button')};
}

test('Both management roles can link Google; SMTP settings stay maintainer-only',async()=>{
  const render=passwordHelpers+source.slice(source.indexOf('async function accountPage()'),source.indexOf("window.addEventListener('beforeunload'"));
  for(const role of ['reviewer','admin','maintainer']){
    const state=context(role);vm.createContext(state);
    await vm.runInContext(render+'\naccountPage();',state);
    assert.equal(state.calls.google,role==='reviewer'?0:1,role);
    assert.equal(state.calls.email,role==='maintainer'?1:0,role);
  }
});

test('Contributor sign-in keeps Google in the separate homepage management panel',()=>{
  const render=source.slice(source.indexOf('function loginPage('),source.indexOf('function policyAcknowledgement('));
  for(const search of ['', 'maintainer=1']){
    const state=context('reviewer',search);vm.createContext(state);
    vm.runInContext(render+'\nloginPage();',state);
    assert.equal(state.calls.google,search?1:0);
    if(search)assert.equal(state.calls.titles[0],'Admin and maintainer sign-in.');
    const text=JSON.stringify(state.calls.nodes);
    assert.ok(text.includes(search?'existing admin or maintainer account':'Admin and maintainer sign-in'));
    assert.ok(text.includes('#contributor-access'));
  }
});

test('A required password change hides Google linking and delivery configuration',async()=>{
  const render=passwordHelpers+source.slice(source.indexOf('async function accountPage()'),source.indexOf("window.addEventListener('beforeunload'"));
  const state=context('maintainer');state.session.user.force_change=1;vm.createContext(state);
  await vm.runInContext(render+'\naccountPage();',state);
  assert.equal(state.calls.google,0);assert.equal(state.calls.email,0);
});
