"""The served manifest must include per-case manifests as well as evidence."""

import json

from website import build as builder


def test_website_root_manifest_keeps_nested_case_manifests(tmp_path, monkeypatch):
    def fixture_build(_records, output, **_kwargs):
        (output / "evidence/fictional-case").mkdir(parents=True)
        (output / "evidence/fictional-case/manifest.json").write_text(
            '{"synthetic": true}', encoding="utf-8"
        )
        (output / "data.json").write_text('{"records": []}', encoding="utf-8")
        return 0

    monkeypatch.setattr(builder, "build_site", fixture_build)
    output = tmp_path / "site"
    builder.build(output)
    for name in ("manifest.json", "integration-files.json"):
        manifest = json.loads((output / name).read_text("utf-8"))
        assert "evidence/fictional-case/manifest.json" in {
            row["path"] for row in manifest["files"]
        }
