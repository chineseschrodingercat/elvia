import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

const source = await readFile(new URL('../site/app.js', import.meta.url), 'utf8');

test('links into consolidated FAQ open the named question and preserve account fragments', () => {
  const start = source.indexOf('function revealQuestion(');
  assert.ok(start >= 0, 'all linked FAQ questions need a shared disclosure handler');
  const questions = new Map(['faq-review', 'faq-search', 'author-contribution'].map(id => [id, {open:false, matches:selector => selector === '.faq details'}]));
  questions.set('contributor-access', {open:false, matches:() => false});
  const handlers = {};
  const location = {hash:'#faq-review'};
  vm.runInNewContext(source.slice(start), {
    location, decodeURIComponent,
    document:{getElementById:id => questions.get(id)},
    window:{addEventListener:(event, handler) => {handlers[event] = handler;}}
  });
  assert.equal(questions.get('faq-review').open, true);
  for (const id of ['faq-search', 'author-contribution']) {
    location.hash = '#' + id; handlers.hashchange();
    assert.equal(questions.get(id).open, true);
  }
  location.hash = '#contributor-access'; handlers.hashchange();
  assert.equal(questions.get('contributor-access').open, false);
  location.hash = '#%ZZ'; assert.doesNotThrow(() => handlers.hashchange());
});
