import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

const source=await readFile(process.env.ELVIA_DUPLICATE_SUBMIT_SOURCE||new URL('../site/workspace.js',import.meta.url),'utf8');
function descendants(node){return node.childNodes.flatMap(child=>child instanceof Element?[child,...descendants(child)]:[]);}
class Element{
 constructor(tag,attrs={},...children){
  this.tagName=tag.toUpperCase();this.attrs={};this.dataset={};this.listeners={};this.childNodes=[];this.disabled=false;this.value='';
  this.classList={add:()=>{}};
  for(const [name,value] of Object.entries(attrs)){
   if(name.startsWith('on'))this.addEventListener(name.slice(2),value);
   else{this[name]=value;this.attrs[name]=value;}
  }
  this.append(...children);
 }
 get textContent(){return this.childNodes.map(n=>n instanceof Element?n.textContent:String(n)).join('');}
 set textContent(value){this.replaceChildren(value);}
 append(...nodes){for(const n of nodes.flat(Infinity))if(n!=null){this.childNodes.push(n);if(n instanceof Element)n.parent=this;}}
 prepend(...nodes){this.childNodes.unshift(...nodes);for(const n of nodes)if(n instanceof Element)n.parent=this;}
 replaceChildren(...nodes){this.childNodes=[];this.append(...nodes);}
 remove(){if(this.parent)this.parent.childNodes=this.parent.childNodes.filter(n=>n!==this);}
 addEventListener(name,fn){this.listeners[name]=fn;}
 setAttribute(name,value){this.attrs[name]=value;}
 removeAttribute(name){delete this.attrs[name];}
 getAttribute(name){return this.attrs[name]??null;}
 querySelectorAll(selector){
  return descendants(this).filter(n=>selector==='button,input,select,textarea'?['BUTTON','INPUT','SELECT','TEXTAREA'].includes(n.tagName)
   :selector.startsWith('[name=')?n.name===selector.slice(6,-1)
   :selector.startsWith('#')?n.id===selector.slice(1)
   :selector.startsWith('.')?String(n.class||'').split(' ').includes(selector.slice(1)):n.tagName.toLowerCase()===selector);
 }
 querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
 reset(){for(const n of descendants(this))if(n.tagName==='INPUT')n.value='';}
}
function harness(search='?view=login'){
 const main=new Element('main'),calls={fetch:[],pending:[],feedback:[],validation:0,navigation:[],timers:[],timeouts:[],now:0};
 const state={main,calls,actionPending:false,navigationPending:false,releasePendingAction:null,dirty:true,
  Blob,params:new URLSearchParams(search),isHomeAccount:true,passwordResetToken:'synthetic-reset-token-only',
  session:{csrf:'synthetic-csrf',user:null,email_registration:{enabled:true,research_domains:[]},google:{enabled:true}},
  document:{querySelector:selector=>main.querySelector(selector),querySelectorAll:()=>[],getElementById:()=>null},
  window:{addEventListener:(name,fn)=>{calls[name]=fn;}},
  location:{set href(value){if(state.failNavigation)throw new Error('Synthetic navigation failure');calls.navigation.push(value);}},
  el:(...args)=>new Element(...args),p:(text,cls='')=>new Element('p',{class:cls},text),
  link:(text,href,cls='')=>new Element('a',{href,class:cls},text),
  button:(text,fn)=>new Element('button',{type:'button',onclick:fn},text),
  field:(name,label,type='text',value='')=>new Element('div',{class:'field'},new Element('input',{name,type,value})),
  title:()=>{},href:query=>'/?'+query,authHref:mode=>'/?view='+mode,afterLogin:()=>'/contribute.html?view=maintainer',
  feedback:(...args)=>calls.feedback.push(args),mailDeliveryGuidance:()=>[],guestReadOnlyPage:()=>{},
  validateForm:()=>{calls.validation++;return state.valid!==false;},
  formData:form=>Object.fromEntries(descendants(form).filter(n=>n.name&&!n.disabled).map(n=>[n.name,n.value])),
  policyAcknowledgement:()=>new Element('label',{},new Element('input',{type:'checkbox',checked:true}),new Element('span')),
  setInterval:fn=>{calls.timers.push(fn);return 1;},clearInterval:()=>{},
  performance:{now:()=>calls.now},setTimeout:(fn,delay)=>{calls.timeouts.push({fn,at:calls.now+delay});},
  fetch:(url,options)=>new Promise(resolve=>calls.fetch.push({url,options,resolve}))};
 vm.createContext(state);
 vm.runInContext(source.slice(source.indexOf('async function api('),source.indexOf('function afterLogin(')),state);
 const original=state.act;state.act=(fn)=>{const promise=original(fn);calls.pending.push(promise);return promise;};
 vm.runInContext(source.slice(source.indexOf("main.addEventListener('submit',"),source.indexOf("main.addEventListener('input',")),state);
 vm.runInContext(source.slice(source.indexOf('function loginPage('),source.indexOf('function policyAcknowledgement(')),state);
 vm.runInContext(source.slice(source.indexOf('function googleSignIn('),source.indexOf('function quotaNote(')),state);
 const lifecycle=source.split('\n').find(line=>line.startsWith("window.addEventListener('pagehide',"));
 vm.runInContext(lifecycle,state);
 function submit(form){const event={target:form,blocked:false,preventDefault(){},stopImmediatePropagation(){this.blocked=true;}};main.listeners.submit(event);if(!event.blocked)form.listeners.submit(event);return event;}
 function resolve(index,{ok=true,result={}}={}){calls.fetch[index].resolve({ok,status:ok?200:401,json:async()=>result});}
 function advance(ms){calls.now+=ms;const due=calls.timeouts.filter(t=>t.at<=calls.now);calls.timeouts=calls.timeouts.filter(t=>t.at>calls.now);for(const timer of due)timer.fn();}
 async function flush(){for(let i=0;i<10;i++)await Promise.resolve();}
 return {state,main,calls,submit,resolve,advance,flush,settled:async()=>{await flush();advance(600);return Promise.all(calls.pending);}};
}
function login(h){h.state.loginPage(false);const form=h.main.querySelector('form');form.querySelector('[name=login]').value='synthetic@example.edu';form.querySelector('[name=password]').value='Synthetic original password!';return form;}

