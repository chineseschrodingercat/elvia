const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('website/preview/site/public-security.js', 'utf8');

function browser() {
  const children = [], removed = [];
  const document = {
    createElement: tag => ({tag, setAttribute() {}, append() {}, showModal() {}, remove() { removed.push(tag); }}),
    body: {append(node) { children.push(node); }},
    head: {append(node) { queueMicrotask(() => node.onload()); }},
  };
  let settings;
  const window = {turnstile: {render(_node, value) {settings=value; queueMicrotask(() => value.callback('fresh-token')); return 'widget';}, remove() {}}};
  vm.runInNewContext(source, {window,document,setTimeout,clearTimeout,
    fetch: async () => ({ok:true,json:async()=>({turnstile_sitekey:'site-key'})})});
  return {window,children,removed,settings:()=>settings};
}
test('protected operations receive a fresh one-use token and clean up the widget', async () => {
  const b = browser();
  assert.equal(await b.window.ELVIA_SECURITY.token('/auth/login'), 'fresh-token');
  assert.equal(b.settings().action, 'login');
  assert.ok(b.removed.includes('dialog'));
});
test('ordinary requests do not load a challenge', async () => {
  const b = browser();
  assert.equal(await b.window.ELVIA_SECURITY.token('/me'), null);
  assert.equal(b.children.length, 0);
});
