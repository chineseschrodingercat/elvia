# Execution Guided Line-by-Line Code Generation



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Held-out success controls retries/selection in a known released evaluation issue. The top-five endpoint also differs from full-distribution classifier-free guidance, including tested guidance settings.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Held-out evaluation success influences retries and candidate selection

Assessment: supported; impact: minor



Source: Section 3.4, PDF p. 6; Section 4, Evaluation Benchmarks, PDF p. 7; Appendix C, Algorithm 1, PDF p. 19.



### Source claim (paraphrase)

Section 4, PDF p. 7, reserves held-out tests for assessment, while Section 3.4 and Appendix C, Algorithm 1, use task-visible feedback. Released datasets_utils.py, lines 173–260, separates public test_list from held-out eval_test_list. eg_cfg_session_manager.py, solve_problem_with_eg_cfg_wrapper and solve_single_problem, lines 491–731, instead use held-out success to stop retries and guidance search.



### Analysis

Let the public test require \(f(0)=0\), satisfied by both candidate \(A:f(x)=0\) and candidate \(B:f(x)=x\), generated in that order. A held-out requirement \(f(1)=0\) makes the controller stop at \(A\), while changing only that held-out requirement to \(f(1)=1\) makes it continue and select \(B\). Candidate and attempt count depend on held-out feedback even when the held-out text never enters a prompt. This is a source-level selection argument, not a new model-generation run.



### Finding and scope

The inspected release performs test-dependent selection. This known release-level concern does not by itself establish the historical benchmark's affected fraction or a corrected score.



### Proposed correction

Use only task-visible feedback for selection and retries, reserving the held-out tests for one final assessment of the selected candidate.

Known evaluation-selection issue independently reproduced by the proposed clarification; historical table impact remains unresolved.

Known evaluation-selection issue independently reproduced by the proposed clarification; historical table impact remains unresolved.



## Problem 2: Top-five zero filling can change the token selected by the stated CFG rule

Assessment: supported; impact: minor



Source: Sections 3.2–3.3, Eqs. (13)–(14), PDF p. 6; Algorithm 2, lines 29–31, PDF p. 19; released endpoint top-five path.



### Source claim (paraphrase)

The token rule in Sections 3.2–3.3, Eqs. (13)–(14), PDF p. 6, and Algorithm 2, lines 29–31, p. 19, applies guidance and takes the resulting argmax. The endpoint implementation requests only five token log probabilities (consts.py:\(215\), inference_endpoint_utils.py:\(432\)–\(472\)). model_utils.py:\(57\)–\(67\) creates a zero vector for the vocabulary and fills only returned probabilities. probs_utils.py:\(38\)–\(48\) applies guidance to those reconstructed vectors.



### Analysis

For six tokens, take full positive probability vectors

\[P=(0.30,0.25,0.20,0.15,0.09,0.01),\qquad P_c=(0.005,0.008,0.010,0.015,0.022,0.940).\]

Both sum to one. At \(\gamma=1/2\), the full rule assigns token \(6\) weight \(\sqrt{0.0094}\approx0.09695\), greater than every competing weight (at most \(\sqrt{0.00225}\approx0.04743\)). At \(\gamma=3\), its weight is \(0.94^3/0.01^2=8305.84\), again uniquely largest. The endpoint zero-fills token \(6\) in the prior because it lies outside that prior’s top five. The outer factor in \(\widetilde P_i[(\widetilde P_{c,i}+\epsilon)/(\widetilde P_i+\epsilon)]^\gamma\) then makes its guided mass zero. Epsilon inside the ratio cannot restore it. The explicitly optimized \(\gamma=1\) path and local full-logit path remain valid countercontrols.



### Finding and scope

This is a supported local finding within the stated source/formulation scope. Its effect on the paper's aggregate experimental results remains unmeasured.



### Proposed correction

For available full positive distributions, use the stated log score \((1-\gamma)\log P_i+\gamma\log P_{c,i}\). If only truncated probabilities are available, identify the sparse approximation explicitly; the full-distribution guarantee is unavailable.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
