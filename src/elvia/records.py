"""Read-only structural, workflow and local artifact validation.

Human declarations are checked for consistency, never authenticated or certified.
"""

import hashlib
import json
import math
import re
from datetime import datetime
from importlib.resources import files
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker


def _timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})",
        value,
    ):
        return False
    try:
        return datetime.fromisoformat(value.replace("z", "Z")).tzinfo is not None
    except ValueError:
        return False


def _location(parts):
    return "$" + "".join(
        f"[{part}]" if isinstance(part, int) else f".{part}" for part in parts
    )


def _artifacts(value, location="$"):
    if isinstance(value, dict):
        if set(value) == {"path", "sha256"}:
            yield location, value
        else:
            for key, item in value.items():
                yield from _artifacts(item, f"{location}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _artifacts(item, f"{location}[{index}]")


def _safe_relative(path):
    """Use portable forward-slash relative paths on every host platform."""
    return (
        "\\" not in path
        and not PurePosixPath(path).is_absolute()
        and not PureWindowsPath(path).drive
        and ".." not in PurePosixPath(path).parts
        and path not in (".", "")
        and ":" not in path
    )


def validate_record(record: dict, root: Path | None = None) -> list[str]:
    """Return located errors; root enables existence/hash and symlink checks.

    With root=None this checks structure, declarations and portable path syntax
    only. It makes no claim that the referenced files exist.
    """
    schema = json.loads(
        files("elvia").joinpath("schema/record.schema.json").read_text("utf-8")
    )
    checker = FormatChecker()
    checker.checks("date-time")(_timestamp)
    validator = Draft202012Validator(schema, format_checker=checker)
    schema_errors = list(validator.iter_errors(record))
    errors = [
        f"{_location(error.absolute_path)}: {error.message}" for error in schema_errors
    ]
    if any(
        error.validator not in {"pattern", "format", "minLength", "enum", "const"}
        for error in schema_errors
    ):
        return errors

    for field in ("revision", "previous_revision"):
        value = record[field]
        if value is not None and type(value) is not int:
            errors.append(f"$.{field}: must be a Python integer, not a float")
    if record["previous_revision"] != (
        None if record["revision"] == 1 else record["revision"] - 1
    ):
        errors.append("$.previous_revision: must identify the preceding revision")

    if "audit" in record:
        for field in ("landing_url", "pdf_url"):
            value = record["audit"][field]
            try:
                url = urlsplit(value)
                safe = (
                    url.scheme == "https"
                    and bool(url.hostname)
                    and url.username is None
                    and url.password is None
                    and "\\" not in value
                    and not any(char.isspace() or ord(char) < 32 for char in value)
                )
                # Accessing port also detects malformed netlocs.
                _ = url.port
            except ValueError:
                safe = False
            if not safe:
                errors.append(f"$.audit.{field}: requires a safe HTTPS source URL")
        if type(record["audit"]["year"]) is not int:
            errors.append("$.audit.year: must be a Python integer, not a float")

    evidence_ids = [item["id"] for item in record["evidence"]]
    if len(set(evidence_ids)) != len(evidence_ids):
        errors.append("$.evidence: duplicate id")
    run_ids = [run["id"] for run in record["runs"]]
    if len(set(run_ids)) != len(run_ids):
        errors.append("$.runs: duplicate id")
    identities = set()
    for i, review in enumerate(record["human_reviews"]):
        identity = review["reviewer_id"].strip().casefold()
        if identity in identities:
            errors.append(f"$.human_reviews[{i}].reviewer_id: duplicate identity")
        identities.add(identity)
        if not set(review["evidence_refs"]).issubset(evidence_ids):
            errors.append(f"$.human_reviews[{i}].evidence_refs: unknown evidence id")

    status = record["adjudication"]["status"]
    if "source_update" in record and (
        status != "pending"
        or record["human_reviews"]
        or record["repair"]["adoption_status"] != "not_requested"
        or record["repair"]["verification_status"] not in {"not_proposed", "pending"}
        or record["repair"]["verification_refs"]
    ):
        errors.append(
            "$.source_update: new source inspection must be pending without "
            "inherited human reviews, repair verification or adoption"
        )
    if (
        record["revision"] == 1
        and record["concern"]["origin"] == "ai"
        and status != "pending"
    ):
        errors.append("$.adjudication.status: an initial AI finding must be pending")
    agreeing = [
        review
        for review in record["human_reviews"]
        if review["decision"] == status
        and review["role"] != "author"
        and review["evidence_refs"]
    ]
    if status in {"confirmed", "rejected"} and not agreeing:
        errors.append(
            "$.human_reviews: a final decision requires agreeing human review"
        )
    concern = record["concern"]
    if status == "confirmed" and (
        concern["severity"] in {"major", "critical"}
        or concern["impact"] == "main_result"
    ):
        independent = {
            review["reviewer_id"].strip().casefold()
            for review in agreeing
            if review["independent"]
            and review["domain_review"]
            and review["role"] == "domain_reviewer"
        }
        if len(independent) < 2:
            errors.append(
                "$.human_reviews: major/main-result confirmation requires two distinct "
                "humans declaring independent domain review and agreement"
            )

    repair = record["repair"]
    if not set(repair["verification_refs"]).issubset(evidence_ids):
        errors.append("$.repair.verification_refs: unknown evidence id")
    if repair["verification_status"] != "not_proposed" and repair["content"] is None:
        errors.append("$.repair.content: required for a proposed repair")
    if repair["verification_status"] == "verified" and not repair["verification_refs"]:
        errors.append("$.repair.verification_refs: verified repair requires evidence")
    if repair["adoption_status"] == "adopted" and repair["content"] is None:
        errors.append("$.repair.adoption_status: adoption requires repair content")
    for i, run in enumerate(record["runs"]):
        if run["cost_usd"] is not None and not math.isfinite(run["cost_usd"]):
            errors.append(f"$.runs[{i}].cost_usd: must be finite or null")
        if not (_timestamp(run["started_at"]) and _timestamp(run["ended_at"])):
            continue
        if datetime.fromisoformat(run["ended_at"].upper()) < datetime.fromisoformat(
            run["started_at"].upper()
        ):
            errors.append(f"$.runs[{i}].ended_at: precedes started_at")

    for location, artifact in _artifacts(record):
        path = artifact["path"]
        if not _safe_relative(path):
            errors.append(
                f"{location}.path: must be a portable relative path without .."
            )
            continue
        if root is not None:
            try:
                resolved_root = Path(root).resolve(strict=True)
                resolved = (resolved_root / path).resolve(strict=True)
                if not resolved.is_relative_to(resolved_root):
                    errors.append(f"{location}.path: artifact escapes dataset root")
                elif not resolved.is_file():
                    errors.append(f"{location}.path: artifact is not a regular file")
                elif (
                    hashlib.sha256(resolved.read_bytes()).hexdigest()
                    != artifact["sha256"]
                ):
                    errors.append(f"{location}.sha256: artifact hash mismatch")
            except (OSError, RuntimeError) as exc:
                errors.append(f"{location}.path: cannot read artifact ({exc})")
    return errors
