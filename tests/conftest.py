"""Original synthetic records; no real people, citations or scientific findings."""

import hashlib

import pytest


@pytest.fixture
def valid_record(tmp_path):
    source = tmp_path / "source.txt"
    source.write_bytes(b"Synthetic source: every positive x is at least one.\n")
    evidence = tmp_path / "evidence.txt"
    evidence.write_bytes(b"Exact counterexample: x=1/2.\n")
    return {
        "schema_version": "1.0.0",
        "case_id": "synthetic-001",
        "revision": 1,
        "previous_revision": None,
        "case_type": "synthetic_demo",
        "created_at": "2026-10-19T00:00:00Z",
        "source": {
            "title": "Original synthetic proposition",
            "version": "1",
            "doi": None,
            "arxiv_id": None,
            "identifier_note": "Original synthetic text; no external identifiers.",
            "artifact": {
                "path": "source.txt",
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            },
            "review_scope": "The single displayed universal claim only.",
        },
        "proposition": {
            "claim": "Every positive rational x is at least one.",
            "domain": "Positive rational numbers",
            "assumptions": ["x > 0"],
            "location": "Synthetic source, sentence 1",
            "dependencies": [],
        },
        "concern": {
            "description": "One half contradicts the universal claim.",
            "type": "counterexample",
            "severity": "major",
            "impact": "main_result",
            "origin": "ai",
        },
        "evidence": [
            {
                "id": "ev-1",
                "stance": "support",
                "description": "Original exact rational counterexample.",
                "method": "Exact rational arithmetic",
                "artifact": {
                    "path": "evidence.txt",
                    "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
                },
            }
        ],
        "runs": [],
        "human_reviews": [],
        "adjudication": {
            "status": "pending",
            "rationale": "Awaiting human review.",
            "history": [],
        },
        "repair": {
            "content": None,
            "verification_status": "not_proposed",
            "verification_refs": [],
            "changed_assumptions": [],
            "changed_conclusion": None,
            "adoption_status": "not_requested",
        },
        "publication": {
            "status": "synthetic_demo",
            "note": "Software demonstration only.",
        },
    }


@pytest.fixture
def human_review():
    return {
        "reviewer_id": "synthetic-reviewer-a",
        "role": "domain_reviewer",
        "independent": True,
        "domain_review": True,
        "decision": "confirmed",
        "rationale": "Synthetic declaration for workflow testing.",
        "evidence_refs": ["ev-1"],
    }
