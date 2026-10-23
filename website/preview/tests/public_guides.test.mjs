import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile, stat} from 'node:fs/promises';

const site = new URL('../site/', import.meta.url);
const collection = new URL('../../../studies/neurips2025/', import.meta.url);

test('public report guide links both complete template pairs without requiring a session', async () => {
  const page = await readFile(new URL('report-templates.html', site), 'utf8');
  for (const route of ['first-report', 'revision-report']) {
    for (const extension of ['tex', 'pdf']) {
      const target = `assets/report-templates/${route}/main.${extension}`;
      assert.ok(page.includes(`href="/${target}"`), `missing ${route} ${extension}`);
      const data = await readFile(new URL(target, site));
      if (extension === 'pdf') assert.equal(data.subarray(0, 5).toString(), '%PDF-');
      else assert.match(data.toString(), /\\end\{document\}/);
    }
  }
  assert.doesNotMatch(page, /(?:workspace|home-entry)\.js|<form\b/);
  for (const anchor of ['first-report-example', 'revision-report-example']) {
    assert.ok(page.includes(`id="${anchor}"`));
    assert.ok(page.includes(`href="#${anchor}"`));
  }
  assert.match(page, /Fictional teaching example/);
  assert.match(page, /excluded from research evidence/);
});

test('showcase links resolve to existing record revisions and real problem numbers', async () => {
  const page = await readFile(new URL('exemplary-cases.html', site), 'utf8');
  const cards = [...page.matchAll(/<article\b[^>]*data-case-id="([^"]+)"[^>]*data-revision="(\d+)"[\s\S]*?<\/article>/g)];
  assert.equal(cards.length, 4);
  for (const [card, caseId, revision] of cards) {
    const record = JSON.parse(await readFile(new URL(`records/${caseId}.r${revision}.json`, collection), 'utf8'));
    const verification = JSON.parse(await readFile(new URL(`evidence/${caseId}/verification.json`, collection), 'utf8'));
    assert.equal(record.revision, Number(revision));
    assert.ok(card.includes('Independent review pending'));
    const caseLinks = [...card.matchAll(new RegExp(`href="(/atlas/cases/${caseId}\\.html)(#problem-(\\d+))?"`, 'g'))];
    assert.ok(caseLinks.length > 0);
    for (const [, , , problem] of caseLinks) {
      if (problem) assert.ok(Number(problem) <= verification.problems.length, `${caseId} has no Problem ${problem}`);
    }
    assert.ok(card.includes(record.audit.pdf_url), 'original source link must match the retained record');
  }
});

test('public guide local styles and in-page navigation have real targets', async () => {
  for (const file of ['report-templates.html', 'exemplary-cases.html']) {
    const page = await readFile(new URL(file, site), 'utf8');
    for (const [, path] of page.matchAll(/<link[^>]*rel="stylesheet"[^>]*href="([^"]+)"/g)) {
      assert.ok((await stat(new URL(path, site))).isFile());
    }
    for (const [, fragment] of page.matchAll(/href="#([^"]+)"/g)) {
      assert.ok(page.includes(`id="${fragment}"`), `${file} has no #${fragment}`);
    }
  }
});
