import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
const source=await readFile(new URL('../site/workspace.js',import.meta.url),'utf8');
const css=await readFile(new URL('../site/workspace.css',import.meta.url),'utf8');
function context(){const state={p:text=>({tag:'p',text}),link:(text,href)=>({tag:'a',text,href}),authHref:mode=>'/?view='+mode+'#contributor-access'};vm.createContext(state);vm.runInContext(source.slice(source.indexOf('function loginFailureDetails('),source.indexOf('function requestPasswordResetPage(')),state);return state;}

test('Fifth through ninth wrong-login warnings show five through one remaining and a local reset link',()=>{
 const state=context();for(let remaining=5;remaining>=1;remaining--){const details=state.loginFailureDetails({details:{login_attempts_remaining:remaining,login_locked:false,retry_after:0,password_reset_url:'https://untrusted.invalid'}});
 assert.match(details[0].text,new RegExp(remaining+' sign-in attempts remain'));
 assert.equal(details[1].text,'Reset your password');assert.equal(details[1].href,'/?view=forgot-password#contributor-access');}
});

test('Locked login presents remaining time while browsing and recovery remain available',()=>{
 const state=context();const details=state.loginFailureDetails({details:{login_attempts_remaining:0,login_locked:true,retry_after:3599}});
 assert.match(details[0].text,/60 minutes/);assert.match(details[0].text,/Browsing and password recovery remain available/);
 assert.equal(details[1].href,'/?view=forgot-password#contributor-access');
 assert.equal(state.loginFailureDetails({details:{login_attempts_remaining:'4'}}).length,0);
});

test('The API retains structured login-lock data for error presentation',async()=>{
 const data={error:'Synthetic wrong login',login_locked:false,login_attempts_remaining:4,retry_after:0};
 const state={Blob,session:{csrf:''},fetch:async()=>({ok:false,status:401,json:async()=>data})};vm.createContext(state);
 vm.runInContext(source.slice(source.indexOf('async function api('),source.indexOf('async function act(')),state);
 await assert.rejects(state.api('/auth/login','POST',{login:'synthetic',password:'wrong'}),error=>error.status===401&&error.details===data);
});

test('Error text, summaries and invalid controls explicitly use the red error hue',()=>{
 assert.match(css,/\.field-error\{color:#b42318/);
 assert.match(css,/\.workspace \.form-message\.error,\.workspace \.validation-summary\{color:#b42318;border:2px solid #b42318/);
 assert.match(css,/input\[aria-invalid=true\].*textarea\[aria-invalid=true\].*border-color:#b42318/);
 assert.ok(source.includes("el('ul',{class:'field-error password-errors',id:oldError}"));
});

test('The first four wrong-password results keep recovery available without a countdown',()=>{
 const state=context();for(const remaining of [9,8,7,6,10,999]){
  const details=state.loginFailureDetails({details:{login_attempts_remaining:remaining,login_locked:false,retry_after:0}});
  assert.equal(details.length,1);assert.equal(details[0].tag,'a');assert.equal(details[0].text,'Reset your password');
  assert.equal(details[0].href,'/?view=forgot-password#contributor-access');
 }
});
