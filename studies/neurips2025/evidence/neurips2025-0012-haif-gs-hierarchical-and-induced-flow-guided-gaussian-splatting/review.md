# HAIF-GS: Hierarchical and Induced Flow-Guided Gaussian Splatting for Dynamic Scene



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Current tables still contain scene-mean inconsistencies, mixed-evaluator rankings and overly broad superiority wording. Motion/displacement and directional-flow notation also require local clarification. These are Minor; temporal variance, cycle-consistency identifiability and binary-penalty observations are retained as scope clarifications, without alleging core-model failure.



## Scope

Full original concern list and current proceedings methods, experimental tables and appendix read; current author README/license checked at the resolved head. Direct arithmetic and identity-motion arguments were checked without executing author or historical verifier code.



## Problem 1: Several scene means exceed rounding bounds

Assessment: supported; impact: minor



Source: Paper pp. 7, 8, 15, 16



### Source claim (paraphrase)

Displayed means aggregate the listed scene values.



### Analysis

The displayed entries give 3DGS PSNR \(20.86\) rather than \(20.29\); TiNeuVox PSNR \(32.785714\) rather than \(31.92\), and LPIPS \(0.049571\) rather than \(0.038\); GauFre PSNR \(23.542857\) rather than 23.64. Seven metric aggregates exceed rounding bounds. Times \(38\), \(26\), \(41\), \(21\), \(23\), \(35\), \(27\) average \(30.142857\) minutes, incompatible with \(29\) under ordinary rounding. Some discrepancies understate the proposed method.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: Different evaluation functions share a ranking column

Assessment: supported; impact: minor



Source: Paper pp. 7



### Source claim (paraphrase)

Values in each ranked metric column are comparable evaluation quantities.



### Analysis

Table 1 discloses mixed SSIM/MS-SSIM and Alex/VGG LPIPS, yet ranks the resulting values in common columns. Disclosure does not make different functions numerically interchangeable; PSNR must be assessed separately.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Universal superiority exceeds the table evidence

Assessment: supported; impact: minor



Source: Paper pp. 8–9



### Source claim (paraphrase)

The method leads across all scenes and metrics.



### Analysis

Cup PSNR is \(24.72\) versus NeRF-DS \(24.91\); Basin is \(19.74\) versus HyperNeRF 20.41. Several same-evaluator LPIPS values also favor baselines. The justified conclusion is metric- and scene-specific.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: Identity motion returns position rather than displacement

Assessment: supported; impact: minor



Source: Paper pp. 6



### Source claim (paraphrase)

Eq.5 returns displacement and combines consistent rotation representations.



### Analysis

With identity rotations, zero translations and normalized weights, Eq. (\(5\)) returns the original center \(\mu\). Its left side is displacement, which should instead be zero under identity motion. The equation therefore needs either a position interpretation or subtraction of \(\mu\). It also combines axis-angle, matrix and quaternion quantities without conversion. For example, opposite unit quaternions \(q\) and \(-q\) represent one rotation but average to zero unless signs are aligned.



### Finding and scope

The motion formula is locally inconsistent. No released core implementation establishes that the same notation error produced the paper's reconstruction results.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: Flow heads and time steps are underspecified

Assessment: supported; impact: minor



Source: Paper pp. 5, 7



### Source claim (paraphrase)

Eq.7 defines a three-dimensional directional flow at the stated time offset.



### Analysis

Eq.7 combines a three-dimensional flow with a bidirectional network output without selecting a head. Adjacent normalized frame times are not generally \(t\pm1\).



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: Translation variance is scale-dependent

Assessment: not_issue; impact: no_issue_found



Source: Paper pp. 6, 14



### Source claim (paraphrase)

The temporal translation variance is a heuristic for anchor refinement.



### Analysis

Equation (6) averages squared translation deviations over \(16\) sampled times. Repeating translations \(0\) and \((1,0,0)\) eight times each gives variance \(0.25\); doubling coordinates gives variance \(1\), crossing the same \(0.75\) threshold. This correctly exposes length-squared units. The paper calls the quantity normalized variance but does not assert coordinate-scale invariance; normalization can mean division by the number of time samples. A common rigid translation or pure rotation further limits its interpretation as nonrigid complexity, without invalidating its declared heuristic use.



### Finding and scope

The variance formula is valid. Its scene-scale and motion-type dependence is a scope clarification, not a demonstrated author error or reconstruction failure.



## Problem 7: The author release lacks the core pipeline

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 14



### Source claim (paraphrase)

