"""Compile reviewed report sources and select exact article PDFs for a release.

This offline maintainer command never discovers website uploads or executes
paper code. The input index explicitly maps case IDs to retained article PDFs.
Tectonic runs with its untrusted-input restrictions and no shell execution.
"""

import argparse
import concurrent.futures
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from elvia.reader import record_digest, report_source
from elvia.storage import load_records


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def format_report(content):
    """Layout-only copy: preserve the maintained scientific source unchanged."""
    content = content.replace(
        r"\IfFontExistsTF{Latin Modern Math}{\setmathfont{Latin Modern Math}}"
        r"{\setmathfont{DejaVu Math TeX Gyre}}",
        r"\setmathfont{latinmodern-math.otf}",
    )
    content = content.replace(
        r"\begin{document}", "\\sloppy\n\\emergencystretch=3em\n\\begin{document}", 1
    )
    # unicode-math maps setminus to a glyph absent from this bundled font.
    # smallsetminus is the same set-difference operator, present as U+2216.
    content = re.sub(r"\\setminus\b", lambda _: r"\smallsetminus", content)

    def display(match):
        equation = match[1]
        if len(equation) > 130 and r"\qquad" in equation and r"\begin" not in equation:
            return (
                r"\[\begin{gathered}"
                + equation.replace(r"\qquad", r"\\ ")
                + r"\end{gathered}\]"
            )
        return match[0]

    content = re.sub(r"\\\[(.*?)\\\]", display, content, flags=re.S)
    parts = re.split(r"(\\\[.*?\\\]|\\\(.*?\\\))", content, flags=re.S)
    for index in range(0, len(parts), 2):
        parts[index] = parts[index].replace(r"\_", r"\_\allowbreak{}")
        parts[index] = re.sub(
            r"(?<=commit )([a-f0-9]{40})(?![a-f0-9])",
            lambda m: r"\nolinkurl{" + m[1] + "}",
            parts[index],
        )
    return "".join(parts)


def build_library(records, article_index, output, tectonic):
    records, output = Path(records), Path(output)
    entries = load_records(records)
    latest = {record["case_id"]: record for _, record in entries}
    index = json.loads(Path(article_index).read_text("utf-8"))
    if set(index) != set(latest):
        raise ValueError("article index must cover exactly the selected collection")
    originals = {}
    for case, record in latest.items():
        path = Path(index[case]).resolve(strict=True)
        if sha(path) != record["audit"]["pdf_sha256"]:
            raise ValueError(f"article identity mismatch: {case}")
        originals[case] = path
    output.mkdir(parents=True, exist_ok=False)
    (output / "logs").mkdir()

    def compile_report(pair):
        case, record = pair
        source = report_source(record, records.parent)
        content = source.read_text("utf-8")
        formatted = format_report(content)
        destination = output / case
        destination.mkdir()
        with tempfile.TemporaryDirectory(prefix="elvia-report-") as temporary:
            build_source = Path(temporary) / "report.tex"
            build_source.write_text(formatted, encoding="utf-8")
            result = subprocess.run(
                [
                    str(tectonic),
                    "--untrusted",
                    "--keep-logs",
                    "--outdir",
                    str(destination),
                    str(build_source),
                ],
                capture_output=True,
                timeout=120,
                check=False,
            )
        (output / "logs" / f"{case}.log").write_bytes(result.stdout + result.stderr)
        report = destination / "report.pdf"
        if result.returncode != 0 or not report.is_file():
            raise ValueError(f"report compilation failed: {case}")
        latex_log = destination / "report.log"
        if latex_log.exists():
            shutil.move(str(latex_log), output / "logs" / f"{case}-tex.log")
        article = destination / "original article.pdf"
        shutil.copyfile(originals[case], article)
        return case, {
            "revision": record["revision"],
            "record_sha256": record_digest(record),
            "article": {
                "path": article.relative_to(output).as_posix(),
                "sha256": sha(article),
            },
            "report": {
                "path": report.relative_to(output).as_posix(),
                "sha256": sha(report),
            },
            "report_source_sha256": sha(source),
            "compiled_source_sha256": hashlib.sha256(formatted.encode()).hexdigest(),
            "revisions": [],
        }

    completed, errors = {}, []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(compile_report, pair): pair[0] for pair in latest.items()}
        for job in concurrent.futures.as_completed(jobs):
            try:
                case, row = job.result()
                completed[case] = row
            except Exception as exc:
                errors.append({"case_id": jobs[job], "error": str(exc)})
            if (len(completed) + len(errors)) % 50 == 0:
                print(
                    f"Reports: {len(completed)} compiled; {len(errors)} failures",
                    flush=True,
                )
    report = {"compiled": len(completed), "errors": errors}
    (output / "logs/build.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    (output / "reader-files.json").write_text(
        json.dumps(
            {"format_version": 1, "cases": dict(sorted(completed.items()))}, indent=2
        )
        + "\n",
        encoding="utf-8",
    )
    if errors:
        raise ValueError(
            f"{len(errors)} reports failed; inspect logs before publishing"
        )
    return len(completed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--article-index", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tectonic", type=Path, required=True)
    args = parser.parse_args()
    print(
        build_library(
            args.records.resolve(),
            args.article_index,
            args.output.resolve(),
            args.tectonic.resolve(),
        )
    )
