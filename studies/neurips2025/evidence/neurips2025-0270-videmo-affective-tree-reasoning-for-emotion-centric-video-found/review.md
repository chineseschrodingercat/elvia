# VidEmo: Affective-Tree Reasoning for Emotion-Centric Video Foundation Models



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current evaluation release can lose the actual labeled question and aggregate failed judge requests with inconsistent denominators. Original published score effects remain unestablished.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Scorer can replace the labeled question with a system instruction

Assessment: supported; impact: minor



Source: Appendix D.3–D.4; eval/eval_results.py, get_response, lines 190–201



### Source claim (paraphrase)

The evaluator scores against messages[0] instead of selecting the user question by role. Released predictions include a system message before the question.



### Analysis

Consider two items with identical system instruction, reference letter A and model response happy. In one user question A means happy; in the other A means sad. Correct judgments differ, but selecting only the system message makes both judge prompts identical and omits both option lists. No deterministic or stochastic judge can recover the missing distinction from identical inputs. A directly inspected released VidEmo emotion record uses this system-first schema.



### Finding and scope

The supplied scorer and raw records have an information-losing interface mismatch. A private user-first cleaning stage might have been used historically; the published score impact is not established.



### Proposed correction

Select and validate the actual user message, preserve task instructions/options and required dialogue context, and remove only known video placeholders.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Scoring failures change denominators inconsistently

Assessment: supported; impact: minor



Source: Appendix D.3; eval/eval_results.py, eval_single and result_evaluate, lines 215–269



### Source claim (paraphrase)

Exhausted judge requests can be absent from the stored results. Numeric scores average stored responses, while yes/no accuracy divides by all submitted records.



### Analysis

For two submitted items with only one successful score of \(100\), the numeric branch reports \(100\), while one successful yes gives accuracy \(50\). The missing numeric value could be anywhere in \([0,100]\), so the full mean is only identified within \([50,100]\). In general, if N are expected, m are scored and observed sum is A, the full mean lies in \([A/N,(A+100(N-m))/N]\).



### Finding and scope

The current metrics use different failure semantics and may summarize different populations. No actual original judge-failure rate or direction of benchmark bias is established; complete successful scoring avoids this problem.



### Proposed correction

Keep one indexed status for every expected record, validate accepted scores, and report complete means or an explicit failure policy. Conditional means and worst-case missing-score bounds should be labeled separately.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
