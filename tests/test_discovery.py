"""Synthetic discovery fixtures; none of these texts is research evidence."""

import copy
import hashlib
import json

import pytest

from elvia.discovery import (
    case_payload,
    compact_search_payload,
    discovery_payload,
    search_payload,
    write_discovery_files,
)

COLLECTION = "b" * 64
MAPS = ("presentation", "case_notes", "reader", "research_fields", "reader_bundles")


@pytest.fixture
def payload():
    record = {
        "case_id": "synthetic-discovery-001",
        "revision": 2,
        "source": {
            "title": "Synthetic title with a symbolic expression",
            "version": "v2",
            "doi": "10.1234/source-identifier",
            "arxiv_id": "0000.00001",
            "review_scope": "Distinct source scope words",
            "artifact": "source.txt",
        },
        "audit": {
            "venue": "Synthetic venue",
            "year": 2026,
            "outcome": "candidate_issue",
            "summary": "Archived assessment: Major. Exact synthetic summary.",
            "authors": ["Fictional Author"],
            "landing_url": "https://example.org/synthetic-paper",
            "limitations": ["A deliberately bounded synthetic limitation."],
            "pdf_sha256": "a" * 64,
        },
        "concern": {
            "severity": "moderate",
            "description": "Distinct synthetic concern text",
        },
        "adjudication": {"status": "pending", "decision": None},
        "proposition": {
            "claim": "A complete original proposition with quantifiers.",
            "location": "Synthetic Theorem 2",
            "assumptions": ["Original recorded condition"],
            "dependencies": ["support-1"],
        },
        "evidence": [{"id": "support-1", "description": "Full evidence retained"}],
        "repair": {"verification": "Original repair verification retained"},
    }
    note = {
        "revision": 2,
        "brief": ["First exact brief.", "Second exact brief with $x$ and its scope."],
        "report": ["UniqueReportOnlyToken appears only in the complete report."],
        "review_scope": ["Complete original review scope"],
        "source_quotes": [{"text": "Exact synthetic quotation", "locator": "p. 2"}],
        "problems": [
            {
                "title": "Supported reasoning, excluded from problem numbering",
                "severity": "major",
                "assessment": "not_issue",
                "claim": ["Supported synthetic statement"],
                "assumptions": [],
                "analysis": ["Retained counterevidence"],
                "result": ["Supported within scope"],
                "source_location": "Synthetic section 1",
            },
            {
                "id": "original-finding-7",
                "title": "Visible synthetic finding",
                "severity": "major",
                "assessment": "candidate_issue",
                "claim": ["Exact original claim"],
                "statement": ["Complete source-bound statement with all conditions"],
                "assumptions": ["Exact original hypothesis"],
                "analysis": ["Exact full argument and counterexample"],
                "result": ["Exact result and unresolved boundary"],
                "source_location": "Synthetic Lemma 7, PDF pages 4, 9",
                "repair": {
                    "paragraphs": ["Exact original proposed revision"],
                    "verification": "Not independently verified",
                },
            },
        ],
    }
    case_id = record["case_id"]
    presentation = {
        "revision": 2,
        "record_sha256": "c" * 64,
        "replacements": [
            {"source": record["source"]["title"], "typeset": "Synthetic $x$ title"},
            {"source": record["audit"]["summary"], "typeset": "Synthetic $x$ summary"},
            {"source": " ".join(note["brief"]), "typeset": "Synthetic $x$ brief"},
            {"source": record["proposition"]["claim"], "typeset": "Proof-only $x$"},
        ],
    }
    return {
        "format_version": "1",
        "case_count": 1,
        "counts": {"candidate_issue": 1, "no_issue_found": 0},
        "records": [record],
        "presentation": {case_id: presentation},
        "case_notes": {case_id: note},
        "reader": {
            case_id: {
                "revision": 2,
                "citation": {
                    "doi": "10.1234/reader-only-identifier",
                    "title": record["source"]["title"],
                    "authors": ["Fictional Author"],
                },
                "contributors": [
                    {"name": "Fictional Contributor", "role": "report author"}
                ],
            }
        },
        "research_fields": {case_id: "Mathematics"},
        "reader_bundles": {case_id: "evidence/" + case_id + ".zip"},
    }


