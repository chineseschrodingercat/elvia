# GeneFlow: Translation of Single-cell Gene Expression to Histopathological Images via Rectified Flow



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The central noisy interpolation target has an incorrect path derivative, which determines Major as a formal flow-matching derivation error. Abstract bijection and velocity-energy interpretations require narrower language. Local source defects and unresolved experimental impacts remain distinct; reported FID advantages and reader preference are not refuted.



## Scope

Claim-focused reading of the identified paper and author-released materials. The arguments below distinguish mathematical contradictions, version-specific implementation defects and unresolved empirical consequences. No author code was executed in this revision.



## Problem 1: The noisy interpolation derivative is wrong in the paper and incomplete in the released target

Assessment: supported; impact: major



Source: Paper p. 5, Eqs. (8)–(10), preceding definition of epsilon_t rectified/rectified_flow.py:53–98, especially 78–91 rectified/rectified_train.py:314–317



### Source claim (paraphrase)

Eq. (\(9\)) identifies the velocity target with the derivative of the noisy interpolation path.



### Analysis

The bridge adds \(\epsilon_t=(1-t)\sigma z\), with \(\sigma=0.05\). Differentiating its plus sign gives \(+d\epsilon_t/dt=-\sigma z\). Equation (\(9\)) instead subtracts \(d\epsilon_t/dt\), giving \(+\sigma z\). The released sample_path omits the entire derivative of the auxiliary noise, returning only the derivative of the sinusoidal interpolation. These are three different targets. The code comment describes its incomplete target as the path derivative. Its sigma_t return value, derived from \(\sigma_{\min}=0.002\) and \(\sigma_{\max}=80\), is not consumed by the training loss; the actual extra noise amplitude is \(0.05(1-t)\). Thus the p. 5 claim that the separate \(0.002\)–\(80\) schedule controls trajectory noise is also unsupported by this implementation.



### Finding and scope

The exact flow-matching justification does not apply to the written/released target. This is a definite mathematical issue even if the numerical effect of \(\sigma=0.05\) turns out small in a corrected experiment. A sinusoidal scalar interpolation without the additional z term can trace a geometrically straight line; changing linear time to sinusoidal time is not itself an error. No assertion is made that this defect alone explains the reported image-quality differences.



### Proposed correction

