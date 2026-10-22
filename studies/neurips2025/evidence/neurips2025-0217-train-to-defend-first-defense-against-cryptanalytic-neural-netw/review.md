# Train to Defend: First Defense Against Cryptanalytic Neural Network Parameter Extraction Attacks



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Exact duplicate neurons preserve their normalized shared signature, matrix rank and downstream function after merging. Two explicit bounded-box examples also invalidate the printed disagreement equality/complement. These affect central mathematical explanations, without disproving measured extraction delays.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: Identical incoming directions survive signature normalization

Assessment: supported; impact: major



Source: Section 3.1, p.5, Eqs.(6)–(8)



### Source claim (paraphrase)

Under identical incoming parameters \(a=b\), the paper says the mixed contribution prevents recovery of the normalized incoming signature.



### Analysis

Provided \((c_1+c_2)a_1\epsilon\ne0\), the displayed ratio is \[(c_1a_2\epsilon+c_2b_2\epsilon)/(c_1a_1\epsilon+c_2b_1\epsilon)=a_2/a_1.\] For \(a=b=(1,2),c_1=1,c_2=3\), the network is \(4\max(0,x_1+2x_2)\). At the common boundary \(0\), positive/negative coordinate perturbations yield changes \(4\epsilon\) and \(8\epsilon\), recovering signature \((1,2)\) exactly. The individual outgoing split remains nonidentifiable; a zero summed coefficient or zero pivot is excluded by the stated nondegeneracy.



### Finding and scope

The paper’s exact-duplication example does not corrupt the shared normalized direction. This does not remove practical finite-precision or nearby-boundary difficulties for approximately equal neurons.



### Proposed correction

State that identical neurons with nonzero summed outgoing coefficient expose their common normalized direction, while the split of outgoing coefficients is not identifiable from function values.

A proposed correction is described; author adoption is not established.



## Problem 2: Exact duplicate merging preserves rank and later activations

Assessment: supported; impact: major



Source: Section 5.2, reduced-representation discussion, pp.9–10



### Source claim (paraphrase)

The discussion attributes loss of rank and corrupted deeper representations to merging exactly duplicate neurons.



### Analysis

For any activation columns, \(H=[h,h,h_3,\ldots]\) and \(H^{\prime}=[h,h_3,\ldots]\) have identical spans and hence identical rank. Replacing outgoing rows \(v_1,v_2\) by \(v_1+v_2\) preserves each subsequent preactivation because \(hv_1^{\top}+hv_2^{\top}=h(v_1+v_2)^{\top}\). Biases and all later deterministic layers are unchanged, so functional preservation holds for every input. For example, with \(h=\max(0,x_1+2x_2)\), preactivations \(h+3h-1\) and \(2h-h+1/2\) become exactly \(4h-1\) and \(h+1/2\).



### Finding and scope

Removing a duplicate reduces width, not rank. Parameter nonuniqueness already exists before merging. Approximate merging and efficient identification require separate error/algorithm analyses.



### Proposed correction

Distinguish recovery of the exact redundant parameter split from recovery of an equivalent function. Attribute any practical difficulty to approximate estimates, conditioning or search costs rather than rank loss from exact duplicate removal.

A proposed correction is described; author adoption is not established.



## Problem 3: The disagreement probability needs clipping and pivot orientation

Assessment: supported; impact: major



Source: Section 3.2, Theorem 1 and Eqs.(14),(17), pp.6–7



### Source claim (paraphrase)

The bounded-input calculation treats an unbounded strip as its portion inside the box and uses the angle between complete normals to decide whether to complement the probability.



### Analysis

Let inputs be uniform on \([-1,1]^2\). Normals \(a=(2,1),b=(3,1)\) give printed probability \(1/4\), but actual disagreement area divided by box area is \[\frac12\left[\int_0^{1/3}x\,dx+\int_{1/3}^{1/2}(1-2x)\,dx\right]=\frac1{24}.\] The strip exits the box, so equality fails although an upper-bound interpretation survives this case.

For \(a=(2,1),b=(-2,1)\), the printed strip expression is \(1\), and the negative dot product selects complement \(0\). Actual disagreement is \(y^2<4x^2\), with probability \(\frac12[\int_0^{1/2}4x\,dx+\int_{1/2}^12\,dx]=3/4\). Complementing even the correctly clipped strip would give \(1/4\), still wrong. The sign governing inside/outside thresholds is \(a_2b_2\), not \(a^{\top}b\).



### Finding and scope

The stated equality and general complement rule are invalid. A uniform-input disagreement volume is also not, by itself, parameter-recovery probability or running time; adaptive attack queries require a specified separate model.



### Proposed correction

With nonzero pivots, integrate the threshold interval intersected with the box. Use that clipped strip when \(a_2b_2>0\), and its complement when \(a_2b_2<0\). In higher dimensions, the triangle-inequality expression remains a same-pivot upper bound under uniform box input; complementing such an upper bound yields a lower bound.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.

- No MNIST retraining, long extraction run or attack-time extrapolation was reproduced; approximately duplicate neurons may still pose practical numerical difficulties.
