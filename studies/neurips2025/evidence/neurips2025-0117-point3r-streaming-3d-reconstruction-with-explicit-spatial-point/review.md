# Point3R: Streaming 3D Reconstruction with Explicit Spatial Pointer Memory



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The hierarchical positional construction introduces absolute-position cross terms; odd-width released rotary blocks fail the rotation contract. Memory fusion also uses a different threshold point set than the paper.



## Scope

Rapid current-version reassessment of every substantive concern in the supplied LaTeX report: the implicated paper passages and relevant author-released source paths were inspected, existing proposed corrections were briefly checked, and impact was calibrated to the demonstrated scope. No author-provided or historical verification program was executed.



## Problem 1: Separate averaging of rotated queries and keys introduces absolute-position cross terms

Assessment: supported; impact: minor



Source: Eqs. (13) and (15), PDF pp. 5–6; Appendix A.2 and Eq. (20), PDF p. 15.



### Source claim (paraphrase)

Equation (13), PDF p. 5, uses ordinary RoPE's relative-position rotation. The hierarchical extension in Eq. (15), PDF p. 6, averages the rotated embeddings over frequency bases; Appendix A.2, Eqs. (20)–(21), PDF p. 15, describes the resulting attention as relative-position rotation.



### Analysis

Averaging rotated queries and keys separately gives terms \(\exp(i(\theta_a p-\theta_b r))\) for every frequency pair. Translating both positions by \(c\) multiplies a cross term by \(\exp(i(\theta_a-\theta_b)c)\), which is generally not one. Ordinary same-frequency cancellation therefore does not remove absolute-position dependence from the averaged construction.

Using the stated four bases, head dimension \(24\), channel \(t=1\), and content \(q=k=1\), frequencies are approximately \[(0.5623413252,0.3162277660,0.1778279410,0.1)\]. At equal positions \(p=r=c\), attention is \[\left|\frac14\sum_{a=1}^4e^{i\theta_ac}\right|^2,\] equal to \(1\) at \(c=0\) but approximately \(0.9694978734\) at \(c=1\). Relative displacement and content are unchanged. This limits a pure-relative reading; the weaker statement that the embedding contains relative information is not disproved.



### Finding and scope

A common translation changes the averaged encoding’s dot product, limiting pure-relative interpretation; mixed absolute/relative information can still be useful empirically.



### Proposed correction

Average matched-base query/key dot products, or concatenate the base-specific rotated copies with scaling \(1/\sqrt h\). Their dot product is then the average of \(q\bar k e^{i\theta_a(p-r)}\), which preserves relative invariance algebraically. This architecture change has no demonstrated reconstruction gain.

The existing local mathematical or consistency proposal remains applicable to current v2/current-head source; no author adoption is established.



## Problem 2: The configured 21/21/22 real-coordinate split does not implement three rotary blocks

Assessment: supported; impact: minor



Source: Eqs. (12)–(14), PDF p. 5; Appendix A.2; released stage 1–3 configurations with dimension 768 and 12 heads.



### Source claim (paraphrase)

Equations (12)-(14), p. 5, use complex rotations for position embedding. Appendix A.2 explicitly pairs real coordinates to form complex query/key entries. The final-supplement configuration files config/stage1.yaml, stage2.yaml, and stage3.yaml all set decoder dimension \(768\) and \(12\) heads, giving \(64\) real coordinates per head.

The corresponding croco/models/pos_embed_con.py defines RoPE3DContinuous. Its forward method splits a nondivisible head into widths \(\lfloor64/3\rfloor,\lfloor64/3\rfloor,64-2\lfloor64/3\rfloor\), namely \(21\), \(21\), and 22. rotate_half calls chunk(\(2\)) and concatenates the negative second chunk with the first. get_angle_emb duplicates the frequency vector and truncates it to the requested width. The same substantive implementation is present in the current repository. croco.py instantiates this class for RoPE3D100; the decoder attention code passes per-head tensors to it.



### Analysis

The configured \(64\)-real-coordinate head is split into widths \((21,21,22)\). The odd-width blocks have unequal half lengths, so chunking and concatenation no longer align coordinate pairs with duplicated sine/cosine frequencies. They are not collections of orthogonal two-dimensional rotations. Even-width single-base blocks and position zero supply matching controls; this does not imply failure for every width or input.

For the produced width \(21\), input \(e_0\), coordinate \(\pi/2\) and base \(10\), rotate_half moves the active entry to coordinate \(10\), whose sine frequency is \(10^{-20/21}\). The output norm is \(\sin((\pi/2)10^{-20/21})\approx0.174386468\), rather than \(1\). This isolates an individual purported rotation, independently of deliberate cross-base averaging.



### Finding and scope

The actual head configuration produces odd axis widths that violate the advertised rotation property; trained-model compensation and benchmark impact are unmeasured.



### Proposed correction

Allocate complete real/imaginary pairs on every axis; for a \(64\)-coordinate head, real widths such as \((22,22,20)\) permit pairwise rotations. Verify norm preservation per base, and separately address the average-before-product issue. Changed allocation requires model evaluation before claiming recovered accuracy.

The existing local mathematical or consistency proposal remains applicable to current v2/current-head source; no author adoption is established.



## Problem 3: The memory-fusion threshold uses different point sets in Eq. (19) and the released code

Assessment: supported; impact: minor



Source: Memory-fusion description, PDF p. 5; Appendix A.1, Eq. (19), PDF p. 15.



### Source claim (paraphrase)

Equation (19), Appendix A.1, p. 15, defines the threshold as the Euclidean norm of the existing memory’s coordinate ranges divided by axis constants, each set to 20. Its explanatory sentence identifies the coordinates as those of the memory \(\mathcal M_{t-1}\). The fusion description on p. 5 then uses this threshold to decide whether an incoming pointer should replace a nearest memory entry or be appended.

The final supplement dust3r/point3r.py, around lines 590-595, instead takes coordinate ranges over the concatenation of existing memory pointers and current incoming pointers. The current repository does the same in src/dust3r/point3r.py, lines 688-693.



### Analysis

For existing memory x-coordinates \(\{0,1\}\) and incoming coordinates \(\{2,100\}\), with common positive depth and other coordinates fixed, memory-only range gives threshold \(1/20=0.05\), so both incoming points append. Current code uses the union range, giving \(100/20=5\); distance \(1\) now merges the incoming point at \(2\) into the old point at \(1\), while \(100\) appends. The same nearest distances therefore produce four entries under the written rule and three under the release.



### Finding and scope

Changing the threshold’s point set changes a valid memory update; this is a reproducibility discrepancy without an established accuracy direction.



### Proposed correction

Either compute the range from existing memory to match the equation, or document the union of existing and incoming pointers to match current code. Neither consistency option is established as scientifically superior.

The existing local mathematical or consistency proposal remains applicable to current v2/current-head source; no author adoption is established.



## Limits

- No author-provided program, training procedure, model inference or wet-lab experiment was executed in this review.

- Historical execution results are retained only with that attribution; a source-level defect alone does not identify the program or configuration used for the published experiments.

- No author contact, adoption, independent human scientific review or novelty determination is established.

- The findings apply only to the identified claims, source versions and stated assumptions; they do not certify or invalidate the entire paper.
