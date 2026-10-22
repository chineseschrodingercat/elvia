# Unlocking SLM Potential for Data Analysis Code Generation via Non-Parametric Knowledge Distillation



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The supplied execution preprocessor deletes valid final-output control flow, and the example planning path bypasses generated query-specific instructions. Both are bounded reproduction-component defects; actual affected model outputs and benchmark changes remain unknown.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Textual print deletion corrupts valid final-answer programs

Assessment: supported; impact: minor



Source: code_utils.py, remove_intermediate_prints lines 467–480; exec_python.py call; workflow, PDF pp.4–5



### Source claim (paraphrase)

The helper deletes every line containing the substring print( except the last matching line before execution.



### Analysis

A valid CSV program loads values \(3,5\), then if their sum exceeds \(7\) prints “yes”, else prints “no”. It emits exactly one final answer at runtime. Deleting the first branch’s print leaves an empty if suite, causing a parse error, independently of which branch the data select. Values \(1,2\) give the same structural failure. A second program assigns the six-character string “print(” to label, sets answer to its length, then prints answer; deleting the assignment instead creates an undefined name. One actual final-print control is unaffected.



### Finding and scope

The component can turn correct admissible programs into failures, potentially changing successful-memory inclusion or inference observations. Original generated-program frequency and numerical benchmark effects are unestablished; SQL evaluation is separate.



### Proposed correction

Remove source-line deletion and handle output according to an explicit runtime contract. Replacing removed statements with pass can still erase the correct final output; no general line-deletion substitute is supplied.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: The example planning path ignores per-query meta-instructions

Assessment: supported; impact: minor



Source: Eqs.(4)–(5), PDF p.6; run_phi-3_python.sh; rag_final_python_cot_gpu.py active planning loader



### Source claim (paraphrase)

The active wrapper inserts shared prompt_sug and never reads each record’s generated rag_mg; the example also points planning at the raw rather than enriched input.



### Analysis

Hold question, data, template and shared guidance fixed, and change rag_mg from “sum the numeric column” to “count distinct identifiers”. The active wrapper’s prompt is identical because the changed field is absent from its dependencies. The existing mg wrapper does read the field and yields distinct prompts. Thus query-specific generation cannot affect this shown path, although a global-guidance variant can intentionally use it.



### Finding and scope

Confirmed example/configuration mismatch for reproducing the MI variant. The paper discusses multiple variants and the correct wrapper exists; no claim is made that the authors never implemented MI or that published MI results used this bypass.



### Proposed correction

For the MI variant, pass the enriched instruction output file and select the existing per-query wrapper. Missing prompts/models/configurations still prevent a complete reproduction claim.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
