# KTAE: A Model-Free Algorithm to Key-Tokens Advantage Estimation in Mathematical Reasoning



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The printed Fisher expression is a single-table mass, and released float32 tie handling plus an exact p=\(1\) gate can create spurious association. Further formula/boundary and efficiency-scope differences do not establish wrong published accuracies.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Equation (4) is a table probability, not the claimed Fisher p-value

Assessment: supported; impact: minor



Source: Section 3.2, Eq. (4), PDF p. 5.



### Source claim (paraphrase)

Section 3.2, p. 5, states, in paraphrase, that Fisher’s test returns the probability of the observed contingency table or a more extreme table under independence. Equation (4) then defines

\[ \operatorname{Fisher}_{\mathrm{printed}}(T) =\frac{(a+b)!(c+d)!(a+c)!(b+d)!}{a!b!c!d!G!}. \]



### Analysis

For a \(2\times2\) table with every cell equal to \(2\), the feasible conditional masses are \((1,16,36,16,1)/70\). The observed mass is \(18/35\), but every feasible table is no more probable, so the probability-ordered two-sided Fisher p-value is \(1\). Equation (4) prints one hypergeometric mass, not the stated tail. The released algorithm does include tail summation, which limits the impact of this printed-formula discrepancy.



### Finding and scope

The displayed statistic is not its stated p-value, but the released algorithm already performs the missing tail summation in principle, limiting the finding to the printed specification.



### Proposed correction

Replace the single mass with the specified probability-ordered tail: sum \(\binom{s}{k}\binom{n-s}{r-k}/\binom nr\) over feasible \(k\) whose numerator weight is no larger than the observed one. The existing code’s tail operation is affirmative counterevidence against assuming it trained on the literal single mass.

The local formula, numerical or scope proposal is retained; current cited passages and author-source paths still contain the relevant behavior. Author adoption is unestablished.



## Problem 2: Float32 ties and the exact-\(p=1\) gate change the released association score

Assessment: supported; impact: minor



Source: Eq. (5), PDF p. 5; released Fisher-tail routine and exact-p-equals-one gate.



### Source claim (paraphrase)

Released compute_key_tokens.py, fisher_exact_test, lines 26–51, computes masses using float32 log-gamma expressions and selects terms by literal probability comparison. Lines 157–159 apply the exact \(p\ne1\) gate corresponding to Eq. (5).



### Analysis

For table \(\begin{pmatrix}0&5\\2&9\end{pmatrix}\), the exact feasible masses are \(11/24,11/24,1/12\), so the two-sided p-value is \(1\). Rounding can separate the equal masses and exclude one tied term. Separately, a rounded value \(1.000000119\) fails the exact equality gate and maps to approximately \(e^{-2p}=0.1353\) instead of zero. These are distinct source-level numerical failure mechanisms; previously reported native outputs are historical.



### Finding and scope

Float32 tie comparisons and the discontinuous endpoint gate can distort token scores; actual training frequencies, CUDA rounding and downstream effects remain unmeasured.



### Proposed correction

Compare exact integer hypergeometric numerator weights to preserve equal-probability ties, then apply an explicitly specified endpoint rule. This local statistic correction does not establish an improvement in training accuracy.

A local correction or qualification is proposed where specified; author adoption is not established.

The local formula, numerical or scope proposal is retained; current cited passages and author-source paths still contain the relevant behavior. Author adoption is unestablished.



## Problem 3: The released token bonus has different weights and scale from Eq. (10)

Assessment: supported; impact: minor



Source: Eq. (10), PDF p. 6.



### Source claim (paraphrase)

Equation (10), p. 6, specifies the additive bonus

\[ \delta_{\mathrm{paper}} =\sigma\big((h_1F+h_2IG)D\big)-\frac12. \]



### Analysis

The released default maps \((F,IG,D)\) to \(2[\operatorname{sigmoid}((F+IG)D/2)-1/2]\), whereas Eq. (10) with the appendix weights uses \(\operatorname{sigmoid}((F+2IG)D)-1/2\). Their ranges are \((-1,1)\) and \((-1/2,1/2)\), respectively, so they cannot be algebraically equivalent. Both give zero at \(D=0\); that matching control does not establish equivalence elsewhere.



