# CURE: Concept Unlearning via Orthogonal Representation Editing in Diffusion Models



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Finite soft erase/retain composition does not exactly preserve shared directions; an explicit identical-subspace calculation disproves that central operator interpretation. Other orientation, arithmetic, disclosure and runtime corrections are Minor. Main tables with no retain projector are not invalidated by the nonempty-retain counterexample.



## Scope

All ten original concerns, fresh current proceedings formulas/results/appendices and current pinned generation/README release inspected. Exact finite operator and count arguments checked; no editing model, attack, author code or old verifier was executed.



## Problem 1: Weighted erase/retain composition does not preserve shared directions as claimed

Assessment: supported; impact: major



Source: PDF p.5 Eq 4–5; Fig 2 p.4; AppendixC pp.23–24



### Source claim (paraphrase)

The finite-weight operator in Eq. (5) removes only discriminative forget directions while preserving components shared with a nonempty retain set.



### Analysis

Use \(E_f=E_r=\operatorname{diag}(\sqrt{0.8},\sqrt{0.2})\) and \(\alpha=2\). Eqs. (\(1\))-(\(5\)) give \(P_f=P_r=\operatorname{diag}(8/9,1/3)\). The purported distinct-forget operator is \(P_f(I-P_r)=\operatorname{diag}(8/81,2/9)\), so the edit is \(A=\operatorname{diag}(73/81,7/9)\). Both directions are completely shared, yet both are attenuated. Zero-padding embeds the example in the paper's higher-dimensional space. Choosing \(W=I\), or a rectangular cross-attention row that reads either affected direction, makes the corresponding output change explicit. The current Appendix C disclaims global optimality and worst-case behavioral guarantees, but the finite linear shared-component assertion after Eq. (5) is still contradicted. Main Tables 1–4 use \(P_r=0\), so this witness is not a reconstruction of those measured outcomes.

Even hard projectors do not generally have intersection projector \(P_fP_r\): for \(P_f=\operatorname{diag}(1,0)\) and \(P_r=\frac12\begin{pmatrix}1&1\\1&1\end{pmatrix}\), their subspaces intersect only at zero but \(P_fP_r\ne0\). However, a truly hard retain projector still preserves every \(v\) with \(P_rv=v\), because \([I-P_f(I-P_r)]v=v\). The soft-retain counterexample must not be generalized to that hard-retain property.



### Finding and scope

The unconditional shared-direction preservation interpretation is false for the paper's finite soft weights. Main tables using \(P_r=0\) are not thereby shown numerically wrong.



### Proposed correction

Describe the edit as soft spectral attenuation, or residualize forget directions against an orthonormal retain basis \(Q_r\). A residual basis \(Q_d\subset R^\perp\) gives \(A_{\rm corr}=I-Q_dQ_d^\top\), with \(A_{\rm corr}Q_r=Q_r\) and \(A_{\rm corr}Q_d=0\). This linear guarantee does not certify all semantic behavior.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: SVD orientation conflicts with appendix matrix dimensions

Assessment: supported; impact: minor



Source: PDF p.4 Eq 1; p.5 Eq 4–6; p.24



### Source claim (paraphrase)

The SVD-based projector acts on the declared embedding dimension.



### Analysis

For a token matrix of shape \(6\times768\), reduced SVD has \(U\in\mathbb R^{6\times6}\) and \(V^\top\in\mathbb R^{6\times768}\). A projector built from \(U\) cannot act on a \(768\)-dimensional embedding. Transposing the token matrix or using the right singular vectors resolves the orientation.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Transpose embedding matrix or use \(V\Lambda V^\top\); specify padding, token selection, rank and normalization.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Table arithmetic inconsistencies

Assessment: supported; impact: minor



Source: PDF p.7 Table 2; p.9 Table 4



### Source claim (paraphrase)

The printed table totals and averages follow from their displayed entries.



### Analysis

In current Table 2, the SA counts \(39,9,4,0,10,32,49,15\) sum to \(158\), whereas the total is \(163\). Current Table 4’s RECE erased entries have only three nonzero values, \(2.0,6.2,0.9\), giving the ten-class mean \(0.91\), not \(0.3\). Its retained values average \(78.38\), not \(78.5\); the difference exceeds the combined displayed-rounding allowance. These show internal arithmetic conflicts, not which input or aggregate was transcribed incorrectly. Unstated unequal class weights would require an explicit alternative definition.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Rebuild all tables from counts and explicit denominators; clarify any nonuniform averaging.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: ASR percent units and I2P protocol ambiguity

Assessment: supported; impact: minor



Source: PDF p.7 Table 2; p.8 Table 3



### Source claim (paraphrase)

ASR units and I \(2\) P detector events define one consistent evaluation protocol.



### Analysis

