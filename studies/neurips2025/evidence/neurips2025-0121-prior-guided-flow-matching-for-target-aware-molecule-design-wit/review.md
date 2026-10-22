# Prior-Guided Flow Matching for Target-Aware Molecule Design with Learnable Atom Number



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The released categorical update uses a mode rather than the declared categorical draw. The affinity argument also mistakes positive Gaussian-noise improvement for proximity to a local minimum.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The released discrete state update selects a mode instead of sampling the declared categorical path

Assessment: supported; impact: minor



Source: Section 4.1, Eqs. (6)–(8) and Algorithm 2 final discrete step; uniform initialization, PDF p. 5.



### Source claim (paraphrase)

Paraphrase of the manuscript: Under the conditional path in Eq. (6), an atom type has categorical probabilities \(q_\alpha\). The vector-field construction in Eq. (7), its update in Eq. (8), and Algorithm 2’s final discrete step provide the sampling procedure for this path. Initialization uses uniformly distributed atom types (Section 4.1, page 5). Algorithm 2, line 13, page 23, explicitly calls for sampling from the updated categorical distribution.

The relevant public implementation is models/molopt_score_model_guide.py, function sample_guided_flow_VP, beginning at line 659. Lines 673–674 initialize the accumulator with the one-hot initial category. Lines 726–729 sample a predicted clean endpoint using torch.multinomial. Lines 732–735 update the accumulator. Lines 737–738 apply a softmax to that accumulator and then call argmax to choose the next atom type. The wrapper scripts/sample_flow_VP_guide.py initializes categories uniformly; the atom-type guidance weight defaults to zero. These locations concern the guided sampler actually being examined, rather than a similarly named function in the unguided model file.



### Analysis

Let the initial category \(a_0\) be uniform on \(\{e_1,e_2\}\), the endpoint be \(e_1\), and \(\alpha=1/4\). The conditional probabilities are \((1-\alpha)a_0+\alpha e_1\). Selecting their mode gives \(e_1\) with marginal probability \(1/2\), while drawing categorically gives \((1+\alpha)/2=5/8\). Earlier endpoint sampling cannot turn the later argmax into the declared categorical draw.



### Finding and scope

The current guided source still uses the mode. The exact conditional-oracle reduction disproves equivalence to the declared intermediate categorical law, without reproducing a full trained trajectory.



### Proposed correction

For the fixed-endpoint construction, draw from \((1-\alpha)a_0+\alpha a_1\); averaging over uniform \(a_0\) gives exactly the declared conditional marginal. A complete learned, guided sampler still needs a derivation ensuring valid probabilities; sampling softmax of an already normalized probability vector is not equivalent.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: Gaussian-noise improvement does not imply proximity to an affinity minimum

Assessment: supported; impact: minor



Source: Appendix A.4, Eqs. (30)–(33), arXiv v2 PDF p. 22.



### Source claim (paraphrase)

Appendix A.4, PDF page 22, Eqs. (30)–(33), compares deterministic affinity \(f(n)\) with \(E[f(n+\delta Z)]\). A second-order expansion yields approximately

\[ E[f(n+\delta Z)]\approx f(n)+\frac{\delta^2}{2}f''(n). \]

The following prose infers that the predicted count lies near a local affinity minimum from the observed benefit of Gaussian noise.



### Analysis

Let \(\Phi\) be the standard normal CDF and \(f(x)=\Phi(x-1)\), a bounded smooth strictly increasing function with no local minimum. For \(n=1/2\) and \(Z\sim N(0,1)\), Gaussian convolution gives \(\mathbb E f(n+\delta Z)=\Phi(-1/(2\sqrt{1+\delta^2}))>\Phi(-1/2)=f(n)\) whenever \(\delta>0\). Noise improvement can therefore arise from curvature without proximity to a minimum.



### Finding and scope

The bounded monotone counterexample removes the minimum interpretation while allowing the reported empirical noise benefit to remain true.



### Proposed correction

Retain a conditional curvature statement: if \(f\in C^4(\mathbb R)\) with \(|f^{(4)}|\le M\), then \(\mathbb E f(n+\delta Z)-f(n)=\delta^2 f^{\prime\prime}(n)/2+r\), with \(|r|\le M\delta^4/8\). This does not imply stationarity or a nearby minimum, nor automatically describe the clipped and rounded integer-count pipeline.

A local correction or qualification is proposed where specified; author adoption is not established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
