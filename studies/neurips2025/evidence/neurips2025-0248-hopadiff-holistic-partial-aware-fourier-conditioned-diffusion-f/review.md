# HopaDIFF: Holistic-Partial Aware Fourier Conditioned Diffusion for Referring Human Action Segmentation in Multi-Person Scenarios



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current release has incorrect interval matching/edit aggregation and mismatched score/label axes. Its conditioning, branch losses, memory and frequency operations also differ materially from the paper’s equations. Exact historical table-generation paths and changed rankings remain unestablished.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Segmental F1 counts nonoverlap and repeated matches

Assessment: supported; impact: minor



Source: Section 5.1, PDF p.7; utils.py, f_score lines 119–148



### Source claim (paraphrase)

The source takes an absolute signed intersection and omits the one-use ground-truth hit guard.



### Analysis

For four one-hot frames, truth \((A,B,B,B)\), prediction \((B,B,B,A)\), true A interval \([0,1)\) and predicted \([3,4)\) are disjoint. Source absolute intersection is \(2\), union \(4\), artificial IoU \(1/2\); B genuinely has IoU \(1/2\). At threshold \(0.5\), source counts \((TP,FP,FN)=(2,0,0)\), F1 \(100\%\), versus correct \((1,1,1)\), \(50\%\). Independently, truth \((A,A,A,A,A)\), prediction \((A,A,B,A,A)\) has two A predictions each IoU \(2/5\) with one true segment; at threshold \(0.25\), omitted uniqueness gives \((2,1,0)\), \(80\%\), versus \((1,2,0)\), \(50\%\). Repeating frames \(750\) or \(600\) times gives legal \(3000\)-frame cases with identical ratios. For disjoint equal-length intervals, false ratio \(g/(g+2\ell)\) even approaches \(1\) as the gap grows.



### Finding and scope

The evaluator fails ordinary temporal-overlap/cardinality semantics on the one-hot subdomain. Perfect-sequence controls still pass; multi-label annotations cannot justify disjoint matches. Historical table impact remains unestablished.



### Proposed correction

Use \(I=\max(0,\min(b,d)-\max(a,c))\), \(U=(b-a)+(d-c)-I\), and require an unused compatible ground-truth match. Declare multi-label compatibility and segment conventions separately; no corrected benchmark ranking is supplied.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: EDIT divides by a two-element container

Assessment: supported; impact: minor



Source: inference.py, paired ground-truth/prediction lists; utils.py, func_eval lines 159–181



### Source claim (paraphrase)

The source sums per-video normalized edit scores but divides by the outer container length \(2\), rather than video count.



### Analysis

For \(N\) perfect videos with labels \((A,A,B,B)\), every per-video score is \(100\). The true mean is always \(100\), while source returns \(50N\): \(50,100,150\) for one, two, three videos. In general the released statistic is \(N/2\) times the equal-video mean, so dataset duplication changes its scale. Within a fixed equal-cardinality comparison the common factor alone preserves ranking, but not normalization.



### Finding and scope

The aggregation is incorrect for the actual paired-list signature. Published values cannot simply be rescaled without authenticating their driver and the separate label-interface behavior.



### Proposed correction

Validate equal nonempty paired video lists and divide by their count. If a different weighted edit metric is intended, define its weights explicitly.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 3: Score vectors and class-axis filtering are passed as temporal labels

Assessment: supported; impact: minor



Source: inference.py, lines 109–122; utils.py, segmentation and nonzero comparisons lines 64–99,131–136,166–169



### Source claim (paraphrase)

The driver passes raw \((T,C)\) scores to discrete segment routines, while its median filter operates across classes in the preceding \((C,T)\) layout.



### Analysis

Constant argmax A with scores \[(.6,.4),(.7,.3),(.8,.2),(.9,.1)\] should give one segment, but exact-vector change detection gives four and per-video edit \(25\), versus discrete edit \(100\). Separately, nonzero on a class vector returns a one-element tuple, so using its length selects only the top one class; truth \(\{0,2\}\) and scores \((.6,.3,.1,0,\ldots)\) pass Hit@1 membership despite not recovering simultaneous labels. Finally, at each of five frames give class \(68\) probability \(0.9\), all other \(136\) classes \(0.1/136\). Proper temporal median filtering preserves this constant signal; source size-\(30\) filtering across class neighborhoods erases its peak and normalization gives \(1/137\) everywhere. This strictly positive example needs no zero-probability limit.



### Finding and scope

The source conflates confidence changes, labels, set membership and temporal smoothing. Multi-label ACC has no single forced convention, so Hit@1 interpretation is a qualification as well as a tuple-cardinality issue; no actual dataset ranking is inferred.



### Proposed correction

