# HETEROGENEOUS SWARMS: Jointly Optimizing Model Roles and Weights for Multi-LLM Systems



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The latest author port corrects the earlier final-answer evaluator and unstable softmax. Two bounded concerns remain: graph decoding mutates an adjacency row and restricts the graph family, while the current paper’s finite-sampling contribution score is undefined when a model is never sampled. Neither establishes damage to the reported aggregate benchmark results.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Decoder topology and input mutation differ from the intended reusable DAG representation

Assessment: supported; impact: minor



Source: Section 3 graph representation; current MoCo model_collaboration/method/text_heterogeneous_swarms.py, graph_decode



### Source claim (paraphrase)

The paper presents general DAG collaboration; the release attaches each newly selected node to one existing node and reuses adjacency rows.



### Analysis

A successful \(n\)-node decode adds \(n-1\) edges with one successor per nonterminal node. It cannot represent every DAG, for example \(0\to1,0\to2,1\to2\). The current author port still assigns adjacency_matrix[selected_node] to a working row without copying it. NumPy row indexing returns a view, so zeroing entries for the unselected nodes changes the caller’s matrix. This is a restricted graph family and a side effect; the output remains acyclic, and corruption of every optimizer state is not established.



### Finding and scope

The same two local properties remain in the latest author-directed MoCo port. Their effect on saved optimization trajectories or published scores has not been established.



### Proposed correction

Copy the row before mutation. That repairs the side effect but does not enlarge the graph family; intended edge-sampling semantics remain to be specified.

The author’s original repository directs readers to MoCo. The current MoCo dev branch retains the row view and single-successor construction; no correction of those properties was found in the inspected function.



## Problem 2: The latest evaluator corrects the historical numeric substring mismatch

Assessment: not_issue; impact: no_issue_found



Source: Current MoCo model_collaboration/data/eval.py, extract_answer_text, calculate_exact_match and get_scores



### Source claim (paraphrase)

The original evaluator treated inclusion of the reference string as an exact match and had a separate judge branch with different score units. The latest author port extracts the final answer and uses type-appropriate equality or numeric comparison.



### Analysis

For the GSM8K example, the correct answer is \(14(6+2)=112\), whereas the wrong answer \(1120\) contains its decimal substring. That distinguishes the old substring rule from exact final-answer comparison. In the current calculate_exact_match, normalized numeric strings are parsed and checked by _numbers_match; these two numbers fail its relative tolerance of \(10^{-2}\). Text falls back to normalized equality after final-answer extraction. The earlier integer-judge branch is not used by the current swarm method’s get_scores path.



### Finding and scope

The precise historical false-positive witness is corrected in the latest author implementation and is not counted as a current problem. This does not establish that historical predictions or tables were recomputed.



## Problem 3: Finite random assignments can leave JFK-score undefined

Assessment: supported; impact: minor



Source: Current paper Algorithm 2, PDF p. 5; current MoCo text_heterogeneous_swarms.py, run_method



### Source claim (paraphrase)

Algorithm 2 divides a model’s summed sampled utility by the number of appearances in a finite set of IID assignments, without requiring positive coverage of every model.



### Analysis

With \(10\) models, \(10\) assignments and \(10\) positions per assignment, there are \(100\) IID model draws. A specified model is absent with probability \(0.9^{100}>0\). For example, appearance counts \[(12,16,15,0,7,9,9,9,8,15)\] sum to \(100\) but give the absent model utility and frequency both zero. Its prescribed ratio is therefore \(0/0\), even for constant positive assignment utility. The latest MoCo port instead fixes model_names and optimizes adjacency; it omits this frequency-based role-selection stage. That removal prevents attributing the same division to the current port, but does not define the score in the still-current published Algorithm 2.



### Finding and scope

The current paper’s finite-sampling definition lacks a zero-frequency convention. This is a domain defect with a positive-probability event, not evidence that a reported run encountered it or that the current MoCo port performs the same division.



### Proposed correction

Define behavior for zero-frequency models. Conditioning samples on complete coverage makes denominators positive but changes the sampling law; no unbiasedness equivalence is asserted.

The current paper retains the unguarded finite-sampling score. The later MoCo port omits that role-selection stage rather than providing a corrected implementation of its stated ratio.



## Problem 4: The latest stable softmax corrects the historical overflow witness

Assessment: not_issue; impact: no_issue_found



Source: Current MoCo text_heterogeneous_swarms.py, softmax and graph_decode



### Source claim (paraphrase)

The original decoder exponentiated reciprocal row sums directly. The latest author port subtracts their finite maximum and separately handles masked or nonfinite entries.



### Analysis

Positive row weights can yield reciprocal row sums \((5000,1,1)\). Direct float64 exponentiation of \(e^{5000}\) overflows despite a well-defined real softmax. The current implementation calculates exponentials after subtracting the maximum finite value, so this witness becomes \((e^0,e^{-4999},e^{-4999})\) before normalization. Its code also handles positive infinity and masks explicitly. This is the previously identified issue and later author correction, not a novelty claim.



### Finding and scope

The exact historical overflow defect is corrected in the latest author port. No general claim is made about every possible nonfinite input or downstream numerical operation.



## Problem 5: Table 7 supports a mean advantage but not every-task superiority

Assessment: not_issue; impact: no_issue_found



Source: Appendix D, Table 7, PDF p. 28.



### Source claim (paraphrase)

The text says the mixed \(7\)-billion/\(2\)-billion-parameter system exceeds the best single \(7\)-billion-parameter model, without explicitly claiming superiority on every task.



### Analysis

The four mixed-minus-single scores are \[(-0.028,0.134,-0.043,0.029)\], with arithmetic means \(0.31875\) and \(0.29575\). Thus the aggregate advantage is consistent with the table, while two task reversals remain. The rounded aggregate arithmetic in Table 1 is also consistent.



### Finding and scope

This is a scope clarification, not an additional demonstrated error. Table 1’s rounded \(18.5\%\) aggregate remains a positive arithmetic control.



## Limits

- No author programs, optimizers or model evaluations were executed. Historical benchmark predictions and run commits were unavailable. The current MoCo port changes the role-selection procedure, so absence of its frequency division is not a validation of the published Algorithm 2.
