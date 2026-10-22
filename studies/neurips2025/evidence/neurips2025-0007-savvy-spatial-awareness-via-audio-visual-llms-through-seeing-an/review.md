# SAVVY: Spatial Awareness via Audio-Visual LLMs through Seeing and Hearing



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The released acoustic calibration, depth conversion and regeneration paths contain local defects, and the localization/temporal definitions need correction. Their effect on the central QA result has not been established; the QA cache reproduces the reported task scores. The strict paper assessment is therefore Minor, with unresolved judging, sampling and deployment questions preserved separately.



## Scope

Claim-focused reading of the identified paper and author-released materials. The arguments below distinguish mathematical contradictions, version-specific implementation defects and unresolved empirical consequences. No author code was executed in this revision.



## Problem 1: The acoustic code treats a coherent fraction as a coherent-to-diffuse ratio

Assessment: supported; impact: minor



Source: Official PDF: Section 4.3, p. 6; Appendix F.3, pp. 34-35. SAVVY/utils/doa_aria.py, lines 24-54 and 436; SAVVY/utils/avmap_utils.py, lines 331 and 356.



### Source claim (paraphrase)

Under the equal-power, uncorrelated coherent/diffuse model in main §\(4.3\) and Appendix F.3, range calibration is intended to use a coherent-to-diffuse power ratio.



### Analysis

Let \(\rho\) denote coherent/direct power divided by diffuse power. Under the standard equal-power, uncorrelated-component coherence model, \[
\Gamma_x=\frac{\rho\Gamma_s+\Gamma_n}{1+\rho}.
\] This model and its inversion are given by Schwarz and Kellermann, Eqs. (\(8\)), (\(9\)), and (\(15\)). The same algebra applies to real parts under the corresponding assumptions. The published SAVVY implementation instead computes \[
\frac{\gamma_x-\gamma_n}{\gamma_s-\gamma_n}
=\frac{\rho}{1+\rho}=\alpha.
\] The result is the coherent fraction of total power, not \(\rho\). Yet the downstream code fits \(K=r^2\alpha\) and predicts \(r=\sqrt{K/\alpha}\), as though \(\alpha\) obeyed the inverse-square relation intended for the coherent-to-diffuse ratio. For a physical inverse-square constant of \(4\,\mathrm{m}^2\), a source at \(1\) m has \(\rho=4\), while one at \(4\) m has \(\rho=0.25\). Calibrating the implemented rule at \(1\) m gives \(K_{\mathrm{fit}}=0.8\). Its prediction for the \(4\) m source is then \[
\widehat r=\sqrt{0.8/0.2}=2\ \mathrm{m}.
\] Correctly converting these ideal fractions to \(\rho=\alpha/(1-\alpha)\) returns \(4\) m. More generally, the implemented rule compresses distances toward the calibration range when direct sound dominates. This directly undermines the claimed physical interpretation of the audio distance component, although the size of its effect on the fused benchmark score remains unmeasured.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Invert the coherence model to obtain the coherent-to-diffuse ratio; a coherent fraction is a different quantity.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: The calibration constant depends on observation order

Assessment: supported; impact: minor



Source: SAVVY/utils/avmap_utils.py: get_audio_track, lines 319-345.



### Source claim (paraphrase)

The released calibration uses DBSCAN to obtain a stable distance constant, selecting cluster label zero.



### Analysis

In get_audio_track, candidate calibration constants are clustered with min_samples set to one, then the mean of clusters[\(0\)] is used. Cluster zero is the first discovered cluster, not necessarily the dominant one. For the ordered constants \([100,1,1,1]\), the chosen mean is \(100\); for the same observations ordered as \([1,1,1,100]\), it is \(1\). Since range scales as \(\sqrt K\), this creates a factor-\(10\) range difference. This is a deterministic consequence of the cited source's cluster selection, not an estimate of the paper's benchmark error.



### Finding and scope

The released calibration rule is order-sensitive. Its frequency and influence in the original scene-mapping runs remain unknown.



### Proposed correction

Select calibration clusters by a declared size/reliability rule rather than the first discovered label.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Depth serialization loses metric precision and the bearing map ignores rectified intrinsics

Assessment: supported; impact: minor



Source: SAVVY/scripts/get_seg.py: lines 61-67, 257, 267-284 and 290. Official PDF: Appendix E.1, p. 31.



### Source claim (paraphrase)

The Seg branch converts estimated metric depth and image position into spatial tracks, using the rectified-image setting stated in Appendix E.1.



### Analysis

