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
    const explanation=document.createElement('p');explanation.textContent='Contribute a focused analysis of this note. Its paper identity and selected finding will follow you through registration. Checking an Atlas note uses the own-analysis track; assignments to review contributor submissions require reviewer approval.';
    panel.append(heading,reading,explanation);
    const next='/contribute.html?'+addCaseContext('',context);
    for(const anchor of document.querySelectorAll('a[href]')){
      const url=new URL(anchor.href);
      if(url.origin!==location.origin)continue;
      if(url.pathname==='/contribute.html')anchor.href=next;
      if(url.pathname==='/'&&['register','login'].includes(url.searchParams.get('view'))){url.searchParams.set('next',next);anchor.href=url.pathname+url.search+url.hash;}
    }
    const action=document.createElement('a');action.className='button button-primary';action.href=next;action.textContent='Continue with this note';panel.append(action);
  }catch(error){panel.textContent=error.message;}
}
