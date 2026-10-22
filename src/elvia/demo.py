"""An original, offline exact-arithmetic demonstration; no scientific review."""

import hashlib
import platform
import shutil
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path

from elvia.storage import save_record


def create_demo(output: Path) -> Path:
    """Create a fresh synthetic dataset and return its pending record path.

    Exact arithmetic executes locally; no model, API, or human review is run.
    Text artifacts use explicit LF bytes, so hashes survive clean checkouts.
    """
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    try:
        started = datetime.now(UTC).isoformat()
        x = Fraction(1, 2)
        difference = x * x - x
        source = (
            "# Original synthetic proposition, version 1\n\n"
            "Claim: For all real x, x² >= x.\n"
            "Domain: real numbers. No additional assumptions.\n"
            "This text was created for ELVIA's software demonstration.\n"
            "It is not a paper, citation, or finding about an external author.\n"
        )
        result = (
            "Original ELVIA exact-arithmetic demonstration\n"
            f"x = {x}\nx² = {x * x}\nx² - x = {difference}\n"
            "The negative exact difference supplies a counterexample to the\n"
            "displayed universal claim. This is a tool computation, not human\n"
            "adjudication; the workflow decision remains pending.\n\n"
            "Repair candidate: restrict the domain to x <= 0 or x >= 1.\n"
            "Derivation: x² - x = x(x - 1). For x <= 0 both factors are\n"
            "nonpositive; for x >= 1 both factors are nonnegative.\n"
            "The derivation is supplied for review; this execution checks only\n"
            "the exact counterexample, not universal repair validity.\n"
            "Repair verification remains pending. Author adoption is not\n"
            "applicable: this is original synthetic material, with no author contact.\n"
        )

        def artifact(relative, text):
            path = output / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = text.encode("utf-8")
            path.write_bytes(payload)
            return {"path": relative, "sha256": hashlib.sha256(payload).hexdigest()}

        source_artifact = artifact("source/proposition.md", source)
        evidence_artifact = artifact("evidence/exact-counterexample.txt", result)
        ended = datetime.now(UTC).isoformat()
        record = {
            "schema_version": "1.0.0",
            "case_id": "synthetic-quadratic-001",
            "revision": 1,
            "previous_revision": None,
            "case_type": "synthetic_demo",
            "created_at": ended,
            "source": {
                "title": "Original synthetic quadratic proposition",
                "version": "1",
                "doi": None,
                "arxiv_id": None,
                "identifier_note": (
                    "Original demonstration; no DOI or arXiv identifier."
                ),
                "artifact": source_artifact,
                "review_scope": "Only the displayed synthetic universal claim.",
            },
            "proposition": {
                "claim": "For all real x, x² >= x.",
                "domain": "Real numbers",
                "assumptions": [],
                "location": "source/proposition.md, Claim",
                "dependencies": [],
            },
            "concern": {
                "description": "At x = 1/2, the exact difference x² - x is -1/4.",
                "type": "counterexample",
                "severity": "major",
                "impact": "main_result",
                "origin": "software",
            },
            "evidence": [
                {
                    "id": "exact-counterexample",
                    "stance": "support",
                    "description": (
                        "Exact counterexample plus a separate restricted-domain "
                        "repair derivation supplied for review."
                    ),
                    "method": "Python fractions.Fraction exact rational arithmetic",
                    "artifact": evidence_artifact,
                }
            ],
            "runs": [
                {
                    "id": "exact-fraction-run",
                    "tool": "Python fractions.Fraction",
                    "tool_version": platform.python_version(),
                    "model": None,
                    "model_note": (
                        "No model executed: this offline demonstration uses only "
                        "local exact arithmetic. Known API cost is zero."
                    ),
                    "config_version": "elvia-demo-v1",
                    "started_at": started,
                    "ended_at": ended,
                    "output_artifacts": [evidence_artifact],
                    "cost_usd": 0,
                }
            ],
            "human_reviews": [],
            "adjudication": {
                "status": "pending",
                "rationale": "Exact computation is separate from human adjudication.",
                "history": [],
            },
            "repair": {
                "content": "For real x with x <= 0 or x >= 1, x² >= x.",
                "verification_status": "pending",
                "verification_refs": [],
                "changed_assumptions": ["x <= 0 or x >= 1"],
                "changed_conclusion": None,
                "adoption_status": "not_requested",
            },
            "publication": {
                "status": "synthetic_demo",
                "note": (
                    "Original software demonstration only. No human review or "
                    "scientific signing; author adoption is not applicable."
                ),
            },
        }
        return save_record(record, output / "records")
    except BaseException:
        shutil.rmtree(output)
        raise