### Finding and scope

The current bonus has different relative coefficients and output range; this defeats exact reconstruction of the printed contract without proving reported accuracies false.



### Proposed correction

Identify the actually trained canonical variant, then either document the released coefficients, normalization and range or align the implementation with Eq. (10). No empirical choice between these variants is established.

The local formula, numerical or scope proposal is retained; current cited passages and author-source paths still contain the relevant behavior. Author adoption is unestablished.



## Problem 4: The directional score is undefined for permitted zero-frequency cases unless a boundary rule is added

Assessment: supported; impact: minor



Source: Section 3.4, Eq. (9), PDF p. 6.



### Source claim (paraphrase)

Section 3.4, Eq. (9), PDF p. 6, defines \(D=\arcsin\sqrt{a/(a+c)}-\arcsin\sqrt{b/(b+d)}+h_3(TF_T/TF_F-TF_F/TF_T)\). Algorithm 1 applies it to tokens in the union of sampled rollouts without requiring positive frequency in each outcome group.



### Analysis

Use four correct rollouts containing the token and four incorrect rollouts not containing it. Both outcome groups exist, but \(TF_T>0\) and \(TF_F=0\). The arcsine term is \(\pi/2\), while \(TF_T/TF_F\) is undefined over the reals. A finite regularization or extended-real limiting convention is an additional definition; it does not follow from the printed formula.

The current source adds \(10^{-5}\) in frequency denominators and \(10^{-10}\) in class-proportion denominators, and returns zero when either outcome group is empty. These protections resolve a runtime boundary in the release; the supported concern is the printed contract’s omission of that regularization.



### Finding and scope

The formula is incomplete at allowed zero frequencies, while current code already supplies numerical safeguards; this is a local documentation/domain discrepancy.



### Proposed correction

State the denominator regularization and empty-group branches used by the implementation. Alternative smoothing requires an explicit changed definition; no empirical effect is claimed.

A local correction or qualification is proposed where specified; author adoption is not established.

The local formula, numerical or scope proposal is retained; current cited passages and author-source paths still contain the relevant behavior. Author adoption is unestablished.



## Problem 5: The no-length-penalty and joint efficiency statements require narrower scope

Assessment: supported; impact: minor



Source: Introduction, PDF p. 2; Section 2.3, PDF p. 4; Table 2, PDF p. 8; Appendix G.3, PDF p. 19.



### Source claim (paraphrase)

The introduction, p. 2, and discussion of Table 2, p. 8, describe reduced response length without a length-penalty reward. Section 2.3, p. 4, explicitly describes DAPO overlong reward shaping. Appendix G.3, p. 19, sets an overlong buffer of \(512\) and a length-penalty coefficient of 1.0.



### Analysis

The current \(7\)-billion-parameter DAPO launch enables a \(512\)-token overlong buffer, maximum length \(3072\), and penalty coefficient \(1\). The reward code adds \(\min(-(L-2560)/512,0)\), so lengths \(2816\) and \(3072\) receive penalties \(-1/2\) and \(-1\). KTAE can add no new penalty while inheriting DAPO’s existing penalty; that narrower interpretation remains coherent.

The current tables give \(7\)-billion-parameter GRPO+KTAE mean accuracy \(51.7\) and length \(718.6\), versus DAPO+KTAE accuracy \(52.5\) and length \(777.2\), so the two extrema belong to different variants. Both beat their base algorithms in mean length; the \(1.5\)-billion-parameter DAPO+KTAE variant has both displayed extrema. Individual MATH500 lengths nevertheless increase from \(635\) to \(884\) and \(617\) to \(983\). These are qualifications of combined-system, average and variant scope, not corrected benchmark measurements.



### Finding and scope

Supported configuration and inference-scope qualification; no new efficiency measurements were obtained.



### Proposed correction

State that KTAE adds no separate length penalty, disclose inherited DAPO reward shaping, and identify which model variant attains each accuracy/length extremum. Distinguish mean response length from every-benchmark length and from latency.

The local formula, numerical or scope proposal is retained; current cited passages and author-source paths still contain the relevant behavior. Author adoption is unestablished.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
