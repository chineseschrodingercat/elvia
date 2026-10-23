"""Transactional attachment ceiling, including every retained revision."""

TABLES = (
    "packages",
    "source_files",
    "revision_files",
    "amendments",
    "contribution_files",
)
QUOTA = 200_000_000_000
DISK_RESERVE = 2_000_000_000


def install_limits(db, quota=QUOTA):
    if not isinstance(quota, int) or quota <= 0:
        raise ValueError("A positive byte quota is required")
    total = " + ".join(
        f"(SELECT COALESCE(SUM(length(body)),0) FROM {table})" for table in TABLES
    )
    for table in TABLES:
        for event in ("INSERT", "UPDATE"):
            old = (
                f"COALESCE((SELECT length(body) FROM {table} WHERE id=NEW.id),0)"
                if event == "INSERT"
                else "COALESCE(length(OLD.body),0)"
            )
            db.execute(f"DROP TRIGGER IF EXISTS elvia_quota_{table}_{event}")
            db.execute(f"""CREATE TRIGGER elvia_quota_{table}_{event}
                BEFORE {event} ON {table}
                WHEN ({total}) + COALESCE(length(NEW.body),0) - {old} > {quota}
                  OR elvia_storage_ok(COALESCE(length(NEW.body),0)) != 1
                BEGIN SELECT RAISE(ABORT, 'ELVIA_STORAGE_QUOTA'); END""")