test('Rapid submit and Enter-like submit issue one complete login request before controls disable',async()=>{
 const h=harness(),form=login(h);h.submit(form);h.submit(form);
 assert.equal(h.calls.fetch.length,1);assert.equal(h.calls.validation,1);
 assert.equal(JSON.parse(h.calls.fetch[0].options.body).password,'Synthetic original password!');
 assert.equal(form.querySelector('button').disabled,true);
 assert.match(form.querySelector('button').textContent,/wait|processing/i);
 const progress=h.main.querySelector('#action-progress');assert.equal(progress.getAttribute('role'),'status');
 h.resolve(0,{ok:false,result:{error:'Synthetic credential error'}});await h.settled();
});

test('A failed request restores button text and allows a corrected password as a new attempt',async()=>{
 const h=harness(),form=login(h),button=form.querySelector('button'),label=button.textContent;
 h.submit(form);h.resolve(0,{ok:false,result:{error:'Synthetic credential error'}});await h.settled();
 assert.equal(button.disabled,false);assert.equal(button.textContent,label);assert.equal(h.main.getAttribute('aria-busy'),null);
 form.querySelector('[name=password]').value='Synthetic corrected password!';h.submit(form);
 assert.equal(h.calls.fetch.length,2);assert.equal(JSON.parse(h.calls.fetch[1].options.body).password,'Synthetic corrected password!');
 h.resolve(1,{ok:false,result:{error:'Synthetic second error'}});await h.settled();
});

test('Successful navigation stays busy through the unload window and pagehide restores bfcache state',async()=>{
 const h=harness(),form=login(h),button=form.querySelector('button');h.submit(form);
 h.resolve(0,{result:{csrf:'synthetic-next-csrf',user:{role:'maintainer',force_change:false}}});await h.settled();
 assert.equal(h.calls.navigation.length,1);assert.equal(button.disabled,true);assert.equal(h.main.getAttribute('aria-busy'),'true');
 h.submit(form);assert.equal(h.calls.fetch.length,1);
 h.calls.pagehide();assert.equal(button.disabled,false);assert.equal(h.main.getAttribute('aria-busy'),null);
 assert.equal(h.state.actionPending,false);assert.equal(h.state.navigationPending,false);assert.equal(h.state.passwordResetToken,'');
});

