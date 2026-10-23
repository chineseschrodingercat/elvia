import {nameNorm,nameContains,uniqueNameMatch} from './name-matching.js';
import {parseCaseContext,addCaseContext,loadCaseContext,draftIdentity} from './case-context.js';
const main = document.querySelector('#workspace');
const isHomeAccount = main.dataset.homeAccount === 'true';
const params = new URLSearchParams(location.search);
const view = params.get('view') || 'home';
const caseRoute = parseCaseContext(isHomeAccount&&params.get('next')?new URL(safeWorkspaceNext(params.get('next'))||'/contribute.html',location.origin).searchParams:params);
let selectedCase = null;
let session, me, scopePolicy, dirty = false, fieldCount = 0, passwordResetToken = '';
let actionPending = false, navigationPending = false, releasePendingAction = null;
const isStaff=()=>['admin','maintainer'].includes(session.user?.role);
const labels = {draft:'Draft',submitted:'Awaiting review',needs_changes:'Changes requested',accepted:'Contribution accepted',declined:'Not accepted',released:'Released',pending:'Application pending',approved:'Approved',needs_information:'More information needed'};
const assessments = {supported:'The reasoning holds within this scope',clarification:'A clarification would help',possible_issue:'A possible issue needs further review',unresolved:'I could not resolve the question'};
const el = (tag, attrs = {}, ...children) => {
  const node = document.createElement(tag);
  for (const [key,value] of Object.entries(attrs)) {
    if (key.startsWith('on')) node.addEventListener(key.slice(2),value);
    else if (key === 'class') node.className = value;
    else if (key === 'text') node.textContent = value;
    else if (value === true) node.setAttribute(key,'');
    else if (value !== false && value != null) node.setAttribute(key,value);
  }
  for (const child of children.flat(Infinity)) if (child != null) node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  return node;
};
const p = (text,cls='') => el('p',{class:cls},text);
const link = (text,href,cls='text-link') => el('a',{href,class:cls},text);
const button = (text,fn,primary=false) => el('button',{type:'button',class:`button ${primary?'button-primary':'button-secondary'}`,onclick:fn},text);
function safeWorkspaceNext(value) {
  if(!value)return '';
  try {
    const url=new URL(value,location.origin);
    if(url.origin!==location.origin||url.username||url.password||url.pathname!=='/contribute.html'||['login','register','forgot-password','reset-password'].includes(url.searchParams.get('view')))return '';
    return url.pathname+url.search+url.hash;
  } catch {return '';}
}
function currentWorkspaceNext() {
  const explicit=safeWorkspaceNext(params.get('next'));
  if(explicit)return explicit;
  if(location.pathname!=='/contribute.html'||['login','register','forgot-password','reset-password'].includes(view))return '';
  return safeWorkspaceNext(location.pathname+location.search+location.hash);
}
function authHref(mode='login',options={}) {
  const query=new URLSearchParams({view:['register','forgot-password','reset-password'].includes(mode)?mode:'login'});
  if(mode==='login'&&options.maintainer)query.set('maintainer','1');
  const next=safeWorkspaceNext(options.next===undefined?currentWorkspaceNext():options.next);
  if(next)query.set('next',next);
  if(options.error)query.set('auth_error',String(options.error));
  return '/?'+query+'#contributor-access';
}
function redirectLegacyAuth() {
  if(isHomeAccount||!['login','register','forgot-password','reset-password'].includes(view))return false;
  location.replace(authHref(view,{maintainer:params.get('maintainer')==='1',next:params.get('next'),error:params.get('auth_error')}));
  return true;
}
const href = (query='',keepCase=true) => {
  const target=new URLSearchParams(query);
  if(['login','register','forgot-password','reset-password'].includes(target.get('view')))return authHref(target.get('view'),{maintainer:target.get('maintainer')==='1',next:target.get('next')||currentWorkspaceNext()});
  const route=addCaseContext(query,keepCase?caseRoute:null);
  return '/contribute.html'+(route?'?'+route:'');
};
const itemLink = id => href('review='+encodeURIComponent(id),false);
const creditLink = id => href('credit='+encodeURIComponent(id));
const fmt = value => new Date(value).toLocaleString(undefined,{dateStyle:'medium',timeStyle:'short'});
const status = text => el('span',{class:'status-label'},text);
function title(text,description) { document.title = `${text} | ELVIA`; main.append(el(isHomeAccount?'h2':'h1',{},text),description?p(description,'lede'):null); }
function mailDeliveryGuidance() {
  return [
    el('p',{},el('strong',{},'Check your inbox and your Spam or Junk folder.')),
    p('If you find the ELVIA message there, mark it as Not spam or Not junk. Allow a few minutes for delivery before requesting another email.','small')
  ];
}
function feedback(text,error=false,details=[]) {
  let box = document.querySelector('#feedback');
  if (!box) { box=el('div',{id:'feedback',tabindex:'-1'}); main.prepend(box); }
  box.className='form-message'+(error?' error':''); box.setAttribute('role',error?'alert':'status'); box.textContent=text;
  box.append(...details);
  box.focus(); box.scrollIntoView({block:'nearest',behavior:'instant'});
}
async function api(path,method='GET',data,headers={}) {
  if (method==='POST' && typeof window !== 'undefined' && window.ELVIA_SECURITY) {
    const token = await window.ELVIA_SECURITY.token(path);
    if (token) data = {...data,turnstile_token:token};
  }
  const options={method,credentials:'same-origin',headers:{'X-CSRF-Token':session?.csrf||'',...headers}};
  if (data instanceof Blob) options.body=data;
  else if(data!==undefined) {options.body=JSON.stringify(data); options.headers['Content-Type']='application/json';}
  let response;
  try {response=await fetch('/api'+path,options);} catch {throw new Error('ELVIA is temporarily unavailable. Please try again later. Keep this page open to preserve unsaved text.');}
  const result=await response.json();
  if(!response.ok) {const error=new Error(result.error||'This action could not be completed.');error.status=response.status;error.details=result;throw error;}
  if(result.csrf!==undefined) session={...session,...result};
  return result;
}
async function act(fn) {
  if(actionPending||navigationPending)return false;
  actionPending=true;
  const started=performance.now();
  document.querySelector('#feedback')?.remove();
  const controls=[...main.querySelectorAll('button,input,select,textarea')].filter(x=>!x.disabled);
  const submitLabels=controls.filter(x=>(x.tagName==='BUTTON'||x.tagName==='INPUT')&&x.type==='submit').map(control=>({control,children:control.tagName==='BUTTON'?[...control.childNodes]:null,value:control.value}));
  const progress=el('p',{id:'action-progress',class:'form-message',role:'status','aria-live':'polite'},'Processing your request. Please wait…');
  main.prepend(progress);
  controls.forEach(x=>x.disabled=true);
  submitLabels.forEach(({control,children})=>{if(children)control.replaceChildren('Please wait…');else control.value='Please wait…';});
  main.setAttribute('aria-busy','true');
  let restored=false;
  const restore=()=>{
    if(restored)return;
    restored=true;
    controls.forEach(x=>x.disabled=x.dataset.locked==='true');
    submitLabels.forEach(({control,children,value})=>{if(control.dataset.locked==='true')return;if(children)control.replaceChildren(...children);else control.value=value;});
    progress.remove();main.removeAttribute('aria-busy');actionPending=false;releasePendingAction=null;
  };
  releasePendingAction=restore;
  try {await fn();return true;}
  catch(error) {navigationPending=false;feedback(error.message,true,loginFailureDetails(error));return false;}
  finally {
    if(!navigationPending){
      const remaining=Math.max(0,600-(performance.now()-started));
      if(remaining)await new Promise(resolve=>setTimeout(resolve,remaining));
      restore();
    }
  }
}
function navigate(url) {
  dirty=false;navigationPending=true;
  try {location.href=url;} catch(error) {navigationPending=false;throw error;}
}
function afterLogin() {
  const next=safeWorkspaceNext(params.get('next'));
  if(next)return next;
  if(params.has('review')||params.has('credit')||params.has('paper')||params.has('final')||params.has('revise')||view==='finals') return location.href;
  return href(isStaff()?'view=maintainer':'view=my-work');
}
function mainPageHref() {
  const next=currentWorkspaceNext();
  return next?'/?next='+encodeURIComponent(next)+'#main':'/';
}
function guestReadOnlyPage() {
  title('Browse ELVIA as a visitor.','You can explore the Atlas and read public contribution records. To contribute, return to the main page to register or sign in.');
  main.append(link('Back to main page',mainPageHref()),el('div',{class:'form-actions'},link('Explore the Atlas','/atlas/','button button-secondary')));
}
function homeAccountPage() {
  if(view==='forgot-password'){requestPasswordResetPage();return;}
  if(view==='reset-password'){completePasswordResetPage();return;}
  if(!session.user){loginPage(view==='register');return;}
  title('You are signed in.','Continue in your contribution workspace with your existing account.');
  main.append(link(session.user.force_change?'Open account settings':'Open contribution workspace',session.user.force_change?href('view=account'):afterLogin(),'button button-primary'));
}
function gate() {
  if(session.user)return false;
  guestReadOnlyPage();return true;
}
function field(name,label,type='text',value='',hint='',required=false,options=[]) {
  label=label.replace(/ \(optional\)$/,'');
  const id='field-'+name+'-'+(++fieldCount);
  const control= type==='textarea'?el('textarea',{id,name,rows:['reasoning','summary'].includes(name)?4:2,required,maxlength:16000},value):
    type==='select'?el('select',{id,name,required},el('option',{value:''},'Select an option'),options.map(([v,t])=>el('option',{value:v,selected:v===value},t))):
    el('input',{id,name,type,value,required,autocomplete:type==='password'?'current-password':name==='email'?'email':'off',maxlength:type==='password'?512:2000});
  if(hint)control.setAttribute('aria-describedby',id+'-hint');
  control.dataset.label=label;
  const wrapper=el('div',{class:'field'},el('label',{for:id},label,el('span',{class:'field-requirement'},required?'Required':'Optional')),control,hint?el('span',{id:id+'-hint',class:'hint'},hint):null);
  return wrapper;
}
function check(name,label,checked=false,required=false) {return el('label',{class:'check-row'},el('input',{type:'checkbox',name,id:'check-'+name+'-'+(++fieldCount),checked,required,'data-label':label}),el('span',{},label,required?el('span',{class:'field-requirement'},'Required'):null));}
function setRequired(control,required) {
  control.required=required;
  const marker=control.closest('.field')?.querySelector('.field-requirement');
  if(marker)marker.textContent=required?'Required':'Optional';
}
function clearInactiveErrors(){for(const control of main.querySelectorAll('[aria-invalid=true]'))if(control.disabled)clearControlError(control);}
function clearControlError(control){
  control.removeAttribute('aria-invalid');document.getElementById(control.id+'-error')?.remove();
  control.setAttribute('aria-describedby',(control.getAttribute('aria-describedby')||'').split(' ').filter(x=>x!==control.id+'-error').join(' '));
  const summary=control.form?.querySelector('.validation-summary');if(!summary)return;
  summary.querySelector(`[data-error-for="${control.id}"]`)?.remove();const count=summary.querySelectorAll('li').length;
  if(!count)summary.remove();else summary.querySelector('strong').textContent=`Check ${count} ${count===1?'field':'fields'} before submitting.`;
}
function optionalFields(label,...children){return el('details',{class:'optional-fields full'},el('summary',{},label),el('div',{class:'optional-content'},...children));}
function validateForm(form) {
  form.querySelector('.validation-summary')?.remove();
  form.querySelectorAll('.field-error').forEach(x=>x.remove());
  const problems=[];
  for(const control of form.querySelectorAll('input,textarea,select')){
    control.removeAttribute('aria-invalid');
    const oldError=control.id+'-error';control.setAttribute('aria-describedby',(control.getAttribute('aria-describedby')||'').split(' ').filter(x=>x&&x!==oldError).join(' '));
    if(control.disabled)continue;
    const value=control.type==='password'?control.value:control.value.trim();let message='',messages=[];
    if(control.dataset.newPassword==='true'){
      messages=newPasswordProblems(value);
      if(control.name==='confirm_password'&&value!==form.querySelector('[name=newpassword]')?.value)messages.push('Enter the same new password in both fields.');
      message=messages.join(' ');
    }
    else if(control.required&&(control.type==='checkbox'?!control.checked:!value))message=control.type==='checkbox'?'Confirm this statement to continue.':'This field is required.';
    else if(value&&control.minLength>0&&Array.from(value).length<control.minLength)message=`Use at least ${control.minLength} characters.`;
    else if(!control.validity.valid)message=control.validationMessage;
    if(!message)continue;
    control.setAttribute('aria-invalid','true');
    control.setAttribute('aria-describedby',((control.getAttribute('aria-describedby')||'')+' '+oldError).trim());
    const error=messages.length?el('ul',{class:'field-error password-errors',id:oldError},messages.map(item=>el('li',{},item))):el('span',{class:'field-error',id:oldError},message);
    (control.closest('.field,.check-row')||control.parentElement).append(error);
    let ancestor=control.parentElement;while(ancestor&&ancestor!==form){if(ancestor.tagName==='DETAILS')ancestor.open=true;ancestor=ancestor.parentElement;}
    problems.push({control,message});
  }
  if(!problems.length)return true;
  const summary=el('div',{class:'validation-summary form-message error',role:'alert',tabindex:'-1'},el('strong',{},`Check ${problems.length} ${problems.length===1?'field':'fields'} before submitting.`),el('ul',{},problems.map(({control,message})=>el('li',{'data-error-for':control.id},el('a',{href:'#'+control.id,onclick:event=>{event.preventDefault();control.focus();}},(control.type==='checkbox'?'Submission confirmation':control.dataset.label||control.name)+': '+message)))));
  form.prepend(summary);summary.focus();summary.scrollIntoView({block:'nearest'});return false;
}
main.addEventListener('submit',event=>{if(actionPending||navigationPending||!validateForm(event.target)){event.preventDefault();event.stopImmediatePropagation();}},true);
main.addEventListener('input',event=>{
  const control=event.target;if(!control.hasAttribute('aria-invalid'))return;
  const value=control.type==='password'?control.value:control.value.trim();if(!control.validity.valid||(control.required&&!value)||(value&&control.dataset.newPassword==='true'&&newPasswordProblem(value))||(value&&control.minLength>0&&Array.from(value).length<control.minLength))return;
  if(control.name==='confirm_password'&&value!==control.form?.querySelector('[name=newpassword]')?.value)return;
  clearControlError(control);
});
function prepareForms(){for(const form of main.querySelectorAll('form'))form.noValidate=true;}
function formData(form){return Object.fromEntries(new FormData(form));}
function trackDirty(form){form.addEventListener('input',()=>dirty=true);}
function steps(current=1) {return el('ol',{class:'flow-steps'},['Create an account','Apply for reviewer access','Choose a review'].map((text,i)=>el('li',{'aria-current':current===i+1?'step':null},el('span',{},String(i+1).padStart(2,'0')),text)));}
function nav() {
  const items=[link('Home','/',''),link('Atlas','/atlas/',''),link('Contributors',href('view=contributors'),'')];
  if(session.user) {
    items.splice(2,0,link(isStaff()?'Manage':'My work',href(isStaff()?'view=maintainer':'view=my-work'),''));
    items.push(link('Account',href('view=account'),''));
  }
  document.querySelector('#workspace-navigation')?.replaceChildren(...items);
}

