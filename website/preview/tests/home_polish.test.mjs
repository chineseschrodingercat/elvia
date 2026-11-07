import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const home = await readFile(new URL('../site/index.html', import.meta.url), 'utf8');

test('homepage keeps the review boundary visible for readers and signed-in contributors', () => {
  assert.ok(!home.includes('class="review-status"'));
  assert.ok(!home.includes('class="evidence-thread"'));
  const boundary = home.match(/<p class="home-review-boundary">[\s\S]*?<\/p>/)?.[0];
  assert.ok(boundary, 'review scope must remain visible independently of session state');
  assert.doesNotMatch(boundary, /data-visitor-notice/);
  assert.match(boundary, /Independent scientific review pending/);
  assert.match(boundary, /read without an account/i);
});

test('all page header navigations omit Approach and Contribute without removing footer reading links', async () => {
  for (const name of ['index.html', 'contribute.html', 'privacy.html', 'terms.html']) {
    const html = await readFile(new URL('../site/' + name, import.meta.url), 'utf8');
    const header = html.match(/<header\b[\s\S]*?<\/header>/)?.[0];
    assert.ok(header, name);
    assert.ok(!/<a\b[^>]*>\s*(Contribute|Approach)\s*<\/a>/.test(header), name);
  }
  const atlas = await readFile(new URL('../../atlas-assets/index.html', import.meta.url), 'utf8');
  assert.ok(!/<a\b[^>]*>\s*Contribute\s*<\/a>/.test(atlas.match(/<header\b[\s\S]*?<\/header>/)?.[0]), 'Atlas header');
  assert.ok(home.includes('Choose your contribution'), 'existing section browsing link remains');
});

test('reading actions precede contribution access while same-homepage form destinations remain intact', () => {
  const start = home.indexOf('<div class="hero-actions">');
  const actions = home.slice(start, home.indexOf('</section>', start));
  assert.ok(actions);
  assert.ok(actions.includes('Explore the Atlas'));
  assert.ok(actions.includes('Follow a worked argument'));
  assert.ok(!actions.includes('Register to contribute'));
  assert.ok(home.includes('/?view=login#contributor-access'));
  assert.ok(home.includes('/?view=register#contributor-access'));
});
