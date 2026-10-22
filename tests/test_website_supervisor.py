import json

import pytest

from website.supervisor import load_config


def test_supervisor_rejects_repository_state_and_missing_credentials(tmp_path):
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"data_dir": str(tmp_path)}))
    with pytest.raises(ValueError):
        load_config(config)


def test_supervisor_rejects_linked_config(tmp_path):
    original = tmp_path / "original.json"
    original.write_text("{}")
    target = tmp_path / "link.json"
    try:
        target.symlink_to(original)
    except OSError:
        pytest.skip("This Windows account cannot create symlinks")
    with pytest.raises(ValueError):
        load_config(target)