def test_discovery_preserves_list_values_without_complete_scientific_text(payload):
    result = discovery_payload(payload, COLLECTION)
    record = payload["records"][0]
    case_id = record["case_id"]
    projected = result["records"][0]
    assert result["format_version"] == "1"
    assert result["payload_kind"] == "discovery"
    assert result["collection_id"] == COLLECTION
    assert result["case_count"] == payload["case_count"]
    assert result["counts"] == payload["counts"]
    assert result["research_fields"] == payload["research_fields"]
    assert projected["case_id"] == case_id
    assert projected["revision"] == record["revision"]
    assert projected["source"]["title"] == record["source"]["title"]
    for key in ("venue", "year", "outcome", "summary"):
        assert projected["audit"][key] == record["audit"][key]
    assert projected["concern"]["severity"] == "moderate"
    assert projected["adjudication"]["status"] == "pending"
    assert (
        result["case_notes"][case_id]["brief"]
        == payload["case_notes"][case_id]["brief"]
    )
    assert result["case_notes"][case_id]["problems"] == [
        {"severity": "major", "assessment": "not_issue"},
        {"severity": "major", "assessment": "candidate_issue"},
    ]
    assert "proposition" not in projected
    assert "evidence" not in projected
    assert "report" not in result["case_notes"][case_id]
    assert all(
        "analysis" not in item for item in result["case_notes"][case_id]["problems"]
    )
    replacements = result["presentation"][case_id]["replacements"]
    assert replacements == payload["presentation"][case_id]["replacements"][:3]


def test_search_preserves_every_current_retrieval_input(payload):
    result = search_payload(payload, COLLECTION)
    record, actual = payload["records"][0], result["records"][0]
    case_id = record["case_id"]
    assert result["payload_kind"] == "search"
    assert result["collection_id"] == COLLECTION
    for group, keys in {
        "source": ("title", "version", "doi", "arxiv_id", "review_scope"),
        "audit": (
            "authors",
            "venue",
            "year",
            "landing_url",
            "summary",
            "limitations",
            "outcome",
        ),
        "proposition": ("claim", "location"),
        "concern": ("description", "severity"),
    }.items():
        for key in keys:
            assert actual[group][key] == record[group][key]
    assert result["research_fields"] == payload["research_fields"]
    note = result["case_notes"][case_id]
    original = payload["case_notes"][case_id]
    assert note["revision"] == original["revision"]
    assert note["report"] == original["report"]
    assert len(note["problems"]) == len(original["problems"])
    for actual_problem, problem in zip(
        note["problems"], original["problems"], strict=True
    ):
        for key in (
            "title",
            "source_location",
            "claim",
            "assumptions",
            "analysis",
            "result",
            "severity",
            "assessment",
        ):
            assert actual_problem[key] == problem[key]
        if problem.get("repair"):
            assert (
                actual_problem["repair"]["paragraphs"]
                == problem["repair"]["paragraphs"]
            )
    assert (
        result["reader"][case_id]["revision"] == payload["reader"][case_id]["revision"]
    )
    assert (
        result["reader"][case_id]["citation"]["doi"]
        == payload["reader"][case_id]["citation"]["doi"]
    )


@pytest.mark.parametrize("outcome", ["no_issue_found", "scope_clarification"])
def test_search_keeps_complete_report_for_cases_without_numbered_problems(
    payload, outcome
):
    payload["records"][0]["audit"]["outcome"] = outcome
    case_id = payload["records"][0]["case_id"]
    result = search_payload(payload, COLLECTION)
    assert (
        result["case_notes"][case_id]["report"]
        == payload["case_notes"][case_id]["report"]
    )


def test_case_projection_keeps_all_original_fields_and_no_other_case(payload):
    record = payload["records"][0]
    case_id = record["case_id"]
    other = copy.deepcopy(record)
    other["case_id"] = "synthetic-discovery-002"
    payload["records"].append(other)
    for key in MAPS:
        payload[key][other["case_id"]] = copy.deepcopy(payload[key][case_id])
    result = case_payload(payload, record, COLLECTION)
    assert result["payload_kind"] == "case"
    assert result["collection_id"] == COLLECTION
    assert result["case_id"] == case_id
    assert result["revision"] == record["revision"]
    assert result["records"] == [record]
    for key in MAPS:
        assert result[key] == {case_id: payload[key][case_id]}


