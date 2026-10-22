# Sim-LLM: Optimizing LLM Inference at the Edge through Inter-Task KV Reuse



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The public Sim-LLM cache path can misassign tasks, rotate reused keys twice, duplicate a fresh cache and evict the wrong recency entry. Variable-length matching also has a known shape restriction.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Cache insertion order does not preserve task identity

Assessment: supported; impact: minor



Source: Section 3.3, PDF p.6; Algorithm 1, PDF p.25; modeling_llama_lsh.py, lines 120–171 and 1522–1535



### Source claim (paraphrase)

The matching loop is cache-first, while deletion and sequential reinsertion use current-batch indices. Neither sorted current indices nor unique current targets are enforced.



### Analysis

Matches \((0,1),(1,0)\) delete the first two current rows, leaving value \(12\). Insert cache value \(100\) at row \(1\), then \(101\) at row \(0\): output is \([101,12,100]\), while task-specific assignment requires \([101,100,12]\). Zero attention logits and constant row values transfer the same mismatch to the attention output. Single or correctly ordered matches can pass.



### Finding and scope

The released assembly can associate a task with another task’s values. Historical incidence is unknown.



### Proposed correction

Choose at most one cache entry per current task under a declared tie rule, then assign each final row by its original task index rather than insertion order.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Already rotated keys receive another rotary transform

Assessment: supported; impact: minor



Source: Section 3.3, PDF p.6; modeling_llama_lsh.py, lines 153–171, 753–782 and 2172–2197



### Source claim (paraphrase)

The traced producer stores post-RoPE keys; the consumer inserts those keys before applying RoPE to the assembled tensor.



### Analysis

At position \(p=1\), raw key \((1,0)\) is stored as \((\cos1,\sin1)\). Equal-position reuse should retain it, but the consumer returns \((\cos2,\sin2)\). A correspondingly rotated query changes its dot product from \(1\) to \(\cos1\). Position zero is a passing special case.



### Finding and scope

The producer/consumer representation contracts disagree. An unrotated-cache convention is a different contract.



### Proposed correction

Insert post-RoPE caches after rotating new keys. To move a cached key from position \(p\) to \(q\), apply \(R_qR_p^\top\) with trustworthy positional metadata.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: A fresh target-layer cache is appended to itself

Assessment: supported; impact: minor



Source: forward_predict_prompt, modeling_llama_lsh.py, lines 2172 and 2239–2254



### Source claim (paraphrase)

`forward_predict_prompt` overwrites the incoming-cache variable with the current output, then concatenates its target layer with the same output layer.



### Analysis

With no incoming past and a three-token prompt, both operands are \((K,V)\). The target cache becomes \(([K;K],[V;V])\); a three-layer layout has lengths \((3,6,3)\) instead of \((3,3,3)\). The duplication occurs after initial hidden states are computed.



### Finding and scope

The returned generation cache is wrong for this fresh-prompt case. Nonempty-prefix behavior requires a separate accumulated-cache contract.



### Proposed correction

Keep the incoming cache under a distinct name and return the fresh target cache once. Append a prefix only where the documented backend returns new segments rather than already accumulated states.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 4: Reference bits do not implement exact LRU

Assessment: supported; impact: minor



Source: Section 3.3, PDF p.6; Appendix B.1, PDF p.23; Algorithm 1, PDF p.25; source lines 1544–1547 and 2214–2234



### Source claim (paraphrase)

The branch labeled LRU stores a reference bit and clears leading set bits rather than recording chronological recency.



### Analysis

For slots \([A,B,C]\), access order \(B,C,A\) leaves bits \((1,1,1)\). The code clears them and replaces slot zero, evicting most-recent \(A\); true LRU evicts \(B\). The same bit vector represents several different recency orders.



### Finding and scope

This is a different cache policy. No throughput advantage for exact LRU is established.



### Proposed correction

Specify the reference-bit approximation, or maintain timestamps/an ordered recency structure and evict the actual oldest access under a deterministic batch convention.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 5: Unequal prompt lengths fail the tokenwise matcher

Assessment: supported; impact: minor



Source: Public repository issue #1; modeling_llama_lsh.py, lines 1522–1535



### Source claim (paraphrase)

The matcher directly compares tokenwise cached and current embeddings without a common-length alignment contract.



### Analysis

Nonzero shapes \((1,2,2)\) and \((1,3,2)\) cannot broadcast across token dimensions \(2\) and \(3\). Equal padded widths avoid this failure, as in fixed-width settings, but do not solve general K/V alignment. Repository issue #1, opened 30 April 2026, already reported the concern.



### Finding and scope

This is a known public shape restriction, not a new discovery or a refutation of fixed-width experiments.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
