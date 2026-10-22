# Structure-Aware Cooperative Ensemble Evolutionary Optimization on Combinatorial Problems with Multimodal Large Language Models



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Three mutable/cached-state defects affect the author-released evolutionary implementation. They are concrete local faults, but damage to the paper's central network results is not quantified. The strict label is Minor, and the EDV objective is not refuted.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Layout outputs alias one mutable candidate

Assessment: supported; impact: minor



Source: EA_utils.py:71–94,181–188; paper Sections 3.4.3 and Figure 2.



### Source claim (paraphrase)

The method obtains separate layout-specific mutations and aggregates them by consensus voting.



### Analysis

MLLM_mutate changes its candidate list in place. Each layout receives the same list, and saved outputs keep that same reference. Successive replacements \(2,3,4\) can leave every voting input equal to \([4,1]\), so the three supposedly independent proposals become the last mutated state. Earlier layouts also receive changed inputs.



### Finding and scope

The layout proposals alias the same mutable candidate, so consensus need not aggregate independent layout outputs.



### Proposed correction

Copy the original list independently for each layout and preserve independent result snapshots; no full-network benchmark repair is asserted.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: Mutation can alter retained parents and elites

Assessment: supported; impact: minor



Source: Single-layout mutation caller, elite storage and EVC generation update.



### Source claim (paraphrase)

Elite preservation assumes the stored candidate and fitness refer to the same solution.



### Analysis

The single-layout branch mutates a list shared with its parent/elite record. Its node set can therefore change without refreshing the associated fitness. This breaks the state/fitness invariant independently of multi-layout voting.



### Finding and scope

The elite’s stored fitness can become inconsistent with its mutated solution.



### Proposed correction

Copy before mutation and recompute fitness for the exact stored candidate; benchmark effect remains unmeasured.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Injected improvements do not refresh processor best state

Assessment: supported; impact: minor



Source: Distributed.py/EVC.py injection and best-state update paths.



### Source claim (paraphrase)

Cross-domain injection is intended to retain a better evaluated solution.



### Analysis

After accepting a superior injected candidate, the processor leaves its cached best solution/fitness unchanged. A later generation or summary can lose the better evaluated solution by consulting stale best state. This is distinct from whether the injected solution is actually feasible.



### Finding and scope

The cross-domain injection route can discard a superior evaluated candidate by keeping stale best state. Historical score effects remain unmeasured.



### Proposed correction

Update the accepted population state and cached best candidate/fitness together. Corrected local bookkeeping does not establish a full MLLM benchmark result.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, model spending, training, author contact or complete benchmark replication.

- Historical numerical results are retained evidence rather than current reruns.

- Local counterexamples do not invalidate every empirical result; missing historical run attribution remains unresolved.
