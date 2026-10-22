// Unicode letters and numbers survive; formatting and punctuation do not.
export const nameNorm=value=>String(value).normalize('NFKD').toLowerCase()
  .replace(/ß/g,'ss').replace(/ς/g,'σ').replace(/[^\p{L}\p{N}]/gu,'');
export function nameKeys(value){
  const text=String(value),variants=[text,text.replace(/^\s*the\s+/i,'')];
  return [...new Set(variants.flatMap(v=>[nameNorm(v),nameNorm(v.replace(/&/g,' and '))]).filter(Boolean))];
}
export const namesMatch=(a,b)=>nameKeys(a).some(x=>nameKeys(b).includes(x));
export const nameContains=(value,query)=>nameKeys(value).some(v=>nameKeys(query).some(q=>v.includes(q)));
export function uniqueNameMatch(name,entries){
  const matches=entries.filter(x=>[x.name,x.full_name||'',...(x.aliases||[])].some(v=>namesMatch(name,v)));
  return matches.length===1?matches[0]:null;
}
