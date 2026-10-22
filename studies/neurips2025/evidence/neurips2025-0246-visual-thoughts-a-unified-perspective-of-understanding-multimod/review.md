# Visual Thoughts: A Unified Perspective of Understanding Multimodal Chain-of-Thought



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The no-VT comparator suppresses visual descriptions, so the measured gain does not isolate improvement over ordinary unrestricted CoT. Attention and blocking evidence is retained at its local scope; no numerical benchmark error is established.



## Scope

Rapid claim-focused reading of current author-paper passages and relevant released source. Direct mathematical or static-source reasoning is stated below. No author program, inherited verifier, model inference or benchmark was executed.



## Problem 1: The no-VT baseline explicitly suppresses visual reasoning

Assessment: supported; impact: minor



Source: Proceedings Section 4.1, PDF p.5; Table 1, p.6; Appendix C.1, pp.23–24; Appendix B.3 and Figure 11, p.22



### Source claim (paraphrase)

The main text describes the no-VT comparator as without extra instructions, while the appendix explicitly instructs it to avoid visual descriptions. The treatment also adds a separate visual-thought generation stage.



### Analysis

Let \(a\) denote success under a two-stage VT protocol, \(b\) under the suppressed baseline and \(c\) under unrestricted ordinary CoT. Then \[a-b=(a-c)+(c-b).\] The reported positive difference does not identify \(a-c\). Probabilities \((a,b,c)=(0.70,0.40,0.80)\) demonstrate the inference failure without pretending to be measured data.

The authors’ auxiliary direct/suppressed comparison reports \((13,12),(42,32),(84,31)\), with differences \(1,10,53\) percentage points. This is counterevidence to treating suppression as innocuous. These auxiliary numbers cannot be subtracted from Table 1 without matched protocols/items. Extra calls and tools are legitimate system components, but the comparison does not isolate their individual effects.



### Finding and scope

The comparison is valid for its documented restricted protocol; the broad ordinary-CoT improvement interpretation and main-text baseline description need qualification. No benchmark number is recomputed.



### Proposed correction

Retain the supplied relabeling: report the suppression instruction in the main protocol and describe the measured effect under that restriction. An unrestricted matched comparison would be additional evidence, not a numerical correction obtainable from the existing table.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Problem 2: Local attention and intervention evidence does not measure all information routes

Assessment: not_issue; impact: no_issue_found



Source: Proceedings Section 5.2, PDF p.9; Figure 10; Appendix D, p.28



### Source claim (paraphrase)

The paper interprets attention, saliency and blocking examples as showing that nearly all image-derived signals pass through visual thoughts.



### Analysis

The statistic is local sensitivity, not a normalized conserved information quantity. For example, \(z(a)=1/2-4(a-1/2)^2\) and cross-entropy \(L(a)=\log(1+e^{-z(a)})\) have \(aL^{\prime}(a)=0\) at \(a=1/2\), although removing the coefficient to \(0\) changes the correct-class logit from \(1/2\) to \(-1/2\). This limits what zero first-order saliency proves. The paper’s actual blocking experiment remains meaningful local causal evidence; the example is not its model output.



### Finding and scope

Retain evidence for the analyzed inputs and interventions. No exhaustive fraction of information flow or global failure of mediation is established by this focused check.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- Exact calculations and static-source findings do not remeasure published experiments or establish the historical experiment-generating revision.
