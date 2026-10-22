import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const css=await readFile(new URL('../site/workspace.css',import.meta.url),'utf8');
// This focused cascade evaluator covers the simple class/type/descendant color
// rules used here. Rendered-browser QA remains the final visual check.
function node(tag,classes='',parent=null){return {tag,classes:classes.split(' ').filter(Boolean),parent};}
function matches(selector,target,pseudo){
  if(/[>+~:#\[]/.test(selector.replace(/::marker/g,'')))return false;
  const marker=selector.endsWith('::marker');
  if(marker!==Boolean(pseudo))return false;
  const parts=selector.replace(/::marker$/,'').trim().split(/\s+/);
  const simple=(part,value)=>{
    const tokens=part.match(/(?:\.[\w-]+)|(?:^[a-z]+)|\*/g)||[];
    return tokens.length>0&&tokens.every(token=>token==='*'||(token.startsWith('.')?value.classes.includes(token.slice(1)):value.tag===token));
  };
  if(!simple(parts.pop(),target))return false;
  let parent=target.parent;
  for(const part of parts.reverse()){
    while(parent&&!simple(part,parent))parent=parent.parent;
    if(!parent)return false;
    parent=parent.parent;
  }
  return true;
}
function color(target,pseudo=''){
  const candidates=[];let order=0;
  for(const rule of css.replace(/\/\*[\s\S]*?\*\//g,'').matchAll(/([^{}]+)\{([^{}]*)\}/g)){
    const value=rule[2].match(/(?:^|;)\s*color\s*:\s*(#[0-9a-f]+)\s*(?:;|$)/i)?.[1];
    for(const selector of rule[1].split(',')){
      order++;
      if(!value||!matches(selector.trim(),target,pseudo))continue;
      const classes=(selector.match(/\.[\w-]+/g)||[]).length;
      const types=(selector.replace(/\.[\w-]+/g,'').match(/\b[a-z]+\b/g)||[]).length;
      candidates.push({value,weight:classes*100+types,order});
    }
  }
  candidates.sort((a,b)=>b.weight-a.weight||b.order-a.order);
  return candidates[0]?.value||(pseudo?color(target):target.parent?color(target.parent):undefined);
}

test('Password rule items and markers override the academic black list rule',()=>{
  const workspace=node('main','workspace'),field=node('div','field',workspace);
  const list=node('ul','field-error password-errors',field),item=node('li','',list);
  assert.equal(color(item),'#b42318');
  assert.equal(color(node('strong','',item)),'#b42318');
  assert.equal(color(item,'::marker'),'#b42318');
});

test('Summary and submitted-error descendants stay red while ordinary lists stay black',()=>{
  const workspace=node('main','workspace');
  for(const classes of ['validation-summary form-message error','form-message error']){
    const box=node('div',classes,workspace),list=node('ul','',box),item=node('li','',list);
    assert.equal(color(item),'#b42318');
    assert.equal(color(node('a','',item)),'#b42318');
    assert.equal(color(item,'::marker'),'#b42318');
    assert.equal(color(node('p','',box)),'#b42318');
  }
  assert.equal(color(node('li','',node('ul','',workspace))),'#000');
  assert.equal(color(node('p','',workspace)),'#000');
});
