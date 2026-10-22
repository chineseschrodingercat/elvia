# Co-PatcheR: Collaborative Software Patching with Component(s)-specific Small Reasoning Models



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The author-released validator/ranker has bounded before/after and verdict-contract defects. Historical benchmark impact has not been demonstrated; voting multiplicity remains an intended-definition question. The strict paper label is Minor.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Normalized voting does not count sample multiplicity

Assessment: needs_evidence; impact: needs_evidence



Source: Section 3.1, p.4; Section 3.3, p.6; Appendix D, pp.24–25; rerank.py:155–199,318–384.



### Source claim (paraphrase)

The method is described as normalized majority voting among equally best validated candidates.



### Analysis

The ranker first deduplicates raw strings. In \([A,B,B,B]\), that leaves one vote per text, so first-seen \(A\) wins. In \([A,A,A,B_1,B_2]\), where \(B_1,B_2\) differ only by whitespace, normalized counting can give \(A\) one vote and \(B\) two. Thus this is voting over distinct raw strings rather than sample multiplicity. The paper does not fully define duplicate weights, so an intentional variant remains possible.



### Finding and scope

This remains a bounded scope or unresolved-source concern; broader experimental invalidity is not established.



### Proposed correction

Define duplicate weights explicitly. If sampling-majority is intended, preserve multiplicities; no claim is made that an intentional deduplicated variant is invalid.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: Final rank ignores a computed rule-based PoC result

Assessment: supported; impact: minor



Source: patchpilot/repair/rerank.py; reproduce/verify.py and task.py; paper PoC contract.



### Source claim (paraphrase)

Assertion-based PoCs are described as independently testing reproduction and repair.



### Analysis

The final ranking path does not use the already computed rule-based PoC judgment. However, ordinary nonzero assertion failures are converted to runner exceptions earlier, so one cannot claim the same normal execution both accepted that failing assertion and reached rank. The supported concern is missing rank-contract enforcement for the records that do reach it.



### Finding and scope

The stated local claim or source contract fails as described. Its effect on historical experiment scores is unmeasured.



### Proposed correction

Define a structured execution/verdict contract and include the applicable assertion verdict in rank; distinguish exceptions from failed tests.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Existing test failures abort validation and count differences miss regressions

Assessment: supported; impact: minor



Source: Author reproduce/verify.py and task.py: baseline/after-patch test execution and failure-count ranking.



### Source claim (paraphrase)

The validator should repair the affected behavior while preserving previously working functionality.



### Analysis

A failing baseline test can raise before patch application, blocking the intended before/after path. Where evaluation reaches ranking by another route, a difference in failure counts cannot distinguish fixing one old failure from introducing one new failure, since both leave the count unchanged. Per-test identities are required. This source-contract example does not estimate SWE-bench performance.



### Finding and scope

The stated local claim or source contract fails as described. Its effect on historical experiment scores is unmeasured.



### Proposed correction

Capture baseline test outcomes without aborting the patch flow, and compare per-test outcome sets for new failures. Full benchmark scores require a separate rerun.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, model spending, training, author contact or complete benchmark replication.

- Historical numerical results are retained evidence rather than current reruns.

- Local counterexamples do not invalidate every empirical result; missing historical run attribution remains unresolved.
