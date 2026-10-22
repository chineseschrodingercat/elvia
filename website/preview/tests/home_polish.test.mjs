import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const home = await readFile(new URL('../site/index.html', import.meta.url), 'utf8');

test('homepage replaces decorative status/process rows with a session-aware visitor invitation', () => {
  assert.ok(!home.includes('class="review-status"'));
  assert.ok(!home.includes('class="evidence-thread"'));
  const invitation = home.match(/<aside\b[^>]*class="[^"]*home-visitor-notice[^\"]*"[^>]*data-visitor-notice[\s\S]*?<\/aside>/)?.[0];
  assert.ok(invitation, 'homepage invitation shares existing authenticated-session visibility');
  assert.match(invitation, /create an account/i);
  assert.match(invitation, /sign in/i);
  assert.match(invitation, /browse all articles and comments without an account/i);
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

test('homepage three-action identity/order and same-homepage form destinations remain intact', () => {
  const start = home.indexOf('<div class="hero-actions">');
  const actions = home.slice(start, home.indexOf('</section>', start));
  assert.ok(actions);
  const labels = ['Explore the Atlas', 'Contributor sign in', 'Register to contribute'];
  assert.ok(labels.every((label, i) => !i || actions.indexOf(labels[i - 1]) < actions.indexOf(label)));
  assert.ok(actions.includes('/?view=login#contributor-access'));
  assert.ok(actions.includes('/?view=register#contributor-access'));
});
