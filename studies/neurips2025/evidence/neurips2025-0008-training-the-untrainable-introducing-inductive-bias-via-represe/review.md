# Training the Untrainable: Introducing Inductive Bias via Representational Alignment



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The author-released stacked RNN violates prefix causality and many-to-one alignment mappings overwrite losses. These are serious local implementation defects, but their effect on the historical guided-versus-unguided results is not established. Manuscript definitions, metric reductions and reporting also need local corrections. The strict assessment is Minor; configuration provenance and causal mechanism interpretations remain unresolved.



## Scope

Claim-focused reading of the identified paper and author-released materials. The arguments below distinguish mathematical contradictions, version-specific implementation defects and unresolved empirical consequences. No author code was executed in this revision.



## Problem 1: The released stacked RNN passes future information between layers

Assessment: supported; impact: minor



Source: Author supplement/repository: language_modeling/rnn_models.py, RNNLM.forward, lines 30-42; paper pp. 6-7, Table 2, and Appendix C.1.3, p. 18. Next-token shifting occurs in language_modeling/language_model.py, function shift_logits_labels and eval_ppl_runner



### Source claim (paraphrase)

The language-model experiment and Appendix C describe a conventional stacked RNN evaluated by next-token perplexity.



### Analysis

In RNNLM.forward, the state returned after processing the entire sequence in one recurrent layer initializes the next layer: \(h_0^{(2)}=h_T^{(1)}\). Then \(h_t^{(2)}=\tanh(W_2h_t^{(1)}+U_2h_{t-1}^{(2)})\), so even \(h_1^{(2)}\) depends on \(x_2,\ldots,x_T\). Shifting logits afterwards cannot remove this dependency.

This violates prefix causality in the released autoregressive model. Each layer requires its own initial state, carried only from a preceding chunk when stateful operation is intended. Both guided and unguided baselines use this class, so the direction of the effect on their difference is unknown. For copying, whose outputs follow the source sequence, the same state flow changes the stated architecture without automatically establishing target-label leakage.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Maintain an independent initial recurrent state per stacked layer so prefix outputs cannot depend on future tokens.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 2: Many-to-one guidance mappings overwrite earlier losses

Assessment: supported; impact: minor



Source: Author supplement: rep_sim/layer_sim.py, lines 131-143 and 168-199; author repository: corresponding lines 19-28 and 60-87. paper Eq. (1), pp. 4-5, and Appendix K, p. 31



### Source claim (paraphrase)

Equation (\(1\)) sums dissimilarities for all mapped guide--target layer pairs.



### Analysis

The guide-to-target mapping permits several guide layers to map to one target. The similarity loop stores each value by target-layer key, replacing an earlier value when another guide reaches that target. Summing the dictionary then includes only the last value for each target, whereas Eq. (\(1\)) sums all mapped pairs. One-to-one mappings are unaffected; the per-experiment mappings are needed to determine paper-result impact.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Accumulate every guide-target pair rather than overwriting target-keyed losses.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 3: Released model and training configurations do not identify the reported experiment

Assessment: needs_evidence; impact: needs_evidence



Source: paper p. 5, p. 18, Table 4 on p. 19, Fig. 4 on p. 9; Author supplement/repository: language_modeling/wikitext.py, rnn_models.py, transformer.py, and imagenet-comparison/mlp.py, image_class.py



### Source claim (paraphrase)

The manuscript states specific tokenizers, sequence lengths, nonlinearities, network widths and training schedules.



### Analysis

The released language tokenizer is BERT rather than the stated GPT-2 tokenizer. Context lengths, tanh versus ReLU, deep FCN widths, learning-rate scheduling, and initialization-only control flow also differ across paper and release. These are identifiable configuration discrepancies; original run logs are needed to determine which settings produced the reported scores.



### Finding and scope

The available material identifies a scope or evidence gap; it does not prove that the reported empirical effect is false.



### Proposed correction

Bind every reported model to tokenizer, context, architecture, schedule and initialization configuration.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 4: Zero content tokens are masked from copying and perplexity lacks a fixed denominator

Assessment: supported; impact: minor



