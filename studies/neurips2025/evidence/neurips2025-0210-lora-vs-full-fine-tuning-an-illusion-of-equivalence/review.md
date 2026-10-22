# LoRA vs Full Fine-tuning: An Illusion of Equivalence



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current public release saves the final model despite a best-checkpoint option, leaves subsequent optimization in evaluation mode after validation, and compares differently rounded reference/tuned matrices. Exact local controls expose each discrepancy; the reported spectral and behavioral findings are not remeasured.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: The best-checkpoint option selects current rather than best state

Assessment: supported; impact: minor



Source: finetuning.py, lines 12–37 and 155–161; utils.py, get_finetuning_state_dict; current author commit 9b83bf208a124eb9d33f7a680d7924f1f1700953



### Source claim (paraphrase)

Both final-save branches serialize the current model. The best-validation state is also captured without an immutable copy.



### Analysis

Take consecutive parameter states \((1,2,3)\) with validation scores \((1,0,0)\), and enable best-state saving. The highest score is at state \(1\), but the shared final expression serializes state \(3\). Reference-based capture can also change while training storage is updated; the ignored best-state object already establishes failure independently of aliasing. Final-best and final-state-only settings are passing cases.



### Finding and scope

The public option does not ensure the saved checkpoint corresponds to its printed best score. The paper does not promise this exact selection rule, and historical use is unresolved.



### Proposed correction

Capture an immutable selected state, metric and step when validation improves; serialize that snapshot when requested, with explicit no-validation and tie handling.

A proposed correction is described; author adoption is not established.



## Problem 2: Validation does not restore the subsequent training mode

Assessment: supported; impact: minor



Source: finetuning.py, train_epoch, lines 12–37, and eval_dataset, lines 40–62; current author commit 9b83bf208a124eb9d33f7a680d7924f1f1700953



### Source claim (paraphrase)

The epoch sets training mode once; periodic validation sets evaluation mode and never restores it before later optimization batches.



### Analysis

With three training batches and validation every two, the control flow gives forward modes \((\mathrm{train},\mathrm{train},\mathrm{eval})\). Mode changes do not disable backpropagation. For scalar prediction \(dw\) with inverted dropout \(d=M/(1-p)\), squared loss has expected training gradient \(w/(1-p)-y\), whereas evaluation mode gives \(w-y\). At \(p=1/2\), \(w=1\), \(y=0\), these are \(2\) and \(1\). Zero dropout or validation only after the final batch removes this particular effect.



### Finding and scope

The current source changes the optimization distribution after validation. The direction or size of any LoRA/full-tuning performance effect is not established.



### Proposed correction

Save the caller’s mode, evaluate without gradient tracking, and restore that mode on every return or exception. Intentionally mixed child-module modes require corresponding per-module restoration.

A proposed correction is described; author adoption is not established.



## Problem 3: Asymmetric reference rounding can create a zero-update intruder

Assessment: supported; impact: minor



Source: Definition 3.1 and Algorithm 1, PDF p.4; find_intruder_dimensions.py, lines 12–17 and 34–40; utils.py, get_model_to_train



### Source claim (paraphrase)

The public entry point first loads the reference in float16 while the tuned-model helper defaults to float32. Casting both to float32 immediately before SVD cannot recover the lost reference entries.



### Analysis

Take identical original matrices \(W=(1-c)I_{16}+c\mathbf1\mathbf1^\top\), with stored diagonal \(1\) and off-diagonal \(c\approx2\times10^{-8}\). The leading vector is \(q=\mathbf1/4\), with simple spectral gap \(16c\). Since \(0<c<2^{-25}\), half-precision round-to-nearest erases each off-diagonal entry, yielding identity. A valid identity SVD uses coordinate vectors, giving \(\max_i|q^\top e_i|=1/4<1/2\): one top-vector intruder despite zero actual tuning update. Equal original inputs instead give cosine \(1\) and count zero. The rounded repeated spectrum makes the outcome basis-dependent; no universal backend result or frequency in real model layers is claimed.



### Finding and scope

The current measurement path admits a precision-history false positive. It does not establish that the observed original intruders or behavioral interventions are all numerical artifacts.



### Proposed correction

Load both original matrices from the same model revision at equal original analysis precision, retain dtype/hash/gap diagnostics, and include a zero-update control. Equalizing dtype after one-sided rounding is insufficient; repeated-spectrum subspace interpretation remains a separate question.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.

- The first two control-flow findings concern the path after its separate evaluation-call arity mismatch is reconciled; no such author-code patch or execution was performed.

- Original checkpoint histories and per-layer matrices were not recovered or remeasured.
