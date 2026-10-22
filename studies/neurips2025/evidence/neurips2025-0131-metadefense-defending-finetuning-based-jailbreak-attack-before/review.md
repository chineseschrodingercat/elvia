# MetaDefense: Defending Finetuning-based Jailbreak Attack Before and During Generation



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The release gives comparison branches different generation limits, substitutes generated diagnostic text for the stated probability rule, and returns flagged partial text. Universal lower-ASR wording also exceeds the reported tables.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: A common requested generation budget becomes \(140\) tokens only on the non-verification branch

Assessment: supported; impact: minor



Source: Tables 2–5; Appendix C experimental settings; released defense_query and nondefense_query max_new_token interfaces.



### Source claim (paraphrase)

The released evaluation caller requests \(512\) new tokens through defense_query. It routes verification-enabled requests to meta_defense and other requests to nondefense_query, which replaces the requested budget with \(140\); the verification branch does not make the same replacement. This concerns the protocol behind Tables 2–5 and Appendix C.



### Analysis

The same caller budget therefore produces branch limits \(512\) and \(140\). EOS can stop either branch earlier, but it does not make these different permitted budgets equal. This is an interface/protocol discrepancy, not a new attack-success measurement.



### Finding and scope

A hard-coded branch budget changes the evaluation contract; no actual ASR or latency effect is measured.



### Proposed correction

Forward the caller response budget unchanged and cap each chunk by its remaining budget; report diagnostic-token accounting separately.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: The released decision rule and check interval differ from Algorithm 1

Assessment: supported; impact: minor



Source: Algorithm 1, lines 4, 9, 13 and 16, PDF p. 6.



### Source claim (paraphrase)

Algorithm 1, PDF p. 6, lines 4 and \(13\), rejects when the next-token diagnostic probabilities satisfy \(p_h>p_b\), for harmful and harmless labels. Lines 9 and \(16\) set the next interval to \(k=\gamma p_b\). Released meta_defense instead checks generated diagnostic text for the harmful substring and applies a different clamped interval update.



### Analysis

A valid first-token distribution can have \(p_h=0.3\), \(p_b=0.2\), and another token with probability \(0.5\). The printed comparator rejects. Unrestricted greedy generation instead selects the third token, whose continuation need not contain the harmful substring, allowing the text rule to accept. A two-label-constrained diagnostic is a matching special case, but the release does not impose that restriction.

For \(\gamma=32\) and harmless probability \(0.2\), the printed interval is \(6.4\), while the current half-scale clamp schedules \(16\). This is not an integer-rounding difference.



### Finding and scope

Valid diagnostic probabilities and low-confidence scheduling differ from Algorithm 1; real-model disagreement frequency remains unknown.



### Proposed correction

Use the already-computed two-label probabilities with a stated tie policy, or explicitly specify and evaluate the generated-text decision. State a coherent rounded and capped interval policy.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 3: Early termination does not establish the stronger claim that flagged content is blocked before exposure

Assessment: supported; impact: minor



Source: Abstract, PDF p. 1; Algorithm 1, line 14, PDF p. 6; Appendix D.12–D.13, PDF p. 22.



### Source claim (paraphrase)

Original claims and locations (paraphrase). The abstract on p.1 describes stopping generation to prevent further harmful content. That is a limited stopping objective. Appendix D.12–D.13, p.22, uses stronger language: the mechanism can block staged harm before emission and prevent unsafe content exposure. Algorithm 1, p.6, line 14, instead returns the accumulated partial response plus a safety reminder after detecting that partial response as harmful.



### Analysis

Algorithm 1 returns the accumulated flagged response with a reminder; the current mid-generation rejection branch returns that decoded response and a rejection flag, without adding the reminder. The evaluator stores the response as output. Thus a successfully detected neutral marker would still be returned, independent of its content. Stopping later chunks does not withhold the flagged prefix; the abstract's narrower continuation-prevention claim survives.



### Finding and scope

Supported limit on the stronger exposure-prevention statement, without claiming every early-stop defense is ineffective.



### Proposed correction

Either state the retained-prefix early-stop scope, or buffer unapproved content and withhold it when flagged. A reminder cannot retract already exposed text, and classifier false negatives remain outside a conditional withholding contract.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 4: The claim of lower ASR across every architecture and baseline contradicts Tables 2–4

Assessment: supported; impact: minor



Source: LLMClassifier baseline, PDF p. 7; Section 5.1, PDF p. 8; Tables 2–4.



### Source claim (paraphrase)

Claim/location (paraphrase). The summary at the end of Section 5.1, p.8, states that MetaDefense consistently has lower ASR across all architectures/templates than alignment, finetuning, inference, and hybrid baselines. LLM-Classifier is expressly identified as an inference-stage baseline on p.7 and included in Tables 2–4.



### Analysis

Tables 2–4 report higher MetaDefense ASR than LLM-Classifier in \(8\) of \(12\) architecture/template averages, including every LLaMA-2 comparison. For example direct LLaMA-2 ASR is \(1.0\%\) versus \(0.1\%\); Qwen refusal-suppression ASR is \(11.1\%\) versus \(0.4\%\). These displayed means contradict universal lower-ASR wording. They do not establish significance or negate the single-model memory advantage.



### Finding and scope

The universal lower-ASR wording is not supported by every displayed comparator. The individual table entries and other advantages are not rejected.



### Proposed correction

State the mixed LLM-Classifier comparison and the separate memory/utility tradeoff; retain the displayed numerical tables.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
