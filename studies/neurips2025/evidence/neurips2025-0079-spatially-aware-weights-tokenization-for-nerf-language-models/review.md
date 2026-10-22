# Spatially-aware Weights Tokenization for NeRF-Language Models



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The public evaluator truncates candidates while leaving references intact, and inference caches omit the task identity. The fine-tuning summary also overstates a small quantitative bound.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: The evaluator ignores candidate text after its character cutoff

Assessment: supported; impact: minor



Source: Section 5, p. 6; traditional_evaluator.py lines 55–73.



### Source claim (paraphrase)

`traditional_evaluator.py`, `evaluate_result`, slices the candidate to its first two hundred characters before all traditional metrics, while retaining the complete reference.



### Analysis

An identical \(639\)-character, \(80\)-word answer can be truncated to \(25\) words. With perfect unigram matches on that prefix, BLEU’s brevity penalty is \(\exp(1-80/25)=e^{-2.2}\approx0.110803\), rather than \(1\). Any changed suffix beyond the cutoff is invisible.



### Finding and scope

The released function does not score complete long answers. Original prediction files and exact experiment versions are needed for publication-wide impact.



### Proposed correction

Remove the character slice or declare and apply a justified symmetric evaluation policy. No recovered benchmark score is supplied.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Inference cache identity omits the task

Assessment: supported; impact: minor



Source: Sections 5–6; eval_spatial_llana.py main, lines 138–154.



### Source claim (paraphrase)

`eval_spatial_llana.py`, `main`, creates a model-basename/split output file and returns if it exists before reading the task-specific data selector.



### Analysis

Brief captions, detailed captions and single-round answers on the same split therefore share a filename and can reuse an earlier task’s output. Model and split alone do not identify the inference request.



### Finding and scope

The public cache key is incomplete. No claim that the authors reused wrong predictions in the reported tables is established.



### Proposed correction

Include task identity and validate model/checkpoint, dataset revision and generation settings before cache reuse.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: The fine-tuning gaps exceed the stated universal one-point bound

Assessment: supported; impact: minor



Source: Section 6, p. 9, Table 6 discussion; Table 5, p. 8.



### Source claim (paraphrase)

Section 6 says frozen-LLM variants stay within one point across reported metrics.



### Analysis

Table 6’s unambiguous question-answering gaps are \(1.06\), \(1.05\), \(1.50\) and \(1.50\) percentage points. These exceed the literal universal bound. Spatial columns differ between Tables 5 and 6 and cannot be reconciled from the inspected text alone.



### Finding and scope

The quantitative summary needs narrowing. The broader observation that freezing retains much performance can remain true.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
