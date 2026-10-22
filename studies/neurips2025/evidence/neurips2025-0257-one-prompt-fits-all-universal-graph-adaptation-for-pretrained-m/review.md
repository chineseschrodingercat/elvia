# One Prompt Fits All: Universal Graph Adaptation for Pretrained Models



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



Two exact affine counterexamples refute the claimed parameter/gradient equivalence. Detached embeddings and incomplete checkpoints are separate release-level concerns.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: Affine composition does not preserve gradient paths

Assessment: supported; impact: major



Source: Theorem 4.1(2), PDF p.4; Proposition 4.2 and discussion, p.5; Appendix A.2, Eqs.(10)–(12), p.24



### Source claim (paraphrase)

The paper claims equivalence in parameter space and gradient-update paths between factorized prompt/classifier optimization and direct affine optimization.



### Analysis

Use scalar \(z=w(ah+b)\), squared loss \(z^2/2\), and \(h=1,a=w=1,b=0\). All three factor gradients equal \(1\), so a step \(\eta=1/10\) gives \(a_+=w_+=0.9,b_+=-0.1\) and prediction \(0.72\). The direct affine model \(vh+c\), initialized at the identical function \((v,c)=(1,0)\), instead gives \((0.9,-0.1)\) and prediction \(0.8\). Initial effective directions \((-2,-1)\) and \((-1,-1)\) are not proportional. Generally, for \(B=AS\) and \(G=\nabla_B L\), the exact factor update is \[B_+=B-\eta(GS^\top S+AA^\top G)+\eta^2GS^\top A^\top G.\]



### Finding and scope

The central gradient-path equivalence is false, even at the favorable scalar orthogonality initialization in the appendix. Forward functional composition remains correct.



### Proposed correction

Retain the forward affine identity and state the induced factor-optimization dynamics, rather than Euclidean gradient equivalence.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 2: Reverse affine correspondence requires sufficient rank

Assessment: supported; impact: major



Source: Definition 4.1, PDF p.4; Appendix A.2, Eq.(9), p.24



### Source claim (paraphrase)

The proof maps arbitrary affine classifier parameters back to factorized parameters without a stated width restriction, and describes a unique mapping.



### Analysis

Every augmented coefficient matrix \(B=AS\) has rank at most the prompt width \(d_{\rm p}\). For \(d=k=2,d_{\rm p}=1\), the identity classifier has augmented matrix \([I_2\ 0]\) of rank \(2\), impossible for those factors. Even at sufficient width, \(AS=(AQ^{-1})(QS)\) for every invertible \(Q\), so the factorization is generally nonunique.



### Finding and scope

The unrestricted reverse parameter-space equivalence fails. The one-way functional proposition is valid, and a chosen inverse after fixing additional factors is a narrower notion than a unique reparameterization.



### Proposed correction

The representable affine maps are exactly those with augmented rank at most \(d_{\rm p}\); all maps are covered when \(d_{\rm p}\geq\min(k,d+1)\). State the nonuniqueness explicitly.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Detached embeddings prevent supervised prompt gradients

Assessment: supported; impact: minor



Source: Section 5, PDF pp.5–6; main.py, lines 130–168; model/DGI.py, lines 121–125; model/GRACE.py, lines 42–45



### Source claim (paraphrase)

The method jointly trains prompt and classifier through a frozen encoder. DGI and GRACE return detached embeddings on that training path.



### Analysis

The supervised prompt derivative should contain \((D_\Psi H)^\top D_H L\). Detachment removes that route while classifier gradients still exist. Including prompt parameters in Adam cannot supply the missing task derivative. Freezing encoder parameter weights does not require severing derivatives with respect to its input graph. Recursive graph fusion can still change forward values without supervised prompt updates.



### Finding and scope

These two released branches do not implement the described label-driven adaptation. GraphMAE returns nondetached embeddings, so the defect is not universal across backbones. Published score effects and exact historical code remain unknown.



### Proposed correction

Return differentiable embeddings during adaptation while freezing encoder weights through parameter settings or optimizer exclusion.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 4: Early stopping does not restore the monitored graph and model

Assessment: supported; impact: minor



Source: Appendix B.1, PDF p.24; main.py, lines 172–200



### Source claim (paraphrase)

The driver assigns state dictionaries as best states and restores them while retaining the current recursively fused graph.



### Analysis

A state dictionary holds tensors sharing live parameter storage: a value saved at \(1\) and later updated to \(2\) remains \(2\) in the un-cloned snapshot. Separately, with \(A_0=0,\tau=1/2,P_1=1,P_2=2\), fused graph states are \(A_1=1/2,A_2=5/4\). Restoring first-epoch parameters while keeping \(A_2\) cannot recreate the monitored first-epoch input.



### Finding and scope

The checkpoint procedure does not generally recover the best-loss evaluation state. The sign and magnitude of benchmark bias are unknown; a final-best epoch can make the mismatch immaterial.



### Proposed correction

Clone prompt/classifier states and fused edge indices/weights at the monitored forward state, and restore that complete tuple for evaluation.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
