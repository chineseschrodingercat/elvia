export function applicationProgress(app,{el,p,fmt,link,href}) {
  const state=app.status;
  const headings={pending:'Your application has been submitted.',under_review:'Your application is under review.',approved:'Your reviewer access is approved.',needs_information:'Additional information is needed.',declined:'Your application was not approved.'};
  const copy={pending:'Please allow 1–3 days for review. Follow the progress below; we will email you when the status changes.',under_review:'An admin or maintainer has opened your application and begun reviewing it. Reviewer access is awaiting a decision. Please allow 1–3 days from submission.',approved:'You can now choose an available review in the contribution workspace.',needs_information:'Read the request below and update your application so the review can continue.',declined:'Read the decision note below. You can continue to browse and submit your own analyses.'};
  const stage=state==='pending'?0:state==='approved'?2:1;
  const names=['Submitted','Under review',state==='needs_information'?'More information needed':state==='declined'?'Not approved':'Approved'];
  const dates=new Map((app.timeline||[]).map(event=>[event.status,event.created]));
  const keys=['pending','under_review',state==='needs_information'||state==='declined'?state:'approved'];
  const terminal=['needs_information','declined'].includes(state);
  const box=el('section',{class:'application-progress',id:'application-progress','aria-labelledby':'application-progress-title'},p('Reviewer access application','eyebrow'),el('h2',{id:'application-progress-title'},headings[state]||'Reviewer application status'),p(copy[state]||'Check this page for updates.'));
  box.append(el('ol',{class:'application-timeline','aria-label':'Reviewer application progress'},names.map((name,i)=>{
    const current=terminal?i===2:i===stage,done=terminal?i<2:i<stage;
    return el('li',{class:(current?'current ':done?'complete ':'')+(terminal&&i===2?'attention':''),'aria-current':current?'step':null},el('span',{class:'application-step-marker','aria-hidden':'true'},done?'✓':String(i+1)),el('div',{},el('strong',{},name),p(dates.get(keys[i])?fmt(dates.get(keys[i])):current?'Current stage':done?'Completed':'Awaiting this stage','small')));
  })));
  if(app.note)box.append(el('div',{class:'application-decision-note'},el('strong',{},'Note from the reviewer'),p(app.note)));
  if(terminal)box.append(link('Update application',href('view=apply'),'button button-secondary'));
  if(state==='approved')box.append(link('Choose a review',href(),'button button-primary'));
  if(state!=='approved')box.append(p('You can submit your own first report while your reviewer application is being considered.','small'));
  box.append(p('Email updates accompany each stage. Check Spam or Junk if a message is missing.','small'),el('div',{class:'application-refresh','data-application-refresh':true,role:'status','aria-live':'polite'},'Status updates automatically while this page is open.'));
  return box;
}
