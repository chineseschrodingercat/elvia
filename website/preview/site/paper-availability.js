(() => {
  const labels={available:'Available for a contribution',in_progress:'Review in progress',awaiting_review:'Awaiting editorial review',awaiting_integration:'Accepted · awaiting integration'};
  let request;
  function catalog(){
    if(!request)request=fetch('/api/paper-availability',{credentials:'same-origin',cache:'no-store'}).then(async response=>{if(!response.ok)throw new Error('Availability unavailable');return (await response.json()).papers;});
    return request;
  }
  async function attach(node,caseId,compact=false){
    node.classList.add('paper-availability');
    if(compact)node.textContent='Checking contribution availability…';
    try{
      const result=(await catalog())[caseId];
      if(!result||!labels[result.status])throw new Error('No current availability');
      node.dataset.status=result.status;
      const message=document.createElement('p');message.textContent=compact?labels[result.status]:result.message;message.setAttribute('role','status');
      if(compact){node.replaceChildren(message);return;}
      const heading=document.createElement('h2');heading.textContent=labels[result.status];
      node.replaceChildren(heading,message);
      if(result.available){
        const action=document.createElement('a');action.href='/contribute.html?'+new URLSearchParams({view:'compose',case:caseId});action.target='_blank';action.rel='noopener';action.className='paper-report-link';action.textContent='Submit a revision ↗';action.setAttribute('aria-label','Submit a revision (opens in a new tab)');
        const hint=document.createElement('p');hint.className='small';hint.textContent='Download the matching template and upload a PDF or LaTeX report. The form opens in a new tab; sign in or register to save your submission.';node.append(action,hint);
      }
    }catch{
      node.textContent='Availability could not be loaded. Open the contribution workspace to check before starting a report.';
      if(!compact){const retry=document.createElement('button');retry.type='button';retry.textContent='Check again';retry.addEventListener('click',()=>{request=null;attach(node,caseId);});node.append(retry);}
    }
  }
  window.ELVIA_PAPER_STATUS={attach};
  document.querySelectorAll('[data-paper-availability]').forEach(node=>attach(node,node.dataset.paperAvailability));
})();
