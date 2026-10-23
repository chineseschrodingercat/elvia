import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

const workspace=await readFile(new URL('../site/workspace.js',import.meta.url),'utf8');
const guide=await readFile(new URL('../site/participate-entry.js',import.meta.url),'utf8');
const moduleSource=await readFile(new URL('../site/case-context.js',import.meta.url),'utf8');
const contextModule=await import('data:text/javascript;base64,'+Buffer.from(moduleSource).toString('base64'));
const context={caseId:'synthetic-paper',problem:2,title:'Synthetic paper',problemTitle:'Synthetic question',caseUrl:'/atlas/cases/synthetic-paper.html#problem-2'};

class Element {
  constructor(tag,attrs={},...children){this.tag=tag;Object.assign(this,attrs);this.children=children.flat(Infinity).filter(x=>x!=null);this.dataset={};}
  append(...children){this.children.push(...children.flat(Infinity).filter(x=>x!=null));}
  setAttribute(name,value){this[name]=value;}
  addEventListener(){}
  get textContent(){return this.text||this.children.map(x=>typeof x==='string'?x:x.textContent||'').join(' ');}
  set textContent(value){this.text=value;this.children=[];}
}
function descendants(node){return [node,...node.children.flatMap(x=>typeof x==='object'?descendants(x):[])];}
function checkReturn(anchor){
  const url=new URL(anchor.href,'https://example.org');
  assert.equal(url.pathname,'/');
  const next=new URL(url.searchParams.get('next'),'https://example.org');
  assert.equal(next.pathname,'/contribute.html');
  assert.equal(next.searchParams.get('case'),context.caseId);
  assert.equal(next.searchParams.get('problem'),'2');
}

test('the participation primary action registers a guest with the selected finding, including session failure',async()=>{
  for(const unavailable of [false,true]){
    const nodes=[];
    const scope=new Element('a',{href:'https://example.org/contribute.html?view=scope'});
    const document={createElement:tag=>{const node=new Element(tag);nodes.push(node);return node;},querySelector:()=>({after(){}}),querySelectorAll:()=>[scope]};
    await vm.runInNewContext('(async()=>{'+guide.replace(/^import[^\n]+\n/,'')+'})()',{
      document,URL,URLSearchParams,location:{search:'?case=synthetic-paper&problem=2',origin:'https://example.org'},
      ...contextModule,loadCaseContext:async()=>context,
      fetch:async()=>{if(unavailable)throw new Error('Synthetic outage');return {ok:true,json:async()=>({user:null})};}
    });
    const primary=nodes.find(node=>node.tag==='a'&&node.className==='button button-primary');
    assert.ok(primary);
    assert.match(primary.textContent,/Register.*finding/i);
    checkReturn(primary);
    const scopeURL=new URL(scope.href,'https://example.org');
    assert.equal(scopeURL.searchParams.get('view'),'scope','eligibility link keeps its own destination');
    assert.equal(scopeURL.searchParams.get('case'),context.caseId);
  }
});

test('the participation primary action lets a signed-in member continue with the selected finding',async()=>{
  const nodes=[];
  const document={createElement:tag=>{const node=new Element(tag);nodes.push(node);return node;},querySelector:()=>({after(){}}),querySelectorAll:()=>[]};
  await vm.runInNewContext('(async()=>{'+guide.replace(/^import[^\n]+\n/,'')+'})()',{
    document,URL,URLSearchParams,location:{search:'?case=synthetic-paper&problem=2',origin:'https://example.org'},
    ...contextModule,loadCaseContext:async()=>context,fetch:async()=>({ok:true,json:async()=>({user:{role:'contributor'}})})
  });
  const primary=nodes.find(node=>node.tag==='a'&&node.className==='button button-primary');
  assert.equal(primary.textContent,'Open revision form ↗');
  assert.equal(primary.target,'_blank');
  assert.equal(primary.href,'/contribute.html?view=compose&case=synthetic-paper&problem=2');
});

test('a guest opening the contextual workspace can register and sign in without a homepage detour',async()=>{
  const main=new Element('main');main.dataset.homeAccount='false';
  const prefix=workspace.slice(workspace.indexOf('const main ='),workspace.indexOf('const itemLink'));
  const pages=workspace.slice(workspace.indexOf('function applicationStatus()'),workspace.indexOf('async function taskPage('));
  await vm.runInNewContext('(async()=>{'+prefix+'\nsession={user:null};selectedCase=fixture;'+pages+'\nawait homePage();})()',{
    URL,URLSearchParams,Node:Element,fixture:context,...contextModule,
    location:{origin:'https://example.org',pathname:'/contribute.html',search:'?case=synthetic-paper&problem=2',hash:''},
    document:{querySelector:()=>main,createElement:tag=>new Element(tag),createTextNode:text=>text},
    title(){},api:async()=>({tasks:[]}),reportStarter:()=>new Element('section')
  });
  const anchors=descendants(main).filter(node=>node.tag==='a');
  const register=anchors.find(node=>/Register.*finding/i.test(node.textContent));
  const signin=anchors.find(node=>/Sign in/i.test(node.textContent));
  assert.ok(register,'guest workspace needs a direct contextual registration action');
  assert.ok(signin,'guest workspace needs a direct contextual sign-in action');
  checkReturn(register);checkReturn(signin);
});
