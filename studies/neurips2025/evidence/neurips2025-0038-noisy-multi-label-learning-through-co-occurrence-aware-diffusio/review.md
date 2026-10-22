# Noisy Multi-Label Learning through Co-Occurrence-Aware Diffusion



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The central marginal-reverse/known-label-bridge identity is false and does not establish universal decoder necessity. Class-numbering, representation, optimizer and metric/protocol defects are local author-release issues with unmeasured historical benchmark effects.



## Scope

Latest-version, claim-focused review of the cited author-paper passages and applicable current author-release paths. The stated counterexamples and scope controls were checked analytically; no author program, old verifier, training run or benchmark was executed.



## Problem 1: A known-label bridge is substituted for a marginal reverse law

Assessment: supported; impact: major



Source: Eq.6, p.5; Appendix A, pp.22–25, Eqs.13–15,50–62.



### Source claim (paraphrase)

Eq. (\(6\)) treats the known-\(y_0\) reverse bridge as the marginal reverse law conditioned only on \(y_t,x\).



### Analysis

The marginal is a mixture over \(q(y_0\mid y_t,x)\). If bridge means are \(a_ty_0+b_ty_t\) and common bridge covariance is \(\widetilde\beta_tI\), total covariance gives \(\operatorname{Cov}(y_{t-1}\mid y_t,x)=\widetilde\beta_tI+a_t^2\operatorname{Cov}(y_0\mid y_t,x)\). A two-point label posterior with nonzero weights has positive extra covariance whenever the bridge coefficient is nonzero. Deleting \(y_0\) from conditioning cannot delete that term, even with arbitrarily small positive forward noise. The proposed universal decoder-gradient necessity does not follow.



### Finding and scope

The claimed exact reverse-law derivation omits posterior-label mixture covariance, undermining the asserted universal decoder-gradient necessity. A Gaussian reverse approximation can still be a useful model.



### Proposed correction

Use the actual mixture or conditional-moment law and justify any Gaussian approximation separately.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: Co-occurrence weights depend on class numbering

Assessment: supported; impact: minor



Source: utils/knn_utils.py and all three training call sites.



### Source claim (paraphrase)

The co-occurrence weighting is intended to depend on label relationships rather than arbitrary class IDs.



### Analysis

The author's class-pair weight function changes sample weights under a simultaneous permutation of label coordinates and co-occurrence rows/columns. Thus arbitrary label numbering can alter the training objective. A symmetric unordered-pair rule can restore numbering invariance, but neither its optimality nor corrected benchmark performance is established.

For a realizable co-occurrence count matrix with pair counts \(c_{01}=1,c_{02}=3,c_{12}=1\), row normalization gives upper-pair scores \((1/4,3/4,1/2)\). A batch containing those three label pairs receives approximately \((1/2,1,3/4)\) after the released min–max scaling. Simultaneously swapping class IDs \(0,1\) and the matrix axes changes the pair scores to \((1/2,3/4,1/2)\), and scaled weights to approximately \((1/2,1,1/2)\). The lower-ID directional lookup changes a sample weight despite unchanged label relations.



### Finding and scope

The released weighting rule is not invariant under arbitrary relabeling of class IDs. No corrected benchmark performance is inferred.



### Proposed correction

Specify and use a permutation-invariant class-pair statistic with an explicit normalization.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: The active target is a vector rather than the described matrix

Assessment: supported; impact: minor



Source: Section 4.2, p.5; Algorithm 1, p.7; train_on_Voc2007.py:96–118; utils/model_diffusion.py.



### Source claim (paraphrase)

The paper and Algorithm1 specify a \(C\)-by-\(C\) one-hot diffusion target.



### Analysis

The release passes batch-by-\(C\) neighborhood vectors to forward_t, and the network returns \(C\) outputs. There is no active conversion to the claimed \(C\times C\) target; an unused one-hot helper does not implement it. Vector diffusion can be valid, but it has a different representation rationale.



### Finding and scope

The released vector target is a different representation from the stated matrix target.



### Proposed correction

Document vector diffusion explicitly or supply the actual matrix encoding/decoding path and rerun matched comparisons.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: The depicted trainable encoder is outside the optimizer

Assessment: supported; impact: minor



Source: Figure B.1, p.25; optimizer construction and training/evaluation mode calls.



### Source claim (paraphrase)

Figure B.1 marks the diffusion feature encoder trainable, distinct from the intentionally frozen fp_encoder.



### Analysis

The optimizer includes the noise head but omits diffusion_encoder. Backward can create encoder gradients without updating its parameters; optimizer.zero_grad also does not clear excluded gradients. Evaluation sets that separate encoder to eval and the next model.train does not restore it. This does not mean every buffer was frozen from the first step.



### Finding and scope

The optimizer does not update the separately declared trainable diffusion encoder, and its mode is not restored as stated.



### Proposed correction

If trainable as specified, include diffusion_encoder parameters and restore its train mode; preserve the separately intended frozen fp_encoder.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: Checkpoint selection uses test mAP

Assessment: supported; impact: minor



Source: Three training entries, best-mAP checkpoint condition and dataset loaders.



### Source claim (paraphrase)

The paper describes a validation-based model-selection protocol.



### Analysis

The release evaluates the held-out test loader each epoch and uses its mAP to update the best checkpoint. This makes those source-path test results part of selection. It does not prove every published experiment used the default snapshot.



### Finding and scope

The public checkpoint selector uses held-out test mAP, differing from a validation-only protocol.



### Proposed correction

Create disjoint training/validation/test identities and select on validation only; the complete paper scores were not recomputed.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: Classwise zero-count guards contaminate overall F1

Assessment: supported; impact: minor



Source: utils/learning.py:214–278, especially 249–268; Section 5.1, p.7.



### Source claim (paraphrase)

The release names its aggregate metric overall F1.



### Analysis

The metric replaces zero per-class prediction/ground-truth counts by one before global summation. With true positives \((1,0)\), predicted-positive counts \((1,0)\), and actual-positive counts \((1,1)\), correct overall F1 is \(2/3\). The fabricated second predicted positive changes it to \(1/2\). Division guards must not change raw global counts.



### Finding and scope

The routine alters raw global counts before computing overall F1 and fails the two-class control.



### Proposed correction

Keep original counts for global precision/recall and use masked division only for classwise summaries.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: COCO noise and validation options are not implemented by the default path

Assessment: supported; impact: minor



Source: train_on_COCO.py and utils/data_coco.py; paper dataset/protocol section.



### Source claim (paraphrase)

The entry exposes noise-type and validation-split options.



### Analysis

The COCO constructor call does not forward the requested noise_type, and the split_per parameter is not used to create the declared validation partition. Passing a different CLI value therefore does not establish a different noise law or a real validation split on that path. External preprocessing could explain historical runs, but is unrecorded.



### Finding and scope

The COCO entry does not implement the exposed noise/split settings on the checked path. Historical external preprocessing is unresolved.



### Proposed correction

Forward the requested noise type and implement an actual disjoint validation split with identifiable samples.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, model spending, training, author contact or complete benchmark replication.

- Historical numerical results are retained evidence rather than current reruns.

- Local counterexamples do not invalidate every empirical result; missing historical run attribution remains unresolved.
