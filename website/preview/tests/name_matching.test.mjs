import test from 'node:test';
import assert from 'node:assert/strict';
import {nameNorm,namesMatch,nameContains,uniqueNameMatch} from '../site/name-matching.js';
test('Unicode letters, extended names and superscript digits survive punctuation removal',()=>{
  assert.equal(nameNorm("Élie-Cartan's Δβ_²: Notes!"),nameNorm('elie cartans ΔΒ2 notes'));
  assert.equal(nameNorm('Straße & Søren (α)'),nameNorm('STRASSE Søren α'));
  assert.notEqual(nameNorm('α Journal'),nameNorm('β Journal'));
  assert.notEqual(nameNorm('ø Journal'),nameNorm('o Journal'));
  assert.equal(nameNorm('中文_期刊 ²'),'中文期刊2');
  assert.equal(nameNorm('Theoretical Biology'),'theoreticalbiology');
});
test('Common aliases remain usable without turning collisions into approvals',()=>{
  assert.ok(namesMatch('Geometry & Topology','geometry and topology'));
  assert.ok(namesMatch('The Annals of Probability','Annals of Probability'));
  assert.ok(nameContains('Søren–α_2 Review','Α 2'));
  assert.equal(uniqueNameMatch('A.B. Journal',[{name:'A B Journal'},{name:'AB Journal'}]),null);
});
