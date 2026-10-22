# Non-Convex Tensor Recovery from Tube-Wise Sensing



Preliminary assessment: Major

Independent scientific review: pending. Author adoption: not requested.



The literal leave-one-out initialization violates its own row-error theorem in an admissible Gaussian limit. Adaptive concentration also needs justification, while incoherence scaling is a scope clarification and the practical recovery algorithm is not refuted.



## Scope

Full supplied technical report read alongside the corresponding original-paper claim passages and applicable author-release source. This pass independently checks the stated reasoning and bounds; historical executions were not rerun.



## Problem 1: The incoherence parameter necessarily scales with tube length

Assessment: not_issue; impact: minor



Source: Assumption 2, Eq. (10); Theorem 2, Eq. (12); sample-complexity discussion



### Source claim (paraphrase)

The stated spectral row bound uses \(\sqrt{\mu r/(nL)}\), while the complexity narrative suppresses \(\mu\) and discusses linear tube-length dependence.



### Analysis

At each Fourier frequency, t-orthogonality gives \(\sum_i\|\widehat U_k(i,:)\|^2=r\). Summing the assumed bounds forces \(r\le\mu r/L\), hence \(\mu\ge L\). A flat rank-one factor \(U(i,1,:)=e_0/\sqrt n\) attains equality. Writing \(\nu=\mu/L\) exposes sufficient per-tube scaling \(\nu^5r^5\kappa^9L^6\log^2N/n\), with the floor \(m\ge1\). This is a theorem-parameter restatement, not a lower bound on algorithmic necessity. Table 1 explicitly measures sensing-operator storage rather than scalar observations.



### Finding and scope

The normalization and resource convention require explicit scope, but this does not refute the theorem for admissible parameters or the storage comparison.



## Problem 2: Pointwise concentration does not justify adaptive sensing errors

Assessment: supported; impact: minor



Source: Lemma 2, Eq. (100); Appendix A.2, Eqs. (41) and (54)



### Source claim (paraphrase)

The proof treats input tensors as fixed while applying the bound to errors selected from the same sensing matrices.



### Analysis

An unrestricted simultaneous reading cannot repair this: choose \(n=4,m=r=1\), one Gaussian sensing row \(z\in\mathbb R^L\), error tube \(\Delta_{11:}=z/\|z\|\), and identity tube in the first row of the right factor. Inputs have unit required norms. The left side is at least \(\|z\|^2-1\), while the proposed right side is only \(2C\sqrt{nL}\log L\). With probability at least \(1-8/L\), the former is at least \(L/2-1\), eventually larger for every fixed \(C\). This input is not claimed to be an actual recovery iterate; it rules out unrestricted uniform reinterpretation. The existence of leave-one-out sequences shows dependence was considered, but does not replace the particular direct application by a proved restricted event.



### Finding and scope

The adaptive invocation lacks the needed concentration justification. The fixed-input lemma and final recovery algorithm are not disproved by this adaptive witness.



### Proposed correction

State fixed-independent-input quantifiers and supply restricted-uniform or independence-restoring control for actual iterates. Fresh measurements would change the algorithm and budget; no complete repair is established.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Problem 3: Literal auxiliary initialization contradicts its claimed row bound

Assessment: supported; impact: major



Source: Leave-one-out Eqs. (19), (24), (59), (62); Theorem 4, Eq. (28); Appendix Eq. (169)



### Source claim (paraphrase)

The literal auxiliary initializer divides the restored ground-truth row by \(m\), while its proof restores that row without division. The auxiliary loss similarly uses coefficient one where later recurrences use \(m\).



### Analysis

For fixed \(n=16,L=8,r=1\), flat \(u_i=1/4\), ground truth \(\mathcal X^*=uu^Te_0\), admissible \(\mu=L\), condition number \(1\), and independent Gaussian sensing, let \(m\to\infty\). All stated lower sample requirements are eventually met; no upper restriction is imposed. The strong law makes the literal initializer converge to the ground truth with the omitted row zeroed. Its isolated leading singular value stays positive, so its balanced left factor’s omitted row converges to zero under every orthogonal alignment. The true row has norm \(1/4\), while Theorem 4’s right side decays as \(m^{-1/2}\). Its asserted high-probability row bound therefore fails. Separately the literal loss population operator is \(mI-(m-1)P_l\), whereas the proof uses \(mI\); this mismatch already occurs with \(m<L\).



### Finding and scope

The displayed auxiliary process and the analyzed one differ, and the literal initializer’s theorem is false. These proof devices are not computed by the actual recovery algorithm, so its empirical failure does not follow.



### Proposed correction

Restore the omitted slice after, rather than inside, division by \(m\), and weight its auxiliary loss by \(m\). This centers the operator and aligns the displayed recurrences, but all dependent proof bounds and the adaptive concentration step still need checking.

The described correction remains a proposal; author adoption or a corresponding erratum is not established.



## Limits

- Preliminary AI source/argument assessment; independent human scientific adjudication remains pending.

- No author-provided or retained verification program was executed. Published empirical results were not independently reproduced.
