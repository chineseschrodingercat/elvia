# DreamLight: Towards Harmonious and Consistent Image Relighting



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The released SD1.5 directional resampler groups attention heads instead of query tokens and multiplies signed logits before softmax. Both differ from the stated directional extraction mechanism, without establishing failure of learned image quality.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: Directional maps are assigned by head rather than query group

Assessment: supported; impact: minor



Source: Section 3.2/Figure 3, PDF pp.4–5; SD15/ip_adapter/resampler.py, lines 209–227



### Source claim (paraphrase)

The paper defines four query-token groups, but reshaped attention is \((B,H,Q,K)\) and the source chunks dimension \(1\), the head axis.



### Analysis

For production \(H=12,Q=16,K=273\), each directional chunk contains three heads and all sixteen queries. At the first spatial key, head \(0\), query \(4\) receives left coefficient \(1\), though query \(4\) belongs to the right group and needs \(0\). Head \(3\), query \(0\) receives right coefficient \(0\), though the left group needs \(1\). Every query within a head shares the same map. Downstream injection treats the resulting token groups as directional keys; no inspected deterministic head-to-token map supplies the missing query grouping.



### Finding and scope

The source mask does not implement the declared query-group routing. Learned queries may still specialize and relighting may improve; no same-defect claim is made for FLUX.



### Proposed correction

For the documented design, broadcast \(G_{bhqk}=m_{\lfloor4q/Q\rfloor}(k)\), with \(Q\) divisible by \(4\), along the query axis. This changes the architecture and requires checkpoint/quality evaluation.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: A zero spatial coefficient can favor a negative logit

Assessment: supported; impact: minor



Source: Section 3.2, PDF p.5; resampler.py, lines 215–224



### Source claim (paraphrase)

The release multiplies raw dot-product scores by maps in \([0,1]\), then softmaxes them.



### Analysis

Two keys with equal logits \(-2\) and left/right coefficients \((1,0)\) become \((-2,0)\); conditional pair shares are \[0.1192029220,0.8807970780\], rather than equal shares before masking. The supposedly removed right key has odds \(e^2\) times the left. These are valid dot products, for example \(q=(1,0,0,0)\), both keys \((-4,0,0,0)\), head width \(4\). The pair odds hold inside the full \(273\)-key row and are not claimed as full-row probabilities. Positive logits can favor the intended side and zero logits are unaffected.



### Finding and scope

The unconditional attenuation interpretation fails on legal signed scores. No actual PSNR/FID or trained-token counterexample is established.



### Proposed correction

For an unnormalized probability gate, compute \(A=\operatorname{softmax}(L)\), then \(\widetilde A=A\odot G\), with no second softmax. This gives \(0\le\widetilde A\le A\) and preserves coefficient-one special keys. A separately normalized gate equals softmax of \(L+\log G\), but changes absolute special-key weights and must be described as a different choice.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
