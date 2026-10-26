"""Derived, public-only citations and bounded context from validated snapshots.

This module does not infer authorship, adjudication or scientific conclusions.
Finding prose is retained verbatim so a shortened view cannot drop its scope.
"""

from elvia.reader import record_digest


def review_status(record):
    status = record["adjudication"]["status"]
    return (
        "Independent review pending"
        if status == "pending"
        else "Scientific decision: " + status.replace("_", " ")
    )


def finding_brief(record, problem=None):
    title = problem["title"] if problem else record["source"]["title"]
    return {
        "question": f"What does the recorded analysis establish about “{title}”?",
        "answer": problem["result"] if problem else [record["audit"]["summary"]],
        "evidence": problem["analysis"]
        if problem
        else [
            e["description"]
            for e in record["evidence"]
            if e["stance"] == "support" and e["id"] != "editable-latex"
        ],
        "location": problem["source_location"]
        if problem
        else record["proposition"]["location"],
        "limits": record["audit"]["limitations"],
        "status": review_status(record),
    }


def analysis_authors(reader):
    """Only explicit report-writing credit; a reviewer is not an author."""
    roles = {"initial report", "report author", "revision report", "report revision"}
    return list(
        dict.fromkeys(
            p["name"]
            for p in reader.get("contributors", [])
            if p["role"].casefold() in roles
        )
    )


def record_url(record, base):
    path = (
        f"evidence/{record['case_id']}/records/"
        f"{record['case_id']}.r{record['revision']}.json"
    )
    return (base if base else "../") + path


def case_url(record, base, number=None):
    path = f"cases/{record['case_id']}.html"
    return (base + path if base else record["case_id"] + ".html") + (
        f"#problem-{number}" if number is not None else ""
    )


def _line(value):
    return " ".join(str(value).split())


def _bib(value):
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "%": r"\%",
        "&": r"\&",
        "_": r"\_",
        "#": r"\#",
        "$": r"\$",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in _line(value))


def _formats(data):
    authors = data["authors"]
    plain = ("; ".join(authors) + ". " if authors else "") + data["title"] + ". "
    plain += data["container"]
    if data.get("volume"):
        plain += f", vol. {data['volume']}"
    plain += f", {data['year']}"
    if data.get("pages"):
        plain += ", pp. " + data["pages"].replace("--", "–")
    plain += ". "
    if data.get("doi") and data["url"] != "https://doi.org/" + data["doi"]:
        plain += f"https://doi.org/{data['doi']}. "
    plain += data["url"]
    if data.get("note"):
        plain += "\n" + data["note"]
    fields = {
        "title": data["title"],
        "author": " and ".join(authors),
        "year": data["year"],
        "publisher" if data["kind"] == "analysis" else "booktitle": data["container"],
        "volume": data.get("volume"),
        "pages": data.get("pages"),
        "doi": data.get("doi"),
        "url": data["url"],
        "note": data.get("note"),
    }
    entry_type = "misc" if data["kind"] == "analysis" else "inproceedings"

    def bib_field(key, value):
        encoded = _bib(value)
        # Preserve scientific capitalization while escaping any literal braces.
        if key == "title":
            encoded = "{" + encoded + "}"
        return f"  {key} = {{{encoded}}}"

    bibtex = (
        "@"
        + entry_type
        + "{"
        + data["key"]
        + ",\n"
        + ",\n".join(bib_field(key, value) for key, value in fields.items() if value)
        + "\n}\n"
    )
    ris = ["TY  - RPRT" if data["kind"] == "analysis" else "TY  - CONF"]
    ris += ["AU  - " + _line(author) for author in authors]
    for key, value in (
        ("TI", data["title"]),
        ("PY", data["year"]),
        ("PB" if data["kind"] == "analysis" else "T2", data["container"]),
        ("VL", data.get("volume")),
        ("SP", data.get("first_page")),
        ("EP", data.get("last_page")),
        ("DO", data.get("doi")),
        ("UR", data["url"]),
        ("N1", data.get("note")),
    ):
        if value:
            ris.append(f"{key}  - {_line(value)}")
    ris.append("ER  -")
    return {"plain": plain, "bibtex": bibtex, "ris": "\n".join(ris) + "\n"}


