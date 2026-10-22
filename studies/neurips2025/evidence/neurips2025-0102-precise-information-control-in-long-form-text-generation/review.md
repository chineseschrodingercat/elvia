# Precise Information Control in Long-Form Text Generation



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The released perturbation and likelihood-scoring paths disagree with the specified preference-data construction, and the judge-based coverage metric needs a directional distinction. Their impact on the published results is unmeasured; the omission-inclusive terminology is retained as counterevidence.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Reduced claims are recorded but are not supplied to the perturbation generator

Assessment: supported; impact: minor



Source: Section 4.2, PDF pp. 5–6; Algorithm 1, PDF p. 47.



### Source claim (paraphrase)

Section 4.2, pp. 5–6, and Algorithm 1, p. 47, require a strict subset \(C_{\mathrm{perturb}}\subset C_{\mathrm{orig}}\) to be passed to the SFT model when \(|C_{\mathrm{orig}}|>1\). Algorithm 1 returns the original set when its size is at most one; the two-claim counterexample below is outside that exception:

\[ y_{\mathrm{perturb}}=\theta_{\mathrm{SFT}}(I,C_{\mathrm{perturb}}). \]



### Analysis

The released function computes perturbed_claims but passes the original claims to format_claims, then stores the reduced set beside the resulting generation. With \(C_{\rm orig}=\{A,B\}\) and \(C_{\rm perturb}=\{A\}\), the generation prompt still includes \(B\). This contradicts the reduced-context construction locally, but the frequency of this path and its downstream training effect are unknown.

The same released pathway also calls save_file_jsonl with a path before its records, whereas the author helper declares data before path. This adjacent persistence mismatch blocks that route when reached; it does not establish which program produced the paper’s training dataset.



### Finding and scope

The generation prompt retains removed claims, violating the released preference-data contract; published training lineage and effect are not established.



### Proposed correction

Format the reduced claims rather than the original list, check prompt/record correspondence, and pass the records before the file path to save_file_jsonl.

A local correction or qualification is proposed where specified; author adoption is not established.

The existing local proposal is retained; the current author-released source still contains the identified behavior. No author adoption is established.



## Problem 2: Batched likelihood scoring uses logits after the target token and can reverse the preference label

Assessment: supported; impact: minor



Source: Section 4.2, PDF p. 6; Algorithm 1, lines 19–24, PDF p. 47.



### Source claim (paraphrase)

Section 4.2, p. 6, and Algorithm 1 lines 19–24, p. 47, choose preferences using

\[ \Delta=\ell_{\mathrm{orig}}-\ell_{\mathrm{perturb}}, \qquad z=\operatorname{sigmoid}(\Delta), \]



### Analysis

In a causal language model the logit at position \(t-1\) predicts token \(t\). For prompt \((1,2)\), original response \((3,4,5)\), and perturbed response \((5,5,5)\), take a vocabulary of size \(12\) and logits \(6\) for the successor of the current token and \(0\) elsewhere. Correct alignment gives \(\ell_{\rm orig}=-0.0269011709\), \(\ell_{\rm perturb}=-6.0269011709\), and \(z=\sigma(6)\approx0.997527\). The current batched code includes the final post-target logit and takes its last three positions, giving both averages \(-6.0269011709\) and \(z=0.5\). The strict test \(z>\tau\) therefore selects different preferences at \(\tau=0.5\). Padding introduces an additional endpoint problem; the correctly shifted single-example source is an unaffected control.



### Finding and scope

The one-position causal shift can reverse the selection statistic, but the score pathway used for the published trained models is not established.



### Proposed correction

The proposed correction aligns each response token with its preceding-position logit and excludes padding.

A local correction or qualification is proposed where specified; author adoption is not established.

The existing local proposal is retained; the current author-released source still contains the identified behavior. No author adoption is established.



## Problem 3: Forward support indices do not establish reverse coverage of the original claims

Assessment: supported; impact: minor



Source: Section 2.3, PDF p. 4; Appendix B.2.2, PDF p. 31.



### Source claim (paraphrase)

Section 2.3, p. 4, defines precision and recall through semantic equivalence, with recall applying support to an input claim against the generated claim set. Appendix B.2.2, p. 31, similarly counts unique input claims actually present in the response. This is a coverage requirement.

The operational prompt, however, asks whether an output claim is supported by one or more input claims; it does not require equivalence or ask whether the supporting input claim is fully recovered. The released claim_verifier.py, lines 27–34, implements that forward direction. Then metrics.py, lines 21–24, computes recall by counting distinct indices returned as forward support.



### Analysis

The input statement ‘exactly two votes’ supports the output ‘at least one vote’, but the output does not recover the input. Returning input index \(1\) as forward support and counting distinct such indices gives recall \(1\), even though reverse entailment fails. Forward support and input coverage require separate decisions.



### Finding and scope

Forward entailment indices do not certify full input recovery; the witness exposes a metric capability without measuring its occurrence in benchmark outputs.



### Proposed correction

The proposed clarification separates output support from reverse input-coverage judgments.

A local correction or qualification is proposed where specified; author adoption is not established.

The existing local proposal is retained; the current author-released source still contains the identified behavior. No author adoption is established.



## Problem 4: Malformed judge responses can be scored as support, and empty outputs acquire invented unsupported counts

Assessment: supported; impact: minor



Source: Appendix B.2, PDF pp. 30–31; released claim_verifier.py, lines 61–66, and empty-output/index handling in the metrics.



### Source claim (paraphrase)

The same verifier, lines 61–66, treats a response as unsupported if it contains the word unsupported; every other response is classified as supported. It does not require the supported label, a valid index list, or an index within the input range. The metric code counts unique indices without range validation.



### Analysis

A malformed judge result is not affirmative support. The inspected permissive parser can accept such outputs, while the empty-output metric substitutes the number of source claims for unsupported generated claims. An empty generated set contains zero unsupported generated claims, even if its recall is zero.



### Finding and scope

Malformed judge text and empty-output counts are mishandled, with unknown incidence in cached experimental judgments.



### Proposed correction

The proposed correction distinguishes supported, unsupported and invalid judgments, and defines empty-set metric counts explicitly.

A local correction or qualification is proposed where specified; author adoption is not established.

The existing local proposal is retained; the current author-released source still contains the identified behavior. No author adoption is established.



## Problem 5: A failure of perfect full-PIC F1 is not necessarily an unsupported-content hallucination

Assessment: not_issue; impact: no_issue_found



Source: Abstract and introduction, PDF pp. 1–2; task-evaluation definition, PDF p. 4.



### Source claim (paraphrase)

The abstract, p. 1, introduces faithfulness hallucination in terms of generated information not substantiated by the input. The introduction on the same page explicitly includes omissions, distortions, and fabrications in its broader usage of hallucination. The introduction, p. 2, and task evaluation, p. 4, relate a less-than-\(30\%\) perfect full-PIC F1 rate to a greater-than-\(70\%\) hallucination statement. Under the explicitly broader convention, an omission can coherently count as a hallucination. The issue below concerns reading that headline as a measured rate of unsupported generated content under the abstract’s narrower description. It is a terminological and inference-scope clarification, not a newly measured hallucination-rate correction.



### Analysis

For input \(\{A,B\}\) and output \(\{A\}\), precision is \(1\), recall is \(1/2\), and \(F_1=2/3\), despite no unsupported assertion. This limits a narrow unsupported-content interpretation of the headline. The introduction explicitly includes omissions in its definition, so the example does not contradict the authors' broader convention.



### Finding and scope

Terminology/scope clarification only; no new numerical benchmark error is established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
