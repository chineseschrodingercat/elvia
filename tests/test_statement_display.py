"""Source-bound statement excerpts preserve conditions without promoting witnesses."""

import copy
import unittest

from elvia.statement_display import statement_paragraphs, verification_assumptions


class StatementDisplayTests(unittest.TestCase):
    def test_curated_statement_is_complete_override_and_inputs_are_unchanged(self):
        statement = [
            r"For every \(x\in X\), there exists \(y\in Y\) with \(f(x,y)=0\).",
            "Neither uniqueness nor a uniform choice of y is asserted.",
        ]
        problem = {
            "claim": ["An older short claim."],
            "statement": statement,
            "assumptions": ["A particular test takes x=1."],
            "analysis": ["### Source claim", "An older report paraphrase."],
        }
        before = copy.deepcopy(problem)
        self.assertEqual(statement_paragraphs(problem), statement)
        self.assertEqual(
            verification_assumptions(problem), ["A particular test takes x=1."]
        )
        self.assertEqual(problem, before)

    def test_explicit_source_assumptions_are_used_without_inventing_connectives(self):
        problem = {
            "claim": [r"For every \(x\in X\), \(f(x)>0\)."],
            "assumptions": ["X is compact.", "No connectedness is assumed."],
            "assumptions_role": "source",
        }
        self.assertEqual(
            statement_paragraphs(problem), problem["assumptions"] + problem["claim"]
        )
        self.assertEqual(verification_assumptions(problem), [])

    def test_math0391_original_hypotheses_remain_separate_complete_paragraphs(self):
        claim = "Lemma 6.7 asserts a positivity extension for representations."
        definition = (
            r"In Definition 6.3, for every loxodromic \(\gamma\in\Gamma\), "
            r"\(\tau(\gamma)\) has a positive eigenvalue of maximal modulus. "
            "Simplicity of that eigenvalue is not required."
        )
        hypotheses = (
            r"Lemma 6.7 assumes that \(\Gamma\) is a Zariski-dense subgroup, "
            r"that \(G'\subset G\) is an open subsemigroup meeting \(\Gamma\), "
            r"and that \(\tau\) is positively \((\Gamma\cap G')\)-semi-proximal. "
            "There is no irreducibility hypothesis."
        )
        first = {"id": "p1", "source_finding_id": "P1", "claim": [claim]}
        second = {"id": "p2", "source_finding_id": "P2", "claim": ["Second claim."]}
        note = {
            "problems": [first, second],
            "report": [
                "# Shared introductory material",
                "## Original hypotheses",
                "A different introductory scope must not be borrowed.",
                "# The reducible positivity extension",
                "Problem 1 (The deletion rule). The review identifies a defect.",
                "## Original hypotheses",
                definition,
                hypotheses,
                "## A counterexample satisfying all of these conditions",
                "Take the product group and a particular matrix A.",
                "# The next finding",
                "Problem 2 (Boundary extension). A separate claim is checked.",
                "## Original hypotheses",
                "The boundary map is strictly contracting in the interior.",
            ],
        }
        before = copy.deepcopy(note)
        self.assertEqual(
            statement_paragraphs(copy.deepcopy(first), note),
            [claim, definition, hypotheses],
        )
        self.assertEqual(note, before)

    def test_report_uses_explicit_source_number_instead_of_catalog_position(self):
        problem = {
            "id": "p1",
            "source_finding_id": "F03",
            "claim": ["The third source finding."],
        }
        note = {
            "problems": [problem],
            "report": [
                "# F03: the source finding",
                "## Source claim",
                "For every finite-dimensional vector space V, the map is defined.",
                "## Proof",
                "The witness has dimension two.",
            ],
        }
        self.assertEqual(
            statement_paragraphs(problem, note),
            problem["claim"]
            + ["For every finite-dimensional vector space V, the map is defined."],
        )

    def test_ambiguous_or_incomplete_report_mapping_falls_back(self):
        problem = {"id": "p1", "claim": ["The retained claim."]}
        for report in (
            ["# Problem 2", "## Source claim", "Wrong numbered claim."],
            [
                "# Problem 1",
                "## Source claim",
                "First version.",
                "# Problem 1",
                "## Source claim",
                "Repeated version.",
            ],
            [
                "# Problem 1",
                "## Source claim",
                "First claim.",
                "# Problem 2",
                "## Source claim",
                "Unexpected additional finding.",
            ],
        ):
            with self.subTest(report=report):
                self.assertEqual(
                    statement_paragraphs(
                        problem, {"problems": [problem], "report": report}
                    ),
                    problem["claim"],
                )

    def test_unbound_same_title_cannot_borrow_a_report_statement(self):
        problem = {"id": "external", "title": "Same title", "claim": ["Known claim."]}
        note = {
            "problems": [{"id": "p1", "title": "Same title"}],
            "report": ["# Problem 1", "## Original hypotheses", "Another scope."],
        }
        self.assertEqual(statement_paragraphs(problem, note), problem["claim"])

    def test_local_source_heading_keeps_formula_and_stops_at_proof(self):
        paragraph = (
            r"For all \(t>0\), the printed formula is"
            "\n"
            r"\[P(t)=P(0)+\int_0^t g(s)^2\,ds.\]"
            " No zero-drift restriction appears in the statement."
        )
        problem = {
            "claim": [paragraph],
            "analysis": [
                "### Source claim (paraphrase)",
                paragraph,
                "### Exact check and correction",
                "Choose a drift of -x/2.",
            ],
        }
        self.assertEqual(statement_paragraphs(problem), [paragraph])

    def test_nested_original_heading_in_repair_or_witness_is_not_a_source_block(self):
        for context in ("Counterexample", "Possible revision", "Proof", "Verification"):
            with self.subTest(context=context):
                problem = {
                    "claim": ["Original broad claim."],
                    "analysis": [
                        "## " + context,
                        "### Original hypotheses",
                        "Choose x=1 and impose the new missing bound.",
                    ],
                }
                self.assertEqual(statement_paragraphs(problem), problem["claim"])

    def test_mixed_claim_and_check_heading_is_not_automatically_promoted(self):
        problem = {
            "claim": ["Original claim."],
            "analysis": [
                "### Source claim and complete static check",
                "The paper makes a claim. The computed witness then contradicts it.",
                "Source claim. A mixed inline paragraph also includes the check.",
            ],
        }
        self.assertEqual(statement_paragraphs(problem), problem["claim"])

    def test_icml0317_witness_parameters_and_repair_stay_out(self):
        problem = {
            "claim": [
                "Low-resolution DCT approximates a scaled low-frequency coefficient "
                "for an arbitrary matrix."
            ],
            "assumptions": [
                "B=2",
                "Orthonormal DCT-II",
                "Pixel background 128 and coefficient D(3,0)=64",
            ],
            "analysis": [
                "#### Exact finite-dimensional derivation",
                "Set B=2 and the single non-DC coefficient to D(3,0)=64.",
                "#### Repair and scope",
                "If every high-frequency coefficient vanishes, the formula is exact.",
            ],
            "repair": {
                "paragraphs": ["Require vanishing high-frequency coefficients."]
            },
        }
        self.assertEqual(statement_paragraphs(problem), problem["claim"])
        self.assertEqual(verification_assumptions(problem), problem["assumptions"])

    def test_neurips0002_witness_and_missing_step_size_restriction_stay_out(self):
        problem = {
            "claim": [
                "Theorem 4.1/Theorem B.3 assert the bound without the restriction "
                "later used in the proof."
            ],
            "assumptions": [],
            "analysis": [
                "### Analysis",
                "Choose d=q=b=b'=1 and alpha=0.9.",
                "### Proposed correction",
                "State and enforce alpha L eta < 1.",
            ],
        }
        self.assertEqual(statement_paragraphs(problem), problem["claim"])

    def test_standalone_tex_role_headings_preserve_paragraph_boundary(self):
        problem = {
            "claim": ["The source claim."],
            "analysis": [
                r"\subsection*{Original hypotheses}",
                "Assume X is compact.",
                r"\paragraph{Counterexample}",
                "Choose a particular finite X.",
            ],
        }
        self.assertEqual(
            statement_paragraphs(problem), ["The source claim.", "Assume X is compact."]
        )

    def test_unparsed_tex_problem_environment_is_not_guessed_or_crossed(self):
        problem = {"id": "p1", "claim": ["The retained claim."]}
        note = {
            "problems": [problem],
            "report": [
                r"\begin{problem}[A source finding]",
                r"\paragraph{Original hypotheses}",
                "Unbound raw hypotheses.",
                r"\end{problem}",
            ],
        }
        self.assertEqual(statement_paragraphs(problem, note), problem["claim"])

    def test_raw_environment_in_analysis_cannot_hide_a_nested_witness_role(self):
        problem = {
            "claim": ["The retained claim."],
            "analysis": [
                r"\begin{counterexample}",
                r"\paragraph{Original hypotheses}",
                "These parameters belong to the witness.",
                r"\end{counterexample}",
            ],
        }
        self.assertEqual(statement_paragraphs(problem), problem["claim"])

    def test_report_problem_marker_under_a_repair_heading_is_not_source_scope(self):
        problem = {"id": "p1", "claim": ["The retained claim."]}
        note = {
            "problems": [problem],
            "report": [
                "# Proposed correction",
                "## Problem 1",
                "### Original hypotheses",
                "A rewritten statement for the repair.",
            ],
        }
        self.assertEqual(statement_paragraphs(problem, note), problem["claim"])


if __name__ == "__main__":
    unittest.main()
