# Segment then Splat: Unified 3D Open-Vocabulary Segmentation via Gaussian Splatting



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current release retains small-mask encoding, correspondence, pruning and query discrepancies. Threshold filtering also does not ensure disjoint pixel ownership; the separate Boolean-IoU allegation remains rejected.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: The small-mask byte encoding removes foreground before supervision

Assessment: supported; impact: minor



Source: Section 3.4, Eq. (8), PDF p. 6; released scene/dataset_readers.py, lines 162–175.



### Source claim (paraphrase)

Section 3.4, Eq. (8), PDF p. 6, includes small-object supervision. Released scene/dataset_readers.py, lines 162–175, thresholds a Pillow mode-L mask by whether each pixel exceeds \(128\). utils/general_utils.py, lines 23–25, divides the resulting bytes by \(255\), and utils/camera_utils.py, lines 46–48, applies threshold \(0.5\). train.py skips small masks that become empty.



### Analysis

The mode-L threshold stores foreground bytes as \(1\), not \(255\). Dividing by \(255\) therefore gives \(1/255\), below the next threshold \(0.5\). Foreground inputs such as \(129\) and \(255\) are erased before the small-mask supervision loop. This is deterministic for the inspected reader, while its role in historical table-producing runs remains unidentified.



### Finding and scope

The current byte reader deterministically erases small foreground; exposure in historical scene training and the corresponding mIoU change are unknown.



### Proposed correction

Preserve the byte convention by returning \(255\) for foreground and \(0\) otherwise before division by \(255\), or use a consistently Boolean path.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 2: Initialization does not consistently preserve frame, granularity, and object identity

Assessment: supported; impact: minor



Source: Section 3.3, Eq. (4), PDF p. 5; released helpers/object_specific_initialization.py.



### Source claim (paraphrase)

Section 3.3, p. 5, assigns an object ID using the visible point’s mask region and merges duplicate object tracks using the means of their Gaussian centers and colors; Equation (4) describes that distance. The following three subcases concern the released helpers/object_specific_initialization.py. They are separate failure mechanisms within one correspondence invariant. The README’s existing To be verified status applies directly to this helper.



### Analysis

Three distinct identity mechanisms fail: a training-only frame counter indexes masks loaded for all frames; small-object means use middle-object membership; and merged masks are renumbered while Gaussian IDs retain old labels. Each can associate valid geometry with the wrong supervision independently of mask encoding.

With sorted frames \(0,1,2\), only \(0,2\) used for training, the second accepted observation reads frame \(1\) masks because the counter advances only for training frames. A point owned by object \(0\) in both actual training frames can therefore be assigned object \(1\).

For small groups with centers \[0.005,10.005,20.005,-9.795\], nested into middle groups \(\{0,1\}\) and \(\{2,3\}\), the wrong selector compares middle centers \(5.005,5.105\). Colors \[(0,0,0),(2,2,2),(1,1,1),(3,3,3)\] yield implemented distance \(0.1+20\sqrt3/255<0.5\), whereas the intended first two small groups give \(10+40\sqrt3/255>0.5\).

Merging initial IDs \(0,1\) among \(0,1,2\) leaves point IDs \((0,0,2)\), but compacted mask folders are \(0,1\). The surviving last object thus has incompatible identifiers.



### Finding and scope

The inspected correspondence helper violates those source-level identity contracts. Its own README marks it ‘To be verified’; this is affirmative reason not to infer that the published experiments used the same incomplete helper.



### Proposed correction

Align frame keys, select membership from the matching granularity, and apply one explicit merge/reindex map to both masks and Gaussian IDs.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 3: The Gaussian persistence loop cancels every pruning proposal

Assessment: supported; impact: minor



Source: Section 3.4, PDF p. 6; released scene/gaussian_model.py, GaussianModel.densify_and_prune, lines 387–421.



### Source claim (paraphrase)

Section 3.4, PDF p. 6, protects an object against complete pruning. Released scene/gaussian_model.py, GaussianModel.densify_and_prune, lines 387–421, clears an object's pruning flags when its original count is below \(1000\). Otherwise it compares that count with a new sum over the same unfiltered object membership and clears the flags when they agree.



### Analysis

The persistence loop compares each object's original count with a fresh sum over that same unfiltered membership, an identity. It consequently clears every nonempty object's pruning flags, even for \(1001\) points proposing one deletion with \(1000\) survivors. The loop does not implement a test of the number of proposed survivors.



### Finding and scope

The current membership-count identity cancels all valid scalar-ID pruning proposals; its full-scene memory and accuracy effects remain unmeasured.



### Proposed correction

Count proposed survivors \(r_g=\sum_{j\in S_g}(1-P_j)\) and explicitly enforce the selected minimum. Comparing the original membership count with itself cannot detect extinction.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 4: The query helper changes both the score and eligible object levels

Assessment: supported; impact: minor



Source: Granularity definitions, PDF p. 4; Section 3.5, Eqs. (9)–(11), PDF p. 7.



### Source claim (paraphrase)

Section 3.5, Equations (9)–(11), p. 7, averages per-view object embeddings, embeds the text query, and selects the object with maximal cosine similarity. The method also introduces large, middle, and small granularities on p. 4.

In helpers/evaluation.py, extract_CLIP_embeddings at line 72 calls model.encode_image and averages the resulting features. calculate_IoU calls model.encode_text at line 143 and forms matrix products at lines 148–149, with no normalization of these mean embeddings. The small-level similarity and selection are commented out at lines 150 and \(156\)–158. The final branch at lines 165–170 compares only large and middle candidates.



### Analysis

For query \((1,0)\), raw dot products rank object \((2,2)\) above \((1,0)\), with scores \(2\) and \(1\). Cosines reverse that order, giving \(1/\sqrt2\) and \(1\). Unnormalized averaged image embeddings therefore do not implement the stated cosine ranking. Independently, omitting small-level candidates prevents selecting a legitimate small-level winner.



### Finding and scope

Unnormalized means can reverse cosine rankings and small candidates are excluded, without a measured benchmark-query failure rate.



### Proposed correction

The proposed correction normalizes final nonzero object means and query, and evaluates the explicitly declared candidate granularities with identities attached.

A local correction or qualification is proposed where specified; author adoption is not established.



## Problem 5: IoU threshold filtering alone does not guarantee unique pixel ownership

Assessment: supported; impact: minor



Source: Section 3.2, PDF p. 5.



### Source claim (paraphrase)

The source describes IoU-based mask filtering as ensuring one object per pixel at a granularity.



### Analysis

Masks \(\{0,1,2,3\}\) and \(\{3,4,5,6\}\) overlap at one pixel but have IoU \(1/7<0.5\), so both survive the stated threshold. Filtering by overlap magnitude does not guarantee disjoint pixel ownership. A later single-valued assignment also does not make the input masks themselves disjoint.



### Finding and scope

Supported scope qualification of the uniqueness guarantee; no arbitrary semantic overlap-resolution rule is invented.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.

- The Boolean-mask IoU denominator allegation is not retained: Boolean addition on the identified path represents union. The cumulative stage order agrees with the paper; the object L1/DSSIM choice is a reproduction qualification, not an additional benchmark refutation.
