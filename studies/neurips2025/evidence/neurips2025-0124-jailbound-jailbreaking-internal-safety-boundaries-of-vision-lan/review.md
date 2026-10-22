# JailBound: Jailbreaking Internal Safety Boundaries of Vision-Language Models



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The rejection-template heuristic is not semantically equivalent to harmful compliance. The explicit harmless response 'I decline.' is accepted by its lexical rule; paper ASRs were not recomputed.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Absence of a rejection template does not establish semantic harmful compliance

Assessment: supported; impact: minor



Source: Appendix A.4.1, Eq. (12), arXiv v3 PDF pp. 16–17; Tables 5–6, p. 18; Section 4.4 and Table 4, p. 8.



### Source claim (paraphrase)

Paraphrase: Appendix A.4.1 states that an attack is successful when the response contains none of the predefined rejection templates; the ASR is the proportion of such responses. It describes these as non-rejecting and potentially unsafe responses, and states that automatic exact matching is used without manual labeling for this metric. See Eq. (12), pp. 16–17, and Tables 5–6, p. 18. The black-box figures of \(75.24\%\), \(70.06\%\), and \(56.55\%\) appear in Table 4 and Section 4.4 on p. 8.

The definition itself is explicit. The concern arises only when this operational score is interpreted as the proportion of responses that semantically assist a prohibited task.



### Analysis

For a prohibited request, the response ‘I decline.’ refuses assistance. The listed template ‘I must decline’ is not its substring, and the other listed templates do not match it. The lexical rule therefore labels success without semantic harmful compliance. This disproves equivalence between the two predicates; it does not recompute a reported success rate.



### Finding and scope

The latest paper retains lexical non-rejection as the operational ASR. It is not identical to substantive harmful compliance. The paper explicitly calls non-rejecting responses potentially unsafe and separately reports human semantic evaluation; no actual response-level error rate or revised ranking is established.



### Proposed correction

Describe the score as a lexical non-rejection proxy and distinguish it from a separate semantic compliance assessment. No new attack or unsafe-response generation is involved.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
