"""Snapshot-bound research fields for discovery, separate from scientific records."""

from elvia.reader import record_digest

FIELDS = (
    "Mathematics",
    "Biological science",
    "Computer science",
    "Chemistry",
    "Others",
)


def prepare_research_fields(records, catalog=None):
    """Default unclassified/new revisions to Others; reject same-revision drift."""
    if catalog is None:
        catalog = {"format_version": 1, "cases": {}}
    if (
        not isinstance(catalog, dict)
        or type(catalog.get("format_version")) is not int
        or catalog["format_version"] != 1
        or not isinstance(catalog.get("cases"), dict)
    ):
        raise ValueError("unsupported research field catalog")
    selected = {}
    for record in records:
        case = record["case_id"]
        selected[case] = "Others"
        row = catalog["cases"].get(case)
        if row is None:
            continue
        if not isinstance(row, dict) or type(row.get("revision")) is not int:
            raise ValueError("research field requires a snapshot revision")
        if row["revision"] != record["revision"]:
            continue
        if row.get("record_sha256") != record_digest(record):
            raise ValueError("research field does not match scientific snapshot")
        if row.get("field") not in FIELDS:
            raise ValueError("unknown research field")
        selected[case] = row["field"]
    return selected
