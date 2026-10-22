import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

const home = await readFile(new URL('../site/index.html', import.meta.url), 'utf8');
const workspace = await readFile(new URL('../site/contribute.html', import.meta.url), 'utf8');
const source = await readFile(new URL('../site/workspace.js', import.meta.url), 'utf8');
const navFunction = source.slice(source.indexOf('function nav()'), source.indexOf('function loginPage('));

function anchors(html) {
  return [...html.matchAll(/<a\b[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/g)]
    .map(([,href,label]) => ({href,label:label.replace(/<[^>]*>/g,'').trim()}));
}

test('Atlas exploration opens the read-only collection from the homepage', () => {
  const links = anchors(home);
  assert.equal(links.find(link => link.label === 'Browse the collection')?.href, '/atlas/');
  assert.equal(links.filter(link => link.label === 'Explore the Atlas').length, 2);
  assert.ok(links.filter(link => link.label === 'Explore the Atlas').every(link => link.href === '/atlas/'));
  assert.ok(!home.includes('id="collection-toggle"'));
});

test('Home and Atlas remain reachable in fallback and every account navigation state', () => {
  const fallback = anchors(workspace);
  for (const [label,href] of [['Home','/'],['Atlas','/atlas/']]) {
    assert.ok(fallback.some(link => link.label === label && link.href === href));
  }
  for (const role of [null,'contributor','admin','maintainer']) {
    let rendered;
    const context = {
      session:{user:role ? {role} : null},
      isHomeAccount:false,
      isStaff:() => ['admin','maintainer'].includes(role),
      href:query => '/contribute.html' + (query ? '?' + query : ''),
      link:(label,href) => ({label,href}),
      document:{querySelector:() => ({replaceChildren:(...items) => {rendered = items;}})},
    };
    vm.runInNewContext(navFunction + '\nnav();', context);
    assert.ok(rendered.some(link => link.label === 'Home' && link.href === '/'), role || 'signed out');
    assert.ok(rendered.some(link => link.label === 'Atlas' && link.href === '/atlas/'), role || 'signed out');
    if (role) {
      const accountLink = role === 'contributor' ? 'My work' : 'Manage';
      assert.ok(rendered.some(link => link.label === accountLink));
    } else {
      assert.ok(!rendered.some(link => /sign in|register|create an account/i.test(link.label)), 'guest entry links belong only on the homepage');
    }
  }
});