Use \(v_*=s'(t)(x_1-\eta)-\sigma z\), where \(s(t)=\sin(\pi t/2)\), and retain the sampled z explicitly. Match the sampler's initial marginal \(N(0,(1+\sigma^2)I)\), or remove the auxiliary perturbation and use a consistently defined bridge/prior. Remove the unused sigma schedule from the description or incorporate a mathematically derived schedule into both bridge and target. Retrain before making empirical claims about the corrected objective.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: The advertised spatial regularizer contributes no gradient in the released training branch

Assessment: supported; impact: minor



Source: Paper pp. 7–8, spatial regularization claim; pp. 23–27, Appendix E, Eq. (11) rectified/rectified_train.py:335–364 src/spatial_graph_loss.py:220–282 and 284–362



### Source claim (paraphrase)

The spatial regularizer is intended to constrain the trained generator through the loss.



### Analysis

The training routine detaches approx_generated before evaluating either spatial loss, disconnecting the spatial term from model parameters. The segmentation branch separately converts to NumPy and constructs a new tensor without autograd, so removing only the caller detach would not make that branch differentiable. This identifies the source graph; the historical paper-training version remains unknown.



### Finding and scope

The current branch cannot enforce the claimed spatial training constraint through gradients. Improvements attributed specifically to this regularizer require fresh evidence with a functioning loss. The optional spatial stage can still change training duration, early stopping, or checkpoint selection. Therefore it is incorrect to claim two complete runs must have identical weights or outputs. The paper-run configuration and whether its historical code had the same detach remain unverified.



### Proposed correction

Keep the generated-image branch attached for the differentiable Sobel/texture surrogate. Use a path-consistent differentiable endpoint estimate or explicitly justify an alternative training surrogate. A bridge-consistent correction derives \(\widehat x_1\) from the sinusoidal bridge without an unstable division near \(t=1\). For segmentation, use a differentiable soft-mask/feature network if this is intended as a training loss; otherwise describe it as evaluation or model selection. Demonstrate a nonzero gradient norm and an actual ablation after retraining.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: The active DOPRI5 solver has an incorrect embedded stage and does not enforce tolerance or endpoint completion

Assessment: supported; impact: minor



Source: Paper p. 5, fifth-order adaptive integration claim rectified/rectified_flow.py:198–270, 272–297, 331–368 rectified/utils.py:35–68



### Source claim (paraphrase)

The paper describes an adaptive fifth-order integration procedure for generation.



### Analysis

The first six Dormand–Prince stages and fifth-order weighted update are correct. Stage seven is not: lines 249–251 rebuild the sixth-stage state using a[\(5\)], rather than evaluate the derivative at the fifth-order endpoint. The embedded fourth-order estimate is therefore wrong. Independently, every proposal is accepted even when normalized error exceeds one. The loop stops after num_steps and returns a clamped sample even when \(t<1\); the final log labels this completed generation. Both single- and multi-cell generation helpers use this solver, so it is an active path.



### Finding and scope

The released generator does not provide the adaptive accuracy/completion guarantee invoked in the paper. Sampling-step budgets are also not equivalent to network evaluations: each attempt here costs seven calls. The fifth-order proposal itself is preserved correctly; this audit does not call the entire tableau wrong. Actual terminal times of the released checkpoints were not measured. A corrected implementation must be tested on those fields before assigning an empirical effect size.



### Proposed correction

Use the correct seventh stage \(f(x_5,t+h)\), reject proposals whose scaled error exceeds tolerance, cap the accepted endpoint at \(t=1\), and raise or report incomplete generation if the attempt budget is exhausted. Prefer a maintained solver or a separately verified reference; report accepted/rejected steps and function evaluations.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: Unsorted cell IDs invalidate reproducible splits across training and evaluation processes

Assessment: supported; impact: minor



Source: src/dataset.py:40–43, CellImageGeneDataset.__init__ rectified/rectified_main.py:279–285 rectified/rectified_evaluate.py:395–400 src/utils.py:249; train.sh and eval.sh



### Source claim (paraphrase)

The released training and evaluation workflow should recreate the same biological-cell split.



### Analysis

CellImageGeneDataset computes a set intersection and converts it directly to a list. Python process hash randomization changes the order of string IDs. Training and standalone evaluation then independently recreate an \(80/20\) split of integer indices with Torch seed 42. Identical integer-index partitions do not imply identical biological-cell partitions when the underlying order changes. No PYTHONHASHSEED setting or persisted split-ID manifest was found in the released workflow.



### Finding and scope

The released standalone workflow can evaluate on cells already used for training. This is a much stronger concern than ordinary spatial correlation because it can involve the identical named cell and its image. The measured \(77.5\%\) belongs to the synthetic reproduction, not to the paper's actual data. Actual contamination requires the original process settings and cell-ID manifests. This specific set-order mechanism is in the single-cell class; the patch class preserves mapping iteration order and should not automatically be assigned the same bug.



### Proposed correction

Sort the common cell IDs deterministically, then save training, validation, and test cell IDs in versioned manifests and load those IDs during evaluation. Include dataset/source hashes and reject missing or changed IDs. Recompute results on untouched test IDs. Sorting alone fixes ordering but does not solve overlapping crops or validation reuse, addressed separately in F 05.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: The released evaluation protocol does not implement the stated folds or establish independent biological generalization

Assessment: supported; impact: minor



Source: Paper pp. 5–7, Sections 4.1–4.2; Table 4; Appendix B.3 p. 17 rectified/rectified_main.py:279–285 rectified/rectified_evaluate.py:395–414 rectified/rectified_train.py:649–738 utils/prepare_xenium_data.py:1071–1086; src/dataset.py:397–998



### Source claim (paraphrase)

The manuscript describes three-fold evaluation and uses the results to discuss biological generalization.



### Analysis

The paper states three-fold cross-validation within each dataset. Public training/evaluation uses a single random \(80/20\) item split, and checkpoint selection minimizes the validation loss on that \(20\)%. Standalone evaluation recreates that same \(20\%\) rather than an independent test set. The split is at cell/patch level, including after combining HEST samples, without a patient, slide, or spatial-block grouping rule. The paper explicitly creates \(256\times256\) patches with \(100\)-pixel overlap and uses unmasked cell-centered crops. Those are correlated observations, not independent donors.



### Finding and scope

Current released results cannot be interpreted as clean patient-level generalization or a faithful reproduction of the stated three-fold experiment. Validation reuse can bias selected-model estimates, and overlapping crops can further inflate apparent generalization. The paper does contain a genuine cross-dataset experiment (Table 4) and explicitly says those models use \(126\) common genes in Appendix B.3. It would be incorrect to say no transfer experiment exists, or to allege that differing gene dimensions alone invalidate it. Original fold leakage and the donor relationship of C1/C2 remain unknown; absence of a manifest is not proof that the historical experiment used the current script.



### Proposed correction

Publish immutable grouped fold manifests and a separate model-selection set, or use nested cross-validation. Split source patients/slides before cropping. If the scientific goal is within-slide interpolation, state that goal and use spatial blocks separated by a buffer at least as wide as the crop footprint. For HEST, report sample/organ-level held-out evaluation. Quantify exact shared pixels/cell IDs across partitions and report donor-level rather than crop-level uncertainty for population claims.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: Table 1 does not reconcile its C2 cell-type counts with its total

Assessment: supported; impact: minor



Source: Paper p. 5, Table 1; p. 15, cell-type annotation description



### Source claim (paraphrase)

Table 1's cell-type subtotals and total describe one reconciled C2 population.



### Analysis

The C2 column lists endothelial \(4\,182\), epithelial \(4\,203\), fibroblast \(9\,694\), macrophage \(12\,088\), melanoma \(33\,309\), and T cells \(15\,272\), summing to \(78\,748\), while the displayed total is \(70\,178\). The text describes clustering and cell-type annotation without explaining overlapping categories or different filtering stages in this table. The fresh current publisher PDF retains these values.



### Finding and scope

The population underlying the reported experiments is not reconstructable from Table 1. Downstream class balance and subgroup comparisons should not be inferred from the unreconciled counts. This does not establish fabricated data. The current 10x Genomics pages also have version-specific raw counts, so differences between those pages and a processed release are not automatically errors. The confirmed issue is internal consistency of the paper's displayed C2 population definitions.



### Proposed correction

Provide a flow diagram or tabulation of raw, quality-controlled, image-matched, classified, and split counts for each dataset. If categories overlap or totals refer to different stages, label that explicitly. Otherwise correct the affected total or category counts from a versioned cell-ID manifest.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: Universal performance claims contradict Table 2 SSIM values

Assessment: supported; impact: minor



Source: Paper abstract p. 1; p. 6 narrative and Table 2; Appendix B.2 p. 16



### Source claim (paraphrase)

The main text describes rectified flow as outperforming the diffusion baseline across all metrics.



### Analysis

The main text describes rectified flow as outperforming the diffusion baseline across all metrics. In Table 2, diffusion has higher SSIM for P1 single (\(0.20\) versus \(0.17\)), C1 multi (\(0.30\) versus \(0.28\)), and C2 single (\(0.36\) versus \(0.35\)). Rectified flow has better FID and Inception feature distance in all six rows. The p. 6 description of a \(3\)–\(6\)-fold FID improvement is also not the full displayed range.



### Finding and scope

The all-metrics statement should be corrected. The FID and feature-distance advantage remains a real reported result and should not be erased by the SSIM correction. Appendix B.2 already acknowledges that diffusion can match or exceed SSIM. That is evidence of appropriate nuance in the paper, but it does not repair the inconsistent main-text wording. Overlapping standard deviations do not, by themselves, prove no difference.



### Proposed correction

State that rectified flow improves the displayed FID/feature-distance measures while SSIM is mixed. Report the actual range if a ratio summary is retained. Use paired confidence intervals on independently held-out units before making inferential superiority claims.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 8: The component ablation table favors removing gene attention on most reported metrics

Assessment: supported; impact: minor



Source: Paper pp. 7–8, ablation discussion and Table 6; Appendix B.2/Figure 8 p. 16



### Source claim (paraphrase)

The component-removal discussion attributes performance declines to removing the encoder components.



### Analysis

The prose argues that removing components causes performance declines. In Table 6, removing gene attention lowers UNI2-h FID from \(39.27\) to \(26.46\) and improves UNI2-h similarity, circularity, solidity, and all three spatial similarities. Full rectified wins only Inception feature distance (\(14.50\) versus \(14.89\)) and eccentricity similarity (\(0.964\) versus \(0.959\)). Other component-removal columns also show favorable changes on multiple metrics. The separate simple-encoder experiment is a different comparison.



### Finding and scope

The table does not justify the asserted empirical necessity of all encoder components. A simpler ablated model may be preferable under several of the paper's own quality criteria. The data do support that the more elaborate encoder can improve FID relative to the fully simplified encoder. No significance level can be assigned to Table 6 differences from the reported summaries alone, and improved attention ablations do not imply gene conditioning is useless.



### Proposed correction

Rewrite the conclusion as a performance/interpretability tradeoff rather than a universal advantage. Re-evaluate matched seeds, training budgets, and independent folds for full, attention-ablated, and simple encoders. Report parameter count, speed, and uncertainty, and select the architecture according to a predeclared objective. If interpretability is the reason to retain attention, validate that property directly.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 9: A conditional noise-to-image flow does not establish a bijection between expression and images

Assessment: supported; impact: minor



Source: Paper abstract p. 1; Methods p. 3; Figure 2 and Sections 3.1–3.2



### Source claim (paraphrase)

A conditional noise-to-image flow does not establish a bijection between expression and images.



### Analysis

The abstract describes an expression/image bijection, but Methods constructs \(I=\Phi_X(\eta)\): a noise-to-image map for fixed expression condition \(X\). ODE uniqueness can establish invertibility between \(\eta\) and \(I\) under its regularity assumptions; it does not establish an inverse between \(X\) and \(I\). Multiple expression profiles may give the same conditional image law, and one expression profile may generate many images.



### Finding and scope

The method can remain a useful conditional generator. The abstract's bijection argument does not resolve the biological many-to-one inverse problem. Methods p. 3 itself largely states the correct conditional-noise interpretation. This finding is about the stronger abstract/conceptual claim, not a proof that conditional generation is mathematically impossible. A dimension argument alone is insufficient because the intrinsic biological manifold dimensions are not established.



### Proposed correction

Describe the model as a conditional generative distribution p_theta(I|X). Restrict invertibility statements to a sufficiently regular continuous ODE at fixed X and distinguish numerical integration/postprocessing. Use posterior uncertainty, cycle tests where justified, or independent expression recovery experiments for any stronger cross-modal claim; do not infer them from the sampler type.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 10: The conditioning representation cannot identify a particular cell arrangement or absolute replicated cell count

Assessment: supported; impact: minor



Source: Paper pp. 3–4, Eqs. (1)–(7); Appendix A p. 15; Appendix D pp. 20–22 src/multi_model.py:169–253 and 342–360



### Source claim (paraphrase)

The gene-set condition is used to support reconstruction of multicell histological structure.



### Analysis

The multi-cell encoder transforms each gene vector and forms normalized attention-weighted means across cells. It receives no cell coordinates. num_cells masks padding; it is not passed as a separate count embedding to the UNet. Permuting cells leaves the embedding unchanged. Replicating every cell the same number of times also leaves normalized weighted means unchanged. The single-cell model is conditioned on one cell's expression while the unmasked image contains its neighborhood.



### Finding and scope

This bounds the biological meaning of spatial reconstruction and perturbation claims. Image realism does not imply recovery of the actual cell arrangement or neighbor relationships. Permutation invariance is desirable for a set encoder and is not a bug. The limitation applies to identifying a particular arrangement from insufficient inputs, not to learning plausible conditional image distributions. Real expression values can correlate with density, but that does not remove the constructed ambiguity.



### Proposed correction

If exact spatial reconstruction is the objective, include aligned coordinates, a spatial graph or layout condition, and explicit density/count information, and evaluate consistency under permutations of storage order. If expression-only synthesis is the objective, define a distribution over plausible arrangements, quantify diversity/uncertainty, and avoid treating a single generated arrangement as an observed biological interaction.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 11: Velocity-energy gradients do not measure endpoint morphology influence

Assessment: supported; impact: minor



Source: Paper pp. 8–9, Section 4.3; Appendix C pp. 19–20 src/utils.py:449–561, especially 506–535



### Source claim (paraphrase)

Velocity-energy sensitivity is interpreted as gene importance for the generated morphology.



### Analysis

The statistic differentiates \(\|v_\theta(x,t;X)\|^2\) with respect to genes, rather than an endpoint morphology \(m(x(1))\). For constant velocity \(v=X\), initial point zero and identity endpoint readout, \(x(1)=X\): the energy derivative is \(2X\), zero at \(X=0\), while the endpoint derivative is one. Full endpoint sensitivity generally requires the trajectory sensitivity equation. The released routine also queries standard Gaussian states at every time rather than the time-dependent bridge/trajectory. This supports a narrower exploratory interpretation, not a claim that every identified gene is irrelevant.



### Finding and scope

The ranking can serve as an exploratory model-internal heuristic, but its stability/enrichment does not establish which genes causally or even endpoint-wise control morphology. The paper itself frames some downstream uses as hypotheses and candidates for experimental validation; that is appropriate. The counterexample does not show every identified gene is biologically irrelevant, only that the proposed statistic lacks the claimed general interpretation.



### Proposed correction

For model sensitivity, differentiate a specified image feature m(Phi_X(eta)) through a differentiable ODE solve or use controlled finite differences with common noise and an appropriate gene-expression perturbation scale. Sample relevant trajectory states if reporting velocity sensitivity and name that statistic precisely. Compare with input scaling, expression abundance, cell-type-only baselines, and gene shuffling. Reserve causal or regulatory claims for intervention data or explicitly justified causal assumptions.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 12: Pathway enrichment and overlap statistics need assay-aware null models and complete reporting

Assessment: supported; impact: minor



Source: Paper pp. 8-9, Figure 4; Appendix C, pp. 19-20, Figure 13 and Table 10; author-described Xenium panel selection.



### Source claim (paraphrase)

The overlap/enrichment results are used as biological evidence for the identified gene sets.



### Analysis

The paper enriches \(34\) genes shared among the top \(50\) in its two panels. Assay-specific eligible genes, complete rankings, library versions and the family of overlap tests are not fully specified. The 10x Genomics panel already targets skin cell types and cancers, so panel selection matters to the null. Table 10 calls pathways significant but includes adjusted \(P=0.0918\), and describes ten pathways while showing six. Adjusted values are reported, and several meet \(0.05\); a missing correction is not established merely because a complete analysis record is absent.



### Finding and scope

The current enrichment is hypothesis-generating evidence whose statistical calibration and independence from panel selection are unresolved. The significant genes/pathways should not be treated as independent proof of causal morphological mechanisms. No incorrect background or missing correction is asserted as a confirmed historical failure merely because it is unreported. The paper does report adjusted P values for enrichment, and several displayed pathways meet 0.05. The narrower confirmed errors are the ambiguous significance description and the six-versus-ten caption.



### Proposed correction

Publish ranked genes and all contingency tables. Use the measured, quality-controlled eligible panel genes as the enrichment universe, or state and justify a different sampling model. For unequal panels, use a common eligible universe with consistent ranking or a panel-specific permutation null. State the multiple-testing procedure and threshold, distinguish raw from adjusted P, and label coagulation accordingly. Compare enrichment against rankings driven by expression and cell-type composition.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 13: The released cell-type accuracy is degenerate for the documented eight-image evaluation batch

Assessment: supported; impact: minor



Source: rectified/utils_uni2h.py:195–234 and 295–303 README.md, custom evaluation batch_size 8



### Source claim (paraphrase)

The released cell-type accuracy routine is used as a biological agreement diagnostic.



### Analysis

classify_cell_types_uni2h assigns every sample label zero whenever a batch has fewer than ten items. Real and generated embeddings are classified separately and their integer labels are compared as if they were biological cell classes. Thus eight unrelated generated embeddings receive perfect agreement with eight real embeddings by construction. For larger batches, independent PCA/scaling/KMeans fits still have arbitrary cluster-label identities and are not trained cell-type classifiers.



### Finding and scope

The released evaluation summary can report perfect biological classification for unrelated inputs. This affects the software's advertised biological-validation output. Cell-type accuracy is not a reported column in Tables 2–6, so this audit does not use the defect to invalidate those particular numbers. The README's eight-image example is the relevant configuration; the CLI's numerical default need not be eight for the counterexample to matter.



### Proposed correction

Use an externally validated, frozen cell-type classifier with a shared label vocabulary; fit any preprocessing only on training data. If measuring unsupervised clustering similarity, use a permutation-invariant statistic and accurately name it. Small batches should return unavailable metrics rather than perfect biological accuracy. Remove this statistic from composite biological plausibility until repaired.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 14: Several biological similarity statistics discard the structure they are used to support

Assessment: supported; impact: minor



Source: Paper pp. 7–8, Tables 5–6; rectified/utils_uni2h.py:123–193, 237–280, 306–340



### Source claim (paraphrase)

The named embedding/spatial statistics are used to support cellular organization and biological similarity.



### Analysis

UNI2-h embedding similarity is one minus a scalar KS statistic after flattening all feature coordinates across images. It loses coordinate identity and multivariate structure. The reported spatial complexity and feature magnitude reduce each embedding to its standard deviation and mean absolute value, without direct cell coordinates or a spatial correspondence test. Nuclear features are extracted from Otsu-thresholded grayscale connected components in this evaluator, not validated nucleus instances. Those are legitimate image statistics when named accurately, but do not by themselves demonstrate cellular organization or diagnostic fidelity.



### Finding and scope

The high scalar similarity values in Tables 5–6 have a narrower interpretation than the prose implies. They cannot on their own clear the identifiability and spatial-reconstruction limitations. The paper also reports UNI2-h FID, which retains means and covariances; the flattened-metric objection does not apply to that separate statistic. A simple Otsu method is not automatically invalid, but its accuracy for these stained nuclei is unestablished without annotations.



### Proposed correction

Retain pooled multivariate feature distances and add paired feature/morphology measures with a declared target. Validate the nucleus segmentation against independently annotated nuclei or an appropriate pretrained model on these images. Evaluate cell count, position, type, shape, adjacency and uncertainty at image and sample level. Report embedding scalar summaries as descriptive diagnostics unless their relationship to spatial organization is empirically validated.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 15: GLCM angles are supplied in degrees to an API that expects radians

Assessment: supported; impact: minor



Source: rectified/utils_uni2h.py:258; paper Tables 5–6 spatial energy Official scikit-image graycomatrix documentation, angles parameter



### Source claim (paraphrase)

The texture evaluator intends to compare four conventional GLCM directions.



### Analysis

The texture evaluator passes angles \([0,45,90,135]\) to graycomatrix, whose documented unit is radians. At unit distance, these induce offsets \[(0,1),(1,1),(1,0),(0,-1)\], repeating a horizontal direction under symmetric counting and omitting the intended opposite diagonal. Both real and generated images use the same convention, so the sign of its effect on comparative rankings is not known.



### Finding and scope

Spatial energy and related texture comparisons are based on a different directional weighting than intended. Both real and generated images pass through the same metric, and a common unit bug does not predetermine which method it favors. Its effect on the reported table rankings has not been measured.



### Proposed correction

Pass \([0,\pi/4,\pi/2,3\pi/4]\), state the angular convention, and recompute affected GLCM metrics. Include a small asymmetric image check so that repeating a horizontal direction cannot silently pass.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 16: The optional DDIM baseline uses the wrong previous time when timesteps are skipped

Assessment: supported; impact: minor



Source: baseline/diffusion.py:318–352, 373–384, 523–540 baseline/diffusion_evaluate.py:149–152; diffusion_evaluate_ddp.py:613–616



### Source claim (paraphrase)

The accelerated DDIM path should transition between the selected diffusion times.



### Analysis

For a selected sequence of diffusion times, DDIM must transition to the preceding selected time. The implementation uses \(\bar\alpha_{\rm prev}(t)=\bar\alpha_{t-1}\), even when its next model evaluation is at a much earlier selected index. The state therefore carries the wrong noise level into the next denoising prediction.



### Finding and scope

Results obtained with the accelerated baseline path cannot support a fair DDIM comparison until this is corrected. Both standalone evaluation parsers default to DDPM; the DDPM path is not affected by this particular bug. Training-time preview helpers default to DDIM. The paper does not identify the historical sampling flag clearly enough to attribute its baseline disadvantage to this defect.



### Proposed correction

Use \(\bar\alpha_{t_{i-1}}\) or one for the final clean endpoint, and test respacing against a maintained DDIM implementation. Match sampling method, noise schedule, training checkpoint, and network-evaluation budget in comparative experiments.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 17: Optional stain matching uses the paired held-out target image

Assessment: supported; impact: minor



Source: rectified/rectified_evaluate.py:732–761 src/stain_normalization.py:8–76; src/utils.py:326–332



### Source claim (paraphrase)

The optional stain-normalized evaluation is presented alongside expression-conditioned synthesis.



### Analysis

When enable_stain_normalization is set, each generated RGB image is histogram-matched to its own corresponding real evaluation image before image and feature metrics are computed. The evaluated pipeline then has access to target-image information that would not be available when synthesizing an unknown histology image from expression alone.



### Finding and scope

Enabled results would estimate a different, easier pipeline than gene-only generation and should not be presented as the same task. The flag is store_true and therefore off by default; the reviewed example evaluation scripts do not establish that it was enabled for the paper tables. This is not a confirmed allegation of historical target leakage through stain matching.



### Proposed correction

Disable per-target matching for the primary expression-only benchmark. If stain standardization is scientifically needed, choose a fixed reference from training data and apply the same predeclared transformation consistently to real/generated images and all models. Clearly label a per-target matching experiment as an oracle-assisted analysis.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 18: The implemented spatial losses do not reproduce the appendix objectives

Assessment: supported; impact: minor



Source: Paper pp. 23–27, Appendix E, Eqs. (19)–(33) src/spatial_graph_loss.py:131–174, 220–282, 284–362, 436–468



### Source claim (paraphrase)

Appendix E's morphology, arrangement, density and texture objectives specify the intended spatial losses.



### Analysis

Appendix E specifies nuclear morphology, matched-neighbor arrangement and density losses, and a separate kNN gradient/texture objective including higher texture moments. The released segmentation loss instead combines centroid assignment and edge-length-distribution distances. The simple loss uses multiscale Sobel magnitudes and local means/variances, with no kNN graph, skewness or kurtosis. The custom centroid function labeled approximate Wasserstein does not enforce uniform transport marginals and can ignore a distant unmatched cell. The segmentation routine recomputes segmentation rather than implementing the stated periodic cache.



### Finding and scope

A reader cannot reproduce Appendix E simply by running the public spatial-loss module. Even after the detach bug is repaired, a faithful experiment requires choosing a consistent mathematical objective. The corrected kernel prefactor would be a scale change at a fixed bandwidth and could be absorbed into a loss weight; it is not evidence of a large empirical failure. The centroid defect is confined to the optional segmentation branch and is not identified as the evaluator used for Table 5 nuclear statistics.



### Proposed correction

Choose and document the actual differentiable objective, align equations and code, and report which loss produced each result. Use a valid balanced or unbalanced transport formulation if Wasserstein terminology is retained. If Eq. (\(22\)) is intended as normalized planar density, use \(1/(2\pi h^2)\); otherwise call it an unnormalized kernel and state its scale. Remove redundant neighbor notation or introduce the intended neighboring feature difference.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 19: Reported uncertainty and FID aggregation are insufficiently tied to independent experimental units

Assessment: supported; impact: minor



Source: Paper Tables 2–4, 6–9; Figure 8 p. 16; checklist p. 30 rectified/rectified_evaluate.py:801–840, 946–1044



### Source claim (paraphrase)

The means and standard deviations summarize the stated image-quality and biological evaluations.



### Analysis

The paper reports means and standard deviations, so absence of error bars is not the issue. It does not consistently identify whether variability comes from folds, model seeds, images, or batches. Figure 8 explicitly labels Batch FID Mean. The released evaluator exports both pooled overall FID and a mean of batch FIDs; it computes SSIM/feature-distance standard deviations over images and biological-statistic standard deviations over batches. Those are not interchangeable with variation over independently trained models or donors.



### Finding and scope

The reported summaries cannot support precise statistical superiority claims or a faithful fold-level reproduction without additional metadata. Batch FID can still be reported as an explicitly named diagnostic, but should not silently replace standard pooled FID. No particular table is asserted to use the wrong estimator without the result file that generated it. Standard deviations overlapping does not prove equality, and non-overlap would not repair correlated sampling. The checklist's claim that all metrics have standard deviations is broader than Tables 5–6, whose overall FID rows show point estimates.



### Proposed correction

Declare the estimator, feature extractor, image count, batch size, independent training-run count and meaning of each uncertainty interval. Keep per-image spread distinct from donor/run-level inference.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 20: The perturbation and minimally invasive diagnostic claims exceed the demonstrated evidence

Assessment: supported; impact: minor



Source: Paper abstract p. 1; pp. 9–10, Section 4.4 and Discussion; Figures 3, 6, 9 Primary 10 x sample descriptions; Appendix F p. 27



### Source claim (paraphrase)

The broader discussion links conditional generation to perturbation analysis and diagnostic applications.



### Analysis

The experiments use observational paired FFPE Xenium/histology samples. No genetic or chemical intervention dataset, prospective diagnostic trial, or minimally invasive specimen acquisition workflow is demonstrated. The human study uses three ACVP-certified pathologists and two residents, \(20\) similarity pairs and \(20\) preference pairs. Its \(86\%\) preference for rectified outputs describes image preference, not disease sensitivity/specificity. Diagnostic examples are representative qualitative cases without a reported complete case denominator or accuracy/confidence analysis.



### Finding and scope

Neither conditional association nor reader preference establishes causal intercellular effects, reliable diagnosis, or replacement of a tissue-based diagnostic process. The Discussion already calls the tile system a proof of concept and acknowledges several practical limits. The human evaluation is real evidence of perceived image quality; it is not dismissed because the certification is veterinary, and no claim is made about misconduct, lack of required approvals, or diagnostic harm.



### Proposed correction

Keep the claim at conditional image synthesis and hypothesis generation. Release the complete blinded reader-study protocol and per-image/per-reader results, analyze crossed reader/image variation, and evaluate disease classification on an independent patient cohort before diagnostic claims. Test perturbations against held-out experimental interventions with explicit uncertainty and out-of-distribution checks. Define the proposed specimen acquisition workflow before claiming reduced invasiveness.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 21: Small mathematical/architectural notation defects should be corrected without being mistaken for implementation failures

Assessment: supported; impact: minor



Source: Paper p. 3 input matrix orientation; p. 4 feature-gating formula; Appendix D pp. 21–23 src/single_model.py:179–203; src/multi_model.py:239–252



### Source claim (paraphrase)

The matrix orientation, feature gate and block descriptions specify the encoder architecture.



### Analysis

The input matrix is defined as \(C\times G\) but described once as genes in rows/cells in columns. The p. 4 gating expression uses Zfinal on both sides, whereas Appendix D and code implement a feedforward gate from the pre-gated embedding. Appendix D's residual-block descriptions also vary from the main text and the released normalization/activation choices. These are avoidable obstacles to implementation from the paper alone.



### Finding and scope

These corrections improve clarity/reproducibility but do not themselves invalidate reported performance. The encoder code clears the possible concern that the gate is actually circular. Likewise, padding uses masked_fill rather than literal floating-point \(0\times\infty\), so the symbolic Eq. (\(4\)) notation is not evidence of a runtime NaN bug.



### Proposed correction

Use one \(C\times G\) orientation consistently; write \(Z_{\rm final}=Z_{\rm gate}\odot\sigma(W_gZ_{\rm gate}+b)\); provide a versioned architecture/configuration table matching the released model. Clarify which appendix equations are schematic and which are exact implementation definitions.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.