The depth routine writes \(\lfloor256d\rfloor\) to a \(16\)-bit PNG, but the later default cv2.imread call decodes it as \(8\)-bit color. That drops the lower eight bits, giving an effective integer-meter value \(\lfloor d\rfloor\) rather than restoring \(d\). Positive submeter depths can therefore become zero and be removed by the positive-depth filter, leaving an undefined mean for an all-submeter mask. This is material to submeter thresholds, but averaging and zero exclusion prevent inferring one universal direction of aggregate error.

The bearing routine maps normalized horizontal offset linearly to \(\pm90^\circ\). A rectilinear camera instead uses \(\theta=\arctan((u-c_x)/f_x)\). With an illustrative \(90^\circ\) field of view, a point halfway from center to edge has bearing \(\arctan(1/2)\simeq26.565^\circ\), whereas the linear rule gives \(45^\circ\). Actual rectified intrinsics and the distinction between optical-axis depth and ray range are needed for the paper's recordings.



### Finding and scope

The released depth/bearing conversion has local defects. The segmentation/depth models were not rerun, so their total effect on the published localization results is unmeasured.



### Proposed correction

Decode depth without losing \(16\)-bit precision, restore physical units and use calibrated rectilinear intrinsics.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: Table 6 uses Cartesian accuracy rather than the stated angular/radial accuracy

Assessment: supported; impact: minor



Source: Official PDF: Section 5.1, p. 7, and Tables 4-6. SAVVY/main.py: lines 344-360.



### Source claim (paraphrase)

Section 5.1 defines localization accuracy for Tables 4--6 by an angle threshold and a radial-distance threshold.



### Analysis

Section 5.1 defines success by angular error below \(45^\circ\) and radial error below \(1\,\mathrm m\). SAVVY/main.py instead tests Cartesian position error below \(1\,\mathrm m\). At equal ranges \(1\,\mathrm m\) and angle error \(50^\circ\), Cartesian error is \(2\sin25^\circ\simeq0.845\,\mathrm m\): the code passes and the stated angular gate fails. At equal ranges \(4\,\mathrm m\) and angle error \(30^\circ\), Cartesian error is \(8\sin15^\circ\simeq2.071\,\mathrm m\): the code fails while the written gates pass.

The released benchmark positions yield \(1196/1522\simeq78.5808\%\) within one Cartesian meter, matching Table 6's \(78.6\%\). Thus Tables 5 and \(6\) cannot be interpreted as a gain under one unchanged localization definition. This does not invalidate the separate QA-task scores.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Choose and name either Cartesian localization or the stated angular/radial gate; recompute under the declared metric.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: Angular error must wrap and missing predictions cannot have zero error

Assessment: needs_evidence; impact: needs_evidence



Source: SAVVY/evaluation/avmap_eval_utils.py: eval_srp_audio, lines 35-51; eval_vis_track2d_loc, lines 112 and 120.



### Source claim (paraphrase)

The release evaluates signed azimuth error and missing audio frames as part of angular and distance metrics.



### Analysis

The cited angular evaluator uses ordinary subtraction. Ground truth \(174^\circ\) and prediction \(-174^\circ\) produce \(348^\circ\), although circular error is \(12^\circ\). The proper error is \[\left|((\widehat\theta-\theta+180^\circ)\bmod360^\circ)-180^\circ\right|\]. A missing audio frame is assigned zero in both error lists as well as in accuracy: zero is a valid accuracy failure but incorrectly denotes perfect angular/range estimation. The local source rule is clear; its relation to historical paper metrics remains unresolved.



### Finding and scope

The available material identifies a scope or evidence gap; it does not prove that the reported empirical effect is false.



### Proposed correction

Use circular azimuth differences and report missing-prediction coverage separately from valid errors.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: The released Seg generator skips allocentric questions and mismanages video identity

Assessment: supported; impact: minor



Source: SAVVY/scripts/get_seg.py: initialization, lines 54-58; regeneration flow, lines 135-148 and 308-337; repository README.



### Source claim (paraphrase)

The README directs regeneration through the published Seg script, while the paper identifies SAM \(2\) as the segmentation component.



### Analysis

In get_det, an ID containing exo triggers return after reference-description collection and before frame extraction or JSON output. This skips both allocentric question types in that script. It does not establish how previously released cached detections were generated.

The metadata loop opens a global video capture. The shuffled question loop does not reopen a capture for each current video_id, while get_det reads and releases that global handle. Without pre-existing extracted frames, a request can therefore use the last opened video and later requests can receive an already released handle.

The paper/README identify SAM \(2\), while the script instantiates SamModel with facebook/sam-vit-huge, an original SAM checkpoint. These are source-version/regeneration discrepancies; no corrected benchmark result is available.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Process allocentric questions, open the correct video per request and declare the intended SAM version.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: Temporal grounding uses eleven thresholds instead of the declared ten

Assessment: supported; impact: minor