function loginPage(register=false) {
  if(!isHomeAccount){guestReadOnlyPage();return;}
  const maintainer=!register&&params.get('maintainer')==='1';
  title(register?'Join the contribution workspace.':maintainer?'Admin and maintainer sign-in.':'Welcome back.',register?'Verify an academic or research-institution email, then submit your own analysis. No endorsement or reviewer application is needed for this track.':'Sign in to pick up your saved work. Your return links work in another browser with the same account.');
  const form=el('form',{class:'form-grid auth-form'});
  if(register)form.append(field('name','Your name','text','','The name you would like us to use.',true));
  form.append(field(register?'email':'login',register?'Academic or research email':'Email or maintainer account',register?'email':'text','',register?'Use .edu, .edu.country, .ac.country or an approved research-institution domain. Personal email accounts are not accepted.':'',true));
  if(register){
    const codeStatus=el('div',{class:'form-message full','aria-live':'polite',hidden:true});
    const request=button('Send verification code',()=>{
      const email=form.querySelector('[name=email]').value.trim();
      act(async()=>{
        await api('/auth/email-code','POST',{email});
        codeStatus.replaceChildren(p('Verification code sent. Your code expires in 10 minutes.'),...mailDeliveryGuidance());
        codeStatus.hidden=false;
        request.dataset.locked='true';request.disabled=true;let seconds=60;request.textContent='Resend in 60 seconds';
        const timer=setInterval(()=>{seconds--;request.textContent=seconds?'Resend in '+seconds+' seconds':'Resend verification code';if(!seconds){clearInterval(timer);delete request.dataset.locked;request.disabled=false;}},1000);
      });
    });
    const code=field('email_code','Email verification code','text','','Six digits; valid for 10 minutes. A new code replaces the previous one.',true);
    Object.assign(code.querySelector('input'),{inputMode:'numeric',maxLength:6,pattern:'[0-9]{6}',autocomplete:'one-time-code'});
    form.append(el('div',{},request,codeStatus),code);
    if(!session.email_registration.enabled){request.disabled=true;form.append(p('Email registration is not open yet. The maintainer needs to configure the domain email service first.','form-message'));}
    const domains=session.email_registration.research_domains;
    if(domains.length)form.append(el('details',{class:'paper-details'},el('summary',{},'Approved research-institution domains'),p(domains.join(', '),'small')));
  }
  form.append(field('password','Password','password','',register?newPasswordHint():'Enter your existing password.',true));
  if(register){configureNewPassword(form.querySelector('[name=password]'));form.append(policyAcknowledgement());}
  form.append(el('div',{class:'form-actions full'},el('button',{class:'button button-primary',type:'submit',disabled:register&&!session.email_registration.enabled},register?'Verify email and create account':'Sign in')));
  if(!register)form.append(link('Forgot your password?',href('view=forgot-password'),'text-link full'));
  form.addEventListener('submit',event=>{event.preventDefault();const data={...formData(form),accept_terms:!!form.querySelector('[name=accept_terms]')?.checked};act(async()=>{await api(register?'/auth/register':'/auth/login','POST',data);navigate(session.user.force_change?href('view=account'):afterLogin());});});
  const aside=el('aside',{class:'side-note'},el('h2',{},register?'Two ways to contribute.':'One account, your saved work.'),p(register?'After email verification, submit up to two papers and analyses a day. Apply once only if you want to review existing analyses; approved reviewers can claim and submit one review a day.':'Applications, claims and packages stay with your account. A return link identifies your contribution; signing in controls access.'),link(register?'Already have an account? Sign in':'New here? Verify an institutional email',href(register?'view=login':'view=register')));
  if(!register&&!maintainer)aside.append(link('Admin and maintainer sign-in',href('view=login&maintainer=1')));
  if(maintainer){form.append(googleSignIn());aside.append(p('Google sign-in works only after it is configured and linked from your existing admin or maintainer account. Use your existing staff account.','small'));}
  if(params.get('auth_error'))main.append(p(params.get('auth_error'),'form-message error'));
  main.append(el('div',{class:'workspace-columns auth-columns'},form,aside));
}