Source: paper p. 5 and Table 2; Author supplement/repository: language_modeling/copy_paste.py; language_modeling/language_model.py, cp_acc, shift_logits_labels, and eval_ppl_runner; wikitext.py lines 31-40



### Source claim (paraphrase)

The copy task is described as copying all ten symbols, and the language model is evaluated by perplexity.



### Analysis

The paper describes content symbols \(1\) through \(10\), but the generator samples \(0\) through \(9\) and also uses zero as padding. Both loss and cp_acc ignore zero targets. Genuine zero content is therefore omitted from the copying objective and score.

For target \([0,0,0,1,0,2,12]\) and prediction \([9,9,9,1,9,2,12]\), let the last five positions be the output interval, including EOS. The nonzero mask counts only \(1,2,12\) and reports \(3/3=1\); the position-based mask reports \(3/5=0.6\). This identifies the task-definition error without estimating its paper-run frequency.

For language evaluation, averaging batch means and then applying a stored-token/word correction need not equal the intended token-weighted loss, particularly with unequal tail batches or shifted positions. Define evaluated set \(\mathcal E\) and use \(\operatorname{PPL}=\exp(\sum_{i\in\mathcal E}-\log p_\theta(x_i\mid x_{<i})/|\mathcal E|)\), or an explicitly defined word denominator. Include boundary/special-token treatment.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Reserve a distinct padding symbol or mask by sequence position; fix the language-model loss denominator.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 5: Import and interface defects block the released reproduction entry points

Assessment: supported; impact: minor



Source: Author supplement/repository: package initializers and command-line entry points; paper checklist items 4-6, pp. 34-35



### Source claim (paraphrase)

Checklist items \(4\)-\(-6\) describe reproducibility, and the supplied package exposes training/evaluation entry points.



### Analysis

The author release contains imports of undefined ParityLSTM, missing similarity functions or reduction modules, and caller/signature mismatches including token_sim and multi_gpu. An allowed parity_rnn] command-line value also differs from the branch condition. These are static import/interface defects in the identified archives; they do not show that the private historical training failed.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Resolve the listed imports, command-line values and caller/signature contracts before claiming a runnable release.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 6: CKA orientation and minibatch layer indexing are inconsistent in the manuscript

Assessment: supported; impact: minor



Source: paper p. 3; Algorithm 1, p. 16; Eqs. (2)-(6), p. 17. original printed equations



### Source claim (paraphrase)

The prose and Algorithm 1 define how CKA-derived guidance is computed and applied.



### Analysis

For nondegenerate centered representations, normalized linear CKA is \(1\) for identical representations, and the loss \(1-\operatorname{CKA}\) is zero. The prose reverses those endpoints and elsewhere says to minimize CKA; the author helper uses the standard orientation.

With \(H=I_b-\mathbf1\mathbf1^\top/b\), \(K_c=HXX^\top H\) and \(L_c=HYY^\top H\), the standard ratio is \[\langle K_c,L_c\rangle_F/(\|K_c\|_F\|L_c\|_F)\]. A singleton batch gives \(H=0\), so a degeneracy rule is needed. The printed tr(K,L) also needs a matrix-product or Frobenius-product definition; a common HSIC scale cancels from the ratio.

Algorithm 1 mixes single-example and minibatch operations, one-based and zero-based indexing, target and guide indices, and similarity versus dissimilarity, and omits an explicit parameter update. With \(50\) target and \(18\) guide layers, reusing the target index can request guide layer \(49\), outside its range. These are manuscript-specification defects, not evidence that the correctly oriented author helper optimized the opposite loss.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Use standard centered minibatch CKA orientation and minimize its complement; specify degenerate-batch handling and layer indices.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 7: The random-guide result does not isolate architectural causation

Assessment: needs_evidence; impact: needs_evidence



Source: paper pp. 2, 4, 8-10; Appendix D, p. 20; Appendix E, p. 21; Appendix I.1, p. 25



### Source claim (paraphrase)

The discussion interprets gains, high alignment and earlier stitching theory as evidence of a purely architectural transfer mechanism.



### Analysis

