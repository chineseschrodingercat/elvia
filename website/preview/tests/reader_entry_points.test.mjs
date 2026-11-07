import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const home = await readFile(new URL('../site/index.html', import.meta.url), 'utf8');
const atlas = await readFile(new URL('../../atlas-assets/index.html', import.meta.url), 'utf8');
const paths = await readFile(new URL('../site/exemplary-cases.html', import.meta.url), 'utf8');

test('a first-time reader can enter a worked argument before contributor access', () => {
  const hero = home.slice(home.indexOf('<section class="hero'), home.indexOf('id="contributor-access"'));
  assert.match(hero, /href="\/exemplary-cases.html"[^>]*>Follow a worked argument/);
  assert.ok(home.indexOf('Follow a worked argument') < home.indexOf('id="contributor-guest-actions"'));
  assert.doesNotMatch(hero, /id="contributor-guest-actions"/);
  assert.match(hero, /Independent scientific review pending/);
  assert.doesNotMatch(hero, /ask a question/i);
});

test('the primary reading selection includes a source-bound mathematics path', () => {
  assert.match(home, /href="\/exemplary-cases.html#incidences"/);
  const math = paths.match(/<article id="incidences"[\s\S]*?<\/article>/)?.[0];
  assert.ok(math, 'a mathematics entry must lead to a complete guide');
  assert.match(math, /data-case-id="math2025-0071" data-revision="1"/);
  assert.match(math, /Lower bounds for incidences/);
  assert.match(math, /s00222-025-01331-2/);
  assert.match(math, /incidence exponents[^<]*not/i);
  assert.match(math, /\/atlas\/cases\/math2025-0071.html#problem-1/);
});

test('secondary filters remain accessible without preceding all results on mobile', () => {
  const secondary = atlas.match(/<details class="more-filters"[\s\S]*?<\/details>/)?.[0];
  assert.ok(secondary, 'venue and finding filters need an explicit disclosure');
  assert.match(secondary, /<summary[^>]*>[\s\S]*More filters/);
  for (const id of ['venue', 'outcome']) assert.match(secondary, new RegExp('id="' + id + '"'));
  for (const id of ['search', 'field', 'severity']) assert.ok(atlas.indexOf('id="' + id + '"') < atlas.indexOf('<details class="more-filters"'));
  assert.doesNotMatch(atlas, /Search papers or ask a question/);
  assert.match(atlas, /conformal coverage/);
  assert.match(atlas, /\/exemplary-cases.html/);
});
