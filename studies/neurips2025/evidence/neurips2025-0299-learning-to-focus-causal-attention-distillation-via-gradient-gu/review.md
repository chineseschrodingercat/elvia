# Learning to Focus: Causal Attention Distillation via Gradient‐Guided Token Pruning



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current detector reads an unretained non-leaf embedding gradient, and the response-only distillation mask omits first-response prediction rows. These are reproducibility and objective-position defects; historical benchmark effects remain unresolved.



## Scope

Rapid, claim-focused reading of the latest applicable author-paper and resource passages. Direct mathematical or static-source reasoning is stated below. No author program, retained verifier, model inference or benchmark was executed.



## Problem 1: The gradient detector indexes an unretained non-leaf gradient

Assessment: supported; impact: minor



Source: Proceedings Section 2.2.1, Eq.(2), PDF p.4; current author src/Confounding_token_detection/run_gradients_{llama,qwen}_{instruct,response}_level.py, compute_token_gradients



### Source claim (paraphrase)

The detector needs teacher/student loss derivatives with respect to token embeddings. Each released kernel constructs embedding outputs, calls requires_grad_(True), backpropagates, then indexes inputs_embeds.grad. The inspected loader leaves embedding weights trainable.



### Analysis

If the embedding matrix \(W\) is trainable, \(E=\operatorname{Embedding}(W,I)\) is a non-leaf operation result. Enabling requires_grad does not detach it or retain its intermediate gradient. Backward can populate \(W\) while leaving \(E.\mathrm{grad}=\mathrm{None}\), which the subsequent indexing cannot use. No detach, retain_grad or explicit returned input-gradient operation appears in the four kernels.

For a concrete derivative oracle, \(L(E)=\sum_{j,d}a_jE_{jd}\) with three-dimensional tokens and \(a=(1,2,4)\) has gradient norms \((\sqrt3,2\sqrt3,4\sqrt3)\), hence normalized sensitivities \((0,1/3,1)\). The failure is retention of that existing derivative, independently of whether the downstream differentiable loss is linear or language-model cross-entropy. Freezing embedding weights before constructing an explicit input leaf is a valid countercontrol.



### Finding and scope

Under the inspected loader configuration, the released detector cannot obtain its gradients through this access. Historical use of frozen parameters, another internal kernel or precomputed outputs remains unresolved; benchmark scores are not refuted.



### Proposed correction

The supplied local correction detaches embedding values, enables their input gradient and explicitly requests the loss derivative with respect to that input. This preserves the requested downstream partial derivative. Retaining the intermediate gradient is another option; full detection and benchmark recovery remain unverified.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Problem 2: The response mask selects shifted target positions incorrectly

Assessment: supported; impact: minor



Source: Proceedings Section 2.2.2, PDF p.5; current author src/Causal_attention_distillation/LeaF_instruct_level/distill_instruct_level.py, lines 201,225–229,423–460; LeaF_response_level analogous reduction



### Source claim (paraphrase)

The release copies token IDs into labels, ignores prompt labels with \(-100\), and applies the unshifted label mask to raw causal-LM output logits in the separate distillation reduction.



### Analysis

Raw logit row \(i\) predicts token \(i+1\). Therefore response prediction rows require \(m_i=\mathbf1\{\ell_{i+1}\ne-100\}\) for \(0\leq i<L-1\). Passing labels to the causal model shifts its internal supervised loss, not the returned raw logits. The source instead uses \(\mathbf1\{\ell_i>-100\}\).

Take four positions: two prompt tokens, one response token and EOS, with labels \((-100,-100,0,1)\). At row \(1\), use teacher probabilities \((0.8,0.2)\) and student probabilities \((0.2,0.8)\); set both distributions to \((0.5,0.5)\) at the other rows. The source selects rows \(2,3\) and gives zero KL. The intended response prediction rows \(1,2\) give \[L=\tfrac12[0.8\log4+0.2\log(1/4)]=0.3\log4\approx0.4158883083.\] Thus it omits the first-response prediction and includes the row after the final supervised token.



### Finding and scope

The current response-only distillation reduction represents a different target-position objective. The model’s ordinary supervised cross-entropy is separate and is not alleged to share this defect. Empirical accuracy effects are unmeasured.



### Proposed correction

With aligned tokenization, prefixes and vocabulary, compare teacher/student logits at rows \(0,\ldots,L-2\) using labels at rows \(1,\ldots,L-1\). State an empty-target convention. This repairs the one-position relation, but not arbitrary cross-tokenizer or differently pruned sequence alignment.

The existing correction is retained as a bounded proposal; author adoption is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- Mathematical counterexamples and source discrepancies do not remeasure published experiments; historical execution results were not rerun.
