const normalize=value=>value.normalize('NFKD').replace(/\p{M}/gu,'').toLocaleLowerCase();
export const matchesExpertise=(label,group,query)=>normalize(label+' '+group).includes(normalize(query.trim()));

export function institutionField(value,{field,el,api}) {
  const wrapper=field('institution','Institution or organization','text',value,'Start typing to search institutions, or enter your affiliation manually.',true);
  wrapper.classList.add('institution-field');
  const input=wrapper.querySelector('input'),id=input.id+'-suggestions';
  const list=el('div',{id,class:'institution-suggestions',role:'listbox',hidden:true,'aria-label':'Institution suggestions'});
  const message=el('span',{class:'hint',role:'status','aria-live':'polite'});
  const source=el('span',{class:'hint'},'Institution names from ',el('a',{href:'https://ror.org/',target:'_blank',rel:'noopener noreferrer'},'ROR'),'.');
  input.maxLength=300;input.setAttribute('role','combobox');input.setAttribute('aria-autocomplete','list');input.setAttribute('aria-controls',id);input.setAttribute('aria-expanded','false');
  let timer,sequence=0,choices=[],active=-1;
  const close=()=>{list.hidden=true;input.setAttribute('aria-expanded','false');input.removeAttribute('aria-activedescendant');active=-1;};
  const choose=index=>{if(!choices[index])return;input.value=choices[index].name;input.dispatchEvent(new Event('input',{bubbles:true}));sequence++;clearTimeout(timer);message.textContent='Institution selected. You can edit the name if needed.';input.focus();close();};
  const highlight=index=>{active=index;[...list.children].forEach((node,i)=>node.setAttribute('aria-selected',i===index?'true':'false'));if(list.children[index]){input.setAttribute('aria-activedescendant',list.children[index].id);list.children[index].scrollIntoView({block:'nearest'});}};
  const search=()=>{
    const query=input.value.trim().slice(0,150),request=++sequence;clearTimeout(timer);close();
    if(query.length<2){message.textContent='';return;}
    timer=setTimeout(async()=>{
      message.textContent='Searching institutions…';
      try {
        const result=await api('/institutions?q='+encodeURIComponent(query));
        if(request!==sequence||document.activeElement!==input)return;
        choices=result.items||[];list.replaceChildren(...choices.map((item,i)=>el('div',{id:id+'-'+i,role:'option','aria-selected':'false',class:'institution-option',onmousedown:event=>{event.preventDefault();choose(i);}},el('strong',{},item.name),el('span',{},item.location))));
        message.textContent=!result.available?'Institution search is temporarily unavailable. Enter your institution manually.':choices.length?choices.length+' suggestions. Use the arrow keys and Enter to select.':'No matching institution found. You can use the name you entered.';
        list.hidden=!choices.length;input.setAttribute('aria-expanded',choices.length?'true':'false');
      }catch {if(request===sequence)message.textContent='Institution search is temporarily unavailable. Enter your institution manually.';}
    },300);
  };
  input.addEventListener('input',search);
  input.addEventListener('keydown',event=>{
    if(event.key==='Escape'){sequence++;clearTimeout(timer);close();return;}
    if(list.hidden)return;
    if(['ArrowDown','ArrowUp'].includes(event.key)){event.preventDefault();highlight((active+(event.key==='ArrowDown'?1:-1)+choices.length)%choices.length);}
    else if(event.key==='Enter'&&active>=0){event.preventDefault();choose(active);}
  });
  input.addEventListener('blur',()=>{sequence++;clearTimeout(timer);close();});
  const control=el('div',{class:'institution-control'});input.replaceWith(control);control.append(input,list);
  wrapper.append(message,source);return wrapper;
}

