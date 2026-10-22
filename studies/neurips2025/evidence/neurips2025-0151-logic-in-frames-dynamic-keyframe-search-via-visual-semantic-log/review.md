# Logic-in-Frames: Dynamic Keyframe Search via Visual Semantic-Logical Verification for Long Video Understanding



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The printed search samples almost all candidate frames in its first iteration, contradicting its square-root total-time claim. Static source checks also establish order-dependent relation bonuses, a global scoring latch and target-confidence inconsistencies; benchmark effects remain unmeasured.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Chronological relation scoring depends on sample-list order

Assessment: supported; impact: minor



Source: Section 2.3.3, Eqs.(6)–(7), PDF p.5; interface_searcher.py, compute_frame_relation_scores and sample_frames



### Source claim (paraphrase)

Temporal and causal bonuses depend on the objects’ frame times. The release enumerates only list positions \(j\geq i\), although later weighted samples are unsorted.



### Analysis

Let object A occur at time \(1\), B at \(4\), with base scores \(0.4,0.6\), relation increment \(0.15\) and temporal window \(5\). List order \((4,2,1,0)\) places B before A. The upper-triangular loop never tests the required A–B orientation, returning \((0.4,0.6)\) at the two endpoints rather than \((0.55,0.75)\). Their actual times satisfy \(1<4\) and \(4-1<5\).



### Finding and scope

The release has an order-dependent scoring omission. Sorting would avoid this particular case; video-answer accuracy is not determined by it.



### Proposed correction

Sort all aligned frame records by time, or enumerate endpoint pairs and apply explicit time predicates.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: A global relation latch suppresses later distinct evidence

Assessment: supported; impact: minor



Source: Eq.(4), PDF p.5; Algorithm 2, PDF p.20; compute_frame_relation_scores



### Source claim (paraphrase)

The paper awards a spatial bonus to each qualifying frame; the release skips a relation after its persistent Boolean has been set.



### Analysis

Two batches contain A and B together at distinct times \(1\) and \(8\), with base scores \(0.4\) and \(0.5\). A \(0.15\) bonus produces \(0.55\) in the first call and sets the latch. The next call returns \(0.5\), although the per-frame formula gives \(0.65\). An unrelated remaining target can keep search active. Multiple matches within the first call can still receive bonuses.



### Finding and scope

The intentional one-shot release policy differs from the unqualified per-frame scoring description; its aggregate search effect is unresolved.



### Proposed correction

Track distinct frame/relation evidence and reconstruct scores from base confidence plus valid bonuses, rather than disabling the whole relation.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: Single-frame verification changes scores and borrows another target’s confidence

Assessment: supported; impact: minor



Source: Eqs.(2)–(4), PDF pp.4–5; verify_and_remove_target, lines 667–713



### Source claim (paraphrase)

Individual verification overwrites a relation-integrated registry entry with the maximum base detection score and uses that frame maximum to certify a named target.



### Analysis

A frame with base \(0.8\) and a valid \(0.15\) relation bonus outranks a competitor at \(0.9\). Verification writes \(0.8\), reversing the ranking although the relation persists. Separately, present objects A and B with confidences \(0.4\) and \(0.95\), unit weights and threshold \(0.7\) yield frame maximum \(0.95\). The target loop can remove A because A is present and that maximum exceeds the threshold, although A’s own confidence does not. Both confidences exceed the detector filter \(0.2\).



### Finding and scope

Both local effects follow from the inspected assignments. Membership prevents certifying an absent object, but does not make a frame maximum target-specific.



### Proposed correction

Preserve score components and reconstruct valid relation evidence after re-detection. Compare the target’s own detections with the confirmation threshold.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 4: The printed first iteration has linear work

Assessment: supported; impact: major



Source: Algorithms 1–2, PDF pp.4,20; Appendix F.1 and F.3, PDF pp.19,21



### Source claim (paraphrase)

The algorithms initialize \(B=N=|V|\), set \(k=\lfloor\sqrt B\rfloor\), and sample \(k^2\) frames; Appendix F.3 claims total time \(O(\sqrt N)\).



### Analysis

For \(N=m^2\), the first round samples exactly \(N\) entries. In general, \[M_1=\lfloor\sqrt N\rfloor^2>N-2\sqrt N+1.\] Thus \(M_1=\Theta(N)\) and \(M_1/N\to1\). Materializing or processing each sampled frame costs at least constant work, giving a first-round \(\Omega(N)\) lower bound. The released constructor instead uses a capped practical budget; that different procedure is not refuted by this literal-pseudocode argument.



### Finding and scope

The ordinary-cost square-root claim is incompatible with the printed algorithm. This does not invalidate measured frame fractions for the differently budgeted release.



### Proposed correction

Specify actual candidate/budget units and account for initialization, sampled entries, relation checks, detector work and dense updates. The printed algorithm’s linear first-round lower bound must be retained.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 5: The alternative Beta sampler needs bounded reward semantics

Assessment: needs_evidence; impact: minor



Source: Appendix F.4, Eq.(18), PDF pp.21–22



### Source claim (paraphrase)

The second Beta shape is \(\beta_t+n-\sum_i S_i(t)\), without an explicit connection between \(S_i\) and bounded rewards.



### Analysis

If \(S_i\) are the integrated scores, base \(1\) plus two bonuses \(0.15\) gives \(1.3\). With \(n=4\) and unit priors, the shapes are \(6.2\) and \(-0.2\), which cannot define a Beta law. If instead \(S_i\in[0,1]\) are separately normalized rewards, the second shape is at least \(\beta_t>0\). The inspected release does not use this alternative sampler.



### Finding and scope

A conditional specification gap remains; an actual release failure or the intended reward interpretation is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