Source: Official PDF: Section 5.1, p. 7, and Table 3. SAVVY/evaluation/metric_utils.py: lines 79-94; SAVVY/main.py: line 327.



### Source claim (paraphrase)

Section 5.1 defines an average of recall across thresholds \(0.05\), \(0.10\), .., \(0.50\) and labels it t-mIoU.



### Analysis

The paper averages Recall@\(1\) over thresholds \(0.05,0.10,\ldots,0.50\), which differs from mean IoU: IoU \(0.52\) has \(100\%\) threshold-averaged recall but IoU \(52\%\). The helper creates \(11\) evenly spaced thresholds using an extra count increment, hence spacing \(0.045\). At IoU \(0.27\), it gives \(5/11\simeq45.45\%\), whereas the written ten-threshold rule gives \(5/10=50\%\).



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Use exactly the ten declared IoU thresholds and name the statistic threshold-averaged Recall@1.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 8: The printed coordinate maps omit yaw and use the wrong microphone plane

Assessment: supported; impact: minor



Source: Official PDF: Stage 2 equation, p. 5; steering vector, p. 6; Appendix E.2 microphone coordinates, p. 31; Algorithm 1, line 2, p. 36.



### Source claim (paraphrase)

The world mapping at p. 5 and the steering definition at p. 6 should agree with camera-relative bearings and the Appendix E.2 microphone geometry.



### Analysis

The printed world map adds \([r\cos\theta,r\sin\theta]\) to camera position without camera heading. A camera at the origin observing a fixed object at \((2,0)\) and then turning \(90^\circ\) can therefore place that object at \((0,2)\), a false displacement \(2\sqrt2\). For the stated right-positive convention, the heading-aware expression is \(\mathbf p=\mathbf L+r[\cos(\psi-\theta),\sin(\psi-\theta)]^\top\). The author's get_possible_locs function includes heading and avoids this printed error.

The printed steering vector lies in the \(x\)-\(y\) plane although microphones \(3\) and \(5\) differ only along \(z\), by \(0.1\,\mathrm m\). It consequently predicts zero delay for that front/rear baseline at every azimuth. The author steering implementation uses the \(x\)-\(z\) plane and preserves that directional information.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Include camera heading and the correct microphone plane in the written geometry; the examined implementation already supplies those corrections.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 9: Several ablation summaries disagree with their displayed numbers

Assessment: supported; impact: minor



Source: Official NeurIPS 2025 PDF: Section 5.3 and Table 6, p. 9; Appendix F.2 and Table 7, p. 34; Table 9 caption and accompanying global-mapping discussion, p. 36; Appendix H and Table 10, p. 37.



### Source claim (paraphrase)

The text around Tables 6, \(7\), \(9\) and \(10\) makes optimum, nearest-competitor and universal-improvement comparisons.



### Analysis

The four-task macro-score is \(58.20\) at threshold \(0.3\) and \(57.95\) at \(0.5\). Egocentric-direction spread is \(3.3\) percentage points, exceeding the stated below-three range. Table 6's nearest-competitor gains are \(0.5,5.2\) points, not the \(3.5,8.3\) differences against weaker rows. Table 9 also worsens some metrics, requiring metric-specific improvement wording.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Replace the overbroad threshold/ablation summaries with the actual displayed differences.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 10: The disclosed input differences define a complete-system comparison

Assessment: not_issue; impact: no_issue_found



Source: Official PDF: experimental inputs, p. 7; Appendices D-F, especially pp. 31-34; Table 6. SAVVY/main.py: baseline/system input paths.



### Source claim (paraphrase)

Main pp. 7 and \(31\)-\(-34\) compare the complete SAVVY system with baselines using different frame, microphone and pose inputs.



### Analysis

SAVVY has \(7\)-channel recordings available and uses a selected four-microphone array, \(128\) sampled frames for Seg, and calibrated closed-loop 6DoF Project Aria trajectories. The open AV-LLM baselines receive \(32\) frames and compressed mono audio. These conditions are disclosed, particularly in Appendices D-F, but mean the main comparison evaluates a richer complete system. It does not isolate an improvement in an otherwise identical AV-LLM's intrinsic spatial reasoning. The camera poses are additional sensor-derived inputs; they should appear explicitly in the task/interface formulation. Table 6 and the mapping ablation provide useful partial controls. A more decisive study would compare methods with matched frame budgets and pose availability, include a pose/depth-based visual geometric baseline, and separate gains from spatial channels from gains due to the fusion rule. No allegation of an impermissible comparison is intended: the present comparison is informative for system performance, while a causal architectural attribution requires these controls.



### Finding and scope

