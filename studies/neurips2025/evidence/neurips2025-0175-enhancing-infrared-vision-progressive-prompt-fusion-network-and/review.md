# Enhancing Infrared Vision: Progressive Prompt Fusion Network and Benchmark



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



Singleton prompt dimensions make the released multi-device training path discard image shards and can break validation. The stated low-contrast formula also differs from its pinned generatorâ€™s brightness offset. Historical experiment correspondence remains unresolved.



## Scope

Claim-focused reading of the original paper and relevant author-released passages; direct mathematical or static-source reasoning. No author program, earlier verifier, model or benchmark was executed during this check.



## Problem 1: A singleton prompt truncates parallel image batches

Assessment: supported; impact: minor



Source: train.py, lines 146â€“156,188; PyTorch 1.12 scatter_map



### Source claim (paraphrase)

Training passes images shaped \((4,1,256,256)\), a degradation prompt \((1,128,128)\), and scenario prompts \((4,64)\) into DataParallel.



### Analysis

Dimension-zero scattering yields four image/scenario chunks but one degradation chunk. The recursive zip stops at one input, leaving a one-image prediction. For scalar predictor \(f_w(x)=wx\), \(w=1\), four constant images/targets \(0.1,0.2,0.7,0.8\) should have zero loss. Broadcasting the surviving first prediction gives mean absolute loss \(0.35\) and gradient \(-0.075\). Validation passes a scenario vector \((64,)\), which is split into length \(16\) on four destinations, incompatible with the released \(64\)-input linear layer. Single-device operation can avoid this scattering defect.



### Finding and scope

The released multi-device call layout fails its per-example contract. This is a static source/shape finding; no claim of four-physical-GPU execution or false published scores is made.



### Proposed correction

Before scattering, give every tensor a matching batch axis: degradation \((B,128,128)\), scenario \((B,64)\). Assert equal prediction/target shapes. This restores the identified correspondence, not end-to-end trained performance.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Problem 2: The corruptionâ€™s brightness offset differs from the printed formula

Assessment: supported; impact: minor



Source: Appendix A.1.1 Eq.(8), PDF p.22; ranges, PDF p.23; dataset.py/create_corrupt.py and Albumentations 1.4.1



### Source claim (paraphrase)

The paper specifies \(C(I)=\alpha(I+\beta M)\); the pinned brightness-by-max transform implements \(\alpha I+\beta M\).



### Analysis

Use valid uint8 intensities \(0,100,200,255\), \(M=255\), and interior hard-range values \(\alpha=0.5,\beta=0.3\). The printed real outputs are \[(38.25,88.25,138.25,165.75)\]; the dependency gives \((76.5,126.5,176.5,204)\). No value saturates, and the real offset difference is \((1-\alpha)\beta M=38.25\). Quantization cannot explain it. Renaming brightness would require correlated parameter changes; at these values the implied paper brightness \(0.6\) exceeds the hard range.



### Finding and scope

The release and printed parameters define different corrupted inputs. Which produced the historical benchmark images is unestablished.



### Proposed correction

Either document the multiply-then-add generator and ranges, or implement the printed correlated offset. Matching one formula locally does not establish improved restoration or recover historical data.

A proposed correction is retained where stated; independent verification and author adoption remain unestablished.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic witnesses and static release checks do not remeasure the published benchmark results.
