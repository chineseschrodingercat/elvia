# A Novel General Framework for Sharp Lower Bounds in Succinct Stochastic Bandits



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The explicit all-horizon lower bound omits scale conditions and can exceed the universal normalized-regret ceiling. A separate finite-seminorm definition needs a spanning/domain restriction. Both concerns were already recorded in the third-party BanditRLlib audit; no priority claim is made.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: The finite-horizon lower bound can exceed normalized regret

Assessment: supported; impact: major



Source: Theorem 3.8, Eq.(3), PDF pp.5–6; proof Step 2/Step 5, pp.6–7



### Source claim (paraphrase)

The theorem gives \[c(C_0)\min\{s^{2/3}n^{2/3}q^{1/3},s\sqrt{pn}\}\], \(c(C_0)=\min\{C_0,e^{-4}/8\}/3\), without a horizon restriction.



### Analysis

Set \(n=1,s=100,k=1,C_0=1,p=1000,q=10^{12},d=99001\). Use atoms \(\{\pm e_j\}\), so \(Q=\|\cdot\|_\infty,R=\|\cdot\|_1\), baseline \(\theta_0=-e_1\), and \(99\) disjoint groups of \(1000\) remaining basis vectors. Let \(H\) contain all vectors with first coordinate \(1\) and remaining coordinates \(\pm10^{-6}\). Then \(Q(H)=1\), baseline reward \(-1\), each group’s average squared inner product on \(H\) is \(10^{-12}=1/q\), on its atoms \(1/1000=1/p\), and every group tuple plus baseline is a support. All displayed domain requirements hold, including \(s\ge3k+3\). The bound is \(e^{-4}100\sqrt{1000}/24=2.4132973204\). Yet every normalized expected one-step regret is at most \(2\). Gaussian realized rewards are not bounded; their zero-mean noise leaves this expected-regret ceiling intact.



### Finding and scope

The literal all-horizon theorem is false, independently of policy or chosen normalized hard instance. Its proof itself requires \(s\epsilon\le C_0/3\), with branch conditions \(9s^2p\le C_0^2n\) or \(27s^2q\le C_0^3n\). Fixed-parameter eventual rates are not refuted.



### Proposed correction

State the appropriate horizon regime, or clip the construction scale to \[\epsilon_*=\min\{\sqrt{p/n},(q/(sn))^{1/3},C_0/(3s)\}\]. The same testing/gap split then yields the conservative extra term \[c(C_0)\min\{s\sqrt{pn},s^{2/3}n^{2/3}q^{1/3},C_0n/3\}\]. Clipping the instance first is essential; merely clipping a final unsupported bound at \(2n\) is not a proof.

Both concerns were previously documented by the third-party BanditRLlib audit. No paper-author adoption of the stated repair is established.



## Problem 2: The dual atomic quantity need not be finite on the ambient space

Assessment: supported; impact: minor



Source: Axiom 3.1 and Definition 3.2, PDF p.5



### Source claim (paraphrase)

Nonempty sign-symmetric unit atoms are allowed without spanning, but \(R(X)=\sup_{Q(Y)\le1}\langle X,Y\rangle\) is called a finite seminorm on all \(V\).



### Analysis

In \(\mathbb R^2\), atoms \(\{\pm e_1\}\) satisfy the axiom and give \(Q(Y)=|y_1|\). For \(X=e_2\), every \(Y_t=(0,t)\) is feasible and \(\langle X,Y_t\rangle=t\), so \(R(e_2)=+\infty\). Finitely atom-supported \(X=\sum a_iE_i\) instead satisfy \(R(X)\le\sum|a_i|\), and the concrete finite-dimensional application atom systems span their spaces.



### Finding and scope

The global finite-valued definition needs a domain qualification. Constructed succinct parameters and the intended spanning application norms are not disproved.



### Proposed correction

Require \(\operatorname{span}(U)=V\), restrict the ambient space to the atom span, or explicitly use an extended-real support function and state finite-domain operations. These are distinct scope choices.

Previously documented in the third-party BanditRLlib audit; author correction/adoption remains unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
