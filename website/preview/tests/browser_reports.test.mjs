import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const source=await readFile(new URL('../site/report-files.js',import.meta.url),'utf8');
const {validateUploadFiles,reportRequirements,uploadSlot,aiReviewGuidance}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const MiB=1024*1024;
function el(tag,attrs={},...children){return {tag,...attrs,children:children.flat(Infinity).filter(x=>x!=null),listeners:{},classList:{add(){},remove(){}},append(...x){this.children.push(...x.flat(Infinity));},addEventListener(name,fn){this.listeners[name]=fn;}};}
const p=text=>el('p',{},text);
const workspace=await readFile(new URL('../site/workspace.js',import.meta.url),'utf8');
const showRecord=new Function('el','p','link','assessments',workspace.slice(workspace.indexOf('function showRecord('),workspace.indexOf('async function summaryPage('))+';return showRecord;')(el,p,(label,url)=>el('a',{href:url},label),{unresolved:'I could not resolve the question'});
function descendants(node){return node.children.flatMap(x=>typeof x==='object'?[x,...descendants(x)]:[]);}

test('file-report receipts do not present a generated unresolved placeholder as the contributor assessment',()=>{
  const output=el('div');showRecord(output,{editor:'files',assessment:'unresolved'});
  assert.ok(!JSON.stringify(output).includes('I could not resolve the question'));
  assert.ok(JSON.stringify(output).includes('Scientific findings, severity and limitations are in the uploaded report.'));
  const legacy=el('div');showRecord(legacy,{assessment:'unresolved'});
  assert.ok(JSON.stringify(legacy).includes('I could not resolve the question'));
});
test('first and revision routes expose only their own matching TeX and PDF template',()=>{
  for(const initial of [true,false]){const node=reportRequirements(initial,{el,p}),links=descendants(node).filter(x=>x.tag==='a');const kind=initial?'first-report':'revision-report';assert.equal(links.length,2);assert.ok(links.every(x=>x.href.includes('/'+kind+'/')));assert.ok(links[0].href.endsWith('.tex'));assert.ok(links[1].href.endsWith('.pdf'));assert.equal(links[1].target,'_blank');}
});
test('report and original-paper slots enforce their separate formats and size limits',()=>{
  validateUploadFiles('report',[{name:'report.tex',size:20*MiB}]);
  validateUploadFiles('source',[{name:'paper.pdf',size:50*MiB}]);
  validateUploadFiles('paper-supplement',[{name:'supp.pdf',size:20*MiB}],30*MiB);
  assert.throws(()=>validateUploadFiles('source',[{name:'paper.pdf',size:30*MiB+1}],20*MiB),/Compress/);
  for(const [slot,name,size] of [['report','report.zip',100],['report','report.pdf',20*MiB+1],['source','paper.tex',10],['paper-supplement','supp.pdf',50*MiB+1]])assert.throws(()=>validateUploadFiles(slot,[{name,size}]));
});
test('verification code accepts one ZIP or up to ten files under a shared five-MB budget',()=>{
  validateUploadFiles('verification-code',Array.from({length:10},(_,i)=>({name:`check${i}.py`,size:100})));
  validateUploadFiles('verification-code',[{name:'code.zip',size:5*MiB}]);
  for(const files of [Array.from({length:11},()=>({name:'check.py',size:1})),[{name:'a.py',size:MiB},{name:'b.py',size:4*MiB+1}],[{name:'code.zip',size:10},{name:'check.py',size:10}]])assert.throws(()=>validateUploadFiles('verification-code',files));
});
test('browse and drag-drop share the same selected-file handler and ignore drops while busy',()=>{
  const received=[],slot=uploadSlot({slot:'verification-code',label:'Code',hint:'Optional',el,p,onFiles:files=>received.push(files)}),files=[{name:'check.py',size:42}];
  slot.input.files=files;slot.input.listeners.change();let prevented=0;
  slot.node.listeners.drop({preventDefault(){prevented++;},dataTransfer:{files}});
  assert.deepEqual(received,[files,files]);assert.equal(prevented,1);
  slot.input.disabled=true;slot.node.listeners.drop({preventDefault(){},dataTransfer:{files}});assert.equal(received.length,2);
});

test('routine report guidance hides PDF limits, shows the code limit, and welcomes both AI and manual review',()=>{
  for(const initial of [true,false]){
    const text=JSON.stringify(reportRequirements(initial,{el,p}));
    assert.ok(!/20 MB|50 MB|up to [0-9]+ MB/.test(text));
  }
  const message=JSON.stringify(aiReviewGuidance({el,p}));
  for(const text of ['strongly encouraged','ChatGPT','Claude','Gemini','manual reviews'])assert.ok(message.includes(text));
});
