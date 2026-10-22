"""Run against an installed wheel, with network denied and model keys removed.

Invoke with the fresh environment's Python, from any working directory.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from elvia.site import ASSETS, FONT_HASHES, MATH_HASHES


def main():
    with tempfile.TemporaryDirectory(prefix="elvia-wheel-smoke-") as name:
        root = Path(name)
        guard = root / "guard"
        guard.mkdir()
        # Imported by every child interpreter before the installed CLI loads.
        (guard / "sitecustomize.py").write_bytes(
            b"import sys\n"
            b"def deny_network(event, args):\n"
            b"    if event.startswith('socket.'):\n"
            b"        raise RuntimeError('Network disabled for ELVIA wheel smoke')\n"
            b"sys.addaudithook(deny_network)\n"
        )
        environment = os.environ.copy()
        for key in list(environment):
            if key.endswith(("API_KEY", "_TOKEN")):
                environment.pop(key)
        environment.update(
            PYTHONPATH=str(guard), PYTHONIOENCODING="utf-8", UV_OFFLINE="1"
        )
        probe = subprocess.run(
            [sys.executable, "-c", "import socket; socket.socket()"],
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert probe.returncode != 0 and "Network disabled" in probe.stderr
        executable = Path(sys.executable).parent / (
            "elvia.exe" if os.name == "nt" else "elvia"
        )
        if not executable.is_file():
            raise AssertionError(f"Installed console script missing: {executable}")

        def run(*args, module=False):
            command = [sys.executable, "-m", "elvia"] if module else [str(executable)]
            result = subprocess.run(
                command + list(args),
                cwd=root,
                env=environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30,
            )
            if result.returncode:
                raise AssertionError(result.stderr)
            print(result.stdout.strip())

        run("demo", "--output", "demo-output")
        run("validate", "demo-output/records")
        record_path = next((root / "demo-output/records").glob("*.json"))
        run("validate", str(record_path), module=True)
        run(
            "index",
            "rebuild",
            "--records",
            "demo-output/records",
            "--db",
            "demo-output/index.sqlite",
        )
        run("export", "demo-output/records", "--output", "demo-output/export")
        run("validate", "demo-output/export/records")
        run("site", "build", "--records", "demo-output/records", "--output", "atlas")
        atlas = root / "atlas"
        # The installed assets must render even an empty public selection;
        # synthetic demonstrations must never enter public scientific counts.
        assert json.loads((atlas / "data.json").read_text("utf-8"))["case_count"] == 0
        assert json.loads((atlas / "data.json").read_text("utf-8"))["case_notes"] == {}
        for asset in (*ASSETS, "data.js"):
            assert (atlas / asset).stat().st_size > 0
        css = (atlas / "atlas.css").read_text("utf-8")
        for asset, expected in FONT_HASHES.items():
            assert hashlib.sha256((atlas / asset).read_bytes()).hexdigest() == expected
            if asset.endswith(".woff2"):
                assert f'url("{asset}")' in css
        assert "https://" not in css
        for asset, expected in MATH_HASHES.items():
            assert hashlib.sha256((atlas / asset).read_bytes()).hexdigest() == expected
        assert 'src="vendor/katex/katex.min.js"' in (atlas / "index.html").read_text(
            "utf-8"
        )
        assert "font-src 'self'" in (atlas / "index.html").read_text("utf-8")
        site_manifest = json.loads((atlas / "manifest.json").read_text("utf-8"))
        for artifact in site_manifest["files"]:
            assert (
                hashlib.sha256((atlas / artifact["path"]).read_bytes()).hexdigest()
                == (artifact["sha256"])
            )
        exported = root / "demo-output/export"
        record = json.loads(record_path.read_text("utf-8"))
        assert record["adjudication"]["status"] == "pending"
        assert record["human_reviews"] == []
        assert record["runs"][0]["model"] is None
        assert (exported / "records" / record_path.name).read_bytes() == (
            record_path.read_bytes()
        )
        manifest = json.loads((exported / "manifest.json").read_text("utf-8"))
        for artifact in manifest["files"]:
            assert (
                hashlib.sha256((exported / artifact["path"]).read_bytes()).hexdigest()
                == (artifact["sha256"])
            )
        print("Installed-wheel offline smoke passed; network denied, no model keys.")


if __name__ == "__main__":
    main()