The richer-input comparison is disclosed and is informative about complete-system performance. It does not isolate architecture-only causation, but this limitation alone does not establish a current paper error.



## Problem 11: Question-level counts do not equal independent scene replication

Assessment: needs_evidence; impact: needs_evidence



Source: Official PDF: benchmark description, p. 4; Table 2; Appendix F.2; statistical-significance checklist, p. 18. Released benchmark/cache: question IDs, sequence prefixes and answer labels.



### Source claim (paraphrase)

The cache has \(1522\) questions, while Appendix F.2 and the checklist discuss operating points and negligible repeated-inference variation.



### Analysis

The released metadata has \(59\) video IDs, \(30\) paired recording-sequence prefixes and three location prefixes, rather than \(1522\) independent scenes. The main text's \(58\) scenarios need a definition mapping, not an automatic contradiction.

An always-A response scores \(194/463\simeq41.9\%\) on egocentric direction, and a difficulty-conditioned majority response scores \(34.4\%\) on allocentric direction. These describe the released label distribution, not independently selected competitors. Resemblance to a named model's rounded score does not identify its answers.

Conditional resampling of the \(30\) sequence groups gives a macro-score interval \(53.91\%\)–\(61.26\%\) between the \(2.5\) and \(97.5\) percentiles over \(5000\) resamples. This is a sensitivity calculation, not a population confidence guarantee for three convenience locations or a paired Gemini test. Low repeated-inference variation does not remove sampling uncertainty.



### Finding and scope

The released counts and conditional resampling describe the finite convenience benchmark. Independent scene-level population uncertainty and paired superiority remain unestablished; the valid question-level sample count is not itself an error.



### Proposed correction

Report sequence/location units and appropriate grouped uncertainty without calling all questions independent scenes.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 12: Human and LLM judging require distinct reliability evidence

Assessment: needs_evidence; impact: needs_evidence



Source: Official PDF: Section 5.1; Appendices C.2-C.4, D.2-D.3 and K (annotations, object referral, human evaluation and reasoning examples).



### Source claim (paraphrase)

Appendices C--D describe annotation correction, human responses and a partly LLM-based object-referral metric.



### Analysis

The annotation procedure is detailed and includes manual correction, but the paper does not quantify independent agreement or positional/timing uncertainty at the \(0.1\) m scale used by the finest distance thresholds. A doubly reviewed subset would allow sensitivity analyses around annotation uncertainty and category boundaries. The object-referral metric also relies partly on LLM judging; its judge version, prompt, alias rules, and audited disagreement cases should accompany results. These are validation requests, not evidence that the ground truth or judge is wrong. The human score aggregates six evaluators who received disjoint shuffled portions of the questions, rather than six ratings per question. It is a useful task baseline but does not establish inter-rater reliability. Qualitative reasoning displays are illustrative explanations; because the standard proprietary-model prompt asks for constrained answers, any separate explanation-generation procedure should be stated before interpreting those narratives as faithful traces of the originally scored inference.



### Finding and scope

The available material identifies a scope or evidence gap; it does not prove that the reported empirical effect is false.



### Proposed correction

Document independent annotation agreement and LLM-judge version, prompt and disagreement audit.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 13: The demonstrated planar task and component timing bound deployment claims

Assessment: needs_evidence; impact: needs_evidence



Source: Official PDF: Appendices C.3 and D.3 (planar task); Appendix G, pp. 36-37 (component timing); conclusion and Appendix I.



### Source claim (paraphrase)

The task templates use horizontal-plane distances, while broader spatial and efficiency interpretations appear in the conclusion and Appendix G.



### Analysis

The benchmark's distance templates and human guidelines explicitly use points projected onto the horizontal plane. Thus the 2D map and horizontal distance evaluation are deliberate, not a hidden mathematical error. However, success on these tasks establishes scene-grounded planar relations, not arbitrary vertical or full 3D reasoning. Generalization to outdoor/driving acoustics, multiple overlapping sources, new microphone geometries, and other camera trajectories remains untested in the reported experiments. Efficiency is likewise a partial-stage analysis. Appendix G reports approximately \(0.52\) s/frame/object for Seg and \(0.44\) s/frame for depth. The Seg number alone corresponds to about \(66.6\) seconds of serial processing for \(128\) frames and one object; the paper should clarify whether the separately quoted depth time is included before adding them. End-to-end latency depends on reuse, parallelism, object count, clip duration, and AV-LLM latency. A streaming latency/throughput experiment is needed to substantiate a deployment claim, even though the system can clearly trade frame count for accuracy.



### Finding and scope

The available material identifies a scope or evidence gap; it does not prove that the reported empirical effect is false.



### Proposed correction

Limit claims to the planar benchmark and measured component times; complete deployment latency remains unmeasured.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.
