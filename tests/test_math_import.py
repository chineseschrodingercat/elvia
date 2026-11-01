"""Regressions for the separately accepted Math 2025 publication boundary."""

import hashlib
import json
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def importer():
    return runpy.run_path(str(ROOT / "scripts/import_math2025.py"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_only_integrity_accepted_ids_enter_publication(importer):
    state = {
        "accepted": 1,
        "accepted_paper_ids": ["M25-0001"],
        "accepted_integrity_records": {"M25-0001": {}},
        "acceptance_ready_records": {"M25-0001": {}, "M25-0002": {}},
    }
    assert importer["selected_ids"](state) == ["M25-0001"]
    state["accepted_paper_ids"].append("M25-0001")
    with pytest.raises(ValueError, match="accepted"):
        importer["selected_ids"](state)


def test_version_is_bound_to_exact_pdf_not_placeholder(importer):
    manifest = {
        "files": [
            {"relative_path": "papers/0001/old.pdf", "version": "old"},
            {
                "relative_path": "papers/0001/0001.pdf",
                "version": "arXiv:1234.5678v3",
                "sha256": "a" * 64,
                "source_url": "https://example.org/exact.pdf",
            },
        ]
    }
    assert importer["source_entry"](manifest, "0001")["version"] == "arXiv:1234.5678v3"
    manifest["files"][1]["version"] = ""
    with pytest.raises(ValueError, match="version"):
        importer["source_entry"](manifest, "0001")


def test_overrides_are_bound_to_both_scientific_inputs(importer):
    findings = {"judgment": {"judgment": "No Issue Found"}, "needs_evidence": [{}]}
    row = {
        "rating": "no_issue_found",
        "basis": "Explicit paper-level judgment.",
        "findings_sha256": "a" * 64,
        "report_tex_sha256": "b" * 64,
    }
    assert (
        importer["reviewed_rating"](
            "M25-0001",
            findings,
            {"findings": "a" * 64, "tex": "b" * 64},
            {"M25-0001": row},
        )
        == "no_issue_found"
    )
    with pytest.raises(ValueError, match="classification"):
        importer["reviewed_rating"](
            "M25-0001",
            findings,
            {"findings": "c" * 64, "tex": "b" * 64},
            {"M25-0001": row},
        )


def test_private_workflow_removed_but_counterevidence_and_math_preserved(importer):
    data = {
        "acceptance_token": "private",
        "original_conversation_url": "private",
        "finding": {
            "claim": r"\(C:\Omega\to\mathbb R\)",
            "counterevidence": "The interior application survives.",
            "repair": "Require compact containment.",
        },
        "evidence": (
            r"D:\ELVIA report raw\Math 15 journals\2025"
            r"\verification\0001\evidence.json"
        ),
    }
    cleaned = importer["public_data"](data)
    assert "acceptance_token" not in cleaned
    assert "original_conversation_url" not in cleaned
    assert cleaned["finding"] == data["finding"]
    assert cleaned["evidence"] == "verification/0001/evidence.json"


def test_separate_severity_containers_keep_scientific_findings(importer):
    result = importer["finding_items"](
        {
            "major": [{"id": "F1", "claim": "A"}],
            "minor": [{"id": "F2", "claim": "B"}],
            "rejected_candidates": [{"id": "F3", "claim": "C"}],
        }
    )
    assert [(x["id"], x["severity"]) for x in result] == [
        ("F1", "major"),
        ("F2", "minor"),
    ]


def test_accepted_receipt_cannot_hide_changed_current_file(importer, tmp_path):
    raw = tmp_path / "raw"
    snapshot = raw / "snapshot"
    paths = importer["core_paths"]("0001")
    artifacts = []
    for relative in paths.values():
        live = raw / relative
        frozen = snapshot / relative
        live.parent.mkdir(parents=True, exist_ok=True)
        frozen.parent.mkdir(parents=True, exist_ok=True)
        live.write_bytes(b"accepted")
        frozen.write_bytes(b"accepted")
        artifacts.append({"path": relative, "bytes": 8, "sha256": digest(live)})
    receipt = snapshot / "acceptance_integrity_receipt.json"
    put(receipt, {"paper_id": "M25-0001", "artifacts": artifacts})
    binding = {
        "snapshot_root": str(snapshot),
        "receipt_path": str(receipt),
        "receipt_sha256": digest(receipt),
    }
    importer["verify_core"](raw, "M25-0001", binding)
    (raw / paths["tex"]).write_bytes(b"changed")
    with pytest.raises(ValueError, match="integrity"):
        importer["verify_core"](raw, "M25-0001", binding)


def test_structured_version_keeps_preprint_equivalence_limit(importer):
    entry = importer["source_entry"](
        {
            "files": [
                {
                    "relative_path": "papers/0001/0001.pdf",
                    "version": {
                        "kind": "author_manuscript_arxiv",
                        "arxiv_version": "1234.5678v3",
                        "journal_version_equivalence_verified": False,
                    },
                }
            ]
        },
        "0001",
    )
    assert "1234.5678v3" in entry["version"]
    assert "not established" in entry["version"]
    assert entry["version_details"]["journal_version_equivalence_verified"] is False


@pytest.mark.parametrize(
    ("item", "expected"),
    [
        ({"category": "Needs Evidence"}, "needs_evidence"),
        ({"severity": "NeedsEvidence"}, "needs_evidence"),
        ({"severity": None, "classification": "scope_clarification"}, "no_issue_found"),
        ({"impact": "Could be Major if the missing premise fails."}, None),
        ({"independent_verification": {"severity": "Minor"}}, "minor"),
    ],
)
def test_finding_labels_do_not_infer_hypothetical_severity(importer, item, expected):
    assert importer["finding_rating"](item) == expected


def test_public_repository_uuid_remains_a_valid_source_identity(importer):
    url = "https://ora.example.org/objects/uuid%3A12345678-abcd-abcd-abcd-123456789abc/file.pdf"
    assert importer["public_text"](url) == url
    assert url in importer["report_text"]("Source: " + url)
    private = "https://chatgpt.com/c/12345678-abcd-abcd-abcd-123456789abc"
    assert private not in importer["public_text"](private)
