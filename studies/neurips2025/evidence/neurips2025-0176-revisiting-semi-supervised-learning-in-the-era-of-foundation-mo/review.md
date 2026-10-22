# Revisiting Semi-Supervised Learning in the Era of Foundation Models



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The default release selects teachers using squared average ranks and transforms vote counts by softmax, differing from the written average-rank and mean-label operations. Exact inputs change selection and distillation gradients; historical benchmark selections remain unresolved.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Mean squared rank can select a different teacher

Assessment: supported; impact: minor



Source: Section 3.3, PDF p.5; Appendix C.1; tune_print.py and gen_config_pet.py rank branches



### Source claim (paraphrase)

The paper minimizes average validator rank; the default and teacher-generation branches square ranks first.



### Analysis

Across seven tie-free validators, let A ranks be \(1,1,1,1,1,3,3\), B ranks \(2,2,2,2,2,1,1\), C ranks \(3,3,3,3,3,2,2\). Ordinary means are \(11/7,12/7,19/7\), uniquely choosing A. Squared means are \(23/7,22/7,53/7\), choosing B. Each validator is a valid strict permutation. This is an operator-input example, without asserting the exact joint scores arise in the reported images. Squared mean equals squared mean rank plus across-validator variance, adding a different preference.



### Finding and scope

The two selection rules are inequivalent. A non-squared reporting option exists, but does not change the separately squared teacher-generation branches; actual published choices remain unknown.



### Proposed correction

Follow the stated mean-rank operation in every relevant branch, or explicitly define and attribute squared-rank selection with its dispersion sensitivity.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: Softmax of counts is not a mean one-hot label

Assessment: supported; impact: minor



Source: Algorithm 1, PDF p.7; PETHook.init_pl voting branch and distillation target path



### Source claim (paraphrase)

The stated target is \(v/K\), whereas the release passes \(\operatorname{softmax}(v)\) into the soft distillation loss.



### Analysis

Four teachers voting for classes \(0,0,1,2\) give counts \((2,1,1,0)\). Mean labels are \((0.5,0.25,0.25,0)\); the release gives approximately \[(0.534447,0.196612,0.196612,0.072329)\]. At zero student logits, the KL gradient is student probability minus target: the written target gives \((-0.25,0,0,0.25)\), while the release gives \[(-0.284447,0.053388,0.053388,0.177671)\]. Argmax labels agree, but soft training differs. Duplicating every teacher preserves vote proportions while sharpening the released distribution.



### Finding and scope

The release retains scale-insensitive teacher argmax voting but uses a different soft target and optimization path. No actual accuracy change is established.



### Proposed correction

Use \(v/K\) to restore Mean Label, or explicitly specify the count-dependent softmax target and distinguish that design from average labels.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