def test_projection_does_not_mutate_the_complete_payload(payload):
    before = copy.deepcopy(payload)
    discovery_payload(payload, COLLECTION)
    search_payload(payload, COLLECTION)
    compact_search_payload(payload, COLLECTION)
    case_payload(payload, payload["records"][0], COLLECTION)
    assert payload == before


def test_discovery_and_search_do_not_reuse_stale_revision_metadata(payload):
    case_id = payload["records"][0]["case_id"]
    for key in ("case_notes", "presentation", "reader"):
        payload[key][case_id]["revision"] = 1
    compact = discovery_payload(payload, COLLECTION)
    search = search_payload(payload, COLLECTION)
    assert case_id not in compact["case_notes"]
    assert case_id not in compact["presentation"]
    assert case_id not in search["case_notes"]
    assert case_id not in search["reader"]
    assert (
        compact["records"][0]["audit"]["summary"]
        == payload["records"][0]["audit"]["summary"]
    )


@pytest.mark.parametrize("kind", ["discovery", "search", "case"])
def test_projection_rejects_a_missing_collection_binding(payload, kind):
    with pytest.raises(ValueError):
        if kind == "case":
            case_payload(payload, payload["records"][0], "")
        else:
            {"discovery": discovery_payload, "search": search_payload}[kind](
                payload, ""
            )


def assignment(text, name):
    prefix = "window." + name + " = "
    assert text.startswith(prefix) and text.endswith(";\n")
    return json.loads(text[len(prefix) : -2])


def test_writer_binds_actual_crlf_bytes_and_preserves_existing_complete_files(
    payload, tmp_path
):
    raw = (
        (json.dumps(payload, indent=2, ensure_ascii=True) + "\n")
        .replace("\n", "\r\n")
        .encode()
    )
    (tmp_path / "data.json").write_bytes(raw)
    (tmp_path / "data.js").write_bytes(
        b"complete export bytes must remain unchanged\r\n"
    )
    cases = tmp_path / "cases"
    cases.mkdir()
    case_id = payload["records"][0]["case_id"]
    protected = {
        "data.json": raw,
        "data.js": (tmp_path / "data.js").read_bytes(),
        "cases/"
        + case_id
        + ".js": b"existing complete citation and context script\r\n",
        "cases/"
        + case_id
        + ".context.json": b'{"existing":"contribution identity"}\r\n',
    }
    for relative, contents in protected.items():
        (tmp_path / relative).write_bytes(contents)
    write_discovery_files(tmp_path, payload)
    expected = hashlib.sha256(raw).hexdigest()
    discovery = assignment((tmp_path / "discovery.js").read_text(), "ELVIA_DISCOVERY")
    search = assignment((tmp_path / "search-data.js").read_text(), "ELVIA_SEARCH_DATA")
    assert discovery == json.loads((tmp_path / "discovery.json").read_text())
    assert discovery["collection_id"] == search["collection_id"] == expected
    case_script = (cases / (case_id + ".data.js")).read_text()
    marker = "window.ELVIA_CASE_DATA[" + json.dumps(case_id) + "] = "
    assert marker in case_script
    actual_case = json.loads(case_script.split(marker, 1)[1].removesuffix(";\n"))
    assert actual_case == case_payload(payload, payload["records"][0], expected)
    for relative, contents in protected.items():
        assert (tmp_path / relative).read_bytes() == contents


def test_generated_scripts_escape_html_delimiters_without_changing_text(
    payload, tmp_path
):
    attack = '</script><script>alert("synthetic fixture")</script>&'
    payload["records"][0]["source"]["title"] = attack
    (tmp_path / "data.json").write_text(json.dumps(payload), encoding="utf-8")
    (tmp_path / "cases").mkdir()
    write_discovery_files(tmp_path, payload)
    for path in (
        tmp_path / "discovery.js",
        tmp_path / "search-data.js",
        *tmp_path.glob("cases/*.data.js"),
    ):
        text = path.read_text()
        assert "</script>" not in text
        assert "<" not in text and ">" not in text and "&" not in text
    for filename, name in (
        ("discovery.js", "ELVIA_DISCOVERY"),
        ("search-data.js", "ELVIA_SEARCH_DATA"),
    ):
        projected = assignment((tmp_path / filename).read_text(), name)
        assert projected["records"][0]["source"]["title"] == attack


