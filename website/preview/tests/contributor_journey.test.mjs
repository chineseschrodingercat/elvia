import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

const source=await readFile(new URL('../site/workspace.js',import.meta.url),'utf8');
const contextModule=async()=>import('data:text/javascript;base64,'+Buffer.from(await readFile(new URL('../site/case-context.js',import.meta.url),'utf8')).toString('base64'));

test('Reading legal documents preserves the active registration page',()=>{
  const links=[];
  const row={classList:{add(){}},querySelector:()=>({append(){}})};
  const node=(tag,attrs,...children)=>{const result={tag,...attrs,children};if(tag==='a')links.push(result);return result;};
  const code=source.slice(source.indexOf('function policyAcknowledgement('),source.indexOf('function googleSignIn('));
  vm.runInNewContext(code+'\npolicyAcknowledgement();',{check:()=>row,el:node,link:(text,href)=>node('a',{href},text)});
  assert.equal(links.length,2);
  for(const link of links){assert.equal(link.target,'_blank');assert.match(link.rel,/noopener/);assert.match(link['aria-label'],/new tab/);}
});

test('Only bounded case identifiers and existing problem numbers become a context',async()=>{
  const {parseCaseContext,resolveCaseContext}=await contextModule();
  for(const value of ['../private','https://evil.example/a','x/../../account','<script>'])assert.equal(parseCaseContext(new URLSearchParams({case:value})),null);
  const record={case_id:'fixture-paper',revision:1,source:{title:'Synthetic title'},audit:{venue:'Fixture',landing_url:'https://example.org/paper',outcome:'candidate_issue'}};
  const payload={records:[record],case_notes:{'fixture-paper':{revision:1,problems:[{title:'Synthetic question'}]}}};
  const context=resolveCaseContext(parseCaseContext(new URLSearchParams('case=fixture-paper&problem=1')),payload);
  assert.equal(context.caseId,'fixture-paper');assert.equal(context.problem,1);
  assert.equal(context.caseUrl,'/atlas/cases/fixture-paper.html#problem-1');
  for(const query of ['case=missing','case=fixture-paper&problem=2','case=fixture-paper&problem=0','case=fixture-paper&problem=999999'])assert.equal(resolveCaseContext(parseCaseContext(new URLSearchParams(query)),payload),null);
});

test('Contribution and application links retain paper context without carrying credentials',async()=>{
  const {addCaseContext}=await contextModule();
  const query=addCaseContext('view=apply',{caseId:'fixture-paper',problem:2,password:'never-copy'});
  const params=new URLSearchParams(query);
  assert.equal(params.get('view'),'apply');assert.equal(params.get('case'),'fixture-paper');assert.equal(params.get('problem'),'2');assert.equal(params.has('password'),false);
});

test('A linked draft carries identity and scope without inventing a scientific assessment',async()=>{
  const {draftIdentity}=await contextModule();
  const data=draftIdentity({caseId:'fixture-paper',problem:1,title:'Synthetic title',venue:'Fixture',sourceUrl:'https://example.org/paper',problemTitle:'Synthetic question'});
  assert.equal(data.title,'Synthetic title');assert.equal(data.source_url,'https://example.org/paper');assert.match(data.scope,/Problem 1/);
  assert.equal(data.assessment,undefined);assert.equal(data.conflict_clear,undefined);assert.equal(data.ai_used,undefined);
});

test('Linked drafts use the assigned research field for either venue instead of guessing from the conference',async()=>{
  const {resolveCaseContext,draftIdentity}=await contextModule();
  const fields=[['Mathematics','mathematics'],['Biological science','biological_science'],['Computer science','computer_science'],['Chemistry','chemistry'],['Others','others']];
  for(const venue of ['NeurIPS','ICML'])for(const [label,expected] of fields){
    const record={case_id:'fixture-paper',revision:1,source:{title:'Synthetic title'},audit:{venue,landing_url:'https://example.org/paper',outcome:'candidate_issue'}};
    const context=resolveCaseContext({caseId:'fixture-paper',problem:null},{records:[record],research_fields:{'fixture-paper':label}});
    assert.equal(context.field,expected,venue+' / '+label);
    assert.equal(draftIdentity(context).field,expected);
  }
});

test('An absent or unknown research field never becomes an inferred conference classification',async()=>{
  const {resolveCaseContext}=await contextModule();
  const record={case_id:'fixture-paper',revision:1,source:{title:'Synthetic title'},audit:{venue:'NeurIPS',landing_url:'https://example.org/paper',outcome:'candidate_issue'}};
  for(const label of [undefined,'Unknown','toString']){
    const context=resolveCaseContext({caseId:'fixture-paper',problem:null},{records:[record],research_fields:{'fixture-paper':label}});
    assert.equal(context.field,'');
  }
});