The public release and manuscript specify the complete reconstruction pipeline.



### Analysis

Training, deformation, rendering and evaluation implementations are absent. Network widths, anchor schedules and run manifests do not determine a unique reimplementation. This does not establish that private experiments failed to run.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 8: Cycle consistency does not certify physical scene flow

Assessment: not_issue; impact: no_issue_found



Source: Paper pp. 5–7



### Source claim (paraphrase)

Cycle consistency encourages temporally coherent internal flow for reconstruction.



### Analysis

Zero forward and backward fields have zero cycle loss, as do arbitrary mutually inverse maps. Therefore cycle loss alone does not identify physical scene flow. Sections 4.3–4.5 describe internal temporal guidance and encouragement of coherence, without claiming an if-and-only-if identification theorem. The full training objective also includes reconstruction, so the zero-flow example does not prove that the trained method collapses or fails.



### Finding and scope

This limits a stronger identifiability interpretation that the paper does not establish. The reported reconstruction ablations remain legitimate evidence for reconstruction usefulness.



## Problem 9: Efficiency is a metric-specific tradeoff

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 16



### Source claim (paraphrase)

The method has the stated general efficiency advantage.



### Analysis

Rendering throughput is about \(1.60\) times 4DGS, but memory is \(3.3\) versus \(1.1\) GB and recomputed training time \(30.14\) versus \(26\) minutes. Matched SC-GS costs are absent, so no universal resource advantage follows.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 10: The loss-weight scan does not explain the default

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 7, 17



### Source claim (paraphrase)

The loss-weight scan supports the reported default selection.



### Analysis

Table 12 reports PSNR \(25.57\) at weight \(1.0\), above final \(24.63\), while default \(0.2\) is absent from that scan. Different protocols or randomness could explain this; \(25.57\) must not be silently replaced by 24.57.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 11: The ratio denominator is missing

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 16



### Source claim (paraphrase)

The displayed ratio has a reproducible denominator.



### Analysis

If Table 10 means anchors/Gaussians, Sieve gives \(3.7/114\simeq0.03246\) rather than 0.287. Another denominator is possible. Missing definition is supported; a numerical-error claim is conditional.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 12: The full weight interval does not emphasize the center

Assessment: supported; impact: minor



Source: Paper pp. 6



### Source claim (paraphrase)

The stated weight interval emphasizes the central time.



### Analysis

For weights \((\lambda,1-2\lambda,\lambda)\), the middle weight exceeds an endpoint only if \(1-2\lambda>\lambda\), or \(\lambda<1/3\). The full stated interval \(\lambda<1/2\) is too broad. The actual setting \(\lambda=0.25\) satisfies the narrower condition.



### Finding and scope

The bounded local discrepancy or counterexample is supported; no change in published benchmark scores is quantified.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 13: The binary term is not Shannon entropy

Assessment: not_issue; impact: no_issue_found



Source: Paper pp. 7



### Source claim (paraphrase)

The binary confidence penalty encourages endpoints and is combined with a sparsity penalty.



### Analysis

The penalty \(\alpha(1-\alpha)\) is Bernoulli variance, or a binary Gini/Tsallis-type impurity, rather than Shannon entropy. It is maximal at \(1/2\) and zero at either endpoint, exactly supporting the stated binary-selection explanation. The combined regularizer \(0.5\alpha+0.2\alpha(1-\alpha)\) has derivative \(0.7-0.4\alpha>0\) on \([0,1]\); its preference for zero is consistent with its declared sparsity purpose, while reconstruction supplies the competing incentive. The paper does not identify this function specifically as Shannon entropy.



### Finding and scope

The defined penalties have the stated endpoint/sparsity roles. Neither their naming nor this derivative proves collapse of the full model.



## Problem 14: Experimental uncertainty is not inapplicable

Assessment: needs_evidence; impact: needs_evidence



Source: Paper pp. 19–25



### Source claim (paraphrase)

Statistical reporting is inapplicable to these experiments.



### Analysis

Stochastic training experiments remain applicable to the statistical-reporting checklist. A displayed \(0.04\) dB gain does not by itself establish a stable cross-run advantage.



### Finding and scope

This is a scope/provenance gap, not proof that the stronger empirical conclusion is false.



### Proposed correction

Reconcile the specific equation, reported quantity or source contract described above. Corrected full-experiment results remain unverified.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.

- No new author-code execution, training, empirical replication or contact.

- Historical verification outputs were inspected but not rerun.

- Missing run provenance and unresolved empirical interpretations remain explicit.