def test_build_publishes_bound_discovery_in_the_signed_manifest(valid_record, tmp_path):
    from elvia.site import build_site
    from elvia.storage import save_record

    record = copy.deepcopy(valid_record)
    record.update(schema_version="1.1.0", case_type="prospective_audit")
    record["publication"] = {
        "status": "preliminary_ai",
        "note": "Synthetic software fixture only.",
    }
    record["audit"] = {
        "venue": "Fixture venue",
        "year": 2026,
        "authors": ["Fictional fixture"],
        "landing_url": "https://example.org/fixture",
        "pdf_url": "https://example.org/fixture.pdf",
        "pdf_sha256": "a" * 64,
        "retrieved_at": "2026-10-19T00:00:00Z",
        "outcome": "candidate_issue",
        "summary": "Original synthetic software fixture only.",
        "limitations": ["No scientific conclusion; software test only."],
    }
    path = save_record(record, tmp_path / "records")
    original = path.read_bytes()
    output = tmp_path / "site"
    assert build_site(path.parent, output) == 1
    full_bytes = (output / "data.json").read_bytes()
    full = json.loads(full_bytes)
    compact = json.loads((output / "discovery.json").read_text())
    assert full["records"] == [record]
    assert "payload_kind" not in full and "collection_id" not in full
    assert compact["case_count"] == full["case_count"] == 1
    assert compact["counts"] == full["counts"]
    assert compact["collection_id"] == hashlib.sha256(full_bytes).hexdigest()
    assert path.read_bytes() == original
    manifest = json.loads((output / "manifest.json").read_text())
    identities = {row["path"]: row["sha256"] for row in manifest["files"]}
    for name in (
        "discovery.json",
        "discovery.js",
        "search-data.js",
        "cases/" + record["case_id"] + ".data.js",
    ):
        assert (
            identities[name] == hashlib.sha256((output / name).read_bytes()).hexdigest()
        )


def test_compact_search_keeps_all_normalized_sequences_and_finding_positions(payload):
    result = compact_search_payload(payload, COLLECTION)
    projection = result["search_projection"]
    assert projection["encoding"] == "word-sequences-v1"
    case_id = payload["records"][0]["case_id"]
    assert "case_notes" not in result
    fields = projection["documents"][case_id]["fields"]

    def text(field):
        return " ".join(
            " ".join(
                projection["vocabulary"][int(word, 36)]
                for word in projection["chunks"][chunk].split()
            )
            for chunk in field[0]
        )

    assert (
        text(fields[0]) == "uniquereportonlytoken appears only in the complete report"
    )
    assert fields[0][1:3] == [1, "complete retained report"]
    assert fields[1][1:] == [5, "Problem 1", 2, "Visible synthetic finding", 1]
    assert text(fields[2]) == (
        "synthetic lemma 7 pdf pages 4 9 exact original claim "
        "exact original hypothesis "
        "exact full argument and counterexample exact result and unresolved boundary "
        "exact original proposed revision"
    )
    assert all("supported synthetic statement" not in text(field) for field in fields)
    assert result["records"] == search_payload(payload, COLLECTION)["records"]


@pytest.mark.parametrize("outcome", ["no_issue_found", "scope_clarification"])
def test_compact_search_keeps_report_only_cases_and_ignores_stale_notes(
    payload, outcome
):
    record = payload["records"][0]
    record["audit"]["outcome"] = outcome
    result = compact_search_payload(payload, COLLECTION)
    fields = result["search_projection"]["documents"][record["case_id"]]["fields"]
    assert len(fields) == 1
    assert fields[0][1:3] == [1, "complete retained report"]
    payload["case_notes"][record["case_id"]]["revision"] -= 1
    stale = compact_search_payload(payload, COLLECTION)
    assert record["case_id"] not in stale["search_projection"]["documents"]
    assert stale["search_projection"]["vocabulary"] == []