def original_citation(record, reader):
    citation = reader.get("citation", {})
    doi = citation.get("doi") or record["source"].get("doi")
    first, last = citation.get("first_page"), citation.get("last_page")
    return _formats(
        {
            "kind": "original",
            "key": record["case_id"] + "-original",
            "authors": citation.get("authors", record["audit"]["authors"]),
            "title": citation.get("title", record["source"]["title"]),
            "container": citation.get("container", record["audit"]["venue"]),
            "year": citation.get("year", record["audit"]["year"]),
            "url": "https://doi.org/" + doi
            if doi
            else citation.get("source_url") or record["audit"]["landing_url"],
            "doi": doi,
            "volume": citation.get("volume"),
            "first_page": first,
            "last_page": last,
            "pages": f"{first}--{last}" if first and last else first,
        }
    )


def context_exports(record, reader, base, problem=None, number=None, *, report=None):
    """Build selected finding or complete-case text with no private/remote input."""
    url = case_url(record, base, number)
    title = "ELVIA analysis of: " + record["source"]["title"]
    if problem:
        title += f" — Problem {number}: " + problem["title"]
    note = (
        f"Case {record['case_id']}; revision {record['revision']}; "
        f"{review_status(record)}. "
        "Assessment is limited to the inspected claims. "
        f"Versioned record: {record_url(record, base)}"
    )
    analysis = _formats(
        {
            "kind": "analysis",
            "key": record["case_id"]
            + f"-r{record['revision']}"
            + (f"-p{number}" if number else ""),
            "authors": analysis_authors(reader),
            "title": title,
            "container": "ELVIA",
            "year": record["created_at"][:4],
            "url": url,
            "note": note,
        }
    )
    original = original_citation(record, reader)
    brief = finding_brief(record, problem)
    lines = [
        title,
        "",
        "Original paper: " + original["plain"],
        "Source version: " + record["source"]["version"],
        "Source location: " + brief["location"],
        "",
        "Question: " + brief["question"],
        "Bounded finding:",
        *brief["answer"],
        "",
        "Recorded check:",
        *brief["evidence"],
        "",
        "Case-wide limitations:",
        *["- " + v for v in brief["limits"]],
    ]
    if problem and problem["assumptions"]:
        lines += ["Finding conditions:", *["- " + v for v in problem["assumptions"]]]
    lines += [
        "",
        "Review status: " + brief["status"],
        "Case: " + record["case_id"],
        f"Revision: {record['revision']}",
        "Record created: " + record["created_at"],
        "Permalink: " + url,
        "Versioned public record: " + record_url(record, base),
        "Canonical record SHA-256: " + record_digest(record),
        "The page follows the latest revision; "
        "the versioned record identifies this snapshot.",
    ]
    short = "\n".join(lines)
    full = lines + ["", "Analysis citation:", analysis["plain"]]
    if problem:
        full += [
            "",
            "Source claim (paraphrase):",
            *problem["claim"],
            "",
            "Full finding analysis:",
            *problem["analysis"],
            "",
            "Finding and scope:",
            *problem["result"],
        ]
        if problem.get("repair"):
            full += [
                "",
                problem["repair"]["heading"] + ":",
                *problem["repair"]["paragraphs"],
            ]
    else:
        full += [
            "",
            "Source claim:",
            record["proposition"]["claim"],
            "",
            "Actual review scope:",
            record["source"]["review_scope"],
            "",
            "Evidence and counterevidence:",
        ]
        for evidence in record["evidence"]:
            full += [
                f"{evidence['id']} ({evidence['stance']}; {evidence['method']}): "
                + evidence["description"]
            ]
    if report:
        full += ["", "Complete retained report:", "", *report]
    full += [
        "",
        "Source PDF SHA-256: " + record["audit"]["pdf_sha256"],
        "Repair verification: " + record["repair"]["verification_status"],
        "Author adoption: " + record["repair"]["adoption_status"],
    ]
    return {
        **{"analysis-" + key: value for key, value in analysis.items()},
        **{"original-" + key: value for key, value in original.items()},
        "ai-short": short,
        "ai-full": "\n".join(full),
    }
