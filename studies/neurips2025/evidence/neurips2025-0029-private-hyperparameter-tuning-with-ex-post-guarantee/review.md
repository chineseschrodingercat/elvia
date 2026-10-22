# Private Hyperparameter Tuning with Ex-Post Guarantee



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current Lemma 16 proof retains a false intermediate exponential upper bound, contradicted by exact admissible rational parameters. The lemma’s final bound survives the witness and has an existing general alternative proof with unchanged constants. This remains a Minor proof-step defect; no current privacy guarantee or experiment is shown false.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: Lemma16 uses a false intermediate exponential bound

Assessment: supported; impact: minor



Source: Official Lemma 16, Appendix B, p.23; arXiv v1 Lemma 15, pp.11–12.



### Source claim (paraphrase)

For \(\varepsilon>0,\alpha>1,a,b\in(0,1)\) with \(a^{1-\alpha}b^\alpha\le e^{\varepsilon(\alpha-1)}\), Lemma 16 bounds \[(1-a)^\alpha(1-e^{-\varepsilon(1+\ell)}b)^{1-\alpha}\le\exp(e^{-\varepsilon(1+\alpha\ell)}).\] Its proof first claims the stronger intermediate upper bound \(\exp((\alpha-1)e^{-\varepsilon(1+\ell)}b-\alpha a)\).



### Analysis

Take \(\alpha=2\), \(\varepsilon=\log2\), \(\ell=1\), \(a=1/200\) and \(b=1/10\); the coupling hypothesis holds at equality. The displayed product is \(39601/39000\), exceeding the claimed intermediate bound \(e^{3/200}\). Indeed \(e^{3/200}<200/197<39601/39000\), with the last comparison reducing to positive integer difference \(1397\). The lemma's final bound \(e^{1/8}\) remains valid; only the intermediate step is refuted.



### Finding and scope

The first inequality of the current proof is false under the lemma’s own hypotheses. The counterexample does not falsify the lemma’s final statement or establish a larger privacy budget. Replacing that proof step suffices at the level established by the existing conditional derivation.



### Proposed correction

Keep the lemma’s domain and constants. Set \(p=\alpha/(\alpha-1)\), \(\lambda=e^{-\varepsilon(1+\alpha\ell)}\), and \(z=be^{\varepsilon\ell(\alpha-1)}\); the hypothesis gives \(a\ge\lambda z^p\). If \(z\ge1\), the original product is at most \(1\). If \(0<z<1\), its logarithm is at most \(L(\lambda)\), where \(L(s)=\alpha\log(1-sz^p)-(\alpha-1)\log(1-sz)\). To show \(L'(s)\le1\), multiply by the positive denominator: its numerator is \[H(s)=1-(\alpha-1+s)z+(\alpha-s)z^p+(s^2-s)z^{p+1}.\] On \([0,\lambda]\), \(H'(s)\le0\), so \(H(s)\ge H(1)=1-\alpha z+(\alpha-1)z^p\ge0\) by convexity. Integrating from \(L(0)=0\) gives \(L(\lambda)\le\lambda\), the original bound. This restores the lemma with unchanged constants; it is not an author-adopted erratum or an independent audit of every privacy proof.

The current proceedings Lemma 16 and latest target arXiv v1 Lemma 15 retain the false intermediate step. The supplied general alternative proof is preserved as an analytic proposed correction. The separately titled later accuracy-first RDP paper is background work, not a newer version of this paper.



## Limits

- No author mechanism, training code or old verifier was executed. The exact witness concerns one intermediate proof inequality, not the final lemma or a demonstrated privacy violation. The alternative proof preserves its constants, but this pass does not certify every other privacy claim or external implementation.
