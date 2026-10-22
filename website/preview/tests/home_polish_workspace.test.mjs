import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

const source=await readFile(new URL('../site/workspace.js',import.meta.url),'utf8');
const navSource=source.slice(source.indexOf('function nav()'),source.indexOf('function loginPage('));
const homeSource=source.slice(source.indexOf('function applicationStatus()'),source.indexOf('async function taskPage('));
const creditSource=source.slice(source.indexOf('async function creditPage('),source.indexOf('async function emailSettings('));

function node(tag,attrs={},...children){return {tag,attrs,children:children.flat(Infinity).filter(child=>child!=null),append(...items){this.children.push(...items.flat(Infinity).filter(child=>child!=null));}};}
function text(node){return typeof node==='object'?node.children.map(text).join(' '):String(node);}
function all(node,predicate){return (predicate(node)?[node]:[]).concat(...(node.children||[]).filter(child=>typeof child==='object').map(child=>all(child,predicate)));}
function context(role=null,application=null){
  const main=node('main');
  return {
    main,session:{user:role?{role}:null},me:{application},
    isStaff:()=>['admin','maintainer'].includes(role),
    el:node,p:(value,cls='')=>node('p',{class:cls},value),
    title:(value,description)=>main.append(node('h1',{},value),description?node('p',{},description):null),
    link:(label,href,cls='text-link')=>node('a',{href,class:cls},label),
    button:(label,callback,primary=false)=>node('button',{callback,class:primary?'button button-primary':'button button-secondary'},label),
    status:value=>node('span',{class:'status-label'},value),quotaNote:()=>null,
    href:(query='')=>'/contribute.html'+(query?'?'+query:''),mainPageHref:()=>'/',
    api:async()=>({tasks:[]}),act:async callback=>callback(),
  };
}

test('The workspace navigation removes Contribute and Approach for visitors and all account roles',()=>{
  for(const role of [null,'reviewer','admin','maintainer']){
    const ctx=context(role);let links;
    ctx.document={querySelector:()=>({replaceChildren(...items){links=items;}})};
    vm.runInNewContext(navSource+'\nnav();',ctx);
    const labels=links.map(text);
    assert.deepEqual(labels.slice(0,2),['Home','Atlas']);
    assert.ok(labels.includes('Contributors'));
    assert.ok(!labels.includes('Contribute'),role||'visitor');
    assert.ok(!labels.includes('Approach'),role||'visitor');
    assert.ok(!labels.some(label=>/sign in|register/i.test(label)));
    if(role){assert.ok(labels.includes(role==='reviewer'?'My work':'Manage'));assert.ok(labels.includes('Account'));}
  }
});

test('Visitors retain both contribution descriptions without action controls',async()=>{
  const ctx=context();
  await vm.runInNewContext(homeSource+'\nhomePage();',ctx);
  const tracks=all(ctx.main,n=>n.attrs?.class==='track-options')[0];
  assert.ok(text(tracks).includes('Submit your own analysis'));
  assert.ok(text(tracks).includes('Review an existing analysis'));
  assert.equal(all(tracks,n=>n.tag==='button'||n.tag==='a').length,0);
});

test('Signed-in reviewers can start an analysis and use the appropriate reviewer action',async()=>{
  for(const status of [null,'pending','approved']){
    const ctx=context('reviewer',status?{status}:null);
    await vm.runInNewContext(homeSource+'\nhomePage();',ctx);
    const tracks=all(ctx.main,n=>n.attrs?.class==='track-options')[0];
    const actions=all(tracks,n=>n.tag==='button'||n.tag==='a').map(text);
    assert.deepEqual(actions,['Start a new analysis',status==='approved'?'See available questions':'Apply for reviewer access']);
    assert.ok(!/register or sign in|You are welcome to explore|Back to main page/i.test(text(ctx.main)));
    if(status==='pending')assert.ok(text(ctx.main).includes('Your reviewer application is pending.'));
  }
});

test('Signed-in management keeps contribution actions and useful account status',async()=>{
  for(const role of ['admin','maintainer']){
    const ctx=context(role);
    await vm.runInNewContext(homeSource+'\nhomePage();',ctx);
    const tracks=all(ctx.main,n=>n.attrs?.class==='track-options')[0];
    assert.deepEqual(all(tracks,n=>n.tag==='button'||n.tag==='a').map(text),['Start a new analysis','See available questions']);
    assert.ok(text(ctx.main).includes('Your management workspace is ready.'));
    assert.ok(!/register or sign in|You are welcome to explore|Back to main page/i.test(text(ctx.main)));
  }
});

test('An accessible private acknowledgement does not ask its signed-in contributor to sign in',async()=>{
  const ctx=context('reviewer');
  ctx.api=async()=>({name:'Synthetic Contributor',roles:['Analysis'],title:'Synthetic record',scope:'Fixture only',id:'fixture',revision:1,accepted:0,issuer:'ELVIA',status:'Accepted',public:false});
  ctx.fmt=()=>'<fixture date>';
  ctx.location={href:'http://127.0.0.1:8797/contribute.html?credit=fixture'};
  ctx.window={print(){}};ctx.copy=()=>{};
  await vm.runInNewContext(creditSource+"\ncreditPage('fixture');",ctx);
  assert.ok(text(ctx.main).includes('This record is private'));
  assert.ok(!/Sign in with the contributing account/i.test(text(ctx.main)));
});
