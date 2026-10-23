const MiB=1024*1024;
export function validateUploadFiles(slot,files,otherPaperBytes=0){
  if(!files.length)throw new Error('Choose a file to upload.');
  if(slot==='verification-code'){
    if(files.length>10)throw new Error('Choose at most 10 code files, or one ZIP.');
    if(files.some(f=>/\.zip$/i.test(f.name))&&files.length!==1)throw new Error('Upload one ZIP by itself, or choose separate code files.');
    if(files.reduce((sum,f)=>sum+f.size,0)>5*MiB)throw new Error('Verification code must total no more than 5 MB.');
    return;
  }
  if(files.length!==1)throw new Error('Choose one file for this upload slot.');
  const report=slot==='report',limit=(report?20:50)*MiB;
  if(!(report?/\.(pdf|tex)$/i:/\.pdf$/i).test(files[0].name))throw new Error(report?'Choose a report PDF or LaTeX (.tex) file.':'Choose a PDF for the original paper or its main supplement.');
  if(files[0].size+(report?0:otherPaperBytes)>limit)throw new Error(report?'Your report is too large. Compress the PDF or reduce the LaTeX file, then upload again (20 MB maximum).':'The original article and supplementary PDF are too large together. Compress one or both PDFs, then upload again (50 MB combined maximum).');
}

export function aiReviewGuidance({el,p}){
  return el('aside',{class:'ai-review-guidance','aria-label':'AI-assisted and manual review'},
    el('h2',{},'AI-assisted review is strongly encouraged.'),
    p('Use ChatGPT, Claude or Gemini to help examine claims, work through derivations and prepare your report. We also warmly welcome fully manual reviews.'),
    p('Suggested settings: Astra 6 Max · Claude Opus 5.5 xhigh · Gemini Argon 4 high. You may use another model or setting; enter what you actually used.','small'),
    p('Use the matching template below. Check the reasoning and cited evidence, and describe the AI assistance and your own checks in the report.','small'));
}

export function reportRequirements(initial,{el,p}){
  const kind=initial?'first-report':'revision-report',label=initial?'first-report':'review/revision';
  const node=el('section',{class:'report-requirements','data-template-kind':kind},el('h2',{},'Report requirements — '+label),
    p('Upload one PDF or complete UTF-8 LaTeX (.tex) document. Put the scientific detail in the report; you do not need to retype it into this form.'),
    el('ol',{class:'report-format-list'},
      el('li',{},initial?'Identify the paper, exact version and the scope of your check.':'Identify the paper, ELVIA case and published revision. Name each existing Problem number you address.'),
      el('li',{},initial?'Number each finding Problem 1, Problem 2, etc. Include its exact source location and claim.':'For each existing problem: state whether you agree, partly agree, disagree or remain uncertain, and explain the requested change. Put new problems in a separate N1, N2, etc. section.'),
      el('li',{},'For every finding: give the assumptions, check/evidence, impact, counterevidence and limits. Select Minor, Major, Needs evidence, or No issue found within scope, and justify it. A proposed correction is optional.'),
      el('li',{},'Include reproducibility details when relevant, references actually checked, conflicts and AI assistance. For AI work, name the actual model/version, settings, dates, tasks and your own verification.')),
    p('AI-assisted review is encouraged. The matching template can be given to your AI assistant; verify the cited sources and results, and keep unresolved claims explicit. A focused check of one claim is enough.'),
    el('div',{class:'form-actions template-actions'},
      el('a',{href:'/assets/report-templates/'+kind+'/main.tex',download:'elvia-'+kind+'.tex',class:'button button-secondary'},'Download '+label+' LaTeX template'),
      el('a',{href:'/assets/report-templates/'+kind+'/main.pdf',target:'_blank',rel:'noopener'},'View '+label+' PDF template ↗')),
    el('details',{class:'paper-details'},el('summary',{},'Simple file and scientific formatting'),
      p('Use headings, numbered findings, short paragraphs, equations and exact references. No special JSON, report ZIP or folder layout is needed. The PDF must be complete and readable. A .tex upload must contain documentclass and begin/end document, with all text, equations and references in that one file; use a PDF if external figures or files are essential.'),
      p('Minor means a bounded local issue. Major requires demonstrated impact on a central result. Needs evidence leaves validity or impact unresolved. No issue found applies only to the scope actually checked. Upload validation checks the file, not the scientific correctness or completeness of these statements.')));
  return node;
}

export function uploadSlot({slot,label,hint,el,p,onFiles}){
  const id='upload-'+slot;
  const input=el('input',{type:'file',id,accept:slot==='report'?'.pdf,.tex':slot==='verification-code'?undefined:'.pdf,application/pdf',multiple:slot==='verification-code','aria-describedby':id+'-hint'});
  const state=el('div',{class:'upload-state','aria-live':'polite'});
  const drop=el('div',{class:'file-drop-zone'},el('label',{for:id},label),p('Drop '+(slot==='verification-code'?'files':'a file')+' here, or browse below.','drop-instruction'),el('p',{class:'hint',id:id+'-hint'},hint),input,state);
  input.addEventListener('change',()=>{const files=Array.from(input.files||[]);if(files.length)onFiles(files,input,state);});
  drop.addEventListener('dragover',event=>{event.preventDefault();if(!input.disabled)drop.classList.add('drag-over');});
  drop.addEventListener('dragleave',()=>drop.classList.remove('drag-over'));
  drop.addEventListener('drop',event=>{event.preventDefault();drop.classList.remove('drag-over');if(input.disabled)return;const files=Array.from(event.dataTransfer?.files||[]);if(files.length)onFiles(files,input,state);});
  return {node:drop,input,state};
}
