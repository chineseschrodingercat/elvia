# A Pre-training Framework for Relational Data with Information-theoretic Principles



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The sufficient-representation theorem is valid, but it does not prove the fitted past-input encoder satisfies its oracle premise. A performance drop also need not imply information loss. Cosine magnitude ambiguity and masking are retained as scope clarifications.



## Scope

Rapid claim-focused reading of current author-paper passages and relevant released source. Direct mathematical or static-source reasoning is stated below. No author program, inherited verifier, model inference or benchmark was executed.



## Problem 1: An oracle sufficient-representation theorem does not prove the fitted encoder reaches it

Assessment: supported; impact: minor



Source: Latest arXiv v2, Section 4.3, Definition 4.1 and Theorem 4.1, PDF p.6; Appendix A.1; contribution statement p.2



### Source claim (paraphrase)

The formal theorem compares sufficient representations of \((X,T)\) and \(X\), but is used to motivate an algorithmic information-preservation guarantee for an encoder that observes past \(X\) at prediction time.



### Analysis

Under the stated Markov and sufficiency conditions, the chain rule correctly gives \[I(Z_1;Y)-I(Z_2;Y)=I(T;Y\mid X)\geq0.\] This theorem is not refuted. For a fitted encoder \(Z=f_D(X)\) at fixed independent training state \(D\), however, \(I(Z;Y\mid X,D)=0\). Joint sufficiency additionally requires \(I(T;Y\mid X,D)=0\). Learning to predict a future target does not by itself supply that condition.

Let \(X,Y\) be independent fair bits and \(T=Y\). An oracle \(Z_1=T\) has one bit about \(Y\), while \(Z_2=X\) has zero; the theorem holds. Every deployed encoder of only \(X\), with independent fixed fitted state, still has zero information about the current \(Y\). The witness exposes the missing application bridge, rather than violating the theorem’s assumptions.



### Finding and scope

Retain the theorem as an information-availability motivation; the proposed training loss does not establish its sufficiency premise. Better empirical inductive bias or sample efficiency remains possible.



### Proposed correction

For two actual encoders of the same prediction input, define \(\delta_j=I(X;Y\mid Z_j,D)\). Then \(I(Z_1;Y\mid D)-I(Z_2;Y\mid D)=\delta_2-\delta_1\). A desired ordering requires a real comparison of those residual information terms, rather than the training protocol alone.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Problem 2: Cosine fitting identifies direction rather than target magnitude

Assessment: not_issue; impact: no_issue_found



Source: Latest arXiv v2 Eq.(4), PDF p.5; current author src/helpers/loss_helper.py, ScaledCosineLoss



### Source claim (paraphrase)

The objective is scaled cosine error; a separate theorem that zero cosine error implies complete task-vector recovery is not stated.



### Analysis

A concrete scope obstruction uses three valid scaled SQL-aggregate vectors \(T_A=(1,1,1,1,0,0,0)\), \(T_B=(0,0,0,0,1/2,0,0)\), \(T_C=(0,0,0,0,1,0,0)\). They arise from numerical future-row multisets \[\{1,1\},\{0,0,0\},\{0,0,0,0\}\], applying mean/min/max/sum/count/sample-SD, per-column min-max scaling and a zero nonempty flag. A representation merging B and C can predict \(T_C\) for both and achieve zero cosine loss while losing their distinct row counts. With equiprobable types, the lost downstream count information is \(2/3\) bit. This does not prove actual training chooses that representation.



### Finding and scope

This is an objective-identifiability limitation supporting the missing bridge above, not a separate refuted zero-loss theorem. The current source explicitly normalizes both vectors.



## Problem 3: A drop with a restricted decoder does not identify information loss

Assessment: supported; impact: minor



Source: Latest arXiv v2 Section 5.3, PDF p.9



### Source claim (paraphrase)

The text interprets a performance drop as a signal of lost input information.



### Analysis

Let \(X\) be uniform on \(\{0,1,2,3\}\), \(Y=\mathbf1\{X\geq2\}\), \(Z_2=X\), and let \(Z_1\) permute those values to \((0,2,1,3)\). Both encoders are invertible and retain one bit about \(Y\). An affine-threshold decoder is perfect on \(Z_2\), but can achieve only \(3/4\) accuracy on the alternating labels ordered by \(Z_1\). Representation geometry and decoder restrictions can reduce accuracy without losing any information.



### Finding and scope

The diagnostic inference is false in general. No particular RelBench score or cause of its observed drop is established by this analytic example.



### Proposed correction

Retain information loss, geometry, decoder expressiveness, optimization and finite-sample effects as distinct candidate explanations. No new numerical information estimate is invented.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Problem 4: Target construction and actual augmentation are different claims

Assessment: not_issue; impact: no_issue_found



Source: Latest arXiv v2 Sections5.4 and Appendix C.2, PDF pp.9,25



### Source claim (paraphrase)

The mechanism discussion says TVE does not rely on augmentations; the appendix explicitly includes masking regularization.



### Analysis

The stated masking probability is \(0.15\). A future-statistic predictive target need not rely on paired augmented views, while the actual training can still use feature masking. The latter does not isolate an augmentation-removal mechanism for stable embeddings.



### Finding and scope

Retain the narrower target-construction interpretation and the documented masking protocol. This is a mechanism clarification, not a separate theorem or numerical error.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- Exact calculations and static-source findings do not remeasure published experiments or establish the historical experiment-generating revision.
