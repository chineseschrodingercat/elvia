# ARMesh: Autoregressive Mesh Generation via Next-Level-of-Detail Prediction



Preliminary assessment: Minor

Independent scientific review: pending. Author adoption: not requested.



The current constrained decoder returns global termination when one full-search branch has no child, even if sibling prefixes remain on its stack. A finite grammar gives an exact missed-solution witness; practical mesh-generation frequency and benchmark effects remain unmeasured.



## Scope

Claim-focused reading of the original paper and relevant author-released source, with direct mathematical and static-source checks. No author program, historical verifier, model training or published benchmark was executed.



## Problem 1: A dead branch prematurely terminates depth-first decoding

Assessment: supported; impact: minor



Source: Section 4.3, pp.6–7; exp/1/exp_utils.py, constrained_decoding, lines 225–299; exp/1/6-gen.py, lines 95–123



### Source claim (paraphrase)

The paper describes backtracking to alternative branches. During the full-candidate pass, the author function returns termination whenever the current prefix has no children, without checking whether its depth-first stack still contains siblings.



### Analysis

Use vocabulary \(\{0,1,2,3\}\) in that order. The empty prefix admits incomplete prefixes \([0]\) and \([1]\); no extension of \([0]\) is valid; \([1,2]\) is complete; all other extensions are invalid. Set maximum length \(3\), first-pass candidate ratio \(0.01\), and no timeout or requested end token. The restricted pass follows \([0]\) and exhausts. The full pass stacks both siblings, explores \([0]\), then returns termination with \([1]\) still pending. Its returned \([0,3]\) is merely the last rejected candidate. Thus a valid complete branch is missed by control flow, independently of model logits or native mesh code.

The reported mesh strengthening uses planar vertices \[(0,0,0),(1,0,0),(1/2,1,0),(-1/2,1,0),(-1,0,0)\] and faces \((0,1,2),(0,2,3),(0,3,4)\). Operation length is \(10+f_v+e_v\): central vertex \(0\) requires \(17\) tokens, boundary vertex \(1\) requires \(13\). A cap of \(13\) can kill the preferred central branch while a boundary branch remains. This supports the mechanism’s relevance, but the original native validator and reported adapted execution were not rerun here; the complete generic finite-grammar witness already establishes the search defect.



### Finding and scope

The current function can report search exhaustion prematurely; its generation caller then stops further splits. Intentional end-token termination, an actually empty search and timeout are separate cases. No claim about typical model orderings or published mesh metrics follows.



### Proposed correction

Continue the depth-first loop after a dead branch. Declare exhaustion only after each pass has exhausted its stack; pending prefixes preserve the ordinary finite-search invariant. No complete patched model-generation run is certified.

A proposed correction is described; author adoption is not established.



## Limits

- Preliminary AI assessment; independent human scientific adjudication remains pending.

- Analytic examples and release discrepancies do not remeasure the paper’s reported experiments.