A random guide has not learned task labels through weight optimization, but its representations still depend on initialization distribution, normalization, the input distribution, and the particular alignment metric. Improvement with that guide establishes that pretrained task weights are not necessary in those configurations. It does not uniquely identify which architectural property causes the improvement. The noise-guide experiment is compatible with a generic geometric regularizer. In particular, biased finite-batch CKA can be close to one for independent high-dimensional random features. For fixed batch size \(b\), independent Gaussian matrices \(X\in\mathbb R^{b\times d}\) and \(Y\in\mathbb R^{b\times d'}\) satisfy \(XX^\top/d\to I_b\) and \(YY^\top/d'\to I_b\) as widths grow. Centering gives matrices proportional to \(H\), so their CKA approaches one even though the feature sets are independent. This is a counterexample to reading high alignment as sufficient evidence of shared task information, not a demonstration that the paper's ImageNet gains are artefacts. It motivates a small set of discriminating controls: random features with matched Gram spectra, permuted sample correspondence, guide architectures with matched width and normalization, and a matched extra-forward/BatchNorm control. The last is relevant because guidance performs another target forward pass, updating BatchNorm statistics again during image training. The stronger claim that residual connections must be trained before influencing representation space is also unsupported. A residual block \(x+F_W(x)\) differs from \(F_W(x)\) before any weight update, and its input Jacobian contains an identity contribution. The failure of one random ResNet-50 guide to improve one target supports a statement about that experiment, not a necessity theorem about residual connections.



### Finding and scope

The available material identifies a scope or evidence gap; it does not prove that the reported empirical effect is false.



### Proposed correction

Use matched random-feature, normalization, width and sample-correspondence controls before assigning architectural causation.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 8: Correctness consistency is distinct from class-label agreement

Assessment: supported; impact: minor



Source: Fig. 3 and accompanying discussion, pp. 8-9; Appendix F, Eq. (7), p. 22; Fig. 13, p. 24



### Source claim (paraphrase)

Equation (\(7\)) uses an accuracy-derived expected-agreement null while parts of the prose describe agreement of predicted labels.



### Analysis

The null \(a_1a_2+(1-a_1)(1-a_2)\) describes agreement of correctness indicators, not multiclass labels. If two classifiers are correct on the same one of ten cases and choose different wrong labels on the other nine, correctness agreement is perfect but class-label agreement is \(0.1\). Combining \(0.1\) with the correctness null gives \(\kappa=-4\), showing the incompatible definitions.

The paper's guided-model pair has consistency \(0.49\), its guide pair \(0.53\), while matched target-guide values are \(0.047\) and \(0.020\). Similar within-pair scalars alone do not establish strategy inheritance: independent pairs can each have within-pair \(\kappa=0.5\) and zero cross-pair association. Original evaluation code is needed to identify the statistic actually plotted.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Define observed agreement using correctness indicators when using the accuracy-based null; do not infer strategy transfer from one matching scalar.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 9: The printed distillation loss reverses the cited KL direction

Assessment: supported; impact: minor



Source: Eq. (8), Appendix H, p. 23; Fig. 5, p. 10; model-distillation discussion, pp. 3-4



### Source claim (paraphrase)

Appendix H Eq. (\(8\)) labels student and teacher distributions and invokes the standard soft-target distillation baseline.



### Analysis

The paper defines \(Q\) as student logits and \(P\) as teacher logits, then writes \[
\mathrm{KL}(\sigma(Q/T)\|\sigma(P/T)).
\] Standard soft-target distillation in the cited Hinton formulation minimizes cross-entropy from teacher probabilities to student probabilities, equivalent up to a teacher-only constant to the opposite direction, \(\mathrm{KL}(p_T\|q_T)\). This is not a notationally interchangeable choice. For teacher probabilities \((0.8,0.15,0.05)\) and student probabilities \((0.25,0.25,0.5)\), the two divergences are \(0.73876755\) and \(0.98821125\), respectively. The gradients and behavior under finite student capacity differ. A correctly stated baseline is \[
L_{KD}=\alpha T^2\mathrm{KL}(p_T\|q_T)
+(1-\alpha)L_{CE}(q_1,y).
\] If reverse KL was intentionally used, label it as a separate baseline and include the referenced forward-KL method. The released materials inspected here do not contain the original distillation experiment code, so the direction used to produce Fig. \(5\) remains unresolved. The related-work section itself acknowledges representation-based distillation and prior use of CKA. Consequently, beating one logit-distillation setting at \(\alpha=0.5,T=2\) does not establish superiority over representation distillation generally. A matched intermediate-feature or CKA-distillation comparator would identify what the random guide, cross-architecture design, and mapping add. That is a targeted comparison, not a demand for every existing distillation method.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

State the intended KL direction; the cited teacher-to-student distillation baseline uses teacher probabilities as the reference distribution.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 10: Uncentered activation SVD is not PCA explained variance

Assessment: supported; impact: minor



Source: Eqs. (9)-(14), pp. 25-26; Fig. 15, p. 27; Appendix I.3, p. 28



### Source claim (paraphrase)

Appendix I defines an ID regularizer through the explained-variance spectrum of activation matrices.



### Analysis

Eq. (\(9\)) needs the smallest integer crossing the variance threshold; otherwise many dimensions satisfy it. More substantially, Eqs. (\(10\))-(\(12\)) take the SVD of raw activations and call the squared singular values explained variances. PCA variance requires centering over samples. Without centering, a common feature offset changes the quantity although the covariance geometry is unchanged. The PCA threshold dimension is an operational linear effective dimension. Calling it the true complexity of the data manifold is stronger than this estimator warrants. The useful result would be that this specified spectral regularizer improves the chosen FCN, rather than a general causal conclusion that low intrinsic dimension causes overfitting. The linear-decoding argument on p. 28 also exceeds its evidence. A probe trained on \(4000\) images for \(1000\) classes is a limited-data test. Accuracy above the \(0.1\%\) chance level, even if below \(0.8\%\), does not demonstrate absence of linearly decodable information. The same paragraph cites a larger-data result with higher accuracy. A more accurate conclusion is that this small probe did not extract strong classification performance. Learning curves or a stronger probe would be optional ways to assess the mechanism further. Let \(X\) have rows \[(1,0),(-1,0),(0,1),(0,-1)\] and let \(X'=X+\mathbf1(100,0)\). Both matrices have four samples and two finite real features. Centering gives \(HX'=HX=X\) and \(X^{\mathsf T}X=\operatorname{diag}(2,2)\), so the \(90\%\) variance threshold requires two dimensions. Without centering, \((X')^{\mathsf T}X'=\operatorname{diag}(40002,2)\), whose leading ratio is \(40002/40004=0.999950005\ldots\); the raw-SVD rule instead returns one. The constant offset is permitted by the stated activation-matrix domain, so translation invariance cannot be assumed unless centering is part of the definition.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Center activations across samples before PCA variance accounting, and state whether the regularizer targets an exact dimension or a lower bound.

Proposed correction; independent verification and author adoption remain unestablished.



## Problem 11: Several performance summaries conflict with the displayed tables

Assessment: supported; impact: minor



Source: Tables 2-3, p. 7; accompanying prose, pp. 7-8; p. 5 and Appendix B.2, p. 17; Table 5, p. 30



### Source claim (paraphrase)

The text describes perplexity reductions, random versus trained guidance and monotonic benefit from more supervised layers.



### Analysis

Small-RNN perplexity reductions are \(29.18\) with trained guidance and \(9.58\) with random guidance. Wide-FCN top-five accuracy is \(39.47\) for random versus \(43.01\) for trained guidance. CIFAR-10 first-five-layer guidance gives \(79.58\), versus \(70.15\) with all-layer guidance. Broad guidance and layer-count summaries therefore require their stated conditions.



### Finding and scope

The stated limitation or local discrepancy is supported within this source version. Stronger causal, historical-run or population conclusions remain unverified.



### Proposed correction

Use condition-specific improvements and the exact displayed numbers instead of universal performance summaries.

Proposed correction; independent verification and author adoption remain unestablished.



## Limits

- Independent scientific adjudication remains pending.

- No author code, model training or full benchmark evaluation was executed in this revision.

- Version-specific source defects do not establish which code produced the published experiments.

- Corrected benchmark scores, empirical effect sizes and author adoption remain unverified unless explicitly stated.