Filter each class over time. Convert scores with a declared prediction-only label/set rule before run-length segmentation; define per-class versus joint-set segments and name ACC accordingly. Using true-label cardinality to choose predictions is a different truth-dependent rule, not a silent repair.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 4: Training and denoising do not follow the stated branch conditions

Assessment: supported; impact: minor



Source: Eqs.(4),(6)–(7), PDF pp.6–7; model.py, lines 153,169–173,248–254,392–405,460–487



### Source claim (paraphrase)

The paper uses feature-conditioned branch decoders, but source fixes zero conditioning, shares one decoder call path, substitutes the holistic clean estimate into the partial update and overwrites the second boundary loss.



### Analysis

With fixed time/noisy labels/parameters, the training decoder receives zeros_like(features), so its output and decoder-loss gradient cannot depend on the feature conditioning tensor. Occasional dropout is not a permanently fixed zero branch; inference instead passes real features. decoder_original is instantiated but unused. For partial DDIM, substituting \(\widehat x_0^h\) for \(\widehat x_0^p\) changes the next value by \(\sqrt{\bar\alpha_{\rm next}}(\widehat x_0^h-\widehat x_0^p)\): at \(0.81,0.2,-0.4\), it is \(0.18\) rather than \(-0.36\), difference \(0.54\). Finally second boundary loss is assigned the first reduced loss, giving \(4L_h\) rather than \(2(L_h+L_p)\) and no direct second-branch boundary gradient. Equal clean branch predictions hide the DDIM discrepancy.



### Finding and scope

The current file materially differs from the described branch dataflow/objective. It may be an ablation or incomplete release; no authenticated experiment manifest resolves historical use, and no corrected model quality is claimed.



### Proposed correction

Use the declared feature conditions, explicitly choose shared or separate decoder parameters, use the partial clean estimate in its own update and reduce its own boundary loss. These restore local dependencies/algebra; architecture/training changes require independent evaluation.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 5: Vector pooled memory is not the matrix recurrence

Assessment: supported; impact: minor



Source: Eq.(5), PDF p.6; xLSTM2/xLSTM.py, lines 421–426,477–512



### Source claim (paraphrase)

The paper uses matrix cell memory with outer product, per-time update and a bounded inner-product normalizer; source uses pooled vector states, elementwise products and one global maximum.



### Analysis

From zero state, choose \(i=1,o=1/2,v=(1,0),k=q=(0,1)\). The paper obtains \(C=vk^\top=\begin{pmatrix}0&1\\0&0\end{pmatrix}\), normalizer \(1\), output \((1/2,0)\). Source elementwise \(v\odot k=0\), and zero-cell layer normalization cannot recover the missing off-diagonal contribution. The source also divides by max of \(n\odot q\) without a lower bound, so \(q=0\) yields zero over zero rather than protected zero. It stores detached batch/time-averaged states across forward calls, and the independent-video driver does not reset them. Consequently order dependence is structurally possible; the earlier bounded component test reported repeated-input differences removed by resetting, which is historical execution evidence, not a new run.



### Finding and scope

The current memory is a different operator with an unprotected domain and unspecified cross-video state. The displayed matrix recurrence itself is not refuted; trained-checkpoint incidence and benchmark impact are unknown.



### Proposed correction

Reset state at independent sequence boundaries to remove that persistence. Implementing Eq.(5) additionally needs a matrix state, outer product, explicit temporal recurrence/scan and specified bounded inner-product normalizer. A vector-memory alternative needs its own definition; reset alone is not a matrix-memory repair.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 6: The release uses pre-fusion DCT-II instead of post-fusion DFT

Assessment: supported; impact: minor



Source: Eq.(6), PDF p.7; model.py dct lines 22–50, training lines 302–305 and sampling lines 424–426



### Source claim (paraphrase)

The source adds an unnormalized DCT-II residual before HP-xLSTM, while the paper specifies DFT of the fused features.



### Analysis

For \(x=(1,0,0,0)\), ordinary DFT is \((1,1,1,1)\), but the implemented DCT-II is \[(2,2\cos(\pi/8),2\cos(\pi/4),2\cos(3\pi/8))\], approximately \[(2,1.847759,1.414214,0.765367)\]. No single global scale makes them equal. A Fourier representation of an extended signal is not the same length transform. For nonlinear fusion \(G\), \(G(z+\mathrm{DCT}_{II}z)\) also need not equal \(G(z)+\mathrm{DFT}(G(z))\); the release constructs no separate post-fusion DFT conditions.



### Finding and scope

The current transform/order differs from the specified operator, without showing cosine features are ineffective or identifying the exact frequency variant behind each table.



### Proposed correction

Accurately describe the existing pre-fusion DCT-II residual and corresponding configurations, or separately implement/validate the stated post-fusion DFT with an explicit complex-to-real representation. No complete trained replacement is supplied.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
