# Robust Egocentric Referring Video Object Segmentation via Dual-Modal Causal Intervention



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The attention-MMSE derivation and memory-bank marginal-mean limit fail on explicit admissible distributions. The standard front-door identification formula and empirical segmentation utility are not refuted.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Dot-product softmax is not the quadratic MMSE optimizer

Assessment: supported; impact: major



Source: Section 4.2, p. 5, Eqs. (7)–(8); Appendix E.1, pp. 23–25; E.3.5, p. 27.



### Source claim (paraphrase)

Equations (7)–(8) and Appendix E identify scaled dot-product attention with a simplex-constrained quadratic MMSE solution.



### Analysis

In dimension \(3\), use mean-zero tokens \(v_1=\sqrt{3/2}(1,-1,0)\) and \(v_2=(1,1,-2)/\sqrt2\). Each has squared norm \(3\), so they meet unit-coordinate-variance LayerNorm normalization and have Gram matrix \(G=3I\); they are not unit Euclidean vectors. Set deterministic mediator \(\mu=3v_1/4+v_2/4\). The true simplex MMSE weights \((3/4,1/4)\) give zero risk. Scaled scores have gap \(\sqrt3/2\), so softmax gives approximately \((0.703918,0.296082)\), with risk \(0.0127413\). The quadratic KKT equations contain \(G\alpha\); replacing them by exponentiated linear scores drops this dependence. Sending linear-score temperature to zero selects a vertex of risk \(3/8\), rather than the interior optimum.



### Finding and scope

The claimed MMSE identity and zero-temperature derivation fail, even in the simple orthogonal case.



### Proposed correction

Solve \(\min_{\alpha\in\Delta}\alpha^\top G\alpha-2b^\top\alpha\). An entropy-regularized version gives an implicit softmax equation retaining \(G\alpha\), not the asserted general explicit linear-score softmax.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Problem 2: Fixed similarity weights converge to a tilted mean

Assessment: supported; impact: major



Source: Section 4.2, p. 6, Eq. (9); Appendix E.3, pp. 26–27, Eq. (E.25).



### Source claim (paraphrase)

Equation (9) and Appendix E.3 claim that an expanding softmax-weighted bank converges to the marginal mean under bounded similarity and moment assumptions.



### Analysis

Let independent \(X\) take values \(\pm1\) equally, query \(q\in\{-1,1\}\), and similarity \(qX\). The ratio law of large numbers gives limit \(\mathbb E[Xe^{qX}]/\mathbb E[e^{qX}]=q\tanh1\), not marginal mean zero. In a balanced bank of \(100\) tokens, the weight distance from uniform is \(\tanh1\approx0.76159\), exceeding the asserted bound \(2(e^2-1)/100\approx0.12778\). Independence is stronger than the stated stationarity.



### Finding and scope

The proposed marginal-mean consistency fails under its assumptions. This does not refute front-door identification as a separate causal formula.



### Proposed correction

Uniform weights with suitable independent or stationary-ergodic assumptions estimate the marginal mean. Retaining fixed similarity instead requires identifying and analyzing the tilted target; a vanishing-temperature parameter needs its own limit argument.

An explicit local correction is described; author adoption and a corresponding published erratum are not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- An analytic counterexample or a release discrepancy does not by itself remeasure the paper’s reported experiments.
