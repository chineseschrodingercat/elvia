# Context-Aware Regularization with Markovian Integration for Attention-Based Nucleotide Analysis



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current public transition-loss path can create undefined or negative empirical targets and subnormalized predicted rows. Its fixed local-attention architecture also limits a single output’s remote-token dependence, while allowing long-array processing and pooled local statistics.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: Empirical transition targets can be undefined or overflow

Assessment: supported; impact: minor



Source: carmania/tokenization_carmania.py, encode_with_bigram; training dataset row normalization; Section 4.1, p.6



### Source claim (paraphrase)

The tokenizer counts bigrams in signed \(16\)-bit integers; the dataset then divides each row by its sum without an unobserved-row policy.



### Analysis

For valid sequence \(A^{114}\), the only nonzero count is \(C_{AA}=113\); the other three rows each divide zero by zero, producing \(12\) undefined entries. Independently, sequence \(A^{40000}TCGA\), with maximum length \(40004\), observes every conditioning base but has \(39999\) repeated \(AA\) transitions. The counter wraps to \(-25537\); its row sum becomes \(-25536\), giving probabilities \(25537/25536>1\) and \(-1/25536<0\). Later addition of \(10^{-6}\) cannot repair either NaNs or the negative logarithm argument. This long-input example does not occur under the default short training-length setting.



### Finding and scope

The released conditional targets are not valid probability rows on these accepted inputs. Neither example estimates their prevalence in historical genomic data.



### Proposed correction

Use sufficiently wide counts and declare either an unobserved-row mask or positive pseudocount \(\alpha\): \(P_{ij}=(C_{ij}+\alpha)/(C_i+4\alpha)\). Positivity and unit row mass follow directly; the pseudocount is a statistical convention that changes the estimator.

A proposed correction is described; author adoption is not established.



## Problem 2: Clamping the predicted row denominator does not normalize it

Assessment: supported; impact: minor



Source: carmania/loss.py, TMLoss.forward, lines 15–26; Appendix B conditional-row description



### Source claim (paraphrase)

The loss forms predicted bigram scores \(S_{ij}\), removes padding, then divides row \(i\) by \(\max(\sum_jS_{ij},1)\). A row sum below one remains deficient.



### Analysis

On valid sequence \(ATCGAT\), the aligned input has \(5\) predicted positions and \(5\) token categories. All-zero finite logits give probability \(1/5\) per category, hence \(S_{ij}=4/25\) and each retained row sum \(16/25=0.64\). Clamping leaves every entry \(0.16\); conditional normalization instead gives \(1/4\). With concentrated empirical successor rows, the unsmoothed loss becomes \(4\log(25/4)\) rather than \(4\log4\). The extra penalty is row-mass deficit, not merely conditional-pattern mismatch.



### Finding and scope

The released quantity is not generally the stated sum of conditional KL divergences. When every score row sums to at least one, the clamp is inactive; no universal per-example failure is alleged.



### Proposed correction

For finite nonnegative scores, normalize \(Q_{ij}=(S_{ij}+\varepsilon)/(\sum_kS_{ik}+4\varepsilon)\), \(\varepsilon>0\). Together with an explicit valid-target convention this gives positive normalized rows and a finite conditional divergence.

A proposed correction is described; author adoption is not established.



## Problem 3: Long arrays do not imply arbitrary long-range single-output memory

Assessment: supported; impact: minor



Source: Figure 4 and Section 4 long-context discussion; carmania/configuration_carmania.py; carmania/model.py, causal local-attention dispatch



### Source claim (paraphrase)

The reported long-context interpretation must distinguish processing an array of \(160\) kbp from one output depending on a remote token. The inspected network has \(5\) local layers with previous-position window \(128\).



### Analysis

For fixed weights, each position in layer \(\ell\) depends only on indices \([\max(0,t-128\ell),t]\), by induction over the union of its local predecessors. Position \(1000\) therefore depends only on input positions \(360\) through \(1000\), at most \(641\) tokens. Two sequences agreeing on that suffix but differing only at position zero have identical logits there under the declared hard local mask. Whole-sequence transition training changes weights, not inference-time edges. Pooling all positions, local motif gains and autoregressive relaying through changed intermediate tokens remain possible.



### Finding and scope

A claim of arbitrary fixed-suffix dependency across the entire input is not supplied by this architecture. The exact Figure 4 rollout/conditioning protocol is unavailable, so its plotted values and long-array task gains are not declared false.



### Proposed correction

Describe local contextual representations plus whole-sequence statistical regularization. Any stronger remote-token memory claim requires an identified mechanism and a fixed-suffix intervention whose correct answer changes with the remote prefix.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
