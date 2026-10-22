import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

const source=await readFile(new URL('../site/workspace.js',import.meta.url),'utf8');
function node(tag,attrs={},...children){const item={tag,tagName:tag.toUpperCase(),attrs,children:[],listeners:{},value:attrs.value||'',dataset:{},type:attrs.type,name:attrs.name,required:attrs.required,validity:{valid:true},
 append(...items){for(const child of items.flat(Infinity)){this.children.push(child);if(child&&typeof child==='object')child.parentElement=this;}},
 prepend(...items){this.children.unshift(...items);},focus(){},scrollIntoView(){},
 addEventListener(name,fn){this.listeners[name]=fn;},
 querySelectorAll(selector){return descendants(this).filter(item=>selector.split(',').some(part=>part.startsWith('.')?String(item.attrs?.class||'').split(' ').includes(part.slice(1)):part.startsWith('[name=')?item.attrs?.name===part.slice(6,-1):item.tag===part));},
 querySelector(selector){return this.querySelectorAll(selector)[0]||null;},closest(){return this.parentElement;},
 removeAttribute(name){delete this.attrs[name];},getAttribute(name){return this.attrs[name]||'';},setAttribute(name,value){this.attrs[name]=value;}};item.append(...children);return item;}
function descendants(item){return (item.children||[]).flat(Infinity).flatMap(child=>child&&typeof child==='object'?[child,...descendants(child)]:[]);}
function context(){const main=node('main');const state={main,isHomeAccount:true,params:new URLSearchParams(),
session:{user:null,email_registration:{enabled:true,research_domains:[]}},
el:node,p:(value,cls)=>node('p',{class:cls},value),field:(name,label,type='text',value='',hint='',required=false)=>node('field',{hint},node('input',{name,type,value,required})),
button:()=>node('button'),link:()=>node('a'),title(){},href:()=>'/synthetic',policyAcknowledgement:()=>node('policy'),googleSignIn:()=>node('google')};
vm.createContext(state);vm.runInContext(source.slice(source.indexOf('function loginPage('),source.indexOf('function policyAcknowledgement(')),state);return state;}

test('Existing login has no new-password minimum or complexity marker; registration does',()=>{
 const state=context();state.loginPage(false);
 let password=state.main.querySelector('[name=password]');
 assert.ok(!password.minLength||password.minLength<=0,'Existing-password sign-in must not enforce the new minimum.');
 assert.equal(password.dataset.newPassword,undefined);
 assert.doesNotMatch(state.main.children.map(item=>item.attrs?.hint||'').join(' '),/At least 12/);
 state.main.children=[];state.loginPage(true);password=state.main.querySelector('[name=password]');
 assert.equal(password.dataset.newPassword,'true');assert.equal(password.minLength,9);
 assert.equal(password.maxLength,512,'UTF-16 input capacity must admit 256 Unicode code points.');
});

test('Actual form validation rejects invalid new values while preserving raw password spaces',()=>{
 for(const [value,expected] of [['Aaaaaaaa!',true],['Aaaaaaa! ',true],['A'+'😀'.repeat(6)+'!a',true],['Aaaaaaa!',false],['aaaaaaaa!',false],['Aaaaaaaaa',false]]){
  const state=context();state.loginPage(true);
  const form=state.main.querySelector('form');
  // Isolate the password control; other registration fields have their own tests.
  const password=form.querySelector('[name=password]');form.children=[password];password.parentElement=form;password.id='synthetic-password';password.value=value;
  vm.runInContext(source.slice(source.indexOf('function validateForm('),source.indexOf("main.addEventListener('submit'")),state);
  assert.equal(state.validateForm(form),expected,value);
 }
});

test('Missing password requirements render as separate inline red error items with accessible field state',()=>{
 const state=context();state.loginPage(true);const form=state.main.querySelector('form');
 const password=form.querySelector('[name=password]');form.children=[password];password.parentElement=form;password.id='all-missing';password.value='';
 vm.runInContext(source.slice(source.indexOf('function validateForm('),source.indexOf("main.addEventListener('submit'")),state);
 assert.equal(state.validateForm(form),false);
 assert.equal(password.attrs['aria-invalid'],'true');
 const inline=form.querySelector('.field-error');
 assert.equal(inline.tag,'ul');assert.equal(inline.children.filter(item=>item.tag==='li').length,3);
 assert.equal(inline.attrs.id,'all-missing-error');
 assert.ok(password.attrs['aria-describedby'].includes('all-missing-error'));
 const summary=form.querySelector('.validation-summary');assert.equal(summary.attrs.role,'alert');
});

test('Front-end policy counts code points and requires ASCII uppercase and punctuation',()=>{
 const state=context();assert.equal(typeof state.newPasswordProblem,'function');
 const punctuation='!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~';
 for(const value of ['Aaaaaaaa!','Aaaaaaaa/','É'.repeat(7)+'A!','A'+'😀'.repeat(6)+'!a','A!'+'😀'.repeat(254),...Array.from(punctuation,p=>'Aaaaaaaa'+p)])assert.equal(state.newPasswordProblem(value),'',String(value));
 for(const value of ['Aaaaaaa!','aaaaaaaa!','Aaaaaaaaa','Éaaaaaaa!','Aaaaaaaa？','A!'+'a'.repeat(255)])assert.ok(state.newPasswordProblem(value),String(value));
 for(let code=0;code<128;code++)assert.equal(!state.newPasswordProblem('Aaaaaaaa'+String.fromCharCode(code)),punctuation.includes(String.fromCharCode(code)),String(code));
});

test('Only newly chosen passwords opt into policy validation and raw codepoint lengths',()=>{
 assert.match(source,/control\.dataset\.newPassword/);
 assert.match(source,/Array\.from\(value\)\.length/);
 assert.ok(source.includes("maxlength:type==='password'?512:2000"),'Current password fields must admit every legacy/new 256-code-point password.');
 assert.match(source,/control\.type==='password'\?control\.value:control\.value\.trim\(\)/);
 const google=source.slice(source.indexOf('function googleAccount('),source.indexOf('async function accountPage('));
 const smtp=source.slice(source.indexOf('async function emailSettings('),source.indexOf('function googleAccount('));
 assert.doesNotMatch(google,/configureNewPassword|newPasswordProblem/);
 assert.doesNotMatch(smtp,/configureNewPassword|newPasswordProblem/);
});
