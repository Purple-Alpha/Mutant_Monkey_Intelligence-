from __future__ import annotations

import json
from pathlib import Path

from scripts.chaos_lab_provisioner import authority_fingerprint, snapshot_authority_fingerprint


def _seed_authority(root: Path) -> None:
    (root / "tasks.json").write_text('{"tasks": []}', encoding="utf-8")
    staging = root / "mmi/project_brain/status"
    staging.mkdir(parents=True)
    (staging / "MMI_PIPE_STAGING.json").write_text('{"pipe": "LOADED"}', encoding="utf-8")


def test_snapshot_overwrites_stale_fingerprint(tmp_path: Path) -> None:
    authority = tmp_path / "authority"
    authority.mkdir()
    _seed_authority(authority)

    ev = tmp_path / "lab" / "m2_test" / "EVIDENCE"
    ev.mkdir(parents=True)
    stale = {"files": {"tasks.json": {"sha256": "deadbeef"}}}
    (ev / "authority_fingerprint_before.json").write_text(json.dumps(stale), encoding="utf-8")

    fp = snapshot_authority_fingerprint(ev, authority, operation="mesh")
    on_disk = json.loads((ev / "authority_fingerprint_before.json").read_text(encoding="utf-8"))
    mesh_disk = json.loads((ev / "authority_fingerprint_before_mesh.json").read_text(encoding="utf-8"))

    assert fp["files"] == authority_fingerprint(authority)["files"]
    assert on_disk["files"] == fp["files"]
    assert mesh_disk["files"] == fp["files"]
    assert on_disk["files"]["tasks.json"]["sha256"] != "deadbeef"
