import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const sourceURL = new URL('../site/visitor-access.js', import.meta.url);

async function run(result, failure=false) {
  const notices=[{hidden:false},{hidden:false}];
  const guest={hidden:false},member={hidden:true},work={href:''};
  const calls=[];
  const document={
    querySelectorAll: selector => selector==='[data-visitor-notice]'?notices:[],
    querySelector: selector => ({'#contributor-guest-actions':guest,'#contributor-member-actions':member,'#contributor-workspace':work})[selector]||null
  };
  vm.runInNewContext(fs.readFileSync(sourceURL,'utf8'),{document,fetch:async(path,options)=>{
    calls.push({path,options});if(failure)throw new Error('offline');
    return {ok:true,json:async()=>result};
  }});
  await new Promise(resolve=>setImmediate(resolve));
  return {notices,guest,member,work,calls};
}
test('guests retain read-only invitation and homepage sign-in choices',async()=>{
  const state=await run({user:null});
  assert.ok(state.notices.every(n=>!n.hidden));assert.equal(state.guest.hidden,false);assert.equal(state.member.hidden,true);
});
test('signed-in readers do not see guest invitation; homepage offers their workspace',async()=>{
  const state=await run({user:{role:'reviewer'}});
  assert.ok(state.notices.every(n=>n.hidden));assert.equal(state.guest.hidden,true);assert.equal(state.member.hidden,false);
  assert.equal(state.work.href,'/contribute.html?view=my-work');
});
test('staff homepage points to management without promoting a guest',async()=>{
  const state=await run({user:{role:'maintainer'}});assert.equal(state.work.href,'/contribute.html?view=maintainer');
});
test('session failure keeps public content and the safe guest invitation',async()=>{
  const state=await run(null,true);assert.ok(state.notices.every(n=>!n.hidden));assert.equal(state.guest.hidden,false);
});
test('visitor detection only reads same-origin session and never mutates state',async()=>{
  const {calls}=await run({user:null});assert.equal(calls.length,1);assert.equal(calls[0].path,'/api/session');
  assert.equal(calls[0].options.credentials,'same-origin');assert.equal(calls[0].options.cache,'no-store');
  assert.equal(calls[0].options.method||'GET','GET');assert.equal(calls[0].options.body,undefined);
});