function newPasswordHint(){return 'Use 9–256 characters, at least one uppercase letter (A–Z) and one ASCII special character, such as ! or /.';}
function newPasswordProblems(value){
  const problems=[],length=Array.from(value).length;
  if(length<9)problems.push('Use at least 9 characters.');
  if(length>256)problems.push('Use no more than 256 characters.');
  if(!/[A-Z]/.test(value))problems.push('Add an uppercase letter (A–Z).');
  if(!/[!-/:-@[-`{-~]/.test(value))problems.push('Add an ASCII special character, such as ! or /.');
  return problems;
}
function newPasswordProblem(value){
  return newPasswordProblems(value).join(' ');
}
function configureNewPassword(control){
  control.dataset.newPassword='true';control.autocomplete='new-password';control.minLength=9;
  // HTML maxlength counts UTF-16 units. The code-point check above is authoritative;
  // 512 units leave room for every valid 256-code-point password.
  control.maxLength=512;
}

function loginFailureDetails(error){
  const details=error?.details;
  if(!details||!Number.isInteger(details.login_attempts_remaining))return [];
  const remaining=Math.max(0,Math.min(10,details.login_attempts_remaining));
  const retry=Number.isFinite(details.retry_after)?Math.max(0,Math.ceil(details.retry_after)):0;
  const recovery=link('Reset your password',authHref('forgot-password'),'text-link');
  if(!details.login_locked&&remaining>5)return [recovery];
  return [p(details.login_locked?'Remaining sign-in lock time: '+Math.ceil(retry/60)+' minutes. Browsing and password recovery remain available.':remaining+' sign-in attempts remain before a 60-minute lock for this connection.'),recovery];
}

function requestPasswordResetPage() {
  if(!isHomeAccount){guestReadOnlyPage();return;}
  title('Reset your password.','Use your verified institutional account email, or the Google email already linked to an admin or maintainer account. If eligible, you will receive a one-time link valid for 15 minutes.');
  const form=el('form',{class:'form-grid auth-form'},field('email','Verified account or linked Google email','email','','Enter the existing account email, rather than a local account name. An email match alone never links accounts.',true),el('div',{class:'form-actions full'},el('button',{class:'button button-primary',type:'submit'},'Send password reset link')));
  form.addEventListener('submit',event=>{
    event.preventDefault();const email=formData(form).email.trim();
    act(async()=>{
      await api('/auth/password-reset/request','POST',{email});
      form.reset();
      feedback('If an eligible account exists, a password-reset link will be sent to its verified email. The link expires in 15 minutes.',false,mailDeliveryGuidance());
    });
  });
  main.append(form,el('div',{class:'form-actions'},link('Back to sign in',authHref('login')),link('Back to main page','/')));
}

function completePasswordResetPage() {
  if(!isHomeAccount){guestReadOnlyPage();return;}
  if(!passwordResetToken){
    title('Open your password reset link.','This page needs the one-time link from your email. If you refreshed or the link is no longer available, request a new one.');
    main.append(link('Request a new password reset link',authHref('forgot-password')),link('Back to main page','/'));
    return;
  }
  title('Choose a new password.',newPasswordHint()+' This resets your password and signs out existing browser sessions. Your account role and any linked Google identity stay unchanged.');
  const form=el('form',{class:'form-grid auth-form'},field('newpassword','New password','password','',newPasswordHint(),true),field('confirm_password','Confirm new password','password','','Enter the same new password again.',true),el('div',{class:'form-actions full'},el('button',{class:'button button-primary',type:'submit'},'Reset password')));
  for(const name of ['newpassword','confirm_password']){
    configureNewPassword(form.querySelector('[name='+name+']'));
  }
  form.addEventListener('submit',event=>{
    event.preventDefault();const values=formData(form);
    if(values.newpassword!==values.confirm_password){feedback('The new passwords do not match. Enter the same password in both fields.',true);return;}
    act(async()=>{
      await api('/auth/password-reset/complete','POST',{token:passwordResetToken,newpassword:values.newpassword});
      passwordResetToken='';form.reset();main.replaceChildren();
      session={...session,user:null,csrf:''};
      for(const notice of document.querySelectorAll('[data-visitor-notice]'))notice.hidden=false;
      const guestActions=document.getElementById('contributor-guest-actions');if(guestActions)guestActions.hidden=false;
      const memberActions=document.getElementById('contributor-member-actions');if(memberActions)memberActions.hidden=true;
      navigate('/password-reset-complete.html');
    });
  });
  main.append(form,el('div',{class:'form-actions'},link('Request a new password reset link',authHref('forgot-password')),link('Back to main page','/')));
}

function policyAcknowledgement(name='accept_terms') {
  const row=check(name,'I have read the privacy notice and agree to the ELVIA terms.',false,true);
  const legal=(label,path)=>el('a',{href:path,target:'_blank',rel:'noopener noreferrer','aria-label':label+' (opens in a new tab)'},label+' ↗');
  row.classList.add('full');row.querySelector('span').append(' ',legal('Privacy','privacy.html'), ' · ',legal('Terms','terms.html'));
  return row;
}
function googleSignIn(){
  const area=el('section',{class:'google-signin full'},el('h2',{},'Or use your Google account'));
  if(session.google.enabled){
    const consent=policyAcknowledgement('google_terms');
    const action=button('Continue with Google',()=>{
      if(!consent.querySelector('input').checked){feedback('Read and acknowledge the privacy notice and terms before continuing with Google.',true);consent.querySelector('input').focus();return;}
      act(async()=>{const result=await api('/auth/google/start','POST',{accept_terms:true});navigate(result.authorization_url);});
    });
    // This consent belongs to the Google action, not the email form submission.
    consent.querySelector('input').required=false;consent.querySelector('.field-requirement')?.remove();
    area.append(consent,action,p('Google sign-in is restricted to already linked admins and maintainers. Continue in a regular browser.','small'));
  } else {
    area.append(el('button',{type:'button',class:'button button-secondary',disabled:true},'Continue with Google'),p(session.google.message+' Use your existing admin or maintainer account and password.','small'));
  }
  return area;
}
function quotaNote(){
  if(!me?.quota||me.quota.unlimited)return null;
  const q=me.quota;
  return p(`Today: ${Math.max(0,2-q.used.new_submit)} of 2 paper submissions left; ${Math.max(0,1-q.used.review_claim)} of 1 review claims and ${Math.max(0,1-q.used.review_submit)} of 1 review submissions left. Resets at midnight America/Chicago.`,'small quota-note');
}

function applicationPage() {
  if(gate())return;
  if(isStaff()){title('You are signed in as '+session.user.role+'.');main.append(p('Reviewer applications use a separate reviewer account.'),link('Open management',href('view=maintainer')));return;}
  if(me.application?.status==='approved'){title('You are ready to contribute.');main.append(link('Choose a contribution',href()));return;}
  title('Apply once to review others’ work.','Share the subjects you can examine carefully. You can already submit your own paper analysis without this application.');
  main.append(steps(2));
  const old=me.application?.profile||{};
  const form=el('form',{class:'form-grid'});
  form.append(field('position','Current position','select',old.position||'','',true,['Doctoral researcher','Master’s student','Postdoctoral researcher','Faculty member','Research scientist','Independent researcher','Other'].map(x=>[x,x])),field('institution','Institution or organization','text',old.institution||'','Use your current affiliation.',true));
  const expertise=field('expertise','Relevant expertise','textarea',old.expertise||'','Name the topics or methods you can check. One or two sentences are enough.',true);expertise.classList.add('full');form.append(expertise);
  if(!/\.(edu|edu\.[a-z]{2}|ac\.[a-z]{2})$/i.test(session.user.login)){const background=field('eligibility_note','Research background','textarea',old.eligibility_note||'','Your email is outside an academic domain. Briefly explain how your background can be assessed.',true);background.classList.add('full');form.append(background);}
  form.append(optionalFields('Add a research profile (optional)',field('profile_url','Research profile','url',old.profile_url||'','An institutional page, ORCID page or personal research website.')));
  form.append(p(`Applying as ${session.user.name} · ${session.user.login}`,'small full'),el('div',{class:'form-actions full'},el('button',{class:'button button-primary',type:'submit'},me.application?'Resubmit application':'Send application')));
  trackDirty(form);
  form.addEventListener('submit',event=>{event.preventDefault();const data=formData(form);act(async()=>{await api('/application','POST',data);navigate(href('view=my-work'));});});
  const aside=el('aside',{class:'side-note'},el('section',{},el('h2',{},'What happens next?'),p('An admin or maintainer reviews your background and areas of expertise. You can check the decision in My work. If more information is needed, the request appears there.'),p('Email verification confirms access to your mailbox. Your research background and expertise are reviewed separately. Application decisions appear in My work.')),el('section',{},el('h2',{},'Credit is your choice.'),p('For each accepted contribution, choose whether your name appears in the contributor directory. You can keep a contribution record private.')));
  if(me.application?.note)main.append(p(me.application.note,'form-message'));
  main.append(el('div',{class:'workspace-columns'},form,aside));
}

function applicationStatus() {
  if(!session.user)return el('div',{class:'status-box'},el('h2',{},'You are welcome to explore.'),p('Browsing is open to visitors. To contribute, return to the main page to register or sign in.'),link('Back to main page',mainPageHref()));
  if(isStaff())return el('div',{class:'status-box'},el('h2',{},'Your management workspace is ready.'),p('Manage applications and submissions. Contributor daily limits do not apply to your account.'),link('Open management',href('view=maintainer')));
  const app=me.application;
  return el('div',{class:'status-box compact-status'},status(app?.status==='approved'?'Reviewer access approved':'Paper submissions open'),p(app?.status==='approved'?'You can submit your own analyses and review existing work.':app?.status==='pending'?'Your reviewer application is pending. You can still submit your own analyses.':'Your account can submit papers now. Apply once to review other contributions.'),quotaNote(),app?.note?p(app.note):null,app?.status!=='approved'?link(app?'View reviewer application':'Apply to review',href('view=apply')):null);
}

async function homePage() {
  title('Take a closer look.','Share your own analysis, or review an existing one. Both manual and AI-assisted work are welcome.');
  if(session.user)main.append(applicationStatus());
  const approved=isStaff()||(session.user?.role==='reviewer'&&me.application?.status==='approved');
  const startNew=()=>act(async()=>{
    const item=await api('/contributions','POST',{kind:'new'});
    if(selectedCase)await api('/contributions/'+item.id,'PUT',{version:item.version,data:{...item.data,...draftIdentity(selectedCase)}});
    navigate(href('review='+encodeURIComponent(item.id)));
  });
  main.append(el('div',{class:'track-options'},
    el('section',{},el('h2',{},'Submit your own analysis'),p(isStaff()?'Bring an eligible paper or arXiv preprint and upload your review ZIP. Your management role has no daily submission limit.':'Verify an institutional email and bring an eligible paper or arXiv preprint. Upload your review ZIP. Up to two paper submissions per day; no reviewer application needed.'),session.user?button('Start a new analysis',startNew,true):null),
    el('section',{},el('h2',{},'Review an existing analysis'),p(isStaff()?'Check the reasoning in an AI or contributor analysis. Your management role can review work without an application or daily limit.':'Check the reasoning in an AI or contributor analysis. Apply once with your background, then claim and submit up to one review per day.'),approved?link('See available questions','#available','button button-secondary'):session.user?link(me.application?'View reviewer application':'Apply for reviewer access',href('view=apply'),'button button-secondary'):null)));
  main.append(el('div',{class:'eligibility-intro'},el('strong',{},'Check a venue before preparing your report.'),p('Chemistry / biological science: most recent verifiable JIF > 10 OR the 2026 TOP journal list (Zone 1 + Top). Computer science: CCF A conferences. Mathematics: the expanded journal list. Verified arXiv preprints: all fields, no venue threshold.','small'),link('Search journals, conferences and arXiv',href('view=scope'))));
  main.append(el('div',{class:'section-heading',id:'available'},el('h2',{},'Available questions'),p('Questions open for contributor review.','small')));
  const {tasks}=await api('/tasks');
  const list=el('div',{class:'paper-list'});
  for(const task of tasks) list.append(el('article',{class:'paper-item'},el('div',{},el('div',{class:'paper-meta'},el('span',{},task.topic),task.synthetic?el('span',{},'Fictional practice task'):el('span',{},'Submitted analysis · review pending')),el('h3',{},task.title),p(task.question)),el('div',{class:'paper-action'},status(task.availability),link(task.my_contribution?'Continue your review':'View question',task.my_contribution?itemLink(task.my_contribution):href('paper='+task.id),'button button-secondary'))));
  main.append(list,p('Review questions appear here as submissions are accepted. Browse the 300-paper Atlas from the main navigation.','small boundary-note'),el('div',{class:'form-actions'},link('View maintainer final versions',href('view=finals'))),el('div',{class:'track-footer'},el('h2',{},'Useful work deserves clear credit.'),p('A confirmation, a clarification and a carefully supported concern can each be a meaningful contribution. Accepted work receives a versioned contribution record; named contributors can appear in the directory.'),link('How contribution credit works',href('view=contributors'))));
}

async function taskPage(id) {
  const {tasks}=await api('/tasks');const task=tasks.find(t=>t.id===id);
  if(!task)throw new Error('This question could not be found.');
  main.append(link('Back to available questions',href()+'#available','back-link'));
  title(task.title,task.question);
  main.append(p(task.synthetic?'Fictional practice task · excluded from research statistics':task.topic+' · independent review pending','small'),el('section',{class:'source-context'},el('h2',{},'The question in context'),p(task.context)));
  if(!session.user){main.append(applicationStatus());return;}
  if(task.my_contribution){main.append(link('Continue your review',itemLink(task.my_contribution),'button button-primary'));return;}
  if(task.maintainer_contribution){main.append(link('Review or revise the current work',itemLink(task.maintainer_contribution),'button button-primary'));return;}
  if(task.final_contribution){main.append(link('Read the final version or request a change',href('final='+task.final_contribution),'button button-primary'));return;}
  if(task.availability!=='Available'){main.append(p('This question already has a contributor. Choose another available question.','form-message'));return;}
  if(!session.user||(!isStaff()&&me.application?.status!=='approved')){main.append(applicationStatus());return;}
  const form=el('form',{},check('conflict','I have no authorship, collaboration or other conflict that would prevent an independent review.',false,true),el('div',{class:'form-actions'},el('button',{type:'submit',class:'button button-primary'},'Claim this review')));
  form.addEventListener('submit',event=>{event.preventDefault();act(async()=>{const item=await api('/contributions','POST',{kind:'review',task_id:id,conflict_clear:true});navigate(itemLink(item.id));});});
  main.append(quotaNote(),form);
}

function myWorkPage() {
  if(gate())return;
  title('Your work, ready to continue.','Saved drafts, decisions and return links stay together here.');
  main.append(applicationStatus());
  if(me.amendments?.length)main.append(el('section',{class:'amendment-list'},el('h2',{},'Your amendment requests'),me.amendments.map(a=>el('article',{class:'amendment-entry'},status(amendmentStatus(a.status)),p(a.reason),a.decision?p(a.decision,'form-message'):null,link('Open the final version',href('final='+a.contribution_id)),p('Requested '+fmt(a.created),'small')))));
  if(!me.contributions.length){main.append(el('section',{class:'empty-state'},el('h2',{},'Start with one question.'),p(me.application?.status==='pending'?'Your reviewer application is pending. You can start your own analysis while you wait.':'Submit your own analysis now, or apply to review an existing one.'),link('Browse contribution options',href())));return;}
  const list=el('div',{class:'paper-list'});
  for(const item of me.contributions)list.append(el('article',{class:'paper-item'},el('div',{},el('div',{class:'paper-meta'},el('span',{},item.kind==='review'?'Review an analysis':'New analysis'),item.data.synthetic?el('span',{},'Practice contribution'):null),el('h2',{},item.data.title||'Untitled analysis'),p('Last saved '+fmt(item.updated),'small'),item.note?p(item.note):null),el('div',{class:'paper-action'},status(labels[item.status]),link(['draft','needs_changes'].includes(item.status)?'Continue draft':'Open contribution',itemLink(item.id),'button button-secondary'))));
  main.append(list);
}

function section(number,heading,...children) {return el('fieldset',{class:'form-section',id:'section-'+number},el('legend',{},el('span',{class:'section-number'},String(number).padStart(2,'0')),heading),...children);}
const arxivDraft=form=>scopeNorm(form.querySelector('[name=venue]')?.value||'')==='arxiv'&&/^https:\/\/(?:(?:www\.)?arxiv\.org\/(?:abs|pdf|html)\/|(?:dx\.)?doi\.org\/10\.48550\/arxiv\.)/i.test(form.querySelector('[name=source_url]')?.value||'');
const admissionLabels={pass:'Eligibility check passed',pending:'Eligibility needs verification',blocked:'Outside the current requirements'};
function scopeRule(fieldName,overview=false) {
  const journalRule='Required: most recent verifiable JIF > 10 OR inclusion in the 2026 TOP journal list (Zone 1 + Top). Either route qualifies.';
  const rules={chemistry:journalRule,biological_science:journalRule,computer_science:'Required: a CCF 2026 A-conference full or regular main-conference paper. Workshops, short papers, demos and Findings are excluded.',mathematics:'Required: a journal on the expanded ELVIA mathematics list.',others:'Not open for journals or conferences yet. Verified arXiv preprints are accepted in all fields.'};
  const info=scopePolicy.fields.find(x=>x.id===fieldName);
  return el('div',{class:'eligibility-rules'},el('strong',{},rules[fieldName]||'Check the collection requirements before preparing a report.'),fieldName==='others'?null:p(info?.description||'Chemistry and biological science: most recent verifiable JIF > 10 or the 2026 TOP journal list (Zone 1 + Top). Computer science: CCF A conferences. Mathematics: the expanded journal list.','small'),fieldName==='others'?p('We are sorry we cannot cover more journals and conferences yet. Our arXiv route remains open across fields, and we hope to expand as review capacity grows.'):overview?null:p('This is an initial collection limit, not a judgment on work outside it. Thank you for helping us keep the review queue manageable.','small'),overview?(fieldName==='others'?null:link(fieldName==='computer_science'?'See the conference list':fieldName==='mathematics'?'See the journal list':'See TOP and JIF sources',fieldName==='computer_science'?'#conference-list':fieldName==='mathematics'?'#journal-list':'#top-list')):link('Read the requirements and venue lists',href('view=scope')));
}
function admissionPanel(result) {
  if(!result)return p('Paper identity and eligibility are checked when you submit. You can also check now, before preparing your report.','small');
  const box=el('section',{class:'admission-result '+result.status,tabindex:'-1'},el('h2',{},result.stale?'Check needs refreshing':admissionLabels[result.status]),p(result.manual?'Verified against evidence by '+result.verifier+'.':'Checked '+fmt(result.checked_at)+' · scope '+result.policy_version,'small'));
  if(result.stale)box.append(p('The saved check is older than 24 hours. Submission will refresh it.'));
  box.append(el('ul',{},result.reasons.map(r=>el('li',{},r.message))));
  if(result.metadata?.title)box.append(p('Detected title: '+result.metadata.title),p('Detected venue: '+result.metadata.venue,'small'));
  if(result.network_note)box.append(p(result.network_note,'small'));
  if(result.evidence?.length)box.append(el('div',{class:'admission-sources'},result.evidence.map(e=>link(e.label,e.url))));
  if(result.status==='pending')box.append(p('Reports awaiting eligibility verification cannot be accepted or sent to another reviewer until the requirements are confirmed.','small'));
  box.append(p('This checks source identity and collection scope. It does not assess whether the paper or review is scientifically correct.','small'));
  return box;
}
const scopeNorm=nameNorm;
const listedTop=name=>uniqueNameMatch(name,scopePolicy.top_journals||[]);
function journalScopeEntries(){
  const entries=new Map();
  for(const top of scopePolicy.top_journals||[])entries.set(scopeNorm(top.name),{...top,topRecord:top,group:'Chemistry / biological science · '+top.group});
  for(const metric of scopePolicy.metric_records){
    const key=scopeNorm(listedTop(metric.journal)?.name||metric.journal),existing=entries.get(key);
    if(!existing)entries.set(key,{name:metric.journal,aliases:metric.aliases||[],group:'Chemistry / biological science',metric,source:metric.source});
    else if(!existing.metric||metric.year>existing.metric.year)existing.metric=metric;
  }
  return [...entries.values()].map(x=>{
    const m=x.metric,top=x.topRecord;
    const detail=top?`Eligible for chemistry / biological science · ${top.year} TOP journal list (Zone 1 + Top).`:(m.value>10?'Eligible':'No qualifying record')+` for chemistry / biological science · JIF ${m.value} (${m.year}).`;
    const extra=top?(m?` JIF ${m.value} (${m.year}); the TOP route qualifies independently.`:' No JIF is required for this route.'):m.value>10?' Most recent verified metric.':' JIF must exceed 10, or the journal must be on the current TOP list.';
    return {...x,detail:detail+extra,blocked:!top&&m.value<=10};
  });
}
function scopeSearch(){
  const input=field('scope_search','Search a journal, conference or arXiv','search','','Try JASA, numerical analysis, NeurIPS or Nature. Case and punctuation do not matter; Greek letters and accented names are supported.');
  const results=el('div',{class:'scope-search-results','aria-live':'polite'});
  const entries=[
    {name:'arXiv',aliases:['arxiv.org','preprints'],group:'All fields',detail:'Eligible preprint route. No JIF or conference threshold; the official identifier, version and title must match.',source:'https://arxiv.org/'},
    ...scopePolicy.math_journals.map(x=>({...x,detail:'Eligible mathematics journal · '+x.group})),
    ...scopePolicy.ccf_conferences.map(x=>({...x,detail:'Eligible computer science conference · CCF A. Full or regular main-conference papers only.',source:scopePolicy.ccf_source})),
    ...journalScopeEntries()
  ];
  const render=()=>{
    const query=input.querySelector('input').value;
    if(!scopeNorm(query)){results.replaceChildren(p('Search the current scope without creating an account. Paper identity is checked again when you submit.','small'));return;}
    const matches=entries.filter(x=>[x.name,x.full_name||'',x.group||'',...(x.aliases||[])].some(value=>nameContains(value,query)));
    results.replaceChildren(p(matches.length?`${matches.length} matching ${matches.length===1?'entry':'entries'}`:'No verified match in the current scope.','search-count'),...matches.slice(0,50).map(x=>el('article',{class:'scope-search-row'+(x.blocked?' outside-scope':'')},el('h3',{},x.name),p(x.detail),link('Source',x.source))));
    if(!matches.length)results.append(p('Try the full name or a common abbreviation. Chemistry and biological science need either a verifiable JIF > 10 or an entry in the current TOP journal list. A missing search result is not proof that a journal has no qualifying JIF; the paper check also consults supported publisher sources. Mathematics and computer science use their published lists.','small'));
    if(matches.length>50)results.append(p('Showing the first 50. Add more of the name to narrow the results.','small'));
  };
  input.querySelector('input').addEventListener('input',render);render();
  return el('section',{class:'scope-search'},input,results);
}
function scopePage(){
  title('Check the scope before you start.','Find an eligible venue before spending time on your report. These limits keep the current review queue manageable.');
  main.append(scopeSearch(),el('div',{class:'arxiv-policy'},el('h2',{},'arXiv preprints are welcome.'),p('All fields are eligible through the official arXiv route, with no JIF or conference requirement. Enter arXiv as the venue and use the paper’s arxiv.org abstract/PDF link or arXiv DOI. We verify the identifier and title, and label the source as a preprint.')));
  main.append(p('The selected field is used only for intake. It does not determine later classification.','small'),el('div',{class:'scope-rules-list'},scopePolicy.fields.map(x=>el('section',{},el('h2',{},x.label),scopeRule(x.id,true)))));
  main.append(p('Chemistry and biological science: either journal route is enough. Zone 1 alone or a Top label alone does not meet the TOP-list rule. Source identity must still match. If neither route can be established, submission is blocked; a temporary identity lookup failure can be retried.','boundary-note'));
  main.append(el('section',{class:'scope-catalog',id:'top-list'},el('h2',{},'2026 TOP journal list'),p(`${scopePolicy.top_journals.length.toLocaleString()} entries with both major-category Zone 1 and Top status. Search by journal name above. The list includes related disciplines for interdisciplinary chemistry and biology; other intake tracks keep their own requirements.`),el('details',{class:'paper-details'},el('summary',{},'List coverage and sources'),p(scopePolicy.top_policy.coverage),p('Checked '+scopePolicy.top_policy.checked_on+'. Public snapshots can contain errors; conflicting records are held out until verified. This list does not establish the quality of an individual paper.','small'),...scopePolicy.top_policy.sources.map(x=>link(x.label,x.url)))));
  for(const [heading,entries,description] of [[`Computer science: ${scopePolicy.ccf_conferences.length} CCF A conferences`,scopePolicy.ccf_conferences,'Seventh edition, 2026. Full or regular main-conference papers.'],[`Mathematics: ${scopePolicy.math_journals.length} selected journals`,scopePolicy.math_journals,'An expanded project selection across pure and applied mathematics, probability, statistics and specialist branches. This is an intake list, not a universal ranking.']]){
    const area=el('section',{class:'scope-catalog',id:entries===scopePolicy.ccf_conferences?'conference-list':'journal-list'},el('h2',{},heading),p(description));
    for(const group of [...new Set(entries.map(x=>x.group))])area.append(el('details',{class:'paper-details'},el('summary',{},group+' ('+entries.filter(x=>x.group===group).length+')'),el('ul',{},entries.filter(x=>x.group===group).map(x=>el('li',{},el('strong',{},x.name),x.full_name?' — '+x.full_name:null,x.aliases?.length?p('Also recognized: '+x.aliases.join(', '),'small'):null,x.source?el('span',{},' · ',link(x.source_label||'Journal identity',x.source)):null)))));
    main.append(area);
  }
  main.append(el('section',{class:'scope-catalog',id:'metric-sources'},el('h2',{},'Use the most recent verifiable JIF.'),p('The threshold is strictly greater than 10. If the latest year is unavailable, a dated, verifiable earlier JIF can qualify. We display the year used. An available newer value takes precedence, even if an older one was higher. Five-year JIF and CiteScore do not substitute.'),p('Metric coverage is partial. We use supported publisher checks and dated records. A journal on the 2026 TOP list qualifies without a JIF. Otherwise a verifiable JIF > 10 is required. The maintainer can add official evidence when a source was missed.'),link('JCR release information',scopePolicy.jcr_source),link('CCF seventh-edition scope',scopePolicy.ccf_source),el('details',{class:'paper-details'},el('summary',{},'View dated metric records'),el('ul',{},scopePolicy.metric_records.map(m=>el('li',{},`${m.journal}: ${m.value} (${m.year}) · `,link('Source',m.source))))),p('Policy '+scopePolicy.version,'small')));
  if(session.user)main.append(link('Choose your contribution',href(),'button button-primary'));
}

async function contributionPage(id) {
  if(gate())return;
  let item=await api('/contributions/'+id);
  const admin=isStaff();
  main.append(link(admin?'Back to management':'Back to My work',href(admin?'view=maintainer':'view=my-work'),'back-link'));
  if((admin&&item.owner!==session.user.id)||item.final_revision||!['draft','needs_changes'].includes(item.status)){await summaryPage(item,admin);return;}
  title(item.kind==='review'?'Share your review.':'Bring a paper into the conversation.','Add a short summary and upload your report. Keep the detailed reasoning and checks in the ZIP.');
  if(admin)main.append(link(session.user.role==='maintainer'?'Write a revision or final decision':'Write an ordinary revision',href('revise='+id)));
  if(item.note)main.append(el('div',{class:'form-message'},el('strong',{},'Changes requested: '),item.note));
  const data=item.data;
  const form=el('form',{class:'review-form'});
  const paper=section(1,'Paper');
  if(data.scope)paper.append(p(data.scope,'form-message'));
  let access,sourceURL,sourceUpload,sourceInput,drawSource,updateField;
  const admissionBox=el('div',{class:'admission-slot','aria-live':'polite'});
  const drawAdmission=()=>admissionBox.replaceChildren(admissionPanel(item.admission));
  if(item.task)paper.append(p(item.task.title,'task-title'),el('details',{class:'paper-details'},el('summary',{},'Read the source analysis'),p(item.task.context)),item.task.synthetic?p('Fictional practice task · excluded from research statistics.','small'):null);
  else {
    const areaField=field('field','Field for eligibility','select',data.field||'','Used only for intake checking, not later classification.',true,scopePolicy.fields.map(x=>[x.id,x.label]));
    const rules=el('div',{'aria-live':'polite'});
    const venueField=field('venue','Journal or conference','text',data.venue||'','Use a journal name, conference acronym or arXiv. Case, spacing and punctuation do not affect matching. Greek letters, extended names and digits are preserved.',true);
    const venueList=el('datalist',{id:'venue-suggestions'});venueField.querySelector('input').setAttribute('list','venue-suggestions');
    updateField=()=>{const selected=areaField.querySelector('select').value;rules.replaceChildren(scopeRule(selected));const entries=selected==='mathematics'?scopePolicy.math_journals:selected==='computer_science'?scopePolicy.ccf_conferences:journalScopeEntries();venueList.replaceChildren(el('option',{value:'arXiv'},'arXiv preprint'),...entries.map(x=>el('option',{value:x.name},x.full_name||x.name)));const submit=form.querySelector('button[type=submit]');if(submit)submit.disabled=selected==='others'&&!arxivDraft(form);if(arxivDraft(form))rules.replaceChildren(el('div',{class:'eligibility-rules'},el('strong',{},'arXiv route: all fields accepted, no venue threshold.'),p('The official identifier, version and title will be checked. The source is labeled as a preprint.','small')));};
    areaField.querySelector('select').addEventListener('change',()=>{updateField();item.admission=null;drawAdmission();});updateField();
    paper.append(areaField,rules,field('title','Paper title','text',data.title||'','',true),venueField,venueList);
    access=field('source_access','Is the paper publicly accessible?','select',data.source_access||'','Include access to any supplementary materials.',true,[['public','Yes — an official public source is available'],['upload','No — I will upload the paper and materials']]);
    sourceURL=field('source_url','Official paper URL','url',data.source_url||'','Use an HTTPS publisher/conference landing page, DOI URL or official arXiv link. A paywalled article still needs its official landing page for identity checking.',true);
    sourceInput=el('input',{type:'file',id:'source-file',accept:'.pdf,.zip,application/pdf,application/zip','data-label':'Paper and supplementary materials'});
    const sourceStatus=el('div',{class:'package-status','aria-live':'polite'});
    sourceUpload=el('div',{class:'field attachment-input'},el('label',{for:'source-file'},'Paper & supplementary materials',el('span',{class:'field-requirement'},'Required')),p('One PDF or ZIP, up to 10 MB. Include the paper and all available supplements; use a ZIP for separate files.','hint'),sourceInput,sourceStatus);
    drawSource=()=>{sourceStatus.replaceChildren(item.source_file?el('div',{},link(item.source_file.name,'/api/source-files/'+item.source_file.id),p('Saved privately with your contribution.','small')):p('No source material uploaded yet.','small'));sourceInput.required=access.querySelector('select').value==='upload'&&!item.source_file;};
    const updateAccess=()=>{const selected=access.querySelector('select').value;sourceUpload.hidden=selected!=='upload';sourceInput.disabled=sourceUpload.hidden;drawSource();clearInactiveErrors();};
    access.querySelector('select').addEventListener('change',updateAccess);updateAccess();
    paper.append(sourceURL,access,sourceUpload,p('Title and venue are checked against public metadata. Your selected field and access to the paper and supplements are confirmed during intake. Uploaded files stay private.','small'),el('div',{class:'form-actions'},button('Check paper eligibility',()=>{const values=readData();act(async()=>{await save(values);admissionBox.replaceChildren(p('Checking the official title, venue and eligibility…','form-message'));try{item=await api('/contributions/'+id+'/check','POST',{version:item.version,refresh:true});}finally{drawAdmission();}admissionBox.querySelector('[tabindex]')?.focus();});})),admissionBox);
    drawAdmission();
    paper.addEventListener('input',event=>{if(['title','venue','source_url','source_access'].includes(event.target.name)){item.admission=null;drawAdmission();updateField();}});
  }
  const review=section(2,'Review',field('assessment','Your assessment','select',data.assessment||'','',true,Object.entries(assessments)),field('summary','Review summary','textarea',data.summary||data.reasoning||'','A few sentences: what you checked and your main conclusion or uncertainty. At least 40 characters.',true));
  const reportInput=el('input',{type:'file',id:'package',accept:'.zip,application/zip','data-label':'Review report ZIP'});
  const packageStatus=el('div',{class:'package-status','aria-live':'polite'});
  function drawPackage(){reportInput.required=!item.package;packageStatus.replaceChildren(item.package?el('div',{},link(item.package.name,'/api/packages/'+item.package.id),p(`${(item.package.size/1024).toFixed(1)} KB · ${item.package.manifest.length} files · saved with your contribution`,'small'),el('details',{class:'paper-details'},el('summary',{},'View package contents'),el('ul',{},item.package.manifest.map(f=>el('li',{},f.name))))):p('No report uploaded yet.','small'));}
  drawPackage();
  review.append(el('div',{class:'field attachment-input'},el('label',{for:'package'},'Review report',el('span',{class:'field-requirement'},'Required')),p('ZIP only, up to 10 MB. Include the report and verification files. Put source locations, reasoning, checks and limitations in the report.','hint'),reportInput,packageStatus));
  const ai=aiDisclosureFields(data,'Did you use AI for this contribution?');
  const primaryRole=item.kind==='review'?'Verification':'Analysis';
  const roles=el('div',{class:'role-choices'},el('p',{class:'field-label'},'Additional contribution roles (optional)'),session.policy.roles.filter(role=>role!==primaryRole).map(role=>check('role-'+role,role,(data.roles||[]).includes(role))));
  const credit=optionalFields('Credit preferences (optional)',p('Your work is recorded as '+primaryRole.toLowerCase()+'. Named credit is optional; your email and application stay private.','small'),roles,check('named_credit','Show my name in the contributor directory after acceptance.',data.credit==='named'),!item.task?check('synthetic','This is a fictional practice submission.',data.synthetic):null);
  const disclosure=section(3,'AI use & credit',ai,credit);
  const attest=check('attest','I have no relevant conflict of interest. I have included the required source materials and take responsibility for the report and AI disclosure.',false,true);
  const saveNote=p('Draft loaded · '+fmt(item.updated),'draft-status');
  function readData(){const values={...data,...formData(form)};values.title=item.task?.title||values.title;values.roles=[primaryRole,...session.policy.roles.filter(r=>form.querySelector(`[name="role-${r}"]`)?.checked)];values.credit=form.querySelector('[name=named_credit]').checked?'named':'private';values.conflict_clear=form.querySelector('[name=attest]').checked;values.synthetic=item.task?!!item.task.synthetic:form.querySelector('[name=synthetic]').checked;return values;}
  async function save(values){item=await api('/contributions/'+id,'PUT',{version:item.version,data:values});dirty=false;saveNote.textContent='Draft saved · '+fmt(item.updated);}
  function upload(input,source=false){input.addEventListener('change',()=>{const file=input.files[0];if(!file)return;const values=readData();act(async()=>{if(!(source?/\.(pdf|zip)$/i:/\.zip$/i).test(file.name)||file.size>session.policy.max_zip_bytes)throw new Error(source?'Choose a PDF or ZIP no larger than 10 MB.':'Choose a ZIP no larger than 10 MB.');await save(values);item=await api('/contributions/'+id+(source?'/source':'/package'),'POST',file,{'Content-Type':'application/octet-stream','X-Filename':encodeURIComponent(file.name),'X-Version':String(item.version)});input.value='';source?drawSource():drawPackage();saveNote.textContent='Draft and upload saved · '+fmt(item.updated);});});}
  upload(reportInput);if(sourceInput)upload(sourceInput,true);
  const saveButton=button('Save draft',()=>{const values=readData();act(async()=>{await save(values);feedback('Your draft is saved. Return with the same link and account.');});});
  form.append(quotaNote(),p('Required fields are marked. You can save an incomplete draft.','small'),paper,review,disclosure,attest,el('div',{class:'form-actions'},saveButton,el('button',{type:'submit',class:'button button-primary'},'Submit contribution')),saveNote);
  form.querySelector('[name=summary]').minLength=40;
  form.addEventListener('submit',event=>{event.preventDefault();const values=readData();act(async()=>{await save(values);if(item.kind==='new')admissionBox.replaceChildren(p('Checking the official title, venue and eligibility before submission…','form-message'));try{await api('/contributions/'+id+'/submit','POST',{version:item.version,attest:true});navigate(itemLink(id));}catch(error){if(item.kind==='new'){item=await api('/contributions/'+id);drawAdmission();}throw error;}});});
  trackDirty(form);
  const returnURL=new URL(itemLink(id),location.href).href;
  const aside=el('aside',{class:'review-support'},el('section',{},el('h2',{},'Come back when you are ready.'),p('Save your draft, then sign in to the same account to continue from this link.'),el('a',{href:returnURL,class:'return-link'},returnURL),button('Copy return link',()=>copy(returnURL))),el('section',{},el('h2',{},'Keep the detail in your report.'),p('Include the passage you examined, the reasoning, checks and limits. The summary helps readers decide where to look.'),link('Paper','#section-1'),link('Review','#section-2'),link('AI use & credit','#section-3')));
  if(item.task?.source_id){const pack=await api('/task-source/'+item.task.id);aside.prepend(el('section',{},el('h2',{},'Materials to review'),link('Download original review ZIP','/api/packages/'+pack.id),pack.source_file?link('Download paper & supplementary materials','/api/source-files/'+pack.source_file.id):null,pack.source_url?link('Open published paper',pack.source_url):null));}
  aside.append(el('details',{class:'paper-details'},el('summary',{},item.kind==='review'?'Release this task':'Set this draft aside'),p('Saved notes remain in My work.'),button('Release saved draft',()=>act(async()=>{await api('/contributions/'+id+'/release','POST',{version:item.version});navigate(href('view=my-work'));}))));
  main.append(el('div',{class:'review-layout'},form,aside));
  if(updateField)updateField();
}

async function copy(value) {try{await navigator.clipboard.writeText(value);feedback('Link copied.');}catch{feedback('Select and copy the visible return link.');}}
function showRecord(container,data) {
  const fields=data.summary?[['title','Paper'],['venue','Venue'],['summary','Review summary']]:[['title','Paper'],['venue','Venue'],['source_version','Source version'],['location','Passage examined'],['scope','Question examined'],['reasoning','Reasoning'],['verification','Checks performed'],['limits','Limits']];
  for(const [key,label] of fields)if(data[key])container.append(el('section',{},el('h2',{},label),p(data[key])));
  if(data.source_url&&/^https?:\/\//.test(data.source_url))container.append(link('Open published source',data.source_url));
  container.append(el('section',{},el('h2',{},'Assessment'),p(assessments[data.assessment]||'Not yet selected')),el('section',{},el('h2',{},'AI disclosure'),p(data.ai_used==='yes'?data.ai_model+' · '+data.ai_details:data.ai_used==='no'?'Completed manually; no AI declared.':'Not yet declared.')),el('section',{},el('h2',{},'Attribution'),p(data.record_author?data.record_author+' · '+(data.record_author_role||'maintainer')+' revision':(data.roles||[]).join(', ')+' · '+(data.credit==='named'?'Named credit after acceptance':'Private contribution record'))));
}
async function summaryPage(item,admin) {
  title(item.data.title||'Untitled analysis',labels[item.status]);
  main.append(p(`${item.owner_name} · ${item.kind==='review'?'Review of an analysis':'New analysis'} · Revision ${item.revision}`,'small'));
  if(admin)main.append(el('div',{class:'form-actions'},link(session.user.role==='maintainer'?'Write a revision or final decision':'Write an ordinary revision',href('revise='+item.id),'button button-primary')));
  if(item.final_revision) main.append(el('div',{class:'status-box final-status'},el('h2',{},'A maintainer final version is in effect.'),p(item.final_revision.author_name+' recorded a final decision on '+fmt(item.final_revision.created)+'. The original contribution below is retained.'),link('Read the final version or request a change',href('final='+item.id))));
  if(item.data.synthetic) main.append(p('Fictional practice contribution · excluded from research statistics and the contributor directory.','form-message'));
  if(item.note)main.append(el('div',{class:'form-message'},el('strong',{},'Review note: '),item.note));
  if(item.kind==='new')main.append(admissionPanel(item.admission));
  if(item.status==='accepted')main.append(el('div',{class:'form-actions'},link('Open contribution record',creditLink(item.id),'button button-primary')),p(item.scientific_status+'. Acceptance credits the work; it does not certify a scientific conclusion.','small boundary-note'));
  const body=el('div',{class:'review-summary'});showRecord(body,item.data);
  const returnURL=new URL(itemLink(item.id),location.href).href;
  const aside=el('aside',{class:'review-support'},el('h2',{},'Saved evidence'));
  aside.append(item.package ? el('section',{},
    link('Download '+item.package.name,'/api/packages/'+item.package.id),
    p(`${(item.package.size/1024).toFixed(1)} KB · SHA-256 recorded`,'small'),
    el('details',{class:'paper-details'},el('summary',{},'Package contents'),
      el('ul',{},item.package.manifest.map(f=>el('li',{},f.name))))) : p('No evidence package saved.'));
  aside.append(el('section',{},el('h2',{},'Return link'),
    el('a',{href:itemLink(item.id),class:'return-link'},returnURL),
    button('Copy return link',()=>copy(returnURL))));
  if(item.source_file)aside.prepend(el('section',{},el('h2',{},'Paper & supplementary materials'),link('Download '+item.source_file.name,'/api/source-files/'+item.source_file.id),p('Private source upload · '+(item.source_file.size/1024).toFixed(1)+' KB','small')));
  main.append(el('div',{class:'review-layout'},body,aside));
  if(item.revisions.length)main.append(el('details',{class:'history-details'},el('summary',{},`Submitted versions (${item.revisions.length})`),item.revisions.map(r=>{const content=el('details',{class:'revision-details'},el('summary',{},`Revision ${r.revision} · ${fmt(r.submitted)}`));const inner=el('div',{class:'review-summary'});showRecord(inner,r.data);content.append(inner,link('Download this version’s report','/api/packages/'+r.package_id),r.data.source_file_id?link('Download this version’s source materials','/api/source-files/'+r.data.source_file_id):null);return content;})));
  if(item.maintainer_revisions?.length)main.append(maintainerHistory(item.maintainer_revisions));
  main.append(el('details',{class:'history-details'},el('summary',{},'Activity history'),el('ol',{},item.events.map(e=>el('li',{},el('strong',{},e.action.replaceAll('_',' ')+' · '),fmt(e.created),e.note?p(e.note,'small'):null)))));
  if(admin&&item.kind==='new')main.append(admissionResolutionForm(item));
  if(admin&&item.status==='submitted')main.append(decisionForm(item));
}

function admissionResolutionForm(item){
  const wrapper=el('section',{class:'admin-section'},el('h2',{},'Verify collection eligibility'),button('Recheck automatic sources',()=>act(async()=>{await api('/admin/contributions/'+item.id+'/check','POST',{version:item.version,refresh:true});navigate(itemLink(item.id));})));
  const details=el('details',{class:'paper-details'},el('summary',{},'Record evidence you have verified'));
  const form=el('form',{},p('Use this when the public metadata is incomplete or a publisher blocks automated access. The field’s hard criteria still apply. This records your verification separately from the automated result.'),check('identity_confirmed','I checked that the official record matches this title and venue.',false,true),field('evidence_url','Official article evidence URL','url',item.data.source_url||'','',true),field('note','Verification note','textarea','','What did you check? At least 20 characters.',true));
  if(item.data.field==='computer_science'&&scopeNorm(item.data.venue)!=='arxiv')form.append(check('full_paper','I verified a full or regular main-conference paper, not a workshop, short paper, demo or Findings.',false,true));
  if(['chemistry','biological_science'].includes(item.data.field)&&scopeNorm(item.data.venue)!=='arxiv'){
    const top=listedTop(item.data.venue);
    if(top)form.append(p(`${top.name} is on the ${top.year} TOP journal list (Zone 1 + Top). Confirm the paper identity; no JIF fields are needed for this route.`,'boundary-note'));
    else form.append(field('jif_year','JIF data year','number',String(item.admission?.metric?.year||scopePolicy.jif_year),'Use the most recent verifiable year.',true),field('jif','Journal Impact Factor','number','','Must be strictly greater than 10.',true),field('metric_url','Official JIF evidence URL','url','','Publisher metrics page or the licensed JCR record. The source must identify the journal and data year.',true));
  }
  form.querySelector('[name=note]').minLength=20;
  const jif=form.querySelector('[name=jif]');if(jif){jif.step='0.1';jif.min='10.1';jif.max='1999.9';}
  form.append(el('button',{type:'submit',class:'button button-secondary'},'Record verified eligibility'));
  form.addEventListener('submit',event=>{event.preventDefault();const values=formData(form);act(async()=>{await api('/admin/contributions/'+item.id+'/admission-resolution','POST',{...values,version:item.version,identity_confirmed:form.querySelector('[name=identity_confirmed]').checked,full_paper:!!form.querySelector('[name=full_paper]')?.checked,jif_year:values.jif_year||scopePolicy.jif_year});navigate(itemLink(item.id));});});
  details.append(form);wrapper.append(details);return wrapper;
}

function decisionForm(item) {
  if(session.user.role==='admin'&&item.owner===session.user.id)return p('Another admin or a maintainer will review your submission. You can still add an ordinary revision.','form-message');
  const form=el('form',{class:'admin-section'},el('h2',{},'Review this contribution'),p('Accept a useful, inspectable contribution. Scientific adjudication remains separate. Accepted new analyses become available for another contributor to review.'),field('note','Decision note','textarea','','Tell the contributor what is useful or what needs to change.',true),field('decision','Decision','select','','',true,[['needs_changes','Request changes'],['accepted','Accept the contribution'],['declined','Do not accept']]),el('div',{class:'form-actions'},el('button',{type:'submit',class:'button button-primary'},'Save decision')));
  if(item.kind==='new'&&(!item.admission||item.admission.status!=='pass'||item.admission.stale)){form.querySelector('option[value=accepted]').disabled=true;form.prepend(p('Acceptance is unavailable until paper identity and eligibility are verified. You can still request changes or decline.','form-message'));}
  form.addEventListener('submit',event=>{event.preventDefault();const data=formData(form);act(async()=>{await api('/admin/contributions/'+item.id+'/decision','POST',{...data,version:item.version});navigate(itemLink(item.id));});});
  return form;
}

async function adminPage() {
  if(gate())return;
  if(!isStaff())throw new Error('Sign in with an admin or maintainer account to open this page.');
  const queue=await api('/admin');
  title('Keep the work moving.','Review applications and submissions. Ask for a focused revision when something is missing, and accept work that another reader can inspect.');
  const tab=params.get('tab')||'applications';
  main.append(p(session.user.role==='maintainer'?'Manage admins and contributors, review submissions and record final decisions. Other maintainers’ accounts and unsubmitted drafts remain separate.':'Review applications and submissions, add ordinary revisions and manage contributor accounts. Daily contribution limits do not apply. Final decisions and role assignments belong to maintainers.','small boundary-note'));
  main.append(el('nav',{class:'queue-tabs','aria-label':'Management queues'},link(`Applications (${queue.applications.filter(a=>a.status==='pending').length} pending)`,href('view=maintainer&tab=applications'),tab==='applications'?'active':''),link(`All work (${queue.contributions.filter(c=>c.status==='submitted').length} submitted)`,href('view=maintainer&tab=submissions'),tab==='submissions'?'active':''),session.user.role==='maintainer'?link(`Amendments (${queue.amendments.filter(a=>a.status==='pending').length} pending)`,href('view=maintainer&tab=amendments'),tab==='amendments'?'active':''):null,link('Accounts',href('view=accounts'))));
  if(tab==='amendments'){amendmentQueue(queue.amendments);return;}
  if(tab==='applications'){
    if(!queue.applications.length)main.append(el('section',{class:'empty-state'},el('h2',{},'No applications yet.'),p('A researcher creates a reviewer account and applies from the contribution page. Their background and contact details will appear here.')));
    for(const app of queue.applications){
      const info=el('dl',{class:'profile-details'});
      for(const [label,value] of [['Email',app.login],['Position',app.profile.position],['Institution',app.profile.institution],['Expertise',app.profile.expertise],['Additional context',app.profile.eligibility_note]])if(value)info.append(el('dt',{},label),el('dd',{},value));
      const entry=el('section',{class:'admin-section'},status(labels[app.status]),el('h2',{},app.name),info,p(app.email_verified?'Email ownership verified. Research background still needs your review.':'This account predates email verification; confirm the contact address during review.','small'));
      if(app.profile.profile_url)entry.append(link('Open research profile',app.profile.profile_url));
      const form=el('form',{},field('note','Application decision note','textarea',app.note,'A note is required when requesting information or declining.'),field('decision','Application decision','select','','',true,[['approved','Approve access'],['needs_information','Ask for more information'],['declined','Decline access']]),el('div',{class:'form-actions'},el('button',{type:'submit',class:'button button-primary'},'Save application decision')));
      form.querySelector('[name=decision]').addEventListener('change',event=>setRequired(form.querySelector('[name=note]'),['needs_information','declined'].includes(event.target.value)));
      form.addEventListener('submit',event=>{event.preventDefault();const data=formData(form);act(async()=>{await api('/admin/applications/'+app.user_id,'POST',data);navigate(href('view=maintainer'));});});
      entry.append(form);main.append(entry);
    }
  }else{
    if(!queue.contributions.length)main.append(el('section',{class:'empty-state'},el('h2',{},'No contributions yet.'),p('Saved drafts and submitted reports appear here with their summaries, source materials and AI disclosures.')));
    const list=el('div',{class:'paper-list'});
    for(const item of queue.contributions)list.append(el('article',{class:'paper-item'},el('div',{},el('div',{class:'paper-meta'},el('span',{},item.owner_name),el('span',{},item.kind==='review'?'Review':'New analysis'),item.data.synthetic?el('span',{},'Practice'):null),el('h2',{},item.data.title||'Untitled draft'),p(item.data.summary||item.data.scope||''),p(`${item.package?.manifest.length||0} report files · ${item.data.ai_used==='yes'?item.data.ai_model:'Manual contribution'} · Revision ${item.revision}`,'small'),item.kind==='new'?p(item.admission?(item.admission.stale?'Eligibility check needs refreshing':admissionLabels[item.admission.status]):'Eligibility not checked yet','small'):null),el('div',{class:'paper-action'},status(labels[item.status]),link('Open contribution',itemLink(item.id),'button button-secondary'))));
    main.append(list);
  }
}

async function accountsPage() {
  if(gate())return;
  if(!isStaff())throw new Error('Sign in with an admin or maintainer account to manage accounts.');
  let directory=await api('/admin/accounts');
  const roleLabel=role=>({reviewer:'Contributor',admin:'Admin',maintainer:'Maintainer'}[role]||role);
  main.append(link('Back to management',href('view=maintainer'),'back-link'));
  title('Manage account access.',directory.can_assign_roles?'Assign roles, manage admins and help contributors return to their work.':'Manage contributor access and retain their saved work.');
  main.append(p(directory.can_assign_roles?'Maintainers manage admins and contributors. Each maintainer controls their own account; other maintainers’ accounts are not listed here.':'Admins manage contributors. Only maintainers can assign roles or manage admin accounts.','small boundary-note'));
  let roleForm,roleDetails;
  function editRole(email,role='reviewer') {
    roleDetails.open=true;
    roleForm.querySelector('[name=email]').value=email;
    roleForm.querySelector('[name=role]').value=role;
    roleForm.querySelector('[name=password]').focus();
    roleDetails.scrollIntoView({block:'start',behavior:'instant'});
  }
  const reservations=el('div',{class:'role-reservations'});
  function drawReservations() {
    reservations.replaceChildren();
    if(!directory.reservations.length)return;
    reservations.append(el('h3',{},'Roles waiting for registration'));
    for(const item of directory.reservations)reservations.append(el('div',{class:'reservation-row'},p(item.email+' · '+roleLabel(item.role)),button('Remove reserved role',()=>editRole(item.email))));
  }
  if(directory.can_assign_roles){
    roleDetails=el('details',{class:'account-role-panel'},el('summary',{},'Assign or change a role'));
    roleForm=el('form',{class:'auth-form form-grid'},field('email','Exact account email','email','','Use a verified account email, or reserve a role before the person registers.',true),field('role','Account role','select','','Contributor removes management access or cancels a reserved role.',true,[['admin','Admin'],['maintainer','Maintainer'],['reviewer','Contributor']]),field('password','Your current password','password','','Confirm the change with your own password.',true),el('button',{type:'submit',class:'button button-primary'},'Save role'));
    roleForm.addEventListener('submit',event=>{event.preventDefault();const values=formData(roleForm);act(async()=>{const result=await api('/admin/roles','POST',values);roleForm.querySelector('[name=password]').value='';directory=await api('/admin/accounts');drawReservations();drawAccounts();feedback(result.message);});});
    roleDetails.append(p('A reserved role activates only after the person verifies that exact institutional email. Existing accounts must sign in again after a role change. No invitation is sent.','small'),roleForm,p('Admins can review submissions and manage contributors. Maintainers also manage admins and record final decisions. Another maintainer’s account cannot be suspended or downgraded here. These roles apply to this website; GitHub and server access are configured separately.','small boundary-note'),reservations);
    main.append(roleDetails);drawReservations();
  }
  const search=field('account_search','Find an account','search','','Search by name, email or role.');
  const accountList=el('div',{class:'account-list'});
  const count=p('','small');count.setAttribute('aria-live','polite');
  function drawAccounts(){
    const query=search.querySelector('input').value.trim().toLocaleLowerCase();
    const accounts=directory.accounts.filter(account=>[account.name,account.email,roleLabel(account.role)].some(value=>value.toLocaleLowerCase().includes(query)));
    count.textContent=accounts.length+' manageable '+(accounts.length===1?'account':'accounts');
    accountList.replaceChildren();
    if(!accounts.length){accountList.append(p(directory.accounts.length?'No matching account. Try a name or an exact email.':'No accounts to manage yet. Registered contributors and, for maintainers, admins will appear here.','empty-state'));return;}
    for(const account of accounts){
      const details=el('details',{class:'account-entry'},el('summary',{},el('span',{},el('strong',{},account.name),el('span',{class:'account-email'},account.email)),el('span',{class:'account-access'},roleLabel(account.role)+' · '+(account.status==='active'?'Active':'Suspended'))));
      const form=el('form',{class:'auth-form form-grid'},field('status','Account access','select',account.status,'Suspending signs the person out immediately. Their work and history remain saved.',true,[['active','Active'],['suspended','Suspended']]),field('note','Reason for this change','textarea','','At least 10 characters. Kept in the management history.',true),el('button',{type:'submit',class:'button button-primary'},'Save account access'));
      form.querySelector('[name=note]').minLength=10;
      form.addEventListener('submit',event=>{event.preventDefault();const values=formData(form);act(async()=>{const result=await api('/admin/accounts/'+account.id+'/status','POST',values);directory=await api('/admin/accounts');drawAccounts();feedback(result.message);});});
      details.append(p(account.email_verified?'Email ownership verified.':'This account predates email verification. Verify the address before assigning a management role.','small'));
      if(account.note)details.append(p('Latest access note: '+account.note,'small'));
      details.append(form);
      if(directory.can_assign_roles)details.append(button('Change role',()=>editRole(account.email,account.role)));
      accountList.append(details);
    }
  }
  search.querySelector('input').addEventListener('input',drawAccounts);
  main.append(el('section',{class:'account-directory'},el('h2',{},'Registered accounts'),search,count,accountList));drawAccounts();
}

function maintainerHistory(revisions) {
  return el('details',{class:'history-details'},el('summary',{},`Signed revisions & decisions (${revisions.length})`),revisions.map(r=>{const block=el('details',{class:'revision-details'},el('summary',{},`${r.mode==='final'?'Final decision':'Ordinary contribution'} · ${r.author_name||r.data.record_author} · ${fmt(r.created)}`));const body=el('div',{class:'review-summary'});showRecord(body,r.data);block.append(body,r.package?link('Download revised report','/api/revision-files/'+r.package.id):null);return block;}));
}

async function maintainerRevisionPage(id) {
  if(gate())return;
  if(!isStaff())throw new Error('Only an admin or maintainer can create this type of signed revision.');
  const item=await api('/contributions/'+id);
  const base=item.final_revision?.data||item.maintainer_revisions?.at(-1)?.data||item.data;
  const amendment=params.get('amendment')?await api('/amendments/'+params.get('amendment')):null;
  main.append(link('Back to contribution',itemLink(id),'back-link'));
  const canFinalize=session.user.role==='maintainer';
  title('Revise with a clear role.',canFinalize?'Add an ordinary signed contribution, or record the maintainer’s final decision. Earlier work remains available in the history.':'Add an ordinary signed revision. Earlier work stays in the history; final decisions remain with a maintainer.');
  if(amendment)main.append(el('section',{class:'status-box'},el('h2',{},'Amendment requested by '+amendment.owner_name),p(amendment.reason),amendment.proposed?p('Proposed change: '+amendment.proposed):null,amendment.package_name?link('Download amendment package','/api/amendments/'+amendment.id+'/package'):null));
  const form=el('form',{class:'review-form maintainer-revision-form'});
  if(canFinalize)form.append(field('mode','How should this revision be treated?','select',amendment?'final':'ordinary','Only maintainer accounts have the final-decision option.',true,[['ordinary','Ordinary signed contribution'],['final','Maintainer final decision']]));
  else form.append(p('Ordinary signed revision · Admin','boundary-note'));
  form.append(p(base.title||'Untitled contribution','task-title'));
  if(!base.title)form.append(field('title','Paper title','text','','',true));
  form.append(field('summary','Revised summary','textarea',base.summary||base.reasoning||'','State the revised conclusion, what changed and why. Put detailed checks in a ZIP if needed. At least 40 characters.',true));
  form.querySelector('[name=summary]').minLength=40;
  form.append(field('assessment','Assessment','select',base.assessment||'','',true,Object.entries(assessments)));
  const revisionFile=el('input',{type:'file',id:'revision-package',accept:'.zip,application/zip'});
  form.append(el('div',{class:'field attachment-input'},el('label',{for:'revision-package'},'Revised report',el('span',{class:'field-requirement'},'Optional')),p('ZIP only, up to 10 MB. Earlier reports stay in the history.','hint'),revisionFile));
  const ai=aiDisclosureFields();form.append(ai);
  form.append(el('div',{class:'form-actions'},el('button',{type:'submit',class:'button button-primary'},'Record revision')),p('An ordinary revision does not replace an existing final decision. A new final decision supersedes the previous final version while keeping it in the history.','small'));
  trackDirty(form);
  form.addEventListener('submit',event=>{event.preventDefault();const values=formData(form);act(async()=>{const attachment=await embeddedZIP(revisionFile.files[0]);await api('/admin/contributions/'+id+'/revisions','POST',{version:item.version,mode:canFinalize?values.mode:'ordinary',note:values.summary,data:{...base,...values},amendment_id:amendment?.id,...attachment});navigate(itemLink(id));});});
  main.append(form);
}

async function embeddedZIP(file){if(!file)return {};if(!/\.zip$/i.test(file.name)||file.size>session.policy.max_zip_bytes)throw new Error('Choose a ZIP no larger than 10 MB.');const encoded=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(String(reader.result).split(',')[1]);reader.onerror=()=>reject(new Error('The ZIP could not be read.'));reader.readAsDataURL(file);});return {package_name:file.name,package_base64:encoded};}
function aiDisclosureFields(data={},label='Did you use AI for this revision or request?') {
  const select=field('ai_used',label,'select',data.ai_used||'','',true,[['no','No — completed manually'],['yes','Yes — AI assisted this work']]);
  const details=el('div',{class:'ai-fields'},field('ai_model','AI configuration','select',data.ai_model||'','',false,session.policy.models.map(x=>[x,x])),field('ai_details','How did AI help?','textarea',data.ai_details||'','State what it did and what you checked (at least 20 characters).'));
  details.querySelector('[name=ai_details]').minLength=20;
  const update=()=>{details.hidden=select.querySelector('select').value!=='yes';details.querySelectorAll('input,textarea,select').forEach(x=>{x.disabled=details.hidden;setRequired(x,!details.hidden);});clearInactiveErrors();};
  select.querySelector('select').addEventListener('change',update);update();
  return el('div',{class:'disclosure-fields'},select,details);
}

async function finalsPage() {
  if(gate())return;
  title('Maintainer final versions.','Final project decisions are signed by a maintainer. Contributors can propose a change to any current final version, with reasons and supporting material.');
  const {finals}=await api('/finals');
  if(!finals.length)main.append(p('No final versions have been recorded yet.','form-message'));
  for(const final of finals)main.append(el('article',{class:'paper-item'},el('div',{},el('h2',{},final.title),p(final.scope),p((final.synthetic?'Fictional practice · ':'')+'Final version recorded '+fmt(final.created),'small')),link('Read final version',href('final='+final.contribution_id),'button button-secondary')));
}

async function finalPage(id) {
  if(gate())return;
  const {final,history}=await api('/finals/'+id);
  main.append(link('Back to final versions',href('view=finals'),'back-link'));
  title(final.data.title,'Maintainer final decision · '+final.author_name+' · '+fmt(final.created));
  main.append(p('This is the current final project version. Independent-review status is tracked separately; prior work and decisions remain in the history.','small boundary-note'));
  if(final.data.synthetic)main.append(p('Fictional practice decision. No published paper is assessed.','small'));
  if(session.user.role!=='maintainer')main.append(link('Propose a change','#amendment-request','text-link'));
  const body=el('div',{class:'review-summary'});showRecord(body,final.data);main.append(body,maintainerHistory(history));
  if(final.package)main.append(link('Download revised report','/api/revision-files/'+final.package.id));
  if(session.user.role==='maintainer'){main.append(link('Write a revision or a new final decision',href('revise='+id),'button button-primary'));return;}
  const form=el('form',{class:'review-form amendment-form',id:'amendment-request'},el('h2',{},'Request a change to this final version'),p('Your request goes to a maintainer and does not overwrite the current version.'),field('reason','What should change, and why?','textarea','','A short explanation is enough. Include supporting details in a ZIP if needed. At least 40 characters.',true),aiDisclosureFields());
  form.querySelector('[name=reason]').minLength=40;
  const file=el('input',{type:'file',id:'amendment-package',accept:'.zip,application/zip'});
  form.append(el('div',{class:'field attachment-input'},el('label',{for:'amendment-package'},'Supporting ZIP (optional, up to 10 MB)'),file),el('div',{class:'form-actions'},el('button',{type:'submit',class:'button button-primary'},'Send amendment request')));
  trackDirty(form);
  form.addEventListener('submit',event=>{event.preventDefault();const values=formData(form);act(async()=>{await api('/finals/'+id+'/amendments','POST',{...values,...await embeddedZIP(file.files[0]),final_revision:final.id});navigate(href('view=my-work'));});});
  main.append(form);
}

function amendmentStatus(value){return {pending:'Amendment pending',accepted:'Change adopted',needs_changes:'More detail requested',declined:'Request declined'}[value]||value;}
function amendmentQueue(requests) {
  if(!requests.length){main.append(el('section',{class:'empty-state'},el('h2',{},'No amendment requests yet.'),p('Requests to change your final versions will appear here. You can adopt a change through a new final revision, ask for more detail or decline with a reason.')));return;}
  for(const request of requests){
    const entry=el('section',{class:'admin-section'},status(amendmentStatus(request.status)),el('h2',{},request.owner_name),p(request.reason),request.proposed?el('h3',{},'Proposed change'):null,request.proposed?p(request.proposed):null,p(request.ai_used==='yes'?request.ai_model+' · '+request.ai_details:'No AI declared.','small'),link('Read current final version',href('final='+request.contribution_id)));
    if(request.package_name)entry.append(link('Download '+request.package_name,'/api/amendments/'+request.id+'/package'));
    if(request.decision)entry.append(p(request.decision,'form-message'));
    if(request.status==='pending'){
      entry.append(el('div',{class:'form-actions'},link('Review and adopt through a new final version',href('revise='+request.contribution_id+'&amendment='+request.id),'button button-primary')));
      const form=el('form',{},field('note','Response to this amendment request','textarea','','Explain what needs to be clarified or why you are declining.',true),field('decision','Amendment decision','select','','',true,[['needs_changes','Ask for more detail'],['declined','Decline this request']]),el('div',{class:'form-actions'},el('button',{class:'button button-secondary',type:'submit'},'Send decision')));
      form.addEventListener('submit',event=>{event.preventDefault();const data=formData(form);act(async()=>{await api('/admin/amendments/'+request.id,'POST',data);navigate(href('view=maintainer&tab=amendments'));});});entry.append(form);
    }
    main.append(entry);
  }
}

async function contributorsPage() {
  title('The people behind the work.','Careful reading, a useful explanation and a reproducible check each deserve credit. Accepted contributions can be listed here with the contributor’s agreement.');
  const {contributors}=await api('/contributors');
  if(!contributors.length)main.append(el('section',{class:'empty-state directory-empty'},el('h2',{},'The directory is waiting for its first contribution.'),p('Only accepted, non-practice contributions with permission for named credit appear here. Private records remain available to their contributors.'),session.user?link('Choose a contribution',href(),'button button-primary'):null));
  else for(const person of contributors)main.append(el('section',{class:'contributor-entry'},el('h2',{},person.name),el('ul',{class:'credit-list'},person.contributions.map(c=>el('li',{},link(c.title,creditLink(c.id)),p(c.roles.join(' · ')+' · Accepted '+fmt(c.accepted),'small'))))));
  main.append(el('div',{class:'track-options credit-explainer'},el('section',{},el('h2',{},'A record you can point to'),p('Each accepted contribution has a stable record with its role, scope, version and acceptance date. Open the record to print a contribution acknowledgement.')),el('section',{},el('h2',{},'Credit for the work itself'),p('The directory credits the contribution, whether it confirms an argument, adds context or identifies a concern. It is not a ranking of people by the number of problems they report.'))),p('These are ELVIA project records. They do not imply journal reviewer appointments, institutional accreditation or automatic ORCID recognition.','small boundary-note'));
}

async function creditPage(id) {
  let record;
  try {record=await api('/credit/'+id);} catch(error) {if(error.status===401&&!session.user){guestReadOnlyPage();return;}throw error;}
  title('Contribution acknowledgement.','A record of work accepted by ELVIA.');
  const sheet=el('article',{class:'acknowledgement'},el('p',{class:'ack-brand'},'ELVIA.'),el('h2',{},record.name),p(`Contributed ${record.roles.join(', ').toLowerCase()} to:`),el('h3',{},record.title),p(record.scope),el('dl',{class:'profile-details'},el('dt',{},'Record'),el('dd',{},record.id),el('dt',{},'Version'),el('dd',{},String(record.revision)),el('dt',{},'Accepted'),el('dd',{},fmt(record.accepted)),el('dt',{},'Issued by'),el('dd',{},record.issuer)),p(record.status,'small'),record.synthetic?p('FICTIONAL PRACTICE RECORD · not a research contribution.','practice-record'):null,el('p',{class:'small'},'Record link: ',el('a',{href:location.href},location.href)),p('Evidence package SHA-256: '+record.sha256,'checksum'));
  main.append(sheet,el('div',{class:'form-actions no-print'},button('Print acknowledgement',()=>window.print(),true),button('Copy record link',()=>copy(location.href))),p(record.public?'This named record is visible in the local contributor directory.':'This record is private to the contributing account.','small boundary-note no-print'));
}

async function emailSettings(){
  const settings=await api('/admin/email-settings');
  const wrapper=el('section',{class:'google-signin'},el('h2',{},'Contributor verification email'),p(settings.enabled?'SMTP settings are saved. Registration sends real verification emails through your domain provider.':'Add your domain email provider’s SMTP settings to open contributor registration.'));
  const details=el('details',{class:'paper-details'},el('summary',{},'Configure email delivery and institutional domains'));
  const form=el('form',{class:'form-grid auth-form'},field('host','SMTP hostname','text',settings.host||'','From your domain email provider.',true),field('port','SMTP port','number',String(settings.port||465),'Usually 465 for SSL/TLS or 587 for STARTTLS.',true),field('security','Transport security','select',settings.security||'ssl','',true,[['ssl','SSL/TLS'],['starttls','STARTTLS']]),field('sender','Sending email address','email',settings.sender||'','The sender approved by your domain email provider.',true),field('username','SMTP username','text',settings.username||'','',true),field('password','SMTP password','password','',settings.password_saved?'A password is saved. Leave blank to keep it.':'Use the provider’s SMTP password or app-specific password.',!settings.password_saved),field('research_domains','Additional research-institution domains','textarea',(settings.research_domains||[]).join('\n'),'One domain per line, for example institute.org. Add only institutions you have checked; subdomains are included. Academic suffixes are accepted automatically.'),el('button',{class:'button button-primary',type:'submit'},'Save email settings'));
  form.querySelector('[name=password]').autocomplete='new-password';
  form.addEventListener('submit',event=>{event.preventDefault();const values=formData(form);act(async()=>{await api('/admin/email-settings','POST',{...values,port:Number(values.port),research_domains:values.research_domains.split(/[\n,]+/).map(x=>x.trim()).filter(Boolean)});navigate(href('view=account'));});});
  details.append(form,p('Credentials remain in the private local service directory. They are never returned to the browser, included in logs or sent to contributors.','small'));wrapper.append(details);main.append(wrapper);
}

function googleAccount(){
  const area=el('section',{class:'google-signin'},el('h2',{},'Google sign-in'));
  if(me?.google_linked){area.append(p('A Google account is linked. You can use Continue with Google on the sign-in page. Your current permissions stay with this account.'));return area;}
  if(!session.google.enabled){area.append(p(session.google.message),p('The maintainer setup guide explains how to add the OAuth client. Your existing email sign-in remains available.','small'));return area;}
  const form=el('form',{class:'auth-form'},field('link_password','Confirm current local password','password','','This protects the account you are linking and its existing permissions.',true),el('button',{type:'submit',class:'button button-secondary'},'Link my Google account'));
  form.addEventListener('submit',event=>{event.preventDefault();const password=formData(form).link_password;act(async()=>{const result=await api('/auth/google/start','POST',{mode:'link',password});navigate(result.authorization_url);});});
  area.append(p('Link from this signed-in admin or maintainer account. Matching an email address alone never creates an account or grants permissions.'),form);return area;
}
async function accountPage() {
  if(gate())return;
  title(session.user.force_change?'Choose your own password.':'Your account.',session.user.force_change?'Replace the temporary password before opening your workspace.':'You are signed in as '+session.user.name+' ('+session.user.login+').');
  const form=el('form',{class:'auth-form form-grid'},field('current','Current password','password','','',true),field('password','New password','password','',newPasswordHint()+' Changing it signs out your other browser sessions.',true),el('div',{class:'form-actions full'},el('button',{class:'button button-primary',type:'submit'},'Save new password')));
  configureNewPassword(form.querySelector('[name=password]'));
  form.addEventListener('submit',event=>{event.preventDefault();const data=formData(form);act(async()=>{await api('/auth/password','POST',data);navigate(afterLogin());});});
  if(session.user.has_password)main.append(form);
  if(!session.user.force_change&&isStaff())main.append(el('div',{class:'form-actions'},link('Manage account access',href('view=accounts'),'button button-secondary')));
  if(!session.user.force_change&&isStaff())main.append(googleAccount());
  if(!session.user.force_change&&session.user.role==='maintainer')await emailSettings();
  main.append(el('div',{class:'divider'},button('Sign out',()=>act(async()=>{await api('/auth/logout','POST',{});navigate(href('view=login'));}))));
}

window.addEventListener('beforeunload',event=>{if(dirty){event.preventDefault();event.returnValue='';}});
window.addEventListener('pagehide',()=>{passwordResetToken='';releasePendingAction?.();releasePendingAction=null;actionPending=false;navigationPending=false;});
export async function initializeHomeAccount(token='') {
  if(!isHomeAccount)return;
  passwordResetToken=token;
  await initializeWorkspace();
}
async function initializeWorkspace() {
 if(!redirectLegacyAuth()) {
  try {
    session=await api('/session');
    main.replaceChildren();
    if(caseRoute){
      try{
        selectedCase=await loadCaseContext(new URLSearchParams(addCaseContext('',caseRoute)));
        main.append(el('section',{class:'status-box case-context','aria-label':'Selected Atlas note'},p('Your selected note','small'),el('h2',{},selectedCase.title),selectedCase.problem?p('Problem '+selectedCase.problem+': '+selectedCase.problemTitle):null,p('Contribute a focused analysis, clarification or supporting evidence. This Atlas note is not an assigned review task.'),el('div',{class:'form-actions'},link('Return to this finding',selectedCase.caseUrl),link('Choose a different contribution','/contribute.html'))));
      }catch(error){main.append(p(error.message,'form-message error'));}
    }
    if(isHomeAccount){homeAccountPage();}
    else {
      scopePolicy=await api('/admission-policy');nav();
      if(session.user?.force_change){await accountPage();}
      else {
        if(session.user)me=await api('/me');
        if(params.has('revise'))await maintainerRevisionPage(params.get('revise'));
        else if(params.has('final'))await finalPage(params.get('final'));
        else if(params.has('review'))await contributionPage(params.get('review'));
        else if(params.has('paper'))await taskPage(params.get('paper'));
        else if(params.has('credit'))await creditPage(params.get('credit'));
        else if(view==='scope')scopePage();
        else if(view==='apply')applicationPage();
        else if(view==='my-work')myWorkPage();
        else if(view==='maintainer')await adminPage();
        else if(view==='accounts')await accountsPage();
        else if(view==='contributors')await contributorsPage();
        else if(view==='finals')await finalsPage();
        else if(view==='account')await accountPage();
        else await homePage();
      }
    }
  }catch(error){feedback(error.message,true);main.append(link('Back to main page',mainPageHref()));}
  prepareForms();
 }
}
if(!isHomeAccount)await initializeWorkspace();
