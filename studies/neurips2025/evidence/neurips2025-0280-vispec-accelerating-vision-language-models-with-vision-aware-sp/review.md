# ViSpec: Accelerating Vision-Language Models with Vision-Aware Speculative Decoding



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Verified blocks can violate EOS/cap stopping, and the baseline logs a zero counter. The public speed script bypasses that field but uses differing token conventions; published speedup consequences remain unresolved.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Whole-block commitment can violate target stopping semantics

Assessment: supported; impact: minor



Source: Sections 3.1 and 5.1; vispec/model/spec_model_ours.py, specgenerate; vispec/model/utils.py, update_inference_inputs



### Source claim (paraphrase)

The method relies on distribution-preserving speculative decoding, but the release appends a complete verified block before checking EOS and generation budget.



### Analysis

Choose unique greedy target outputs \(a\), then EOS \(e\), then \(b\) after that EOS prefix, and a matching draft path \((a,e,b)\). All positions satisfy argmax verification, but whole-block commitment returns \((a,e,b)\); ordinary stopped generation returns \((a,e)\). The GQA caller removes EOS strings without truncating the ordinary suffix. Independently, a budget \(M=2\) permits lengths \(2\) then \(3\) because the check is strictly greater after appending; a long block can overshoot even with a non-strict comparison. A separate Vicuna caller does truncate final text, limiting a repository-wide claim.



### Finding and scope

The released general routine does not guarantee the same stopped sequence under admissible EOS/cap boundaries. This does not measure the frequency or quality impact in pretrained benchmark outputs.



### Proposed correction

Before commitment, truncate the verified block to the remaining budget and earliest stopping token. Advance counters and caches by the committed prefix length and stop immediately when exhausted. The prefix invariant proves stopping correctness conditional on valid target verification.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: The baseline counter stays zero and speed accounting uses different units

Assessment: supported; impact: minor



Source: Section 5.1 and Table 1; gen_baseline_answer_gqa.py baseline generation; speed.py



### Source claim (paraphrase)

The baseline returns a generated-token field used for logging, while timing analysis is intended to compare cost per generated token.



### Analysis

The baseline initializes new_token to \(0\) and never updates it, despite appending tokens; the counter-based limit therefore stays inactive. A valid generated suffix \((7,8,2)\), with EOS \(2\), has length \(3\) but the returned count remains \(0\). Evaluation callers also omit a common explicit cap, leaving baseline/speculative defaults \(2048\) and \(512\). Contrary evidence matters: speed.py retokenizes cleaned baseline text instead of using the zero field, so zero recorded counts do not imply its denominator is zero. That script uses a fixed LLaVA tokenizer even for Qwen, while speculative counts use target token IDs; equality of those units is not guaranteed.



### Finding and scope

The release’s baseline field and budget plumbing are defective. Existing timing compensation prevents a direct zero-denominator allegation, and the effect on published speedups is unquantified.



### Proposed correction

Set count from sequence length minus prompt length, pass the same explicit cap and stopping convention, and use comparable validated token units for both sides. Reanalysis requires the actual saved responses and timing records.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
