# LLMs Encode Harmfulness and Refusal Separately



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The inversion evaluator changes the refusal-rate denominator and the extraction path defaults to a mismatched prompt template. The different intervention masks are disclosed and remain a scope qualification.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Invalid answers change the refusal-rate denominator

Assessment: supported; impact: minor



Source: Current arXiv v5 Section 2, PDF p.4; Section 3.5, PDF pp.8–9; src/eval.py, easy_eval and process_layer_evaluation



### Source claim (paraphrase)

Section 2 describes refusal over all test examples. `src/eval.py`, `easy_eval` and `process_layer_evaluation`, instead discard invalid inversion labels before computing the saved rate.



### Analysis

For replies No, Certainly and two abstentions, one negative answer among all four is \(1/4\), but the conditional valid-only rate is \(1/2\). The substring branches also accept “unknown” as containing “no” while rejecting uppercase “NO”. These are denominator and parser differences, not estimates of the actual frequency in Figure 4.



### Finding and scope

The released rate is conditional on accepted labels. The original prediction counts are needed to determine the numerical impact.



### Proposed correction

Retain negative, affirmative and invalid counts. Report unconditional rate \(N_{\rm No}/N\), validity, and any separately named valid-only rate. Use an explicit case-insensitive label contract rather than unrestricted substrings.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Direction extraction defaults to the wrong model template

Assessment: supported; impact: minor



Source: Current arXiv v5 Section 2, PDF p.3, model-template convention; src/extract_hidden.py, generate_directions; src/utils.py, formatInp_llama_persuasion



### Source claim (paraphrase)

The advertised Qwen/Llama3 extraction path calls the prompt formatter without its model argument; `src/utils.py` defaults that argument to Llama2. Intervention passes the model explicitly.



### Analysis

Thus the same selected model can receive Llama2 markers during extraction and model-specific markers during intervention. This changes the formatted sequence and semantic token positions. The release does not establish the extraction provenance of every cached direction.



### Finding and scope

The public reproduction path has a template mismatch; cached directions and cross-model results remain unverified.



### Proposed correction

Pass the selected model explicitly, use the same template as intervention, and identify instruction positions on the complete tokenized sequence rather than an unverified isolated-suffix length.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 3: Direction and intervention support vary together

Assessment: not_issue; impact: no_issue_found



Source: Current arXiv v5 Section 3.5, PDF pp.8–9; Appendix E.1, PDF p.20, Figure 10



### Source claim (paraphrase)

Section 3.5 compares harmfulness and refusal interventions; Appendix E.1 explicitly discloses their different token masks.



### Analysis

Writing outcomes as \(Y(v,m)\), comparing \(Y(v_h,m_{\rm inst})\) with \(Y(v_r,m_{\rm all})\) changes both direction and support. It identifies different intervention packages, rather than an isolated direction effect. Appendix E.1 explicitly explains this choice, and Figure 10 retains the same-support refusal controls.



### Finding and scope

This disclosed design choice does not establish a separate error or invalidate all evidence for distinct directions.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
