import {loadCaseContext,addCaseContext} from './case-context.js';

const params=new URLSearchParams(location.search);
if(params.has('case')){
  const panel=document.createElement('section');
  panel.className='status-box';panel.setAttribute('aria-label','Selected Atlas note');
  document.querySelector('.guide-page .lede').after(panel);
  try{
    const context=await loadCaseContext(params);
    if(!context)throw new Error('Choose a valid note from the Atlas to keep it linked to your contribution.');
    const heading=document.createElement('h2');heading.textContent='Your selected note';
    const reading=document.createElement('a');reading.href=context.caseUrl;reading.textContent=context.title+(context.problem?' · Problem '+context.problem+': '+context.problemTitle:'');
    const explanation=document.createElement('p');explanation.textContent='Check one claim, add a clarification or share supporting evidence. Your selected paper and finding will stay linked through registration. You do not need a reviewer application to submit your own analysis of this note.';
    panel.append(heading,reading,explanation);
    const next='/contribute.html?'+addCaseContext('view=compose',context);
    for(const anchor of document.querySelectorAll('a[href]')){
      const url=new URL(anchor.href);
      if(url.origin!==location.origin)continue;
      if(url.pathname==='/contribute.html'&&anchor.dataset?.firstReport!=='true')anchor.href='/contribute.html?'+addCaseContext(url.search,context)+url.hash;
      if(url.pathname==='/'&&['register','login'].includes(url.searchParams.get('view'))){url.searchParams.set('next',next);anchor.href=url.pathname+url.search+url.hash;}
    }
    const actions=document.createElement('div');actions.className='form-actions';
    const action=document.createElement('a');action.className='button button-primary';action.target='_blank';action.rel='noopener';action.href='/?'+new URLSearchParams({view:'register',next})+'#contributor-access';action.textContent=context.problem?'Register to contribute to this finding':'Register to contribute to this note';
    const signin=document.createElement('a');signin.href='/?'+new URLSearchParams({view:'login',next})+'#contributor-access';signin.textContent='Sign in to continue';
    actions.append(action,signin);panel.append(actions);
    // A usable guest action is present even when the session check is unavailable.
    try{
      const response=await fetch('/api/session',{credentials:'same-origin',cache:'no-store'});
      if(response.ok&&(await response.json()).user){action.href=next;action.textContent='Open revision form ↗';signin.hidden=true;}
    }catch{/* Keep the contextual registration and sign-in links available. */}
  }catch(error){panel.textContent=error.message;}
}
