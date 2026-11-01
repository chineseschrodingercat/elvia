"""Problem-bound revision extraction; synthetic statements test no mathematics."""

import copy
import unittest

from elvia.revision_display import possible_revision


class RevisionDisplayTests(unittest.TestCase):
    def test_explicit_revision_has_priority_and_inputs_remain_unchanged(self):
        problem = {
            "repair": {
                "paragraphs": ["Use the exact replacement recorded by the report."]
            },
            "analysis": ["The repair is to use a different temporary construction."],
            "result": [],
        }
        before = copy.deepcopy(problem)
        self.assertEqual(possible_revision(problem), problem["repair"]["paragraphs"])
        self.assertEqual(problem, before)

    def test_concrete_actions_are_retained_even_when_the_global_repair_is_unproved(
        self,
    ):
        proposals = [
            "The repair is to replace the denominator by n - 1.",
            "Replacing the denominator by n - 1 restores the checked identity. "
            "No complete global repair is certified here.",
            "The corrected local formula is y = 2x, rather than y = x.",
            "Repair: Require x > 0, or retain the boundary case "
            "as a separate statement.",
            "A repair must restrict the domain to x > 0 and handle x = 0 separately.",
        ]
        for paragraph in proposals:
            with self.subTest(paragraph=paragraph):
                self.assertEqual(
                    possible_revision(
                        {"repair": None, "analysis": [paragraph], "result": []}
                    ),
                    [paragraph],
                )

    def test_negated_repairs_and_negated_report_claims_are_not_proposals(self):
        non_proposals = [
            "Changing this normalization cannot repair the estimate.",
            "Removing empty words alone does not repair the dead automaton.",
            "Restricting to smooth inputs does not restore a uniform estimate.",
            "Adding that equality would not repair the missing covariance identities.",
            "This report does not claim that adding equidimensionality alone proves "
            "the desired descent, nor that the original argument becomes correct.",
            "Simply adding sigma(0) = 0 has not been verified as a complete repair.",
        ]
        for paragraph in non_proposals:
            with self.subTest(paragraph=paragraph):
                self.assertEqual(
                    possible_revision(
                        {"repair": None, "analysis": [paragraph], "result": []}
                    ),
                    [],
                )

    def test_unspecified_future_work_and_missing_proofs_do_not_create_a_revision(self):
        non_proposals = [
            "A complete correction requires rechecking the energy argument and all "
            "transferred estimates. No such full repair is claimed here.",
            "A complete repair must recheck the local matrix, analyticity, matching, "
            "all remaining jumps, and small-norm estimates. "
            "It is not established here.",
            "A repair must prove an appropriate conditional or averaged multi-scale "
            "estimate under the actual exposed edge set. "
            "No replacement is verified here.",
            "The specification must be corrected before the example can be reproduced. "
            "There is no uniquely justified numerical repair.",
            "A repair must state a defensible loss/class restriction and rederive "
            "constants. No repaired generalization theorem is supplied.",
            "Either a component or the total should be corrected from the construction "
            "manifest; the acquired source does not resolve which.",
        ]
        for paragraph in non_proposals:
            with self.subTest(paragraph=paragraph):
                self.assertEqual(
                    possible_revision(
                        {"repair": None, "analysis": [], "result": [paragraph]}
                    ),
                    [],
                )

    def test_a_real_proposal_and_its_negative_scope_sentence_stay_together(self):
        paragraph = (
            "Replacing the denominator by n - 1 restores this local identity. "
            "Changing the notation alone does not repair the larger proof. "
            "No complete replacement theorem is claimed."
        )
        self.assertEqual(
            possible_revision(
                {"repair": None, "analysis": [paragraph], "result": [paragraph]}
            ),
            [paragraph],
        )

    def test_a_proposal_never_leaks_into_a_different_problem(self):
        first = {
            "analysis": ["The repair is to replace the coefficient by 2."],
            "result": [],
        }
        second = {
            "analysis": ["The second claim remains unresolved."],
            "result": ["No correction was supplied for this finding."],
        }
        self.assertEqual(possible_revision(first), first["analysis"])
        self.assertEqual(possible_revision(second), [])
        self.assertEqual(
            possible_revision({"repair": None, "analysis": [], "result": []}), []
        )


if __name__ == "__main__":
    unittest.main()
