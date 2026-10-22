# Fairness-Regularized Online Optimization with Switching Costs



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The auxiliary fairness domain can exclude required averages. A two-round example disproves equivalence, and a separate admissible finite construction contradicts the main performance bound. The positive-switching and empirical claims retain their separate scope.



## Scope

Rapid, claim-focused reading of the latest applicable author-paper and resource passages. Direct mathematical or static-source reasoning is stated below. No author program, retained verifier, model inference or benchmark was executed.



## Problem 1: The auxiliary fairness domain need not contain its required averages

Assessment: supported; impact: major



Source: Proceedings Section 5.1.1, Eq.(3), PDF pp.6–7; Algorithm 1, p.7; Theorems 5.1–5.2, p.8; current arXiv v 1 corresponding statements



### Source claim (paraphrase)

The reformulation restricts \(z_t\in\mathcal Z=\{Ax:A\in\mathcal A,x\in\mathcal X\}\) and claims equal optimum to the original horizon-fairness objective, by choosing each \(z_t\) to be the average fairness vector. The assumptions do not make \(\mathcal Z\) convex.



### Analysis

Take \(T=2\), \(\mathcal X=\{1\}\), \(\mathcal A=\{-1,1\}\), \((A_1,A_2)=(-1,1)\), zero hitting/switching costs and \(g(z)=|z|\). Then \(\mathcal Z=\{-1,1\}\), and the original optimum is \(0\). The auxiliary equality requires \(z_1+z_2=0\), but each feasible pair has average fairness cost \(1\). The proposed constant choice \(z_t=0\) is infeasible.

The central performance bound also fails on a convex action domain. Set \(T=10^6\), \(\eta=1/100=T^{-1/3}\), \(R=2,\delta=0\), \(\mathcal X=[1,2]\), alternating \(A_t=1,-1\), losses \(f_{2j-1}(x)=(x-2)^2\), \(f_{2j}(x)=(x-1)^2\), \(g=|\cdot|\), \(\beta_1=\lambda_1=\lambda_2=0\), quadratic mirror reference and \(\kappa_1=0\). Then \(\mathcal Z=[-2,-1]\cup[1,2]\), diameter \(Z=4\), and \(L=l=\beta_2=1\). The constant comparator \(x_t^*=3/2\) has cost \(1/4\) and satisfies the exact frame restriction. Convexity shows no comparator is better.

Let \(a=1-\eta/2\) and \(k=\kappa_{2j-1}\). The printed exact minimizers and unrestricted mirror update give pair maps \[k\mapsto ak+\eta-3\eta^2/2\quad(k<0),\qquad k\mapsto a^2k-\eta-\eta^2/2\quad(k\geq0).\] They preserve \([-\eta-\eta^2/2,\eta]\), starting from zero. The auxiliary minimizer has the sign of \(\kappa_t\); at zero choose \(z_t=1\), an allowed minimizer. Consequently odd actions are at least \(2-\eta/2\) and even actions at most \(1+3\eta/2\). Average fairness cost is at least \(1/2-\eta=0.49\), so total cost is at least \(0.49\). Yet Theorem 5.1 gives \[J\leq1/4+0.16+\sqrt{0.000816}<0.439.\] Theorem 5.2 has the same failed specialization at its allowed zero-switching boundary with \(\lambda_1=1,\lambda_2=0,m=2\).

This witness follows Algorithm 1’s stated minimization over \(\kappa\in\mathbb R^M\). Nearby prose calls the update projected mirror descent; an additionally projected update would be a different algorithm and is not refuted by the displayed recurrence.



### Finding and scope

The auxiliary equivalence and central stated bounds fail on allowed instances. The independent lower-bound results, positive-switching regimes and data-center empirical tables are not refuted by this construction.



### Proposed correction

Replace the auxiliary domain by \(\overline{\operatorname{conv}}(\mathcal Z)\) and require the fairness function to be convex and Lipschitz there. Constant average vectors become feasible, and Jensen proves equivalence. The supplied correction proves the Euclidean zero-switching performance case; it does not establish the full general-reference, positive-switching theorem.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- Mathematical counterexamples and source discrepancies do not remeasure published experiments; historical execution results were not rerun.