The current Table 3 caption uses percent units but lists values such as \(0.061\), ambiguous between \(0.061\%\) and a fraction \(6.1\%\). Under the additional condition that Tables 2 and 3 use the same \(4703\) images, detector threshold, categories and image-positive event, Table 2’s \(11\) detected parts imply at most \(11\) positive images, hence \(\mathrm{ASR}\le11/4703\approx0.234\%\). This cannot equal a fraction \(0.061\), but different samples, detectors or event definitions could reconcile the tables. The units discrepancy is direct; the cross-table numerical conflict remains conditional.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Publish per-column count/denominator, detector, threshold, seeds, image counts, prompts and attack budgets; separate differing cohorts/events.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: LLM evaluation disclosure contradiction

Assessment: supported; impact: minor



Source: PDF p.6 style evaluation; p.20 alpha ablation; pp.17–18 checklist 16



### Source claim (paraphrase)

The evaluation/checklist consistently disclose LLM judging.



### Analysis

GPT-4o classifier described in method, checklist explicitly denies LLM evaluation.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Correct declaration and release exact evaluator version, prompt, labels, image order, repetitions and raw judgments.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: Artist scaling narrative exceeds Figure6 retention range

Assessment: supported; impact: minor



Source: PDF p.6 artist paragraph; p.9 Figure 6 and caption



### Source claim (paraphrase)

The artist-scaling results preserve the stated retention across the claimed range.



### Analysis

CLIP plot approximately \(20.8\) at \(100\), \(15.7\) at \(500\), \(12.6\) at \(1000\); caption itself bounds near-original regime to 100.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Report the tested maximum \(1000\) separately from the near-preservation regime around \(100\) or fewer concepts. Identify retain-set and joint/sequential edit conditions.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: Finite-alpha soft erasure is generally invertible

Assessment: not_issue; impact: no_issue_found



Source: Paper Eqs. (3)-(6); Appendix C; main experiments use \(P_r=0\).



### Source claim (paraphrase)

Finite soft spectral editing is used for behavioral concept suppression.



### Analysis

With \(P_r=0\), an edit eigenvalue is \((1-r)/(1+(\alpha-1)r)\), positive for finite \(\alpha>0\) and \(r<1\). Thus an example \(A=\operatorname{diag}(1/9,2/3)\) is invertible, and someone knowing \(A\) and \(WA\) can algebraically recover \(W\). This is a linear information-scope observation, not a successful concept-recovery attack. The paper’s behavioral unlearning target does not require every weight transform to be irreversible.



### Finding and scope

Invertibility alone does not refute the specified behavioral target; no separate current error is established by this observation.



## Problem 8: Public release lacks core unlearning implementation

Assessment: needs_evidence; impact: needs_evidence



Source: Pinned official repository snapshot; official PDF: code-availability checklist item 5, p. 15.



### Source claim (paraphrase)

The public release includes the core unlearning operation.



### Analysis

The unchanged current author release supplies generation code, environment and example prompts; its README says complete unlearning code will be released later. The public source therefore cannot settle operator orientation, padding/top-component choices or paper timing. The generation script creates a model-specific directory but writes images to the shared save_path with case/number names, so reusing one output directory across models can overwrite matching filenames. This is a static output-path risk, not evidence that historical evaluation files were actually overwritten. The paper’s claim of an attachment supplied to reviewers does not establish that it is publicly available.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Publish core editor, complete experiment configs, prompt lists and metric outputs; generation script should save into model-specific directory to avoid overwrites.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 9: Significance and broad retention/superiority claims lack matching evidence

Assessment: needs_evidence; impact: needs_evidence



Source: PDF pp.6–8 Tables 1/3; p.16 checklist 7; p.21 Table 7



### Source claim (paraphrase)

The shown evidence supports the unrestricted significance, retention and superiority claims.



### Analysis

No confidence intervals, small style prompt set; UnlearnDiffAtk difference \(.281\) vs \(.282\); Table 7 overall improvement but not best in hate/harassment/illegal activity.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Use paired prompt-level estimates and confidence intervals, separate aggregate and category-specific conclusions, identify actual retain evaluation population.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 10: Normalization limit and constant-runtime explanation inaccurate

Assessment: supported; impact: minor



Source: PDF p.5 Eq 2–4; p.24 runtime discussion



### Source claim (paraphrase)

Normalization limits and runtime have the stated interpretation.



### Analysis

\(\alpha=1\) recovers normalized \(r\), not unnormalized \(\sigma^2\). Text encoding/SVD cost depends on token/concept count despite fixed weight-application cost.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Normalize Eq \(2\) or clarify proportional equivalence; report encoding/SVD/edit cost separately versus input size.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, training, empirical replication or contact.

- Historical verification outputs were inspected but not rerun.

- Missing run provenance and unresolved empirical interpretations remain explicit.
