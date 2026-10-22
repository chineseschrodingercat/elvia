# Efficient Prompt Compression with Evaluator Heads for Long-Context Transformer Inference



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Table 6 averages disagree with displayed dataset scores, an even pooling width can duplicate a suffix token, and released NMI timing double-counts prefill. These do not constitute a new full benchmark/timing run.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Table 6 cannot be reconciled with its displayed dataset scores

Assessment: supported; impact: minor



Source: Section 5.2, Table 6, PDF p. 9.



### Source claim (paraphrase)

Table 6 compares NMI methods at \(1024\)- and \(2048\)-token KV-cache budgets for Llama-\(3.1\)-8B-Instruct and Phi-\(3.5\)-Mini-3.8B-Instruct. It lists \(16\) dataset scores and an Average for each of \(18\) rows. The following results paragraph describes EHPC as achieving the best average across compression rates Section 5.2, p. 9.

This finding concerns the aggregate comparison actually used to support that interpretation. It is not a claim that an individual score is fabricated or that every qualitative advantage disappears.



### Analysis

The displayed Llama SnapKV scores at budget \(2048\) sum to \(603.37\), giving the equal-dataset mean \(37.710625\), while Table 6 reports \(35.80\). The EHPC scores at the same budget sum to \(606.72\), giving \(37.92\) rather than \(37.86\). These differences exceed display rounding. An unreported weighting rule is not assumed; individual dataset values are not replaced.



### Finding and scope

This is a supported local finding within the stated source/formulation scope. Its effect on the paper's aggregate experimental results remains unmeasured.



### Proposed correction

Make the Average entries consistent with the stated aggregation of the displayed dataset cells, or state the different weighting or aggregation rule explicitly.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: Even-width pooling can duplicate a token instead of deleting only

Assessment: supported; impact: minor



Source: Sections 3.1–3.2, Eq. (1), PDF p. 4; Appendix D, PDF p. 23 (pooling defaults).



### Source claim (paraphrase)

Paraphrase. Section 3.1 defines compression by dropping tokens, and Section 3.2 constructs the compressed prompt from retained tokens in their original order p. 4, Equation 1. The output is therefore intended to be a subsequence of original positions. Appendix D sets average pooling with kernel width \(32\), using observation windows \(16\) for Llama and \(4\) for Phi p. 23.

The active implementation is standard_dis_index in my_baseline/GemFilter/gem_filter_utils.py, lines 92–131. It is called by find_context, which passes the returned indices to the model layer. get_layer_context in my_utils/my_generation.py, lines 9–20, sorts and gathers those indices, then appends the last observation window.



### Analysis

Stride-one symmetric pooling of \(M\) prefix scores with width \(r\) produces \(M+2\lfloor r/2\rfloor-r+1\) outputs. For even \(r=32\), this is \(M+1\). The extra index \(M\) already belongs to the original suffix. If selected by top-k and then followed by the appended suffix, it occurs twice, so the result is not a deletion-only subsequence.

An explicit valid indexing fixture has \(N=80\), suffix window \(W=16\), prefix length \(M=64\), target budget \(k=48\) and pool width \(r=32\). Use one-dimensional unit queries, with prefix keys zero except key \(63\) equal to \(20\). Its dominant positive attention score contributes to every pooled position from \(48\) through \(64\). All these \(17\) positions belong to the top \(32\), so the out-of-prefix index \(64\) is selected and then appended again with suffix \(64,\ldots,79\). No author routine was executed in this reassessment.



### Finding and scope

This is a supported local finding within the stated source/formulation scope. Its effect on the paper's aggregate experimental results remains unmeasured.



### Proposed correction

Before top-k selection, restrict the pooled scores to the original prefix length \(M=N-W\). The selected prefix indices then lie in \(\{0,\ldots,M-1\}\), disjoint from the appended suffix \(\{M,\ldots,N-1\}\); sorting gives exactly \(k\) distinct original positions for the valid budget \(W\leq k\leq N\). This repairs the indexing invariant, not benchmark accuracy.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 3: Released NMI timing double-counts prefill and mislabels per-token time

Assessment: supported; impact: minor



Source: Section 5.1, PDF pp. 8–9 (EMI); Appendix F, PDF p. 24 (NMI); released my_utils/my_generation.py, lines 147–185 and 226–247.



### Source claim (paraphrase)

Appendix F reports separate prefill and decode-per-token speed ratios for NMI, while Section 5.1 has a distinct EMI compression-time comparison pp. 8–9, 24. The following defect is in the released NMI implementation, not a direct reconstruction of the published timing table.

eval/LongBench/pred.py calls my_greedy_generate_config for the compressed-prompt path and stores its returned times fields alongside predictions. Other native-model paths call my_greedy_generate_standard_time. The relevant functions are in my_utils/my_generation.py, lines 147–185 and \(226\)–247.



### Analysis

Write selection, compressed-prefill and decode intervals as \(C,P,D\). The released latency sums \(C+2P+D\), although the main elapsed interval is \(C+P+D\). Its per-token field is \((P+D)/G\), including prefill, and its time-to-first-token adds a separate post-response generation probe. Those labels do not partition the declared operation. The published timing-table incidence is unestablished.



### Finding and scope

This is a supported local finding within the stated source/formulation scope. Its effect on the paper's aggregate experimental results remains unmeasured.



### Proposed correction

Use the main elapsed interval for latency and measure the actual first and last generated-token events. With start \(t_0\), first token \(t_F\), last token \(t_L\) and \(G>1\), define TTFT as \(t_F-t_0\) and TPOT as \((t_L-t_F)/(G-1)\), stating synchronization and overhead conventions. The post-first-token mean is undefined for \(G=1\). This does not reconstruct the published speed table.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
