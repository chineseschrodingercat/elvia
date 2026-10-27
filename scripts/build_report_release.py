"""Build a new explicit PDF library, reusing only unchanged accepted reports.

Only maintained report TeX is compiled with Tectonic's untrusted-input mode.
Original article PDFs and published revisions are selected by the old manifest;
directories, website uploads and author programs are never discovered/executed.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import hashlib
import json
import re
import runpy
import shutil
import subprocess
from pathlib import Path

from elvia.reader import _bytes, _file, record_digest, report_source
from elvia.storage import load_records


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, value):
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_release(entries, baseline, output, tectonic, *, workers=4):
    """Use validated (record, dataset-root) pairs and a complete baseline library."""
    baseline, output = Path(baseline).resolve(), Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError("report publication requires a new output directory")
    if output.resolve().is_relative_to(baseline):
        raise ValueError("new report library must be outside its baseline")
    manifest = json.loads((baseline / "reader-files.json").read_text("utf-8"))
    if manifest.get("format_version") != 1:
        raise ValueError("unsupported baseline library")
    cases = manifest["cases"]
    prepared = {}
    for record, dataset in entries:
        case = record["case_id"]
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,79}", case) or case in prepared:
            raise ValueError("invalid or duplicate report case")
        row = cases.get(case)
        if row is None or row["revision"] != record["revision"]:
            raise ValueError("baseline revision differs from selected snapshot")
        # All old members must still be their accepted bytes, even if a report
        # is about to be recompiled. This prevents a corrupt baseline hiding.
        original = _bytes(baseline, row["article"], pdf=True)
        if hashlib.sha256(original).hexdigest() != record["audit"]["pdf_sha256"]:
            raise ValueError("baseline article differs from inspected source")
        _bytes(baseline, row["report"], pdf=True)
        source = report_source(record, Path(dataset))
        changed = sha(source) != row["report_source_sha256"]
        if not changed and record_digest(record) != row["record_sha256"]:
            raise ValueError("snapshot changed without a corresponding report source")
        for revision in row.get("revisions", []):
            if revision.get("published") is not True:
                raise ValueError("unpublished revision in baseline reader library")
            for member in revision["files"]:
                _bytes(baseline, member, pdf=True)
        prepared[case] = (record, source, copy.deepcopy(row), changed)
    if set(cases) != set(prepared):
        raise ValueError("baseline must cover exactly the selected collections")
    formatter = runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "website/reader_library.py")
    )["format_report"]
    output.mkdir(parents=True)
    (output / "logs/compiled-sources").mkdir(parents=True)

    def produce(case):
        record, source, row, changed = prepared[case]
        destination = output / case
        destination.mkdir()
        article = destination / "original article.pdf"
        shutil.copyfile(_file(baseline, row["article"]["path"]), article)
        if sha(article) != record["audit"]["pdf_sha256"]:
            raise ValueError("article bytes changed during publication")
        report = destination / "report.pdf"
        source_bytes = source.read_bytes()
        current_source_hash = hashlib.sha256(source_bytes).hexdigest()
        expected_source_hash = next(
            item["artifact"]["sha256"]
            for item in record["evidence"]
            if item["artifact"]["path"].endswith("/report.tex")
        )
        if current_source_hash != expected_source_hash:
            raise ValueError("report source changed during publication")
        if changed:
            formatted = formatter(source_bytes.decode("utf-8")).encode("utf-8")
            build_dir = output / "logs/compiled-sources" / case
            build_dir.mkdir()
            actual_source = build_dir / "report.tex"
            actual_source.write_bytes(formatted)
            process = subprocess.run(
                [
                    str(tectonic),
                    "--untrusted",
                    "--keep-logs",
                    "--outdir",
                    str(destination),
                    str(actual_source),
                ],
                capture_output=True,
                timeout=180,
                check=False,
            )
            (output / "logs" / (case + ".log")).write_bytes(
                process.stdout + process.stderr
            )
            if process.returncode or not report.is_file():
                raise ValueError("report compilation failed; inspect private build log")
            latex_log = destination / "report.log"
            if latex_log.exists():
                shutil.move(str(latex_log), output / "logs" / (case + "-tex.log"))
            row["compiled_source_sha256"] = sha(actual_source)
        else:
            shutil.copyfile(_file(baseline, row["report"]["path"]), report)
            if sha(report) != row["report"]["sha256"]:
                raise ValueError("accepted report bytes changed during publication")
        # Published revision files keep their explicit names and hashes.
        for revision in row.get("revisions", []):
            for member in revision["files"]:
                old = _file(baseline, member["path"])
                new = destination / ("r" + str(revision["revision"])) / old.name
                new.parent.mkdir(exist_ok=True)
                shutil.copyfile(old, new)
                if sha(new) != member["sha256"]:
                    raise ValueError("published predecessor changed during publication")
                member["path"] = new.relative_to(output).as_posix()
        row.update(
            record_sha256=record_digest(record),
            report_source_sha256=current_source_hash,
            article={
                "path": article.relative_to(output).as_posix(),
                "sha256": sha(article),
            },
            report={
                "path": report.relative_to(output).as_posix(),
                "sha256": sha(report),
            },
        )
        _bytes(output, row["report"], pdf=True)
        return case, row, changed

    complete, errors, compiled = {}, [], 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        jobs = {pool.submit(produce, case): case for case in prepared}
        for future in concurrent.futures.as_completed(jobs):
            case = jobs[future]
            try:
                case, row, changed = future.result()
                complete[case] = row
                compiled += changed
            except Exception as exc:
                errors.append({"case_id": case, "error": str(exc)})
            if (len(complete) + len(errors)) % 25 == 0:
                print(
                    f"Reports: {len(complete)} ready, {compiled} compiled, "
                    f"{len(errors)} failed",
                    flush=True,
                )
    result = {
        "status": "passed" if not errors else "failed",
        "compiled": compiled,
        "reused": len(complete) - compiled,
        "errors": errors,
    }
    write_json(output / "logs/build.json", result)
    if errors:
        raise ValueError(
            "report release is incomplete; no reader manifest was published"
        )
    write_json(
        output / "reader-files.json",
        {"format_version": 1, "cases": dict(sorted(complete.items()))},
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--records", type=Path, nargs="+", required=True)
    parser.add_argument("--baseline-library", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tectonic", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4, choices=range(1, 9))
    args = parser.parse_args()
    selected = []
    for directory in args.records:
        selected.extend(
            (record, directory.parent) for _, record in load_records(directory)
        )
    print(
        json.dumps(
            build_release(
                selected,
                args.baseline_library,
                args.output,
                args.tectonic,
                workers=args.workers,
            )
        )
    )