test('Invalid form submission does not acquire a pending lock',async()=>{
 const h=harness(),form=login(h);h.state.valid=false;h.submit(form);
 assert.equal(h.calls.fetch.length,0);assert.equal(form.querySelector('button').disabled,false);
 h.state.valid=true;h.submit(form);assert.equal(h.calls.fetch.length,1);
 h.resolve(0,{ok:false,result:{error:'Synthetic error'}});await h.settled();
});

test('Originally disabled and newly cooldown-locked controls stay disabled after failure',async()=>{
 const h=harness();const disabled=new Element('button',{type:'submit',disabled:true},'Unavailable');
 const cooldown=new Element('button',{type:'button'},'Send code');h.main.append(disabled,cooldown);
 const pending=h.state.act(async()=>{await h.state.api('/auth/email-code','POST',{email:'synthetic@example.edu'});cooldown.dataset.locked='true';cooldown.textContent='Resend in 60 seconds';throw new Error('Synthetic follow-up error');});
 h.resolve(0);await h.settled();await pending;
 assert.equal(disabled.disabled,true);assert.equal(disabled.textContent,'Unavailable');
 assert.equal(cooldown.disabled,true);assert.equal(cooldown.textContent,'Resend in 60 seconds');
});

test('Programmatic action reentry cannot start a second request or prematurely clear busy',async()=>{
 const h=harness();const first=h.state.act(()=>h.state.api('/auth/login','POST',{password:'synthetic'}));
 const second=h.state.act(()=>h.state.api('/auth/login','POST',{password:'synthetic'}));
 assert.equal(h.calls.fetch.length,1);assert.equal(h.main.getAttribute('aria-busy'),'true');
 await second;h.resolve(0);await h.settled();await first;assert.equal(h.main.getAttribute('aria-busy'),null);
});

test('Non-form Google actions are protected while the first authorization request is pending',async()=>{
 const h=harness(),area=h.state.googleSignIn();h.main.append(area);
 const action=area.querySelector('button');action.listeners.click();action.listeners.click();assert.equal(h.calls.fetch.length,1);
 h.resolve(0,{result:{authorization_url:'https://synthetic.invalid/oauth'}});await h.settled();
 assert.equal(h.calls.navigation.length,1);assert.equal(action.disabled,true);h.calls.pagehide();
});

test('Verification-code action reentry keeps the single request and existing resend cooldown',async()=>{
 const h=harness('?view=register');h.state.loginPage(true);const form=h.main.querySelector('form');
 form.querySelector('[name=email]').value='synthetic@example.edu';const action=form.querySelector('button');
 action.listeners.click();action.listeners.click();assert.equal(h.calls.fetch.length,1);
 h.resolve(0);await h.settled();assert.equal(action.disabled,true);assert.equal(action.dataset.locked,'true');
 assert.match(action.textContent,/60 seconds/);assert.equal(h.main.getAttribute('aria-busy'),null);
});

test('A fast failed login absorbs a double click for 600 ms, then permits a changed-password retry',async()=>{
 const h=harness(),form=login(h);h.submit(form);h.resolve(0,{ok:false,result:{error:'Synthetic immediate error'}});await h.flush();
 h.submit(form);assert.equal(h.calls.fetch.length,1);assert.equal(form.querySelector('button').disabled,true);
 h.advance(599);await h.flush();h.submit(form);assert.equal(h.calls.fetch.length,1);
 h.advance(1);await h.settled();form.querySelector('[name=password]').value='Synthetic changed retry!';h.submit(form);
 assert.equal(h.calls.fetch.length,2);assert.equal(JSON.parse(h.calls.fetch[1].options.body).password,'Synthetic changed retry!');
 h.resolve(1,{ok:false,result:{error:'Synthetic retry error'}});await h.settled();
});

test('A synchronous navigation error restores the form rather than retaining a false navigation lock',async()=>{
 const h=harness(),form=login(h);h.state.failNavigation=true;h.submit(form);
 h.resolve(0,{result:{csrf:'synthetic-next-csrf',user:{role:'maintainer',force_change:false}}});await h.settled();
 assert.equal(h.state.navigationPending,false);assert.equal(form.querySelector('button').disabled,false);
 assert.equal(h.main.getAttribute('aria-busy'),null);assert.match(h.calls.feedback.at(-1)[0],/navigation failure/);
});
