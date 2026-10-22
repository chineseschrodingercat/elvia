// Public reading context only. Never store credentials or infer a review decision.
export function parseCaseContext(params) {
  const caseId=params.get('case');
  if(!caseId||!/^[-a-z0-9_]{1,160}$/.test(caseId))return null;
  const value=params.get('problem');
  if(value!==null&&!/^[1-9][0-9]{0,2}$/.test(value))return null;
  return {caseId,problem:value===null?null:Number(value)};
}

export function addCaseContext(query,context) {
  const target=new URLSearchParams(query);
  if(context){target.set('case',context.caseId);if(context.problem)target.set('problem',String(context.problem));}
  return target.toString();
}

export function resolveCaseContext(candidate,payload) {
  if(!candidate)return null;
  const record=payload.records?.find(row=>row.case_id===candidate.caseId);
  if(!record)return null;
  const note=payload.case_notes?.[candidate.caseId];
  const problems=note?.revision===record.revision?note.problems:[];
  const count=['no_issue_found','scope_clarification'].includes(record.audit.outcome)?0:(problems?.length||1);
  if(candidate.problem&&candidate.problem>count)return null;
  let sourceUrl='';
  try{const url=new URL(record.audit.landing_url);if(url.protocol==='https:'&&!url.username&&!url.password)sourceUrl=url.href;}catch{/* A missing identity is left for the contributor. */}
  return {...candidate,title:record.source.title,venue:record.audit.venue,sourceUrl,
    field:record.audit.venue==='NeurIPS'?'computer_science':'',
    problemTitle:candidate.problem?(problems?.[candidate.problem-1]?.title||'The recorded claim'):'',
    caseUrl:'/atlas/cases/'+candidate.caseId+'.html'+(candidate.problem?'#problem-'+candidate.problem:'')};
}

export async function loadCaseContext(params) {
  const candidate=parseCaseContext(params);
  if(!candidate)return null;
  const response=await fetch('/atlas/cases/'+candidate.caseId+'.context.json',{credentials:'omit'});
  if(!response.ok)throw new Error('The selected Atlas note could not load. Return to the Atlas and try again.');
  const context=resolveCaseContext(candidate,await response.json());
  if(!context)throw new Error('This Atlas note or finding is not available. Choose a note from the Atlas.');
  return context;
}

export function draftIdentity(context) {
  return {title:context.title,venue:context.venue,field:context.field||'',source_url:context.sourceUrl,
    scope:'Follow-up to '+context.title+(context.problem?' · Problem '+context.problem+': '+context.problemTitle:'')+'. Original Atlas note: https://elvia-atlas.org'+(context.caseUrl||'/atlas/cases/'+context.caseId+'.html'),
    source_version:'Check the source version against the linked Atlas note.'};
}
