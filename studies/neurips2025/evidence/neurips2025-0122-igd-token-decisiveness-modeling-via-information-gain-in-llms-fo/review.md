# IGD: Token Decisiveness Modeling via Information Gain in LLMs for Personalized Recommendation



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The prefix score is unnormalized prior entropy mass rather than conditional Shannon entropy. A separate title-frequency converter loses counts when distinct item IDs share a title.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The prefix quantity is residual prior entropy mass, not conditional Shannon entropy

Assessment: supported; impact: minor



Source: Section 3.1, Eqs. (4)–(5), PDF p. 4; released code/trie.py, lines 39–61 and compute_information_gain from line 126.



### Source claim (paraphrase)

Section 3.1, Eqs. (4)–(5), PDF p. 4, interprets a prefix score as Shannon uncertainty and its parent-minus-child difference as information gain. The displayed \(R_s\) sums fixed prior terms \(-p_i\log p_i\) over compatible items without conditional renormalization. Released code/trie.py, lines 39–61 and compute_information_gain from line 126, implements that same prior-mass sum.



### Analysis

For prior \((0.8,0.1,0.1)\), a prefix retaining the last two items gives posterior \((0.5,0.5)\). Its entropy is \(\log2\approx0.6931\), greater than the original \(0.6390\), but removing the first item's contribution produces a positive declared gain. If the retained mass is \(M\) and its normalized entropy is \(H\), the implemented residual is \(MH-M\log M\), not \(H\). The score remains a definable heuristic, with a different information-theoretic interpretation.



### Finding and scope

The normalized-entropy interpretation fails, but the implemented pruning score has a coherent unchanged interpretation and no recommendation-accuracy refutation follows.



### Proposed correction

Describe the unchanged quantity as residual prior entropy mass, or separately define and evaluate a conditionally normalized entropy score. These alternatives are different scoring rules.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: Converting item-ID frequencies to title frequencies overwrites collisions

Assessment: supported; impact: minor



Source: Released code/compute_item_freq.py, load_item_titles, lines 9–29, and count_item_frequencies, lines 32–56.



### Source claim (paraphrase)

This is a released-code correctness finding, not an assertion that the paper contains a theorem about duplicate titles. In code/compute_item_freq.py, load_item_titles, lines 9–29, accepts a tab-separated title followed by an integer item ID. count_item_frequencies, lines 32–56, counts interaction rows by item ID and converts that counter to a dictionary keyed by title.



### Analysis

Two item IDs have frequencies \(5\) and \(7\) but share a title; a third title has frequency \(11\). Repeated title-key assignment overwrites the first frequency, producing total \(18\) instead of \(23\). Summing colliding frequencies restores title-level mass; keeping distinct item identities requires retaining an identifier.



### Finding and scope

Conditional preprocessing defect; its exposure in the actual benchmarks was not established.



### Proposed correction

For title-level aggregation, add frequencies on title collisions rather than overwriting them. If item identity matters, preserve the separate item ID as well.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