export function expertiseField(old,catalog,{el,p,field,setRequired}) {
  const chosen=new Set(old.expertise_fields||[]);
  let custom=old.expertise_other||'';
  if(!chosen.size&&old.expertise){chosen.add('Other');custom=old.expertise;}
  const wrapper=el('div',{class:'field full expertise-field'},el('div',{class:'field-heading'},'Relevant expertise',el('span',{class:'field-requirement'},'Optional')),p('Choose up to five areas, including Other. Search by subject or method.','hint'));
  const chips=el('div',{class:'expertise-chips','aria-label':'Selected expertise'});
  const summary=el('summary',{}),picker=el('details',{class:'expertise-picker'},summary);
  const search=field('expertise_search','Search areas of expertise','search','','Search '+catalog.fields.reduce((n,g)=>n+g.items.length,0)+' subjects and methods.');
  const input=search.querySelector('input'),list=el('div',{class:'expertise-options'}),count=p('','hint');count.setAttribute('role','status');
  const other=field('expertise_other','Other area of expertise','text',custom,'Describe your additional specialty.');
  const otherInput=other.querySelector('input');otherInput.maxLength=3000;
  const groups=[...catalog.fields,{group:'Additional expertise',items:['Other']}];
  const controls=[];
  function refresh(){
    summary.textContent=chosen.size?'Selected '+chosen.size+' of 5 areas':'Search and select areas (up to 5)';
    other.hidden=!chosen.has('Other');otherInput.disabled=other.hidden;setRequired(otherInput,!other.hidden);
    chips.replaceChildren(...[...chosen].map(name=>el('button',{type:'button',class:'expertise-chip','aria-label':'Remove '+name,onclick:()=>{chosen.delete(name);refresh();}},name+' ×')));
    for(const [name,control] of controls){control.checked=chosen.has(name);control.disabled=chosen.size>=5&&!chosen.has(name);if(control.disabled)control.dataset.locked='true';else delete control.dataset.locked;}
    otherAction.disabled=chosen.has('Other')||chosen.size>=5;
    if(otherAction.disabled)otherAction.dataset.locked='true';else delete otherAction.dataset.locked;
    filter();
  }
  for(const group of groups){
    const section=el('fieldset',{},el('legend',{},group.group));
    for(const name of group.items){
      const control=el('input',{type:'checkbox',checked:chosen.has(name),'aria-label':name,onchange:()=>{if(control.checked&&chosen.size<5)chosen.add(name);else chosen.delete(name);refresh();}});
      const row=el('label',{class:'expertise-option'},control,el('span',{},name));row.dataset.name=name;row.dataset.group=group.group;section.append(row);controls.push([name,control]);
    }
    list.append(section);
  }
  function filter(){
    let visible=0;
    for(const section of list.children){let total=0;for(const row of section.querySelectorAll('.expertise-option')){row.hidden=!matchesExpertise(row.dataset.name,row.dataset.group,input.value);if(!row.hidden)total++;}section.hidden=!total;visible+=total;}
    count.textContent=chosen.size>=5?'Five areas selected. Remove an area to choose another.':visible?visible+' matching options · '+chosen.size+' of 5 selected.':'No matching area. Choose Other to add your specialty.';
  }
  input.addEventListener('input',filter);
  input.addEventListener('keydown',event=>{if(event.key==='Enter')event.preventDefault();if(event.key==='Escape'){picker.open=false;summary.focus();}});
  const otherAction=el('button',{type:'button',class:'text-link expertise-other-action',onclick:()=>{if(chosen.size<5){chosen.add('Other');refresh();picker.open=false;otherInput.focus();}}},'Add another specialty with Other');
  picker.append(search,list,count,otherAction);
  picker.addEventListener('toggle',()=>{if(picker.open)input.focus();});
  wrapper.append(chips,picker,other);refresh();
  return {element:wrapper,values:()=>({expertise_fields:[...chosen],expertise_other:chosen.has('Other')?otherInput.value.trim():''})};
}

export function researchProfileFields(old,catalog,{el,field,setRequired}) {
  const area=el('div',{class:'form-grid full research-profile-fields'});
  const type=field('profile_type','Research profile','select',old.profile_type||(old.profile_url?'Other':''),'Choose a profile service, then enter its full URL.',false,catalog.profile_types.map(x=>[x,x]));
  type.querySelector('option').textContent='No profile added';
  const url=field('profile_url','Profile URL','url',old.profile_url||'','');
  const other=field('profile_other','Other profile service','text',old.profile_other||(old.profile_url&&!old.profile_type?'Research profile':''));
  const select=type.querySelector('select'),address=url.querySelector('input'),custom=other.querySelector('input');
  custom.maxLength=100;
  function refresh(){
    setRequired(select,!!address.value.trim());setRequired(address,!!select.value);
    other.hidden=select.value!=='Other';custom.disabled=other.hidden;setRequired(custom,!other.hidden);
    address.placeholder=select.value==='ORCID'?'https://orcid.org/0000-0000-0000-0000':select.value==='Google Scholar'?'https://scholar.google.com/citations?user=…':'https://';
  }
  select.addEventListener('change',refresh);address.addEventListener('input',refresh);
  area.append(type,url,other);refresh();return area;
}
