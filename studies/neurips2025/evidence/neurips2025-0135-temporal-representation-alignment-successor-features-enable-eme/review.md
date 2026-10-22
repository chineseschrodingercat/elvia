# Temporal Representation Alignment: Successor Features Enable Emergent Compositionality in Robot Instruction Following



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



A geometric-series proof bound fails on admissible parameters. A reported Welch comparison matches two-sided rather than specified one-sided p-values, and the linked latent-width configuration is ignored.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The geometric-series term in Equation (20) exceeds its claimed bound

Assessment: supported; impact: minor



Source: Section 3.5, Theorem 1, PDF p. 5; Appendix F.1 restatement p. 16 and Eq. (20), p. 18.



### Source claim (paraphrase)

Mathematical transcription, with surrounding assumptions paraphrased: Theorem 1, Section 3.5, PDF p. 5, and Appendix F.1, p. 16, asserts

\[\operatorname{ERR}(\pi;D^\ast) \leq \operatorname{ERR}(\pi;D) +\frac{\alpha-1}{2\alpha} +\frac{\alpha-2}{2\alpha}\mathbf 1_{\{\alpha>2\}},\]



### Analysis

Set \(H=2\), \(H'=3\), \(\gamma=3/4\), and \(\alpha=3/2\), satisfying the printed scalar restrictions. The geometric term is \((1+3/4)/3=7/12\), whereas the claimed upper bound is \((\alpha-1)/(2\alpha)=1/6\). The proof's \(7/12\le1/6\) step is false. This calculation invalidates that step without purporting to refute every possible proof of the final task-error statement.



### Finding and scope

The cited geometric bound needs replacement or stronger assumptions. No task-performance or learning experiment was rerun.



### Proposed correction

The scalar term is at most \(H/H^{\prime}\) for \(0\le\gamma<1\), since every summand is at most one. Replacing this one bound does not by itself repair the full task-error theorem.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: Table 6 uses two-sided p-values where a one-sided Welch test is specified

Assessment: supported; impact: minor



Source: Section 4.3, PDF p. 8; Appendix D.2, PDF p. 15; Table 3, PDF p. 16; Appendix H, Table 6, PDF p. 20.



### Source claim (paraphrase)

Paraphrase: Section 4.3, PDF p. 8, and Appendix H, p. 20, specify a one-sided Welch comparison to the best-performing method, with significance level 0.05. Table 6 gives language-conditioned t- and p-values; Table 7 gives image-conditioned values. Appendix D.2, p. 15, specifies five baseline trials, while Table 3, p. 16, lists ten task trials.

For cloth folding, Table 1 reports TRA \(1.00\) and LCBC 0.40. Table 6 reports \(t=2.45\), \(p=0.070\). The table formatting treats this comparison as not significantly different from the best method.



### Analysis

Under the documented binary-success trial interpretation, ten successes versus two successes in five trials give Welch \(t=\sqrt6\) and \(4\) degrees of freedom. The one-sided p-value is \(0.035242\), while the two-sided value is \(0.070484\), matching the printed \(0.070\). Thus this reconstructed comparison crosses the stated unadjusted \(0.05\) threshold under the specified directional test. The conclusion is conditional on that published trial protocol.



### Finding and scope

The reconstructed binary-trial comparison changes a nominal significance annotation, in the direction of strengthening the observed TRA advantage; raw trial logs are still needed for a complete table audit.



### Proposed correction

If the stated one-sided Welch comparison is the intended prespecified test, the folding p-value under the published binary-trial reconstruction is approximately \(0.035\), and its ‘not significantly different’ marking changes under the nominal unadjusted \(0.05\) rule. This is conditional on that trial interpretation; no unreported comparisons or multiplicity correction are inferred.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 3: The linked implementation ignores the documented latent-dimension setting

Assessment: supported; impact: minor



Source: Table 5, PDF p. 19; released latent-dimension constructor.



### Source claim (paraphrase)

Table 5, PDF p. 19, specifies latent width \(64\). Released agents/tra.py, from line 193, constructs the encoder output width from the example observation dimension rather than value_latent_dim.



### Analysis

An observation width of \(29\) therefore creates width \(29\) even when value_latent_dim requests \(64\), and changing that configuration alone has no effect. This is static configuration correspondence, not a reproduced robotic-learning result.



### Finding and scope

Current linked code ignores the documented width, but it predates the expanded proceedings and does not identify the final simulation implementation.



### Proposed correction

Identify the final experiment commit and consistently parameterize feature and actor dimensions, checking their coupled initialization and forward shapes before treating a constructor edit as a safe fix.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
